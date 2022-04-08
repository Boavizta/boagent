#!/usr/bin/env python3

from openapi_client import ApiClient, Configuration
from openapi_client.api.component_api import ComponentApi
from openapi_client.model.cpu import Cpu

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
    call_api()

def get_disks():
    disk = Disk()
    disk.lookup()
    return disk

def call_api():
    config = Configuration(
        host="http://localhost:5000",
    )
    client = openapi_client = ApiClient(
        configuration=config, pool_threads=2
    )

    component_api = ComponentApi(client)

    kwargs={
        "units": 1,
        "core_units": 24,
        "family": "Skylake",
        "manufacture_date": "2017",
        "die_size_per_core": 2.0
    }

    cpu = Cpu(
        **kwargs
    )

    res = component_api.cpu_impact_bottom_up_v1_component_cpu_post(
        cpu=cpu
    )

    pprint(res)

if __name__ == '__main__':
    main()
