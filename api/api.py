from fastapi import FastAPI
from subprocess import run
import time, json
from contextlib import redirect_stdout
from pprint import pprint

hardware_file_name = "hardware_data.json"
impact_file_name = "impact_data.json"
app = FastAPI()

@app.get("/query")
async def query(start_time: float = 0.0, end_time: float = 0.0):
    now: float = time.time()
    if start_time == 0.0:
        start_time = now - 30
    if end_time == 0.0:
        end_time += now

    hardware_data = get_hardware_data()
    emboddied_impact_data = get_emboddied_impact_data(hardware_data)

    res = {
        "start_time": start_time,
        "end_time": end_time,
        "hardware": hardware_data,
        "emboddied_impact_data": emboddied_impact_data,
        "total_emissions": "not implemented yet",
        "total_power_consumption": "not implemented yet",
        "total_embedded_emissions": "not implemented yet",
        "total_operational_emissions": "not implemented yet"
    }

    return res

def get_hardware_data():
    hardware_cli = "../hardware/hardware.py"
    p = run([hardware_cli, "--output-file", hardware_file_name])
    with open(hardware_file_name, 'r') as fd:
        data = json.load(fd)
        return data

def get_emboddied_impact_data(hardware_data):
    impact_cli = "../impact/impact.py"
    p = run([impact_cli, "--output-file", impact_file_name])
    with open(impact_file_name, 'r') as fd:
        data = json.load(fd)
        return data
