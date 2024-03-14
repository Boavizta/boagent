#!/usr/bin/env python3

import click
import json
import sys
from lshw import Lshw

# from disk import search_physical_drives
# from cpu import get_cpus
# from ram import get_ram_info

lshw = Lshw()

lshw_cpus = lshw.cpus
lshw_ram = lshw.memories
lshw_disks = lshw.disks


@click.command()
@click.option("--output-file", help="File to output the hardwate data to")
def main(output_file):
    res = {}
    res["disk"] = get_disks()
    res["cpu"] = get_cpus()
    res["ram"] = get_ram()
    if output_file is not None:
        with open(output_file, "w") as fd:
            json.dump(res, fd, indent=4)
    else:
        json.dump(res, sys.stdout, indent=4)
    return 0


""" def disks():
    disks = search_physical_drives()
    for disk in disks:
        disk.lookup()
    return disks


def format_disks(disks):
    res = []
    for disk in disks:
        res.append(
            {"capacity": disk.size, "manufacturer": disk.vendor, "type": disk.type}
        )
    return res """


def get_disks():
    disks = lshw_disks
    return disks


def get_cpus():
    cpus = lshw_cpus
    return cpus


def get_ram():
    rams = lshw_ram
    return rams


""" def format_rams(rams):
    res = []
    for ram in rams:
        options = {
            "capacity": ram.size_gb,
        }
        if ram.manufacturer is not None and len(ram.manufacturer) > 0:
            options["manufacturer"] = ram.manufacturer
        res.append(options)
    return res
 """

if __name__ == "__main__":
    main()
