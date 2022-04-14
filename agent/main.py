#!/usr/bin/env python3

from openapi_client import ApiClient, Configuration
from openapi_client.api.component_api import ComponentApi
from openapi_client.model.cpu import Cpu
from openapi_client.model.ram import Ram

from pprint import pprint

from disk import Partition, Disk, DiskException
from ram.ram import get_ram_info
from cpu import get_cpu

def main():
    disks = get_disks()
    pprint(disks)
    ram = get_ram_info()
    pprint(ram)
    cpu = get_cpu()
    pprint(cpu)
    call_api(cpu, ram, disks)

def get_disks():
    disk = Disk()
    disk.lookup()
    return disk

def extract_cpu(cpu_info):
    request = {
        "units": 1,
        "core_units": cpu_info["cpu_info"]["count"],
        "family": cpu_info["microarch"][0],
        #"manufacture_date": "2017",
        #"die_size_per_core": 2.0
    }
    return request

def extract_ram(ram_info):
    request = {
        "units": len(ram_info),
        "capacity": ram_info[0].size_gb,
        "manufacturer": ram_info[0].manufacturer,
        "model": ram_info[0].model
    }
    return request

def extract_disks(disks_info):
    request = {

    }
    return request

def call_api(cpu, ram, disks):
    config = Configuration(
        host="http://localhost:5000",
    )
    client = openapi_client = ApiClient(
        configuration=config, pool_threads=2
    )

    component_api = ComponentApi(client)

    kwargs_cpu = extract_cpu(cpu)
    print("############# request CPU ############")
    pprint(kwargs_cpu)

    cpu = Cpu(**kwargs_cpu)
    #TODO : check CPU Name case sensistive or not

    res_cpu = component_api.cpu_impact_bottom_up_v1_component_cpu_post(cpu=cpu)

    print("############# answer CPU ############")
    pprint(res_cpu)

    kwargs_ram = extract_ram(ram)
    print("############# request RAM ############")
    pprint(kwargs_ram)

    ram = Ram(**kwargs_ram)

    res_ram = component_api.ram_impact_bottom_up_v1_component_ram_post(ram=ram)

    print("############# answer RAM ############")
    pprint(res_ram)

    kwargs_disks = extract_disks(disks)
    print("############# request Disks ############")
    pprint(kwargs_cpu)

if __name__ == '__main__':
    main()
