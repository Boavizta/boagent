import json
import math
import os
import time
import requests
import pytz
import pandas as pd

from datetime import datetime, timedelta
from subprocess import run
from typing import Dict, Any, Tuple, List, Optional
from croniter import croniter
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from boaviztapi_sdk.api.server_api import ServerApi
from boaviztapi_sdk.model.server_dto import ServerDTO
from utils import iso8601_or_timestamp_as_timestamp, format_prometheus_output, format_prometheus_metric, \
    get_boavizta_api_client, sort_ram, sort_disks
from config import settings
from database import create_database, get_session, get_engine, insert_metric, select_metric, \
    CarbonIntensity, add_from_scaphandre, get_most_recent_data, get_max, new_highlight_spikes, \
    setup_database


HARDWARE_FILE_PATH = settings.hardware_file_path
POWER_DATA_FILE_PATH = settings.power_file_path
PUBLIC_PATH = settings.public_path
ASSETS_PATH = settings.assets_path
DB_PATH = settings.db_path
DEFAULT_LIFETIME = settings.default_lifetime
SECONDS_IN_ONE_YEAR = settings.seconds_in_one_year
HARDWARE_CLI = settings.hardware_cli
AZURE_LOCATION = settings.azure_location
BOAVIZTAPI_ENDPOINT = settings.boaviztapi_endpoint
CARBON_AWARE_API_ENDPOINT = settings.carbon_aware_api_endpoint
CARBON_AWARE_API_TOKEN = settings.carbon_aware_api_token


def configure_static(app):
    app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="assets")


def configure_app():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description=settings.PROJECT_DESCRIPTION,
        contact={
            "name": "Boavizta Members",
            "url": "https://boavizta.org/en"
        },
        license_info={
            "name": "Apache-2.0"
        },
        openapi_tags=settings.TAGS_METADATA
    )
    configure_static(app)
    return app


app = configure_app()
items = {}

setup_database()


@app.get("/info", tags=["info"])
async def info():
    return {
        "seconds_in_one_year": SECONDS_IN_ONE_YEAR,
        "default_lifetime": DEFAULT_LIFETIME,
        "hardware_file_path": HARDWARE_FILE_PATH,
        "power_file_path": POWER_DATA_FILE_PATH,
        "hardware_cli": HARDWARE_CLI,
        "boaviztapi_endpoint": BOAVIZTAPI_ENDPOINT
    }


@app.get("/web", tags=["web"], response_class=HTMLResponse)
async def web():
    res = ""
    with open("{}/index.html".format(PUBLIC_PATH), 'r') as fd:
        res = fd.read()
    fd.close()
    return res


@app.get('/csv', tags=["csv"])
async def csv(data: str, since: str = "now", until: str = "24h", inwatt: bool = True) -> Response:
    start_date, stop_date = parse_date_info(since, until)


    '''session = get_session(DB_PATH)
    df = select_metric(session, data, start_date, stop_date)
    df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
    session.close()

    if data == "power" and inwatt:
        df['value'] = df['value'] / 1000.0

    return Response(
        content=df.to_csv(index=False),
        media_type="text/csv"
    )'''

    return Response(
            status_code=200,
            content="not implemented yet"
            )


@app.get("/yearly_embedded")
async def yearly_embedded():
    hardware_data = get_hardware_data(False)
    boaviztapi_data = query_machine_impact_data(
        model=None,
        configuration=generate_machine_configuration(hardware_data),
        usage={}
    )
    if "manufacturer" in boaviztapi_data:
        return boaviztapi_data["impacts"]["gwp"]["manufacturer"] / DEFAULT_LIFETIME
    else:
        return Response(
                status_code=200,
                content="SSD/HDD manufacturer not recognized by BoaviztAPI yet."
                )

@app.get("/yearly_operational")
async def operational_impact_yearly():
    since = "now"
    until = "24h"
    start_date, stop_date = parse_date_info(since, until)
    session = get_session(DB_PATH)

    df_power = select_metric(session, 'power', start_date, stop_date)
    df_power['power_watt'] = df_power['value'] / 1000
    # df_power = df_power.drop(columns=['value'])
    df_power = df_power.set_index('timestamp')

    df_carbon_intensity = select_metric(session, 'carbonintensity', start_date, stop_date)
    df_carbon_intensity['carbon_intensity_g_per_watt_second'] = df_carbon_intensity['value'] / (1000 * 3600)

    yearly_operational = (df_power['power_watt'].mean()*df_carbon_intensity["carbon_intensity_g_per_watt_second"].mean())*(3600*24*365) # in gCO2eq

    return round(yearly_operational/1000.0)  # in kgCO2eq


