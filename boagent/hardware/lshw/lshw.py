from shutil import which
import subprocess
import logging
import json
import sys
import re
import os

# Commented elements only available when runnning `lshw` as `sudo`.

SYS_BLOCK_PATH = "/sys/block"


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable"""
    return which(name) is not None


def check_disk_vendor(model_string: str) -> str:
    split_model = model_string.split(" ")

    if len(split_model) == 1:
        check_string_for_numbers = bool(re.search("\\d", model_string))
        if check_string_for_numbers:
            raise Exception(
                "Lshw did not output an acceptable manufacturer name for this device."
            )
        else:
            return model_string

    model_first_str = split_model[0]
    model_second_str = split_model[1]
    check_first_string_for_numbers = bool(re.search("\\d", model_first_str))
    if check_first_string_for_numbers:
        return model_second_str
    else:
        return model_first_str


def get_rotational_int(dev_path: str) -> int:

    device = dev_path.removeprefix("/dev")

    try:
        rotational_fp = os.path.realpath(
            f"{SYS_BLOCK_PATH}{device}/queue/rotational", strict=True
        )

    except OSError:
        print("Rotational file was not found")
        return 2
    else:
        with open(rotational_fp, "r") as file:
            rotational_int = int(file.read())
    return rotational_int


def get_disk_type(dev_path: str) -> str:

    rotational = get_rotational_int(dev_path)

    if rotational == 0:
        return "ssd"
    if rotational == 1:
        return "hdd"
    if rotational == 2:
        return "unknown"
    return "unknown"


class Lshw:
    def __init__(self):
        if not is_tool("lshw"):
            logging.error("lshw does not seem to be installed")
            sys.exit(1)

        data = subprocess.getoutput("sudo lshw -quiet -json 2> /dev/null")
        json_data = json.loads(data)
        # Starting from version 02.18, `lshw -json` wraps its result in a list
        # rather than returning directly a dictionary
        if isinstance(json_data, list):
            self.hw_info = json_data[0]
        else:
            self.hw_info = json_data
        self.info = {}
        self.memories = []
        # self.interfaces = []
        self.cpus = []
        self.power = []
        self.disks = []
        self.gpus = []
        # self.vendor = self.hw_info["vendor"]
        # self.product = self.hw_info["product"]
        # self.chassis_serial = self.hw_info["serial"]
        self.motherboard_serial = self.hw_info["children"][0].get("serial", "No S/N")
        self.motherboard = self.hw_info["children"][0].get("product", "Motherboard")

        for k in self.hw_info["children"]:
            if k["class"] == "power":
                # self.power[k["id"]] = k
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
                        "manufacturer": check_disk_vendor(device["vendor"]).lower(),
                        "capacity": device["size"] // 1073741824,
                        "logicalname": device["logicalname"],
                        "type": get_disk_type(device["logicalname"]),
                    }
                    self.disks.append(d)
                    self.disks[0]["units"] += 1
        if "nvme" in obj["configuration"]["driver"]:
            if not is_tool("nvme"):
                logging.error("nvme-cli >= 1.0 does not seem to be installed")
                raise Exception("nvme-cli >= 1.0 does not seem to be installed")
            try:
                nvme = json.loads(
                    subprocess.check_output(
                        ["sudo", "nvme", "-list", "-o", "json"], encoding="utf8"
                    )
                )
                for device in nvme["Devices"]:
                    d = {
                        "units": +1,
                        "logicalname": device["DevicePath"],
                        "manufacturer": check_disk_vendor(
                            device["ModelNumber"]
                        ).lower(),
                        "type": get_disk_type(device["DevicePath"]),
                    }
                    if "UsedSize" in device:
                        d["capacity"] = device["UsedSize"] // 1073741824
                    if "UsedBytes" in device:
                        d["capacity"] = device["UsedBytes"] // 1073741824
                    self.disks.append(d)
            except Exception:
                pass

    def find_cpus(self, obj):
        if "product" in obj:
            self.cpus.append(
                {
                    "units": +1,
                    "name": obj["product"],
                    "vendor": obj["vendor"],
                    "core_units": obj["configuration"]["cores"],
                    # "description": obj["description"],
                    # "location": obj["slot"],
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
                    # if b["class"] == "network":
                    #    self.find_network(b)
                    if b["class"] == "display":
                        self.find_gpus(b)


"""
if __name__ == "__main__":
    pass """
