import json
import time
from typing import Dict, Any, List, Union
from fastapi import FastAPI, Response, Body, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from boaviztapi_sdk.api.server_api import ServerApi
from boaviztapi_sdk.models.server import Server
from boagent.api.exceptions import InvalidPIDException
from boagent.hardware.lshw import Lshw
from .utils import (
    iso8601_or_timestamp_as_timestamp,
    format_prometheus_output,
    get_boavizta_api_client,
    sort_ram,
    sort_disks,
)

from .config import Settings
from .process import Process
from .models import WorkloadTime, time_workload_example

settings = Settings()

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
PROJECT_NAME = settings.project_name
PROJECT_VERSION = settings.project_version
PROJECT_DESCRIPTION = settings.project_description
TAGS_METADATA = settings.tags_metadata


def configure_static(app):
    app.mount("/assets", StaticFiles(directory=ASSETS_PATH), name="assets")


def configure_app():
    app = FastAPI(
        title=PROJECT_NAME,
        version=PROJECT_VERSION,
        description=PROJECT_DESCRIPTION,
        contact={"name": "Boavizta Members", "url": "https://boavizta.org/en"},
        license_info={"name": "Apache-2.0"},
        openapi_tags=TAGS_METADATA,
    )
    configure_static(app)
    return app


app = configure_app()


@app.get("/info", tags=["info"])
async def info():
    return {
        "seconds_in_one_year": SECONDS_IN_ONE_YEAR,
        "default_lifetime": DEFAULT_LIFETIME,
        "hardware_file_path": HARDWARE_FILE_PATH,
        "power_file_path": POWER_DATA_FILE_PATH,
        "hardware_cli": HARDWARE_CLI,
        "boaviztapi_endpoint": BOAVIZTAPI_ENDPOINT,
    }


@app.get("/web", tags=["web"], response_class=HTMLResponse)
async def web():
    res = ""
    with open("{}/index.html".format(PUBLIC_PATH), "r") as fd:
        res = fd.read()
    fd.close()
    return res


@app.get("/metrics", tags=["metrics"])
async def metrics(
    start_time: str = "0.0",
    end_time: str = "0.0",
    verbose: bool = False,
    location: str = "",
    measure_power: bool = True,
    lifetime: float = DEFAULT_LIFETIME,
    fetch_hardware: bool = False,
):
    return Response(
        content=format_prometheus_output(
            get_metrics(
                iso8601_or_timestamp_as_timestamp(start_time),
                iso8601_or_timestamp_as_timestamp(end_time),
                verbose,
                location,
                measure_power,
                lifetime,
                fetch_hardware,
            ),
            verbose,
        ),
        media_type="plain-text",
    )


@app.get("/query", tags=["query"])
async def query(
    start_time: str = "0.0",
    end_time: str = "0.0",
    verbose: bool = False,
    location: str = "EEE",
    measure_power: bool = True,
    lifetime: float = DEFAULT_LIFETIME,
    fetch_hardware: bool = False,
):
    """
    start_time: Start time for evaluation. Accepts either UNIX Timestamp or ISO8601 date format. \n
    end_time: End time for evaluation. Accepts either UNIX Timestamp or ISO8601 date format. \n
    verbose: Get detailled metrics with extra information.\n
    location: Country code to configure the local electricity grid to take into account.\n
    measure_power: Get electricity consumption metrics from Scaphandre or not.\n
    lifetime: Full lifetime of the machine to evaluate.\n
    fetch_hardware: Regenerate hardware.json file with current machine hardware or not.\n
    """
    return get_metrics(
        iso8601_or_timestamp_as_timestamp(start_time),
        iso8601_or_timestamp_as_timestamp(end_time),
        verbose,
        location,
        measure_power,
        lifetime,
        fetch_hardware,
    )


@app.post("/query", tags=["query"])
async def query_with_time_workload(
    start_time: str = "0.0",
    end_time: str = "0.0",
    verbose: bool = False,
    location: str = "EEE",
    measure_power: bool = True,
    lifetime: float = DEFAULT_LIFETIME,
    fetch_hardware: bool = False,
    time_workload: Union[dict[str, float], dict[str, List[WorkloadTime]]] = Body(
        None, example=time_workload_example
    ),
):
    """
    start_time: Start time for evaluation. Accepts either UNIX Timestamp or ISO8601 date format. \n
    end_time: End time for evaluation. Accepts either UNIX Timestamp or ISO8601 date format. \n
    verbose: Get detailled metrics with extra information.\n
    location: Country code to configure the local electricity grid to take into account.\n
    measure_power: Get electricity consumption metrics from Scaphandre or not.\n
    lifetime: Full lifetime of the machine to evaluate.\n
    fetch_hardware: Regenerate hardware.json file with current machine hardware or not.\n
    time_workload: Workload percentage for CPU and RAM. Can be a float or a list of dictionaries with format
    {"time_percentage": float, "load_percentage": float}
    """
    return get_metrics(
        iso8601_or_timestamp_as_timestamp(start_time),
        iso8601_or_timestamp_as_timestamp(end_time),
        verbose,
        location,
        measure_power,
        lifetime,
        fetch_hardware,
        time_workload,
    )