@app.get('/last_data')
async def last_data(table_name: str) -> Response:
    data = get_most_recent_data(table_name)
    if data is None:
        return Response(status_code=404)
    else:
        df = pd.DataFrame([[data.timestamp, data.value]], columns=['timestamp', 'value'])
        return Response(
            content=df.to_csv(index=False),
            media_type="text/csv",
            status_code=200
        )


@app.get("/metrics", tags=["metrics"])
async def metrics(start_time: str = "0.0", end_time: str = "0.0", verbose: bool = False, output: str = "json",
                  location: str = None, measure_power: bool = True, lifetime: float = DEFAULT_LIFETIME,
                  fetch_hardware: bool = False):
    return Response(
        content=format_prometheus_output(
            get_metrics(
                iso8601_or_timestamp_as_timestamp(start_time),
                iso8601_or_timestamp_as_timestamp(end_time),
                verbose, location, measure_power, lifetime, fetch_hardware
            )
        ), media_type="plain-text"
    )


@app.get("/query", tags=["query"])
async def query(start_time: str = "0.0", end_time: str = "0.0", verbose: bool = False, location: str = None,
                measure_power: bool = True, lifetime: float = DEFAULT_LIFETIME, fetch_hardware: bool = False):
    """
    start_time: Start time for evaluation. Accepts either UNIX Timestamp or ISO8601 date format. \n
    end_time: End time for evaluation. Accepts either UNIX Timestamp or ISO8601 date format. \n
    verbose: Get detailled metrics with extra information.\n
    location: Country code to configure the local electricity grid to take into account.\n
    measure_power: Get electricity consumption metrics from Scaphandre or not.\n
    lifetime: Full lifetime of the machine to consider.\n
    fetch_hardware: Regenerate hardware.json file with current machine hardware or not.\n
    """
    return get_metrics(
        iso8601_or_timestamp_as_timestamp(start_time),
        iso8601_or_timestamp_as_timestamp(end_time),
        verbose, location, measure_power, lifetime, fetch_hardware
    )


@app.get("/last_info")
async def actual_intensity():
    res = {"power": get_most_recent_data("power"), "carbonintensity": get_most_recent_data("carbonintensity"),
           "cpu": get_most_recent_data("cpu"), "ram": get_most_recent_data("ram")}

    return res


@app.get("/max_info")
async def actual_intensity():
    res = {"power": get_max("power"), "carbonintensity": get_max("carbonintensity"), "ram": get_max("ram"),
           "cpu": get_max("cpu")}
    return res


@app.get("/all_cron")
async def actual_intensity():
    return get_cron_info()


@app.get("/update")
async def update():
    response = query_electricity_carbon_intensity()
    info = parse_electricity_carbon_intensity(response)
    session = get_session(DB_PATH)

    add_from_scaphandre(session)  # lots lot insert_metric called here
    if info['value'] > 0:
        insert_metric(session=session, metric_name='carbonintensity', timestamp=info['timestamp'], value=info['value'])
    session.commit()
    session.close()
    return Response(status_code=200)


@app.get("/carbon_intensity_forecast")
async def carbon_intensity_forecast(since: str = "now", until: str = "24h") -> Response:
    df = carbon_intensity_forecast_data(since, until)
    df = new_highlight_spikes(df, "value")
    return Response(
        content=df.to_csv(index=False),
        media_type="text/csv"
    )


def carbon_intensity_forecast_data(since: str, until: str) -> pd.DataFrame:
    start_date, stop_date = parse_date_info(since, until, forecast=True)
    start_date, stop_date = start_date, stop_date

    start_date = upper_round_date_minutes_with_base(start_date, base=5)
    response = query_forecast_electricity_carbon_intensity(start_date, stop_date)
    forecasts = parse_forecast_electricity_carbon_intensity(response)
    return pd.DataFrame(forecasts)


