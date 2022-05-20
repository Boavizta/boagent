from dataclasses import dataclass
import os
import re

class DiskException(Exception):
    pass


@dataclass
class Partition:
    major: int = None
    minor: int = None
    blocks: int = None
    name: str = None

    @classmethod
    def from_proc(cls, data=None):
        if not data:
            raise DiskException('No data found!')

        data = data.strip().split()
        obj = {'major': int(data[0]),
               'minor': int(data[1]),
               'blocks': int(data[2]),
               'name': data[3]}
        return cls(**obj)


class Disk:
    def __init__(self, sysfs_device_path):
        self._type = None
        self._size = None
        self._blocks = None
        self._model = None
        self._major_minor = None
        self._partitions = []
        self._sysfs_path = sysfs_device_path
        self._name = os.path.basename(sysfs_device_path)
        self._looked_up = False

    @property
    def type(self):
        return self._type

    @property
    def size(self):
        return self._size

    def vendor(self):
        return self._model.split(' ')[0]

    @property
    def model(self):
        return self._model

    @staticmethod
    def __try_to_read_first_line(item_path, default_value):
        retour = default_value
        if os.path.exists(item_path):
            with open(item_path, 'r') as f:
                retour = f.readline().strip()
        return retour

    @staticmethod
    def __safe_int(maybeint):
        if maybeint is not None:
            try:
                return int(maybeint)
            except ValueError:
                # on retournera null
                pass
        return None

    @staticmethod
    def __rotational_info_to_disk_type(info):
        retour = "Unknown"
        iinfo = Disk.__safe_int(info)
        if iinfo is not None:
            if iinfo == 0:
                retour = "ssd"
            elif iinfo == 1:
                retour = "hdd"
        return retour

    def _populate_partitions(self):
        """
        Retrieve partitions information for one device from sysfs
        """

    def lookup(self):
        """
        Retrieve disk information from /sys/block/xxx where xxx is device logical name.
        Data read/guessed :
        * disk model (usually "Vendor Model")
        * disk type (hdd / ssd), guessed from /sys/block/xxx/queue/rotational
        * disk size, computed from sectors count
        * partitions
        """
        device = None

        if self._looked_up:
            return

        self._model = Disk.__try_to_read_first_line(f'{self._sysfs_path}/device/model', 'Unknown model')
        rotational = Disk.__try_to_read_first_line(f'{self._sysfs_path}/queue/rotational', None)
        self._type = Disk.__rotational_info_to_disk_type(rotational)
        self._major_minor = Disk.__try_to_read_first_line(f'{self._sysfs_path}/dev', None)
        sectors_count = Disk.__safe_int(Disk.__try_to_read_first_line(f'{self._sysfs_path}/size', None))
        if sectors_count is not None:
            # Linux uses 512 bytes sectors
            self._size = sectors_count // (2 * 1024 * 1024)
            self._blocks = sectors_count
        self._populate_partitions()

        self._looked_up = True

    def __repr__(self):
        if not self._looked_up:
            self.lookup()

        ret = ''
        ret = f'Disk ({self._major_minor}) {self._name}: \n'
        ret += f'\tBlocks: {self._blocks}\n'
        ret += f'\tSize: {self._size}Gb\n'
        ret += f'\tModel: {self._model}\n'
        ret += f'\tType: {self._type}\n'
        ret += '\n'

        ret += f'Disk has {len(self._partitions)} partition(s): \n'
        for part in self._partitions:
            if part.minor != 0:
                ret += f'\tBlocks: {part.blocks}\n'
                ret += f'\tSize: {part.blocks // (1024 * 1024)}Gb\n'
                ret += f'\tName: {part.name}\n'
                ret += '\n'

        return ret


def search_physical_drives():
    disks = []

    virtual_drive_pattern = re.compile('.*/devices/virtual/.*')
    for possible_drive in os.scandir('/sys/block'):
        realpath = os.path.realpath(possible_drive.path)
        # path seems to point to a "real" drive
        if virtual_drive_pattern.match(realpath) is None:
            disks.append(Disk(sysfs_device_path=realpath))

    return disks
