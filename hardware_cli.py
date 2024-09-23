#!/usr/bin/env python3

import click
import json
import sys

from boagent.hardware.lshw import Lshw

lshw = Lshw()

lshw_cpus = lshw.cpus
lshw_ram = lshw.memories
lshw_disks = lshw.disks


@click.command()
@click.option("--output-file", help="File to output the hardwate data to")
def main(output_file):
    hardware_data = {}
    hardware_data["disks"] = get_disks()
    hardware_data["cpus"] = get_cpus()
    hardware_data["rams"] = get_ram()
    if output_file is not None:
        with open(output_file, "w") as fd:
            json.dump(hardware_data, fd, indent=4)
    else:
        json.dump(hardware_data, sys.stdout, indent=4)
    return 0


def get_disks():
    disks = lshw_disks
    return disks


def get_cpus():
    cpus = lshw_cpus
    return cpus


def get_ram():
    rams = lshw_ram
    return rams


if __name__ == "__main__":
    main()