@app.get("/carbon_intensity")
async def carbon_intensity(since: str = "now", until: str = "24h") -> Response:
    _, stop_date = parse_date_info(since, until, forecast=True)
    start_date, now = parse_date_info(since, until, forecast=False)

    session = get_session(DB_PATH)
    df_history = select_metric(session, 'carbonintensity', start_date, now)

    now = upper_round_date_minutes_with_base(now, base=5)
    response = query_forecast_electricity_carbon_intensity(now, stop_date)
    forecasts = parse_forecast_electricity_carbon_intensity(response)
    df_forecast = pd.DataFrame(forecasts)
    df_forecast['timestamp'] = df_forecast['timestamp'].apply(
        lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))

    df = pd.concat([df_history, df_forecast])
    df = df[['timestamp', 'value']]
    df = new_highlight_spikes(df, "value")
    df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
    return Response(
        content=df.to_csv(index=False),
        media_type="text/csv"
    )


@app.get("/init_carbon_intensity")
async def init_carbon_intensity():
    engine = get_engine(DB_PATH)
    CarbonIntensity.__table__.drop(engine)
    create_database(engine)

    session = get_session(DB_PATH)
    now = datetime.utcnow()
    curr_date = now - timedelta(hours=24)

    while curr_date < now:
        # TODO: make bulk select in boaviztapi
        response = query_electricity_carbon_intensity(curr_date, curr_date + timedelta(minutes=5))
        info = parse_electricity_carbon_intensity(response)
        insert_metric(session, 'carbonintensity', info['timestamp'], info['value'])
        curr_date += timedelta(minutes=5)
    session.commit()


@app.get("/impact")
async def impact(since: str = "now", until: str = "24h"):
    start_date, stop_date = parse_date_info(since, until)
    session = get_session(DB_PATH)

    df_power = select_metric(session, 'power', start_date, stop_date)
    df_power['power_watt'] = df_power['value'] / 1000
    df_power = df_power.drop(columns=['value'])
    df_power = df_power.set_index('timestamp')
    df_power = df_power.resample('1s').mean()
    df_power = df_power.fillna(method='ffill')

    df_carbon_intensity = select_metric(session, 'carbonintensity', start_date, stop_date)
    df_carbon_intensity['carbon_intensity_g_per_watt_second'] = df_carbon_intensity['value'] / (1000 * 3600)
    df_carbon_intensity = df_carbon_intensity.drop(columns=['value'])
    df_carbon_intensity = df_carbon_intensity.set_index('timestamp')
    df_carbon_intensity = df_carbon_intensity.resample('1s').mean()
    df_carbon_intensity = df_carbon_intensity.fillna(method='ffill')
    df = df_power.merge(df_carbon_intensity, on='timestamp')
    df['operational'] = df['power_watt'] * df['carbon_intensity_g_per_watt_second']

    hardware_data = get_hardware_data(False)
    boaviztapi_data = query_machine_impact_data(
        model=None,
        configuration=generate_machine_configuration(hardware_data),
        usage={}
    )

    if "manufacturer" in boaviztapi_data:
        yearly_embedded_emissions = boaviztapi_data["impacts"]["gwp"]["manufacturer"] / DEFAULT_LIFETIME

        df['embedded'] = yearly_embedded_emissions  / (3.6*24*365) # from kgCO2eq/year to gCO2eq/s
        df = df.drop(columns=['power_watt', 'carbon_intensity_g_per_watt_second']).reset_index()
        return Response(
            content=df.to_csv(index=False),
            media_type="text/csv"
        )

