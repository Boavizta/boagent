#!/usr/bin/env python3

import click
from disk import Partition, Disk, DiskException
from pprint import pprint

@click.command()
@click.option("--count", default=1, help="Number of greetings")
def main(count):
    pprint(format_disk_output(disk()))

def disk():
    disk = Disk(mount_point='/boot/efi')
    disk.lookup()
    print(disk._mount_point)
    return disk

def format_disk_output(disk):
    print(type(disk))
    print(dir(disk))
    return disk



if __name__ == '__main__':
    main()
