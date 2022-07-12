from fastapi import FastAPI, Response
from subprocess import run, Popen
import time, json
from contextlib import redirect_stdout
from pprint import pprint
from boaviztapi_sdk import ApiClient, Configuration
from boaviztapi_sdk.api.component_api import ComponentApi
from boaviztapi_sdk.api.server_api import ServerApi
from boaviztapi_sdk.model.cpu import Cpu
from boaviztapi_sdk.model.ram import Ram
from boaviztapi_sdk.model.disk import Disk
from boaviztapi_sdk.model.mother_board import MotherBoard
from boaviztapi_sdk.model.usage_server import UsageServer
from boaviztapi_sdk.model.server_dto import ServerDTO
from datetime import datetime
from dateutil import parser
#from os import env

hardware_file_name = "hardware_data.json"
power_file_name = "power_data.json"
app = FastAPI()
items = {}

#@app.start()
#async def start():
#    config_file = env.get("BOAGENT_CONFIG_FILE", "./config.yaml")
#    with open(config_file, 'r') as fd:

def get_metrics(start_time: float, end_time: float, verbose: bool, location: str, measure_power: bool):
    now: float = time.time()
    if start_time == 0.0:
        start_time = now - 200
    if end_time == 0.0:
        end_time = now

    hardware_data = get_hardware_data()
    embedded_impact_data = get_embedded_impact_data(hardware_data)
    total_embedded_impacts = get_total_embedded_impacts(embedded_impact_data)

    res = {"emissions_calculation_data":{}}

    host_avg_consumption = None
    if measure_power:
        power_data = get_power_data(start_time, end_time)
        host_avg_consumption = power_data["host_avg_consumption"]
        if "warning" in power_data:
            res["emissions_calculation_data"]["energy_consumption_warning"] = power_data["warning"]
    boaviztapi_data = get_total_operational_emissions(start_time, end_time, host_avg_consumption, location)

    if measure_power :
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
        "value": total_embedded_impacts["gwp"]+boaviztapi_data["impacts"]["gwp"]["use"],
        "description": "Total Green House Gaz emissions calculated for manufacturing and usage phases, between start_time and end_time",
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
        "value": total_embedded_impacts["gwp"],
        "description": "Embedded carbon emissions (manufacturing phase)",
        "type": "gauge",
        "unit": "kg CO2eq",
        "long_unit": "kilograms CO2 equivalent"
    }
    res["embedded_abiotic_resources_depletion"] = {
        "value": total_embedded_impacts["adp"],
        "description": "Embedded abiotic ressources consumed (manufacturing phase)",
        "type": "gauge",
        "unit": "kg Sbeq",
        "long_unit": "kilograms ADP equivalent"
    }
    res["embedded_primary_energy"] = {
        "value": total_embedded_impacts["pe"],
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
            "value": boaviztapi_data["verbose"]["USAGE-1"]["gwp_factor"]["used_value"],
            "description": "Carbon intensity of the elextricity mixed. Mix considered : {}".format(location),
            "type": "gauge",
            "unit": "kg CO2eq / kWh",
            "long_unit": "Kilograms CO2 equivalent per KiloWattHour"
        }
    }
    usage_location_status = boaviztapi_data["verbose"]["USAGE-1"]["usage_location"]["status"]
    if usage_location_status == "MODIFY":
        res["emissions_calculation_data"]["electricity_carbon_intensity"]["description"] += " WARNING : The provided trigram doesn't match any existing country. So this result is based on average European electricity mix. Be careful with this data."
    elif usage_location_status == "SET":
        res["emissions_calculation_data"]["electricity_carbon_intensity"]["description"] += "WARNING : As no information was provided about your location, this result is based on average European electricity mix. Be careful with this data."

    if verbose:
        res["emissions_calculation_data"]["raw_data"] = {
            "hardware_data": hardware_data,
            "embedded_impact_data": embedded_impact_data,
            #"power_data": power_data,
            "resources_data": "not implemented yet",
            "boaviztapi_data": boaviztapi_data
        }

    return res

def iso8061_as_timestamp(iso_time):
    if iso_time == "0.0" or iso_time == "0":
        return float(iso_time)
    else:
        dt = None
        try:
            dt = parser.parse(iso_time)
            print("{} is an iso 8601 datetime".format(iso_time))
        except Exception as e:
            print("{} is not an iso 8601 datetime".format(iso_time))
            print("Exception : {}".format(e))
            try:
                dt = datetime.fromtimestamp(int(round(float(iso_time))))
                print("{} is a timestamp".format(iso_time))
            except Exception as e:
                print("{} is not a timestamp".format(iso_time))
                print("Exception : {}".format(e))
                print("Parser would give : {}".format(parser.parse(iso_time)))
        finally:
            if dt:
                return dt.timestamp()
            else:
                return float(iso_time)

@app.get("/metrics")
async def metrics(start_time: str = "0.0", end_time: str = "0.0", verbose: bool = False, output: str = "json", location: str = None, measure_power: bool = True):
    return Response(
        content=format_prometheus_output(
            get_metrics(
                iso8061_as_timestamp(start_time),
                iso8061_as_timestamp(end_time),
                verbose, location, measure_power
            )
        ), media_type="plain-text"
    )

@app.get("/query")
async def query(start_time: str = "0.0", end_time: str = "0.0", verbose: bool = False, location: str = None, measure_power: bool = True):
    return get_metrics(
        iso8061_as_timestamp(start_time),
        iso8061_as_timestamp(end_time),
        verbose, location, measure_power
    )