def get_metrics(start_time: float, end_time: float, verbose: bool, location: str, measure_power: bool, lifetime: float,
                fetch_hardware: bool = False):

    now: float = time.time()
    if start_time and end_time:
        ratio = (end_time - start_time) / (lifetime * SECONDS_IN_ONE_YEAR)
    else:
        ratio = 1.0
    if start_time == 0.0:
        start_time = now - 3600
    if end_time == 0.0:
        end_time = now
    if end_time - start_time >= lifetime * SECONDS_IN_ONE_YEAR:
        lifetime = (end_time - start_time) / float(SECONDS_IN_ONE_YEAR)

    hardware_data = get_hardware_data(fetch_hardware)

    res = {"emissions_calculation_data": {}}

    host_avg_consumption = None

    if measure_power:
        power_data = get_power_data(start_time, end_time)
        host_avg_consumption = power_data["host_avg_consumption"]
        if "warning" in power_data:
            res["emissions_calculation_data"]["energy_consumption_warning"] = power_data["warning"]

    boaviztapi_data = query_machine_impact_data(
        model=None,
        configuration=generate_machine_configuration(hardware_data),
        usage=format_usage_request(start_time, end_time, host_avg_consumption, location)
    )

    if measure_power:
        res["total_operational_emissions"] = {
            "value": boaviztapi_data["impacts"]["gwp"]["use"],
            "description": "GHG emissions related to usage, from start_time to end_time.",
            "type": "gauge",
            "unit": "kg CO2eq",
            "long_unit": "kilograms CO2 equivalent"
        }
        res["total_operational_abiotic_resources_depletion"] = {
            "value": boaviztapi_data["impacts"]["adp"]["use"],
            "description": "Abiotic Resources Depletion (minerals & metals, ADPe) due to the usage phase.",
            "type": "gauge",
            "unit": "kgSbeq",
            "long_unit": "kilograms Antimony equivalent"
        }
        res["total_operational_primary_energy_consumed"] = {
            "value": boaviztapi_data["impacts"]["pe"]["use"],
            "description": "Primary Energy consumed due to the usage phase.",
            "type": "gauge",
            "unit": "MJ",
            "long_unit": "Mega Joules"
        }       
        res["start_time"] = {
            "value": start_time,
            "description": "Start time for the evaluation, in timestamp format (seconds since 1970)",
            "type": "counter",
            "unit": "s",
            "long_unit": "seconds"
        }
        res["end_time"] = {
            "value": end_time,
            "description": "End time for the evaluation, in timestamp format (seconds since 1970)",
            "type": "counter",
            "unit": "s",
            "long_unit": "seconds"
        }

        if "manufacturer" in boaviztapi_data:
            res["calculated_emissions"] = {
                "value": boaviztapi_data["impacts"]["gwp"]["manufacturer"] * ratio + boaviztapi_data["impacts"]["gwp"]["use"],
                "description": "Total Green House Gaz emissions calculated for manufacturing and usage phases, between "
                               "start_time and end_time",
                "type": "gauge",
                "unit": "kg CO2eq",
                "long_unit": "kilograms CO2 equivalent"
            }
            res["embedded_emissions"] = {
                "value": boaviztapi_data["impacts"]["gwp"]["manufacturer"] * ratio,
                "description": "Embedded carbon emissions (manufacturing phase)",
                "type": "gauge",
                "unit": "kg CO2eq",
                "long_unit": "kilograms CO2 equivalent"
            }
            res["embedded_abiotic_resources_depletion"] = {
                "value": boaviztapi_data["impacts"]["adp"]["manufacturer"] * ratio,
                "description": "Embedded abiotic ressources consumed (manufacturing phase)",
                "type": "gauge",
                "unit": "kg Sbeq",
                "long_unit": "kilograms ADP equivalent"
            }
            res["embedded_primary_energy"] = {
                "value": boaviztapi_data["impacts"]["pe"]["manufacturer"] * ratio,
                "description": "Embedded primary energy consumed (manufacturing phase)",
                "type": "gauge",
                "unit": "MJ",
                "long_unit": "Mega Joules"
            }

        if "USAGE" in boaviztapi_data:
            res["emissions_calculation_data"] = {
                "average_power_measured": {
                    "value": host_avg_consumption,
                    "description": "Average power measured from start_time to end_time",
                    "type": "gauge",
                    "unit": "W",
                    "long_unit": "Watts"
                },
                "electricity_carbon_intensity": {
                    "value": boaviztapi_data["verbose"]["USAGE"]["gwp_factor"]["value"],
                    "description": "Carbon intensity of the electricity mix. Mix considered : {}".format(location),
                    "type": "gauge",
                    "unit": "kg CO2eq / kWh",
                    "long_unit": "Kilograms CO2 equivalent per KiloWattHour"
                }
            }
            usage_location_status = boaviztapi_data["verbose"]["USAGE"]["usage_location"]["status"]
            if usage_location_status == "MODIFY":
                res["emissions_calculation_data"]["electricity_carbon_intensity"][
                    "description"] += "WARNING : The provided trigram doesn't match any existing country. So this result is " \
                                      "based on average European electricity mix. Be careful with this data. "
            elif usage_location_status == "SET":
                res["emissions_calculation_data"]["electricity_carbon_intensity"][
                    "description"] += "WARNING : As no information was provided about your location, this result is based on " \
                                      "average European electricity mix. Be careful with this data. "

    if verbose:
        res["emissions_calculation_data"]["raw_data"] = {
            "hardware_data": hardware_data,
            "resources_data": "not implemented yet",
            "boaviztapi_data": boaviztapi_data,
            "power_data": power_data,
            "start_time": start_time,
            "end_time": end_time
        }
    return res


