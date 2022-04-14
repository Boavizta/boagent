#!/usr/bin/env python3

import click
import json
import sys
from disk import Partition, Disk, DiskException
from pprint import pprint

@click.command()
@click.option("--count", default=1, help="Number of greetings")
def main(count):
    res = format_disks(disks())
    json.dump(res, sys.stdout, indent=4)
    return 0

def disks():
    disks = [Disk(mount_point='/boot')]
    for disk in disks:
        disk.lookup()
    return disks

def format_disks(disks):
    res = {"disks": []}
    for disk in disks:
        res["disks"].append({
                "capacity": disk.size,
                "manufacturer": disk.vendor()
            })
    return res

if __name__ == '__main__':
    main()
