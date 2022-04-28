#!/usr/bin/env python3

import click
import json
import sys
from disk import Partition, Disk, DiskException
from cpu import get_cpus
from ram import get_ram_info
from pprint import pprint

@click.command()
@click.option("--output-file", help="File to output the hardwate data to")
def main(output_file):
    res = {}
    res["disks"] = format_disks(disks())
    res["cpus"] = format_cpus(cpus())
    res["rams"] = format_rams(rams())
    res["mother_board"] = format_mother_board(mother_board())
    if output_file is not None:
        with open(output_file, 'w') as fd:
            json.dump(res, fd, indent=4)
    else:
        json.dump(res, sys.stdout, indent=4)
    return 0

def disks():
    disks = [Disk(mount_point='/boot')]
    for disk in disks:
        disk.lookup()
    return disks

def format_disks(disks):
    res = []
    for disk in disks:
        res.append({
            "capacity": disk.size,
            "manufacturer": disk.vendor(),
            "type": disk.type
        })
    return res

def cpus():
    cpus = get_cpus()
    return cpus

def format_cpus(cpus):
    res = []
    for cpu in cpus:
        res.append({
            "units": 1,
            "core_units": cpu["cpu_info"]["count"],
            "family": cpu["microarch"][0]
        })
    return res

def rams():
    rams = get_ram_info()
    return rams

def format_rams(rams):
    res = []
    for ram in rams:
        res.append({
            "capacity": ram.size_gb,
            "manufacturer": ram.manufacturer
        })
    return res

def mother_board():
    pass

def format_mother_board(mother_board):
    return {}

if __name__ == '__main__':
    main()