def format_usage_request(start_time, end_time, host_avg_consumption=None, location=None):
    hours_use_time = (end_time - start_time) / 3600.0
    kwargs_usage = {
        "hours_use_time": hours_use_time
    }
    if location:
        kwargs_usage["usage_location"] = location
    if host_avg_consumption:
        kwargs_usage["hours_electrical_consumption"] = host_avg_consumption
    return kwargs_usage


def get_power_data(start_time, end_time):
    power_data = {}
    with open(POWER_DATA_FILE_PATH, 'r') as fd:
        # Get all items of the json list where start_time <= host.timestamp <= end_time
        data = json.load(fd)
        res = [e for e in data if start_time <= float(e['host']['timestamp']) <= end_time]
        power_data['raw_data'] = res
        power_data['host_avg_consumption'] = compute_average_consumption(res)
        if end_time - start_time <= 3600:
            power_data[
                'warning'] = "The time window is lower than one hour, but the energy consumption estimate is in " \
                             "Watt.Hour. So this is an extrapolation of the power usage profile on one hour. Be " \
                             "careful with this data. "
        return power_data


def get_timeseries_data(start_time, end_time):
    with open(POWER_DATA_FILE_PATH, 'r') as fd:
        # Get all items of the json list where start_time <= host.timestamp <= end_time
        data = json.load(fd)
        res = [e for e in data if start_time <= float(e['host']['timestamp']) <= end_time]
        power_data['raw_data'] = res
        power_data['host_avg_consumption'] = compute_average_consumption(res)
        if end_time - start_time <= 3600:
            power_data[
                'warning'] = "The time window is lower than one hour, but the energy consumption estimate is in " \
                             "Watt.Hour. So this is an extrapolation of the power usage profile on one hour. Be " \
                             "careful with this data. "
        return power_data


def compute_average_consumption(power_data):
    # Host energy consumption
    total_host = 0.0
    avg_host = 0.0
    if len(power_data) > 0:
        for r in power_data:
            total_host += float(r['host']['consumption'])

        avg_host = total_host / len(power_data) / 1000000.0  # from microwatts to watts

    return avg_host


def get_hardware_data(fetch_hardware: bool):
    data = {}
    if fetch_hardware:
        build_hardware_data()
    try:
        data = read_hardware_data()
    except Exception as e:
        build_hardware_data()
        data = read_hardware_data()
    return data


def read_hardware_data():
    with open(HARDWARE_FILE_PATH, 'r') as fd:
        data = json.load(fd)
    return data


def build_hardware_data():
    p = run([HARDWARE_CLI, "--output-file", HARDWARE_FILE_PATH])


def query_machine_impact_data(model: dict = None, configuration: dict = None, usage: dict = None):
    server_api = ServerApi(get_boavizta_api_client())

    server_impact = None

    if configuration:
        server_dto = ServerDTO(usage=usage, configuration=configuration)
        server_impact = server_api.server_impact_by_config_v1_server_post(server_dto=server_dto)
    elif model:
        server_dto = ServerDTO(usage=usage, model=model)
        server_impact = server_api.server_impact_by_model_v1_server_get(server_dto=server_dto)

    return server_impact


def generate_machine_configuration(hardware_data):
    config = {
        "cpu": {
            "units": len(hardware_data["cpus"]),
            "core_units": hardware_data['cpus'][0]["core_units"],
            "family": hardware_data['cpus'][0]['family']
            },
        "ram": sort_ram(hardware_data["rams"]),
        "disk": sort_disks(hardware_data["disks"]),
        "motherboard": hardware_data["mother_board"] if "mother_board" in hardware_data else {"units": 1},
        # TODO: improve once the API provides more detail input
        "power_supply": hardware_data["power_supply"] if "power_supply" in hardware_data else {"units": 1}
        # TODO: if cpu is a small one, guess that power supply is light/average weight of a laptops power supply ?
    }
    return config


