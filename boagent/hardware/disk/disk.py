from dataclasses import dataclass
import os
import re


class DiskException(Exception):
    pass


@dataclass
class Partition:
    major: int | None = None
    minor: int | None = None
    blocks: int | None = None
    name: str | None = None

    @classmethod
    def from_proc(cls, data=None):
        if not data:
            raise DiskException("No data found!")

        data = data.strip().split()
        obj = {
            "major": int(data[0]),
            "minor": int(data[1]),
            "blocks": int(data[2]),
            "name": data[3],
        }
        return cls(**obj)


class Disk:
    def __init__(self, sysfs_device_path):
        self._type: str = "type"
        self._size: int = 0
        self._blocks: int | str = 0
        self._model: str = "model"
        self._vendor: str = "vendor"
        self._major_minor: str = "major:minor"
        self._partitions: list = []
        self._sysfs_path: str = sysfs_device_path
        self._name: str = os.path.basename(sysfs_device_path)
        self._looked_up: bool = False

    @property
    def type(self):
        return self._type

    @property
    def size(self):
        return self._size

    @property
    def model(self):
        return self._model

    @property
    def vendor(self):
        self._vendor = self.__check_vendor(self._model).lower()
        return self._vendor

    @staticmethod
    def __try_to_read_first_line(item_path: str, default_value: str) -> str:
        first_line = default_value
        if os.path.exists(item_path):
            with open(item_path, "r") as f:
                first_line = f.readline().strip()
        return first_line

    @staticmethod
    # If one of the strings in /sys/block/***/device/model has numbers, it is not a valid vendor
    def __check_vendor(model_string: str) -> str:
        split_model = model_string.split(" ")
        model_first_str = split_model[0]
        model_second_str = split_model[1]
        check_first_string_for_numbers = re.search("\\d", model_first_str)
        result = bool(check_first_string_for_numbers)
        if result:
            return model_second_str
        else:
            return model_first_str

    @staticmethod
    def __safe_int(maybeint: str) -> int | str:
        try:
            return int(maybeint)
        except ValueError:
            return "Unknown"

    @staticmethod
    def __rotational_info_to_disk_type(info):
        disk_type = "Unknown"
        iinfo = Disk.__safe_int(info)
        if iinfo is not None:
            if iinfo == 0:
                disk_type = "ssd"
            elif iinfo == 1:
                disk_type = "hdd"
        return disk_type

    def _populate_partitions(self):
        """
        Retrieve partitions information for one device from sysfs
        """
        part_info_path_base = f"{self._sysfs_path}/{self._name}"
        index = 1
        part_info_path = f"{part_info_path_base}{index}"
        while os.path.exists(part_info_path):
            majmin = Disk.__try_to_read_first_line(
                f"{part_info_path}/dev", "-1:-1"
            ).split(":")

            self._partitions.append(
                Partition(
                    major=Disk.__safe_int(majmin[0]),
                    minor=Disk.__safe_int(majmin[1]),
                    blocks=Disk.__safe_int(
                        Disk.__try_to_read_first_line(f"{part_info_path}/size", 0)
                    ),
                    name=f"{self._name}{index}",
                )
            )
            index += 1
            part_info_path = f"{part_info_path_base}{index}"

    def lookup(self):
        """
        Retrieve disk information from /sys/block/xxx where xxx is device logical name.
        Data read/guessed :
        * disk model (usually "Vendor Model")
        * disk type (hdd / ssd), guessed from /sys/block/xxx/queue/rotational
        * disk size, computed from sectors count
        * partitions
        """

        if self._looked_up:
            return

        self._model = Disk.__try_to_read_first_line(
            f"{self._sysfs_path}/device/model", "Unknown model"
        )
        rotational = Disk.__try_to_read_first_line(
            f"{self._sysfs_path}/queue/rotational", "Unknown"
        )
        self._type = Disk.__rotational_info_to_disk_type(rotational)
        self._major_minor = Disk.__try_to_read_first_line(
            f"{self._sysfs_path}/dev", "Unknown"
        )
        sectors_count = Disk.__safe_int(
            Disk.__try_to_read_first_line(f"{self._sysfs_path}/size", "Unknown")
        )
        if type(sectors_count) is int:
            # Linux uses 512 bytes sectors
            self._size = sectors_count // (2 * 1024 * 1024)
            self._blocks = sectors_count
        self._populate_partitions()

        self._looked_up = True

    def __repr__(self):
        if not self._looked_up:
            self.lookup()

        ret = ""
        ret = f"Disk ({self._major_minor}) {self._name}: \n"
        ret += f"\tBlocks: {self._blocks}\n"
        ret += f"\tSize: {self._size}Gb\n"
        ret += f"\tModel: {self._model}\n"
        ret += f"\tType: {self._type}\n"
        ret += "\n"

        ret += f"Disk has {len(self._partitions)} partition(s): \n"
        for part in self._partitions:
            if part.minor != 0:
                ret += f"\tBlocks: {part.blocks}\n"
                ret += f"\tSize: {part.blocks // (2 * 1024 * 1024)}Gb\n"
                ret += f"\tName: {part.name}\n"
                ret += "\n"

        return ret


def search_physical_drives():
    disks = []

    virtual_drive_pattern = re.compile(".*/devices/virtual/.*")
    for possible_drive in os.scandir("/sys/block"):
        realpath = os.path.realpath(possible_drive.path)
        # path seems to point to a "real" drive
        if virtual_drive_pattern.match(realpath) is None:
            disks.append(Disk(sysfs_device_path=realpath))

    return disks
