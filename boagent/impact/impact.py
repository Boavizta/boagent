#!/usr/bin/env python3

import click

@click.command()
@click.option("--file", default="./hardware.json", help="Path to a JSON file containing hardware specifications.")
@click.option("--output-file", help="File to output the impact data to")
def main():
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