def query_electricity_carbon_intensity(start_date: Optional[datetime] = None,
                                       stop_date: Optional[datetime] = None) -> Dict[str, Any]:
    url = BOAVIZTAPI_ENDPOINT + f'/v1/usage_router/gwp/current_intensity?location={AZURE_LOCATION}'
    start_date = start_date or (datetime.utcnow() - timedelta(minutes=5))
    stop_date = stop_date or datetime.utcnow()
    response = requests.post(url, json={
        "source": "carbon_aware_api",
        "url": CARBON_AWARE_API_ENDPOINT,
        "token": CARBON_AWARE_API_TOKEN,
        "start_date": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stop_date": stop_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    })
    return response.json()


def parse_electricity_carbon_intensity(carbon_aware_api_response: Dict[str, Any]):
    intensity_dict = carbon_aware_api_response['_value']
    if 'endTime' in intensity_dict and 'carbonIntensity' in intensity_dict:
        return {
            'timestamp': datetime.fromisoformat(intensity_dict['endTime']),
            'value': round(intensity_dict['carbonIntensity'], 3)
        }
    else:
        return {
            'timestamp': datetime.now(),
            'value': 0
        }


def query_forecast_electricity_carbon_intensity(start_date: datetime, stop_date: datetime) -> Dict[str, Any]:
    url = BOAVIZTAPI_ENDPOINT + f'/v1/usage_router/gwp/forecast_intensity?location={AZURE_LOCATION}'
    retry = 0
    while retry < 3:
        retry += 1
        try:
            response = requests.post(url, json={
                "source": "carbon_aware_api",
                "url": CARBON_AWARE_API_ENDPOINT,
                "token": CARBON_AWARE_API_TOKEN,
                "start_date": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "stop_date": stop_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            })
            return response.json()[0]
        except KeyError:
            response_err = response.json()
            if response_err['title'] == 'ArgumentException':
                errors = response_err['errors']
                if 'dataStartAt' in errors:
                    if len(errors['dataStartAt']) == 1:
                        error_msg = errors['dataStartAt'][0].split("'")
                        start_date = datetime.strptime(error_msg[1][:-10], '%m/%d/%Y %H:%M:%S')
                        stop_date = datetime.strptime(error_msg[3][:-10], '%m/%d/%Y %H:%M:%S')
                elif 'dataEndAt' in errors:
                    if len(errors['dataEndAt']) == 1:
                        error_msg = errors['dataEndAt'][0].split("'")
                        start_date = datetime.strptime(error_msg[1][:-10], '%m/%d/%Y %H:%M:%S')
                        stop_date = datetime.strptime(error_msg[3][:-10], '%m/%d/%Y %H:%M:%S')


def parse_forecast_electricity_carbon_intensity(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    forecasts = response['forecastData']
    results = []
    for item in forecasts:
        results.append({
            'timestamp': datetime.fromisoformat(item['timestamp']).strftime("%Y-%m-%dT%H:%M:%SZ"),
            'value': item['value']
        })
    return results


def parse_date_info(since: str, until: str, forecast: bool = False) -> Tuple[datetime, datetime]:
    if forecast:
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(hours=1)
    else:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=1)

    if since == 'now' and not forecast:
        end_date = datetime.utcnow()
    elif since == 'now' and forecast:
        start_date = datetime.utcnow()
    else:
        ValueError(f'unknown value since={since}')

    if until.endswith('d'):
        days = int(until.replace('d', ''))
        if forecast:
            end_date = start_date + timedelta(days=days)
        else:
            start_date = end_date - timedelta(days=days)
    if until.endswith('h'):
        hours = int(until.replace('h', ''))
        if forecast:
            end_date = start_date + timedelta(hours=hours)
        else:
            start_date = end_date - timedelta(hours=hours)
    elif until.endswith('m'):
        minutes = int(until.replace('m', ''))
        if forecast:
            end_date = start_date + timedelta(minutes=minutes)
        else:
            start_date = end_date - timedelta(minutes=minutes)
    else:
        ValueError(f'unknown value until={until}')

    return start_date.astimezone(pytz.UTC), end_date.astimezone(pytz.UTC)


def upper_round_date_minutes_with_base(date: datetime, base: int) -> datetime:
    delta_minutes = base * math.ceil((date.minute + 1) / base) - date.minute
    return date + timedelta(minutes=delta_minutes)


def get_cron_per_user():
    user = []
    with open("/etc/passwd", "r") as f:
        for line in f.readlines():
            user.append(line.split(":")[0])
        user.sort()
        cron_user = []
        for item in user:
            output = os.popen(f"crontab -u {item} -l").read()
            for line in output.splitlines():
                if line == f"no crontab for {item}":
                    break
                else:
                    cron_user.append(line)
        return cron_user


def get_all_cron():
    crons = []

    if os.geteuid() == 0:
        cron_user = get_cron_per_user()
        if cron_user:
            crons.append(cron_user)
    else:
        output = os.popen(f"crontab -l").read()
        for line in output.splitlines():
            if line != "" and (line[0].isdigit() or line[0] == "*"):
                crons.append(line)

    with open("/etc/crontab", "r") as f:
        for line in f.readlines():
            if line != "" and (line[0].isdigit() or line[0] == "*"):
                crons.append(line)
    return crons


def get_cron_info():
    crons_info = []
    base = datetime.today()
    cron_lines = get_all_cron()
    for cron in cron_lines:
        info = {}
        sched = ""
        for char in cron:
            if char.isdigit() or char == "*" or char == " " or char == "\t":
                sched += char
        info["next"] = croniter(sched, base).get_next(datetime).astimezone(pytz.UTC)
        info["previous"] = croniter(sched, base).get_prev(datetime).astimezone(pytz.UTC)
        info["job"] = cron.strip()
        crons_info.append(info)
    return crons_info


def event_is_in_bad_time(event, df: pd.DataFrame):
    df = df.set_index('timestamp')
    index = df.index.get_indexer([event], method='nearest')
    return df.iloc[index].peak.values[0] == 1


def compute_recommendations(since="now", until="24h"):
    start_date, stop_date = parse_date_info(since, until)
    session = get_session(DB_PATH)
    df_power = select_metric(session, 'power', start_date, stop_date)
    # df_power['timestamp'] = pd.to_datetime(df_power['timestamp'])
    df_history = select_metric(session, 'carbonintensity', start_date, stop_date)

    df_forecast = carbon_intensity_forecast_data(since, until)
    df_forecast['timestamp'] = df_forecast['timestamp'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))

    df_carbon_intensity = pd.concat([df_history, df_forecast])
    df_carbon_intensity['timestamp'] = df_carbon_intensity['timestamp'].apply(pytz.utc.localize)
    df_carbon_intensity = new_highlight_spikes(df_carbon_intensity, "value")

    recommendations = []
    crons = get_cron_info()
    for cron in crons:
        if event_is_in_bad_time(cron['next'], df_carbon_intensity):
            recommendations.append({
                'type': 'CRON',
                'execution_date': cron['next'],
                'preferred_execution_date': find_preferred_execution_date_in_future(df_forecast),
                'mode': 'forecast',
                'job': cron['job']
            })
        if event_is_in_bad_time(cron['previous'], df_carbon_intensity):
            recommendations.append({
                'type': 'CRON',
                'execution_date': datetime.strptime(str(cron['previous'])[:-6], '%Y-%m-%d %H:%M:%S'),
                'preferred_execution_date': find_preferred_execution_date_in_history(cron['previous'], df_power,
                                                                                     df_history),
                'mode': 'history',
                'job': cron['job']
            })
    return recommendations


def find_preferred_execution_date_in_future(df_forecast: pd.DataFrame):
    bests = df_forecast[df_forecast['value'] == df_forecast['value'].min()]
    return bests.iloc[0].timestamp


def find_preferred_execution_date_in_history(execution_date: datetime,
                                             df_power: pd.DataFrame,
                                             df_intensity: pd.DataFrame) -> datetime:
    df_power = df_power.rename(columns={'value': 'power'})
    df_power = df_power.set_index('timestamp')
    df_power = df_power.resample('1s').mean()
    df_power = df_power.fillna(method='ffill')
    df_intensity = df_intensity.rename(columns={'value': 'carbon_intensity'})
    df_intensity = df_intensity.set_index('timestamp')
    df_intensity = df_intensity.resample('1s').mean()
    df_intensity = df_intensity.fillna(method='ffill')
    df = df_power.merge(df_intensity, on='timestamp')
    df = df.reset_index(names='timestamp')

    df['ratio'] = df['power'] * df['carbon_intensity']
    bests = df[df['ratio'] == df['ratio'].min()]

    for row in bests.itertuples():
        new_execution_date = pytz.utc.localize(datetime.strptime(str(row.timestamp), '%Y-%m-%d %H:%M:%S'))
        if new_execution_date >= execution_date:
            return new_execution_date

    return bests.iloc[0].timestamp


@app.get("/recommendation")
async def recommendation():
    return compute_recommendations()
