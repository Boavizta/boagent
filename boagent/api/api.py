import json
import math
import os
import time
from datetime import datetime, timedelta
from subprocess import run
from typing import Dict, Any, Tuple, List, Optional
from urllib import response

import pytz
from croniter import croniter

import pandas as pd
import requests
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from boaviztapi_sdk.api.server_api import ServerApi
from boaviztapi_sdk.model.server_dto import ServerDTO

from utils import iso8601_or_timestamp_as_timestamp, format_prometheus_output, format_prometheus_metric, \
    get_boavizta_api_client, sort_ram, sort_disks
from config import settings
from database import create_database, get_session, get_engine, insert_metric, select_metric, \
    new_highlight_spikes, CarbonIntensity, add_from_scaphandre, get_most_recent_data


def configure_static(app):
    app.mount("/assets", StaticFiles(directory=settings.assets_path), name="assets")


def configure_app():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    configure_static(app)
    return app


app = configure_app()
items = {}

create_database(get_engine(db_path=settings.db_path))


@app.get("/info")
async def info():
    return {
        "seconds_in_one_year": settings.seconds_in_one_year,
        "default_lifetime": settings.default_lifetime,
        "hardware_file_path": settings.hardware_file_path,
        "power_file_path": settings.power_file_path,
        "hardware_cli": settings.hardware_cli,
        "boaviztapi_endpoint": settings.boaviztapi_endpoint
    }


@app.get("/web", response_class=HTMLResponse)
async def web():
    res = ""
    with open("{}/index.html".format(settings.public_path), 'r') as fd:
        res = fd.read()
    fd.close()
    return res


@app.get('/csv')
async def csv(data: str, since: str = "now", until: str = "24h") -> Response:
    start_date, stop_date = parse_date_info(since, until)

    session = get_session(settings.db_path)
    df = new_highlight_spikes(select_metric(session, data, start_date, stop_date), 'value')
    # df['timestamp'] = df['timestamp'].apply(lambda x: x + timedelta(hours=2))
    # df = df[df['timestamp'] >= datetime(2022, 10, 29, 19, 30, 0)]
    # df = df[df['timestamp'] <= datetime(2022, 10, 29, 20, 0, 0)]
    df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
    session.close()

    return Response(
        content=df.to_csv(index=False),
        media_type="text/csv"
    )


@app.get('/last_data')
async def last_data(table_name: str) -> Response:
    data = get_most_recent_data(table_name)
    if data is None:
        return Response(status_code=404)
    else:
        df =pd.DataFrame([[data.timestamp, data.value]], columns=['timestamp', 'value'])
        return Response(
        content=df.to_csv(index=False),
        media_type="text/csv",
        status_code=200
        )


