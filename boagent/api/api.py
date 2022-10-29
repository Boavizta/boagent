from inspect import _void
import json
import math
import os
import time
from datetime import datetime, timedelta
from subprocess import run
from typing import Dict, Any, Tuple, List
from urllib import response

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
from database import Power, create_database, get_session, get_engine, insert_metric, select_metric, power_to_csv, \
    highlight_spikes, insert_metric_and_commit, add_from_scaphandre, Power


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
    df = highlight_spikes(select_metric(session, data, start_date, stop_date))
    df['timestamp'] = df['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
    session.close()
    return Response(
        content=df.to_csv(index=False),
        media_type="text/csv"
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


@app.get("/update")
async def update():
    response = query_electricity_carbon_intensity()
    info = parse_electricity_carbon_intensity(response)
    session = get_session(settings.db_path)
    add_from_scaphandre(session, table=Power)
    insert_metric(session=session, metric_name='carbonintensity', timestamp=info['timestamp'], value=info['value'])
    session.commit()
    session.close()
    session.close()
    return Response(status_code=200)


@app.get("/carbon_intensity_forecast")
async def carbon_intensity_forecast(since: str = "now", until: str = "24h") -> Response:
    start_date, stop_date = parse_date_info(since, until, forecast=True)
    start_date = upper_round_date_minutes_with_base(start_date, base=5)
    response = query_forecast_electricity_carbon_intensity(start_date, stop_date)
    forecasts = parse_forecast_electricity_carbon_intensity(response)
    df = highlight_spikes(pd.DataFrame(forecasts),"value")
    return Response(
        content=df.to_csv(index=False),
        media_type="text/csv"
    )


@app.get("/recommendation")
async def info():
    return get_reco()


@app.get("/carbon_intensity")
async def carbon_intensity(since: str = "now", until: str = "24h") -> Response:
    _, stop_date = parse_date_info(since, until, forecast=True)
    start_date, now = parse_date_info(since, until, forecast=False)

    session = get_session(settings.db_path)
    df_history = select_metric(session, 'carbonintensity', start_date, now)
    df_history['forecast'] = False

    now = upper_round_date_minutes_with_base(now, base=5)
    response = query_forecast_electricity_carbon_intensity(now, stop_date)
    forecasts = parse_forecast_electricity_carbon_intensity(response)
    df_forecast = pd.DataFrame(forecasts)
    df_forecast['forecast'] = True
    df = pd.concat([df_history, df_forecast])
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


def query_electricity_carbon_intensity() -> Dict[str, Any]:
    url = settings.boaviztapi_endpoint + f'/v1/usage_router/gwp/current_intensity?location={settings.azure_location}'
    today = datetime.now()
    start_date = (today - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    stop_date = today.strftime("%Y-%m-%dT%H:%M:%SZ")
    response = requests.post(url, json={
        "source": "carbon_aware_api",
        "url": settings.carbon_aware_api_endpoint,
        "token": settings.carbon_aware_api_token,
        "start_date": start_date,
        "stop_date": stop_date
    })
    return response.json()


def parse_electricity_carbon_intensity(carbon_aware_api_response: Dict[str, Any]):
    from pprint import pprint
    print("carbon aware api response : ")
    pprint(carbon_aware_api_response)
    intensity_dict = carbon_aware_api_response['_value']
    return {
        'timestamp': datetime.fromisoformat(intensity_dict['endTime']),
        'value': round(intensity_dict['carbonIntensity'], 3)
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
        start_date = datetime.now()
        end_date = start_date + timedelta(hours=1)
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=1)

    if since == 'now' and not forecast:
        end_date = datetime.now()
    elif since == 'now' and forecast:
        start_date = datetime.now()
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

    return start_date, end_date


def upper_round_date_minutes_with_base(date: datetime, base: int) -> datetime:
    delta_minutes = base * math.ceil((date.minute + 1) / base) - date.minute
    return date + timedelta(minutes=delta_minutes)


def get_cron_per_user():
    user = []
    with open("/etc/passwd", "r") as f:
        for line in f.readlines():
            user.append(line.split(":")[0])
        user.sort()
        for item in user:
            output = os.popen(f"crontab -u {item} -l").read()
            for line in output.splitlines():
                print(line)


def get_all_cron():
    crons = []

    if os.geteuid() == 0:
        crons.append(get_cron_per_user())
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
        info["job"] = cron_lines
        crons_info.append(info)
    return crons_info


def get_reco():
    reco = []
    for cron in get_cron_info():
        if cron['next']:
            reco.append({'date': cron['next'], 'mode': 'forcast', 'job': cron['job']})
        if cron['previous']:
            reco.append({'date': cron['previous'], 'mode': 'history', 'job': cron['job']})
    return reco


@app.get("/toto")
def toto():
    session = get_session(settings.db_path)
    add_from_scaphandre(session, table=Power)
    session.close()
    session.close()

    return Response(status_code=200)





@app.get("/recommendation")
async def info():
    return get_reco()