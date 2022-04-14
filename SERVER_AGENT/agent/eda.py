#!/usr/bin/env python3

import click

@click.command()
@click.option("--count", default=1, help="Number of greetings")
def main(count):
    print("count = {}".format(count))


if __name__ == '__main__':
    main()