@app.get("/metrics")
async def metrics(start_time: str = "0.0", end_time: str = "0.0", verbose: bool = False, output: str = "json",
                  location: str = None, measure_power: bool = True, lifetime: float = settings.default_lifetime,
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


@app.get("/query")
async def query(start_time: str = "0.0", end_time: str = "0.0", verbose: bool = False, location: str = None,
                measure_power: bool = True, lifetime: float = settings.default_lifetime, fetch_hardware: bool = False):
    return get_metrics(
        iso8601_or_timestamp_as_timestamp(start_time),
        iso8601_or_timestamp_as_timestamp(end_time),
        verbose, location, measure_power, lifetime, fetch_hardware
    )

@app.get("/actual_intensity")
async def actual_intensity():
    response = query_electricity_carbon_intensity()
    info = parse_electricity_carbon_intensity(response)
    return info['value']

@app.get("/update")
async def update():
    response = query_electricity_carbon_intensity()
    info = parse_electricity_carbon_intensity(response)
    session = get_session(settings.db_path)
    add_from_scaphandre(session) # lots lot insert_metric called here
    insert_metric(session=session, metric_name='carbonintensity', timestamp=info['timestamp'], value=info['value'])
    session.commit()
    session.close()
    return Response(status_code=200)


@app.get("/carbon_intensity_forecast")
async def carbon_intensity_forecast(since: str = "now", until: str = "24h") -> Response:
    start_date, stop_date = parse_date_info(since, until, forecast=True)
    start_date, stop_date = start_date, stop_date

    start_date = upper_round_date_minutes_with_base(start_date, base=5)
    response = query_forecast_electricity_carbon_intensity(start_date, stop_date)
    forecasts = parse_forecast_electricity_carbon_intensity(response)
    df = new_highlight_spikes(pd.DataFrame(forecasts), "value")
    return Response(
        content=df.to_csv(index=False),
        media_type="text/csv"
    )


@app.get("/reco")
async def info():
    return get_reco()


@app.get("/carbon_intensity")
async def carbon_intensity(since: str = "now", until: str = "24h") -> Response:
    _, stop_date = parse_date_info(since, until, forecast=True)
    start_date, now = parse_date_info(since, until, forecast=False)

    session = get_session(settings.db_path)
    df_history = select_metric(session, 'carbonintensity', start_date, now)
    df_history['timestamp'] = df_history['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))

    now = upper_round_date_minutes_with_base(now, base=5)
    response = query_forecast_electricity_carbon_intensity(now, stop_date)
    forecasts = parse_forecast_electricity_carbon_intensity(response)
    df_forecast = pd.DataFrame(forecasts)
    df_forecast['timestamp'] = df_forecast['timestamp'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S'))

    df = pd.concat([df_history, df_forecast])
    df = df[['timestamp', 'value']]
    df = new_highlight_spikes(pd.DataFrame(df), "value")

    return Response(
        content=df.to_csv(index=False),
        media_type="text/csv"
    )


@app.get("/init_carbon_intensity")
async def init_carbon_intensity():
    engine = get_engine(settings.db_path)
    CarbonIntensity.__table__.drop(engine)
    create_database(engine)

    session = get_session(settings.db_path)
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
    session = get_session(settings.db_path)

    df_power = select_metric(session, 'power', start_date, stop_date)
    df_power['power_watt'] = df_power['value'] / 1000
    df_power = df_power.drop(columns=['value'])
    df_power = df_power.set_index('timestamp')
    df_power = df_power.resample('1s').mean()
    df_power = df_power.fillna(method='ffill')

    df_carbon_intensity = select_metric(session, 'carbonintensity', start_date, stop_date)
    df_carbon_intensity['carbon_intensity_g_per_watt_second'] = df_carbon_intensity['value'] / (1000*3600)
    df_carbon_intensity = df_carbon_intensity.drop(columns=['value'])
    df_carbon_intensity = df_carbon_intensity.set_index('timestamp')
    df_carbon_intensity = df_carbon_intensity.resample('1s').mean()
    df_carbon_intensity = df_carbon_intensity.fillna(method='ffill')
    df = df_power.merge(df_carbon_intensity, on='timestamp')
    df['operational'] = df['power_watt'] * df['carbon_intensity_g_per_watt_second']

    metrics = get_metrics(
        start_time=start_date.timestamp(),
        end_time=stop_date.timestamp(),
        verbose=False,
        location='FRA',
        measure_power=False,
        lifetime=settings.default_lifetime,
        fetch_hardware=False
    )
    embedded_emissions = metrics['embedded_emissions']['value']
    df['embedded'] = embedded_emissions / len(df)
    df = df.drop(columns=['power_watt', 'carbon_intensity_g_per_watt_second']).reset_index()
    return Response(
        content=df.to_csv(index=False),
        media_type="text/csv"
    )


def get_metrics(start_time: float, end_time: float, verbose: bool, location: str, measure_power: bool, lifetime: float,
                fetch_hardware: bool = False):
    now: float = time.time()
    if start_time and end_time:
        ratio = (end_time - start_time) / (lifetime * settings.seconds_in_one_year)
    else:
        ratio = 1.0
    if start_time == 0.0:
        start_time = now - 3600
    if end_time == 0.0:
        end_time = now
    if end_time - start_time >= lifetime * settings.seconds_in_one_year:
        lifetime = (end_time - start_time) / float(settings.seconds_in_one_year)

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

    res["calculated_emissions"] = {
        "value": boaviztapi_data["impacts"]["gwp"]["manufacture"] * ratio + boaviztapi_data["impacts"]["gwp"]["use"],
        "description": "Total Green House Gaz emissions calculated for manufacturing and usage phases, between "
                       "start_time and end_time",
        "type": "gauge",
        "unit": "kg CO2eq",
        "long_unit": "kilograms CO2 equivalent"
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
    res["embedded_emissions"] = {
        "value": boaviztapi_data["impacts"]["gwp"]["manufacture"] * ratio,
        "description": "Embedded carbon emissions (manufacturing phase)",
        "type": "gauge",
        "unit": "kg CO2eq",
        "long_unit": "kilograms CO2 equivalent"
    }
    res["embedded_abiotic_resources_depletion"] = {
        "value": boaviztapi_data["impacts"]["adp"]["manufacture"] * ratio,
        "description": "Embedded abiotic ressources consumed (manufacturing phase)",
        "type": "gauge",
        "unit": "kg Sbeq",
        "long_unit": "kilograms ADP equivalent"
    }
    res["embedded_primary_energy"] = {
        "value": boaviztapi_data["impacts"]["pe"]["manufacture"] * ratio,
        "description": "Embedded primary energy consumed (manufacturing phase)",
        "type": "gauge",
        "unit": "MJ",
        "long_unit": "Mega Joules"
    }
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
            "description": "Carbon intensity of the elextricity mixed. Mix considered : {}".format(location),
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
            "boaviztapi_data": boaviztapi_data
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
    with open(settings.power_file_path, 'r') as fd:
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
    with open(settings.hardware_file_path, 'r') as fd:
        data = json.load(fd)
    return data


def build_hardware_data():
    p = run([settings.hardware_cli, "--output-file", settings.hardware_file_path])


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
    url = settings.boaviztapi_endpoint + f'/v1/usage_router/gwp/current_intensity?location={settings.azure_location}'
    start_date = start_date or (datetime.utcnow() - timedelta(minutes=5))
    stop_date = stop_date or datetime.utcnow()
    response = requests.post(url, json={
        "source": "carbon_aware_api",
        "url": settings.carbon_aware_api_endpoint,
        "token": settings.carbon_aware_api_token,
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
    url = settings.boaviztapi_endpoint + f'/v1/usage_router/gwp/forecast_intensity?location={settings.azure_location}'
    response = requests.post(url, json={
        "source": "carbon_aware_api",
        "url": settings.carbon_aware_api_endpoint,
        "token": settings.carbon_aware_api_token,
        "start_date": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stop_date": stop_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    })
    return response.json()[0]


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
        info["next"] = croniter(sched, base).get_next(datetime)
        info["previous"] = croniter(sched, base).get_prev(datetime)
        info["job"] = cron
        crons_info.append(info)
    return crons_info


def event_is_in_bad_time(event, since="now", until="24h"):
    start_date, stop_date = parse_date_info(since, until, forecast=True)
    start_date = upper_round_date_minutes_with_base(start_date, base=5)
    response = query_forecast_electricity_carbon_intensity(start_date, stop_date)
    forecasts = parse_forecast_electricity_carbon_intensity(response)
    df = new_highlight_spikes(pd.DataFrame(forecasts), "value")
    index = df.timestamp.searchsorted(f"{event}")

    if index == 0 or index == len(df.index):
        return False

    if df['peak'][index] == 1:
        return True

    return False


def get_reco(since="now", until="24h"):
    reco = []
    cron_list = get_cron_info()
    for cron in cron_list:
        if event_is_in_bad_time(event=cron['next'], since=since, until=until):
            reco.append({'type': 'CRON', 'date': cron['next'], 'mode': 'forcast', 'job': cron['job']})
        if event_is_in_bad_time(event=cron['previous'], since=since, until=until):
            reco.append({'type': 'CRON', 'date': cron['previous'], 'mode': 'history', 'job': cron['job']})
    return reco


@app.get("/toto") # root for clumsy test
def toto():
    # session = get_session(settings.db_path)
    # session.close()
    # session.close()
    return Response(status_code=200)





@app.get("/recommendation")
async def info():
    return get_reco()