def format_prometheus_output(res):
    response = ""
    for k, v in res.items():
        if "value" in v and "type" in v:
            if "description" not in v:
                v["description"] = "TODO: define me"
            response += format_prometheus_metric(k, "{}. {}".format(v["description"], "In {} ({}).".format(v["long_unit"], v["unit"])), v["type"], v["value"])
    #response += format_prometheus_metric("energy_consumption", "Energy consumed in the evaluation time window (evaluated at least for an hour, be careful if the time windows is lower than 1 hour), in Wh", "counter", res["emissions_calculation_data"]["energy_consumption"])
        else:
            for x, y in v.items():
                if "value" in y and "type" in y:
                    if "description" not in y:
                        y["description"] = "TODO: define me"
                    response += format_prometheus_metric("{}_{}".format(k,x), "{}. {}".format(y["description"], "In {} ({}).".format(y["long_unit"], y["unit"])), y["type"], y["value"])

    return response

def format_prometheus_metric(metric_name, metric_description, metric_type, metric_value):
    response = """# HELP {} {}
# TYPE {} {}
{} {}
""".format(metric_name, metric_description, metric_name, metric_type, metric_name, metric_value)
    return response

def get_total_operational_emissions(start_time, end_time, host_avg_consumption = None, location = None):
    hours_use_time = (end_time - start_time) / 3600.0
    #if hours_use_time < 1.0:
    #    hours_use_time = 1.0
    print("hours_use_time: {}".format(hours_use_time))
    kwargs_usage = {
        "hours_use_time": hours_use_time
    }
    if location:
        kwargs_usage["usage_location"] = location
    if host_avg_consumption:
        kwargs_usage["hours_electrical_consumption"] = host_avg_consumption

    # else guess location TODO # https://github.com/Boavizta/boagent/issues/25

    usage_server = UsageServer(**kwargs_usage)
    server_dto = ServerDTO(usage=usage_server)
    server_api = ServerApi(get_boavizta_api_client())
    res = server_api.server_impact_by_config_v1_server_post(server_dto=server_dto)
    return res#['impacts']['gwp']['use']

def get_power_data(start_time, end_time):
    power_cli = "scaphandre"
    power_data = {}
    with open(power_file_name, 'r') as fd:
        # Get all items of the json list where start_time <= host.timestamp <= end_time
        data = json.load(fd)
        res = [e for e in data if start_time <= float(e['host']['timestamp']) <= end_time]
        power_data['raw_data'] = res
        power_data['host_avg_consumption'] = compute_average_consumption(res)
        if end_time - start_time <= 3600:
            power_data['warning'] = "The time window is lower than one hour, but the energy consumption estimate is in Watt.Hour. So this is an extrapolation of the power usage profile on one hour. Be careful with this data."
        return power_data

def compute_average_consumption(power_data):
    # Host energy consumption
    total_host = 0.0
    avg_host = 0.0
    if len(power_data) > 0:
        for r in power_data:
            total_host += float(r['host']['consumption'])

        avg_host = total_host / len(power_data) / 1000000.0 # from microwatts to watts

    return avg_host

def get_total_embedded_impacts(embedded_impact_data):
    res = {}

    for imp in ["gwp", "pe", "adp"] :
        total = 0.0

        for d in embedded_impact_data['disks_impact']:
            total += float(d['impacts'][imp]['manufacture'])

        for r in embedded_impact_data['rams_impact']:
            total += float(r['impacts'][imp]['manufacture'])

        for c in embedded_impact_data['cpus_impact']:
            total += float(c['impacts'][imp]['manufacture'])

        total += float(embedded_impact_data['motherboard_impact']['impacts'][imp]['manufacture'])

        if imp != "adp":
            res[imp] = round(total,1)
        else:
            res[imp] = total

    return res

def get_hardware_data():
    hardware_cli = "../hardware/hardware.py"
    p = run([hardware_cli, "--output-file", hardware_file_name])
    with open(hardware_file_name, 'r') as fd:
        data = json.load(fd)
        return data

def get_boavizta_api_client():
    config = Configuration(
        host="http://localhost:5000",
    )
    client = ApiClient(
        configuration=config, pool_threads=2
    )
    return client

def get_embedded_impact_data(hardware_data):
    client = get_boavizta_api_client()
    component_api = ComponentApi(client)
    res_cpus = []
    for c in hardware_data['cpus']:
        cpu = Cpu(**c)
        res_cpus.append(component_api.cpu_impact_bottom_up_v1_component_cpu_post(cpu=cpu))
    res_rams = []
    for r in hardware_data['rams']:
        ram = Ram(**r)
        res_rams.append(component_api.ram_impact_bottom_up_v1_component_ram_post(ram=ram))

    res_disks = []
    for d in hardware_data['disks']:
        disk = Disk(**d)
        if d == "ssd":
            res_disks.append(component_api.disk_impact_bottom_up_v1_component_ssd_post(disk=disk))
        else:
            res_disks.append(component_api.disk_impact_bottom_up_v1_component_hdd_post(disk=disk))

    res_motherboard = component_api.motherboard_impact_bottom_up_v1_component_motherboard_post(mother_board=MotherBoard(**hardware_data['mother_board']))

    return {
        "disks_impact": res_disks,
        "rams_impact": res_rams,
        "cpus_impact": res_cpus,
        "motherboard_impact": res_motherboard
    }
