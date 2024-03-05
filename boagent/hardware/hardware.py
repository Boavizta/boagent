#!/usr/bin/env python3

import click
import json
import sys
from disk import search_physical_drives
from cpu import get_cpus
from ram import get_ram_info

@click.command()
@click.option("--output-file", help="File to output the hardwate data to")
def main(output_file):
    res = {}
    res["disks"] = format_disks(disks())
    res["cpus"] = format_cpus(get_cpus())
    res["rams"] = format_rams(rams())
    res["mother_board"] = format_mother_board(mother_board())
    if output_file is not None:
        with open(output_file, 'w') as fd:
            json.dump(res, fd, indent=4)
    else:
        json.dump(res, sys.stdout, indent=4)
    return 0

def disks():
    disks = search_physical_drives()
    for disk in disks:
        disk.lookup()
    return disks

def format_disks(disks):
    res = []
    for disk in disks:
        res.append({
            "capacity": disk.size,
            "manufacturer": disk.vendor,
            "type": disk.type
        })
    return res

def format_cpus(cpus):
    for cpu in cpus:
        cpu["core_units"] = cpu["cpu_info"]["count"]
        print("cpu[microarch][0][0] : {}".format(cpu["microarch"][0][0]))
        cpu["family"] = cpu["microarch"][0][0].upper()+cpu["microarch"][0][1:] # Ensure first letter of CPU family is upper case, while boaviztapi 2.0 is not released and cpu family usage is not fixed
    return cpus

def rams():
    rams = get_ram_info()
    return rams

def format_rams(rams):
    res = []
    for ram in rams:
        options = {
            "capacity": ram.size_gb,
        }
        if ram.manufacturer is not None and len(ram.manufacturer) > 0:
            options["manufacturer"] = ram.manufacturer
        res.append(options)
    return res

def mother_board():
    pass

def format_mother_board(mother_board):
    return {}

if __name__ == '__main__':
    main()
