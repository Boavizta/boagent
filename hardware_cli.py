#!/usr/bin/env python3

import json
import sys

from boagent.hardware.lshw import Lshw
from click import command, option, ClickException


@command()
@option("--output-file", help="File to output the hardwate data to")
def main(output_file):
    try:
        lshw = Lshw()

        lshw_cpus = lshw.cpus
        lshw_ram = lshw.memories
        lshw_disks = lshw.disks
    except KeyError:
        error_message = "Hardware_cli was not executed with privileges, try `sudo ./hardware_cli.py`."
        exception = ClickException(error_message)
        exception.show()
    else:
        hardware_data = {}
        hardware_data["disks"] = lshw_disks
        hardware_data["cpus"] = lshw_cpus
        hardware_data["rams"] = lshw_ram
        if output_file is not None:
            with open(output_file, "w") as fd:
                json.dump(hardware_data, fd, indent=4)
        else:
            json.dump(hardware_data, sys.stdout, indent=4)
        return 0


if __name__ == "__main__":
    main()
