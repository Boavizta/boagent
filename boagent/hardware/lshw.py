from shutil import which
import subprocess
import logging
import json
import sys
import re

# Commented elements only available when runnning `lshw` as `sudo`.


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable"""
    return which(name) is not None


def check_disk_vendor(model_string: str) -> str:
    split_model = model_string.split(" ")
    model_first_str = split_model[0]
    model_second_str = split_model[1]
    check_first_string_for_numbers = re.search("\\d", model_first_str)
    result = bool(check_first_string_for_numbers)
    if result:
        return model_second_str
    else:
        return model_first_str

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
        self.memories = [{"units": 0}]
        # self.interfaces = []
        self.cpus = [{"units": 0}]
        self.power = []
        self.disks = [{"units": 0}]
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
                if "vendor" in device:
                    d = {
                        "manufacturer": check_disk_vendor(device["vendor"]).lower(),
                        "capacity": device["size"],
                    }
                    if "type" in device == "SCSI Disk":
                        d["type"] = "hdd"
                    if "type" in device == "NVMe device":
                        d["type"] = "ssd"
                    if "type" in device == "Mass storage device":
                        d["type"] = "usb"
                    else:
                        d["type"] = "unknown"
                    self.disks.append(d)
                    self.disks[0]["units"] += 1
        if "nvme" in obj["configuration"]["driver"]:
            if not is_tool("nvme"):
                logging.error("nvme-cli >= 1.0 does not seem to be installed")
                return
            try:
                nvme = json.loads(
                    subprocess.check_output(
                        ["sudo", "nvme", "-list", "-o", "json"], encoding="utf8"
                    )
                )
                for device in nvme["Devices"]:
                    d = {
                        "manufacturer": check_disk_vendor(device["ModelNumber"]).lower(),
                        "type": "ssd",
                    }
                    if "UsedSize" in device:
                        d["capacity"] = (device["UsedSize"] // 1073741824)
                    if "UsedBytes" in device:
                        d["capacity"] = (device["UsedBytes"] // 1073741824)
                    self.disks.append(d)
            except Exception:
                pass

    def find_cpus(self, obj):
        if "product" in obj:
            self.cpus.append(
                {
                    "name": obj["product"],
                    "vendor": obj["vendor"],
                    "core_units": obj["configuration"]["cores"],
                    # "description": obj["description"],
                    # "location": obj["slot"],
                }
            )
            self.cpus[0]["units"] += 1

    def find_memories(self, obj):
        if "children" not in obj:
            # print("not a DIMM memory.")
            return

        for dimm in obj["children"]:
            if "empty" in dimm["description"]:
                continue

            self.memories[0]["units"] += 1

            self.memories.append(
                {
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
