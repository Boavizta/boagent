"""
This file is modified code issued from https://github.com/Solvik/netbox-agent/blob/master/netbox_agent/lshw.py,
copyright under Apache-2.0 licence.
"""

from shutil import which
import subprocess
import json
import sys
import re
import os

SYS_BLOCK_PATH = "/sys/block"


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable"""
    return which(name) is not None


def serialized_lshw_output():
    try:
        lshw_output = subprocess.getoutput("lshw -quiet -json 2> /dev/null")
        serialized_lshw_output = json.loads(lshw_output)
    except json.JSONDecodeError:
        raise Exception("lshw does not seem do be executed as root.")
    else:
        if isinstance(serialized_lshw_output, list):
            return serialized_lshw_output[0]
        else:
            return serialized_lshw_output


def serialized_nvme_output():
    nvme_output = subprocess.check_output(
        ["nvme", "-list", "-o", "json"], encoding="utf8"
    )
    serialized_nvme_output = json.loads(nvme_output)
    return serialized_nvme_output


class Lshw:
    def __init__(self):
        if not is_tool("lshw"):
            raise Exception("lshw does not seem to be installed.")
        self.hw_info = serialized_lshw_output()
        self.info = {}
        self.memories = []
        self.cpus = []
        self.power = []
        self.disks = []
        self.gpus = []
        self.motherboard_serial = self.hw_info["children"][0].get("serial", "No S/N")
        self.motherboard = self.hw_info["children"][0].get("product", "Motherboard")

        for k in self.hw_info["children"]:
            if k["class"] == "power":
                self.power.append(k)

            if "children" in k:
                for j in k["children"]:
                    if j["class"] == "generic":
                        continue

                    if j["class"] == "storage":
                        self.find_storage(j)

                    if j["class"] == "memory":
                        self.find_memories(j)

                    if j["class"] == "processor":
                        self.find_cpus(j)

                    if j["class"] == "bridge":
                        self.walk_bridge(j)

    def get_hw_linux(self, hwclass):
        if hwclass == "cpu":
            return self.cpus
        if hwclass == "gpu":
            return self.gpus
        """ if hwclass == "network":
            return self.interfaces """
        if hwclass == "storage":
            return self.disks
        if hwclass == "memory":
            return self.memories

    """
    def find_network(self, obj):
        # Some interfaces do not have device (logical) name (eth0, for
        # instance), such as not connected network mezzanine cards in blade
        # servers. In such situations, the card will be named `unknown[0-9]`.
        unkn_intfs = []
        for i in self.interfaces:
            # newer versions of lshw can return a list of names, see issue #227
            if not isinstance(i["name"], list):
                if i["name"].startswith("unknown"):
                    unkn_intfs.push(i)
            else:
                for j in i["name"]:
                    if j.startswith("unknown"):
                        unkn_intfs.push(j)

        unkn_name = "unknown{}".format(len(unkn_intfs))
        self.interfaces.append(
            {
                "name": obj.get("logicalname", unkn_name),
                "macaddress": obj.get("serial", ""),
                "serial": obj.get("serial", ""),
                "product": obj["product"],
                "vendor": obj["vendor"],
                "description": obj["description"],
            }
        )
    """

    def find_storage(self, obj):
        if "children" in obj:
            for device in obj["children"]:
                if "vendor" in device and "size" in device:
                    d = {
                        "units": +1,
                        "manufacturer": self.check_disk_vendor(
                            device["vendor"]
                        ).lower(),
                        "capacity": device["size"],
                        "logicalname": device["logicalname"],
                        "type": self.get_disk_type(device["logicalname"]),
                    }
                    self.disks.append(d)
        if "configuration" in obj:
            if "nvme" in obj["configuration"]["driver"]:
                if not is_tool("nvme"):
                    raise Exception("nvme-cli >= 1.0 does not seem to be installed")
                try:
                    nvme = serialized_nvme_output()
                    for device in nvme["Devices"]:
                        d = {
                            "units": +1,
                            "logicalname": device["DevicePath"],
                            "manufacturer": self.check_disk_vendor(
                                device["ModelNumber"]
                            ).lower(),
                            "type": "ssd",
                            "capacity": device["PhysicalSize"] // 1073741824,
                        }
                        self.disks.append(d)
                except Exception:
                    pass

    def find_cpus(self, obj):
        if "product" in obj:
            self.cpus.append(
                {
                    "units": +1,
                    "name": obj["product"],
                    "manufacturer": obj["vendor"],
                    "core_units": int(obj["configuration"]["cores"]),
                }
            )

    def find_memories(self, obj):
        if "children" not in obj:
            # print("not a DIMM memory.")
            return

        for dimm in obj["children"]:
            if "empty" in dimm["description"]:
                continue

            self.memories.append(
                {
                    "units": +1,
                    "manufacturer": dimm.get("vendor", "N/A"),
                    "capacity": dimm.get("size", 0) // 2**20 // 1024,
                }
            )

    def find_gpus(self, obj):
        if "product" in obj:
            self.gpus.append(
                {
                    "product": obj["product"],
                    "vendor": obj["vendor"],
                    "description": obj["description"],
                }
            )

    def walk_bridge(self, obj):
        if "children" not in obj:
            return

        for bus in obj["children"]:
            if bus["class"] == "storage":
                self.find_storage(bus)
            if bus["class"] == "display":
                self.find_gpus(bus)

            if "children" in bus:
                for b in bus["children"]:
                    if b["class"] == "storage":
                        self.find_storage(b)
                    if b["class"] == "display":
                        self.find_gpus(b)

    def check_disk_vendor(self, model_string: str) -> str:
        split_model = model_string.split(" ")
        vendor = ""

        if len(split_model) == 1:
            check_string_for_numbers = bool(re.search("\\d", model_string))
            if check_string_for_numbers:
                raise Exception(
                    "Lshw did not output a parsable manufacturer name for this device."
                )
            else:
                return model_string

        model_first_str = split_model[0]
        model_second_str = split_model[1]
        check_first_string_for_numbers = re.search("\\d", model_first_str)
        result = bool(check_first_string_for_numbers)

        if result:
            vendor = model_second_str
            return vendor
        else:
            vendor = model_first_str
            return vendor

    def get_disk_type(self, dev_path: str) -> str:

        rotational = self.get_rotational_int(dev_path)

        if rotational == 0:
            return "ssd"
        if rotational == 1:
            return "hdd"
        if rotational == 2:
            return "unknown"
        return "unknown"

    def get_rotational_int(self, dev_path: str) -> int:

        device = dev_path.removeprefix("/dev")

        try:
            rotational_fp = os.path.realpath(
                f"{SYS_BLOCK_PATH}{device}/queue/rotational", strict=True
            )

        except OSError:
            sys.stderr.write("Rotational file was not found")
            return 2
        else:
            with open(rotational_fp, "r") as file:
                rotational_int = int(file.read())
        return rotational_int
