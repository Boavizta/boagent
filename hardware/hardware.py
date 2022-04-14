#!/usr/bin/env python3

import click
from disk import Partition, Disk, DiskException

@click.command()
@click.option("--count", default=1, help="Number of greetings")
def main(count):
    print(disk())

def disk():
    disk = Disk()
    disk.lookup()

    return disk


if __name__ == '__main__':
    main()