@app.get("/process_embedded_impacts", tags=["process"])
async def process_embedded_impacts(
    process_id: int = 0,
    start_time: str = "0.0",
    end_time: str = "0.0",
    location: str = "EEE",
    lifetime: float = DEFAULT_LIFETIME,
    fetch_hardware: bool = False,
):
    """
    process_id: The process ID queried to be evaluated for embedded impacts for each available component. \n
    start_time: Start time for evaluation. Accepts either UNIX Timestamp or ISO8601 date format. \n
    end_time: End time for evaluation. Accepts either UNIX Timestamp or ISO8601 date format. \n
    location: Country code to configure the local electricity grid to take into account.\n
    lifetime: Full lifetime of the machine to evaluate.\n
    """

    verbose = True
    measure_power = True

    metrics_data = get_metrics(
        iso8601_or_timestamp_as_timestamp(start_time),
        iso8601_or_timestamp_as_timestamp(end_time),
        verbose,
        location,
        measure_power,
        lifetime,
        fetch_hardware,
    )
    try:
        queried_process = Process(metrics_data, process_id)
    except InvalidPIDException as invalid_pid:
        raise HTTPException(status_code=400, detail=invalid_pid.message)
    else:
        process_embedded_impact_values = queried_process.embedded_impact_values
        json_content = json.dumps(process_embedded_impact_values)
        return Response(status_code=200, content=json_content)


def get_metrics(
    start_time: float,
    end_time: float,
    verbose: bool,
    location: str,
    measure_power: bool,
    lifetime: float,
    fetch_hardware: bool,
    time_workload: Union[dict[str, float], dict[str, List[WorkloadTime]], None] = None,
):

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

    avg_power = None

    if len(location) < 3 or location == "EEE":
        res["location_warning"] = {
            "warning_message": "Location is either set as default, or has not been set, and is therefore set to the default BoaviztAPI location. "
            "Be aware that the presented results can be drastically different due to location. "
            "It is recommended that you set the asset location with the corresponding country code, see: https://doc.api.boavizta.org/Explanations/usage/countries/"
        }

    if measure_power:
        power_data = get_power_data(start_time, end_time)
        avg_power = power_data["avg_power"]
        if "warning" in power_data:
            res["emissions_calculation_data"][
                "energy_consumption_warning"
            ] = power_data["warning"]

    boaviztapi_data = query_machine_impact_data(
        model={},
        configuration=hardware_data,
        usage=format_usage_request(
            start_time, end_time, avg_power, location, time_workload
        ),
    )

    if measure_power:
        res["total_operational_emissions"] = {
            "value": boaviztapi_data["impacts"]["gwp"]["use"],
            "description": "GHG emissions related to usage, from start_time to end_time.",
            "type": "gauge",
            "unit": "kg CO2eq",
            "long_unit": "kilograms CO2 equivalent",
        }
        res["total_operational_abiotic_resources_depletion"] = {
            "value": boaviztapi_data["impacts"]["adp"]["use"],
            "description": "Abiotic Resources Depletion (minerals & metals, ADPe) due to the usage phase.",
            "type": "gauge",
            "unit": "kgSbeq",
            "long_unit": "kilograms Antimony equivalent",
        }
        res["total_operational_primary_energy_consumed"] = {
            "value": boaviztapi_data["impacts"]["pe"]["use"],
            "description": "Primary Energy consumed due to the usage phase.",
            "type": "gauge",
            "unit": "MJ",
            "long_unit": "Mega Joules",
        }
        res["start_time"] = {
            "value": start_time,
            "description": "Start time for the evaluation, in timestamp format (seconds since 1970)",
            "type": "counter",
            "unit": "s",
            "long_unit": "seconds",
        }
        res["end_time"] = {
            "value": end_time,
            "description": "End time for the evaluation, in timestamp format (seconds since 1970)",
            "type": "counter",
            "unit": "s",
            "long_unit": "seconds",
        }
        res["average_power_measured"] = {
            "value": avg_power,
            "description": "Average power measured from start_time to end_time",
            "type": "gauge",
            "unit": "W",
            "long_unit": "Watts",
        }

    """ res["calculated_emissions"] = {
        "value": boaviztapi_data["impacts"]["gwp"]["value"] * ratio
        + boaviztapi_data["impacts"]["gwp"]["use"]["value"],
        "description": "Total Green House Gas emissions calculated for manufacturing and usage phases, between "
        "start_time and end_time",
        "type": "gauge",
        "unit": "kg CO2eq",
        "long_unit": "kilograms CO2 equivalent",
    } """

    res["embedded_emissions"] = {
        "value": boaviztapi_data["impacts"]["gwp"]["embedded"]["value"] * ratio,
        "description": "Embedded carbon emissions (manufacturing phase)",
        "type": "gauge",
        "unit": "kg CO2eq",
        "long_unit": "kilograms CO2 equivalent",
    }
    res["embedded_abiotic_resources_depletion"] = {
        "value": boaviztapi_data["impacts"]["adp"]["embedded"]["value"] * ratio,
        "description": "Embedded abiotic ressources consumed (manufacturing phase)",
        "type": "gauge",
        "unit": "kg Sbeq",
        "long_unit": "kilograms ADP equivalent",
    }
    res["embedded_primary_energy"] = {
        "value": boaviztapi_data["impacts"]["pe"]["embedded"]["value"] * ratio,
        "description": "Embedded primary energy consumed (manufacturing phase)",
        "type": "gauge",
        "unit": "MJ",
        "long_unit": "Mega Joules",
    }

    if verbose:
        res["raw_data"] = {
            "hardware_data": hardware_data,
            "resources_data": "not implemented yet",
            "boaviztapi_data": boaviztapi_data,
            "start_time": start_time,
            "end_time": end_time,
        }
        res["electricity_carbon_intensity"] = {
            "value": boaviztapi_data["verbose"]["gwp_factor"]["value"],
            "description": "Carbon intensity of the electricity mix. Mix considered : {}".format(
                location
            ),
            "type": "gauge",
            "unit": "kg CO2eq / kWh",
            "long_unit": "Kilograms CO2 equivalent per KiloWattHour",
        }

        if measure_power:
            res["raw_data"]["power_data"] = power_data

    return res


