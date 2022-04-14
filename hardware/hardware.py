#!/usr/bin/env python3

import click
import json
import sys
from disk import Partition, Disk, DiskException
from cpu import get_cpus
from pprint import pprint

@click.command()
@click.option("--count", default=1, help="Number of greetings")
def main(count):
    res = {}
    res["disks"] = format_disks(disks())
    res["cpus"] = format_cpus(cpus())
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
            "manufacturer": disk.vendor()
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

if __name__ == '__main__':
    main()