def format_usage_request(
    start_time: float,
    end_time: float,
    avg_power: Union[float, None] = None,
    location: str = "EEE",
    time_workload: Union[dict[str, float], dict[str, List[WorkloadTime]], None] = None,
):
    hours_use_time = (end_time - start_time) / 3600.0
    kwargs_usage = {"hours_use_time": hours_use_time}
    if location:
        kwargs_usage["usage_location"] = location
    if avg_power:
        kwargs_usage["avg_power"] = avg_power
    if time_workload:
        kwargs_usage["time_workload"] = time_workload
    return kwargs_usage


def get_power_data(start_time, end_time):
    # Get all items of the json list where start_time <= host.timestamp <= end_time
    power_data = {}
    with open(POWER_DATA_FILE_PATH, "r") as power_data_file:
        formatted_data = f"{power_data_file.read()}]"
        data = json.loads(formatted_data)
        queried_power_data = [
            e for e in data if start_time <= float(e["host"]["timestamp"]) <= end_time
        ]
        power_data["raw_data"] = queried_power_data
        power_data["avg_power"] = compute_average_consumption(queried_power_data)
        if end_time - start_time <= 3600:
            power_data["warning"] = (
                "The time window is lower than one hour, but the energy consumption estimate is in "
                "Watt.Hour. So this is an extrapolation of the power usage profile on one hour. Be "
                "careful with this data. "
            )
        return power_data


def compute_average_consumption(power_data) -> float:
    # Host energy consumption
    total_host = 0.0
    avg_host = 0.0
    if len(power_data) > 0:
        for r in power_data:
            total_host += float(r["host"]["consumption"])

        avg_host = total_host / len(power_data) / 1000000.0  # from microwatts to watts

    return avg_host


def get_hardware_data(fetch_hardware: bool):
    data = {}
    if fetch_hardware:
        build_hardware_data()
    try:
        data = read_hardware_data()
    except Exception:
        build_hardware_data()
        data = read_hardware_data()
    return data


def read_hardware_data() -> Dict:
    with open(HARDWARE_FILE_PATH, "r") as fd:
        data = json.load(fd)
    return data


def build_hardware_data():
    lshw = Lshw()
    with open(HARDWARE_FILE_PATH, "w") as hardware_file:
        hardware_data = {}
        hardware_data["disks"] = lshw.disks
        hardware_data["cpus"] = lshw.cpus
        hardware_data["rams"] = lshw.memories
        json.dump(hardware_data, hardware_file)


def query_machine_impact_data(
    model: dict[str, str],
    configuration: dict[str, dict[str, int]],
    usage: dict[str, Any],
) -> dict:
    server_api = ServerApi(get_boavizta_api_client())

    server_impact = None

    if configuration:
        server = Server(usage=usage, configuration=configuration)
        server_impact = server_api.server_impact_from_configuration_v1_server_post(
            server=server
        )
    elif model:
        # server = Server(usage=usage, model=model)
        # TO IMPLEMENT
        # This conditional was based on a previous version of BoaviztAPI, where a server model could
        # be sent to /v1/server through a GET method. BoaviztAPI now expects an archetype string to
        # return a prerecorded impact from an asset.
        server_impact = server_api.server_impact_from_model_v1_server_get(
            archetype="dellR740"
        )

    return server_impact


def generate_machine_configuration(hardware_data) -> Dict[str, Any]:
    # Either delete or transfer this logic to hardware_cli / lshw
    config = {
        "cpu": {
            "units": len(hardware_data["cpus"]),
            "core_units": hardware_data["cpus"][1]["core_units"],
            # "family": hardware_data['cpus'][1]['family']
        },
        "ram": sort_ram(hardware_data["rams"]),
        "disk": sort_disks(hardware_data["disks"]),
        "power_supply": (
            hardware_data["power_supply"]
            if "power_supply" in hardware_data
            else {"units": 1}
        ),
        # TODO: if cpu is a small one, guess that power supply is light/average weight of a laptops power supply ?
    }
    return config
