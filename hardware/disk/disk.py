from dataclasses import dataclass
from os import stat, path, major as _major
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
    def __init__(self, mount_point=None):
        self._type = None
        self._size = None
        self._model = None
        self._partitions = []
        self._mount_point = mount_point
        if not mount_point:
            self._mount_point = '/boot'
        self._sysfs_path = None
        self._looked_up = False

    def __init__(self, sysfs_device_path):
        self._type = None
        self._size = None
        self._model = None
        self._partitions = []
        self._mount_point = None
        self._sysfs_path = sysfs_device_path
        self._looked_up = False

    def __get_type(self):
        name = self._partitions[0].name.split('0')[0]

        disk_type = "not sure"
        type_path = "/sys/block/{}/queue/rotational".format(name)
        if path.exists(type_path):
            with open(type_path, 'r') as fd:
                res = fd.read()
                disk_type = Disk.__rotational_info_to_disk_type(res)

        return disk_type

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

    # TODO kept for now, maybe remove if lookup_by_sysfs is sufficient
    def _lookup_by_mountpoint(self):
        try:
            device = stat(self._mount_point).st_dev
        except FileNotFoundError as ex:
            raise DiskException('Cannot find mount point '
                                f'{self._mount_point}.') from ex

        # Get Major
        major = _major(device)

        with open('/proc/partitions', 'r') as fs:
            lines = fs.readlines()

            # Skip two first lines
            lines.pop(0)  # major minor  #blocks  name
            lines.pop(0)  # Empty line

            for line in lines:
                part = Partition.from_proc(line)
                if part.major == major:
                    self._partitions.append(part)

        # Extract device information
        device_path = f'/sys/dev/block/{major}:0/device'
        try:
            with open(f'{device_path}/model', 'r') as fs:
                self._model = fs.readline().strip()
        except FileNotFoundError:
            self._model = 'Unknown model'

        self._type = self.__get_type()
        # Get total size and type
        for part in self._partitions:
            if part.minor == 0:
                self._size = part.blocks // (1024 * 1024)

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

    def _lookup_by_sysfs_path(self):
        self._model = Disk.__try_to_read_first_line(f'{self._sysfs_path}/device/model', 'Unknown model')
        rotational = Disk.__try_to_read_first_line(f'{self._sysfs_path}/queue/rotational', None)
        self._type = Disk.__rotational_info_to_disk_type(rotational)
        sectors_count = Disk.__safe_int(Disk.__try_to_read_first_line(f'{self._sysfs_path}/size', None))
        if sectors_count is not None:
            # Linux uses 512 bytes sectors
            self._size = sectors_count // (2 * 1024 * 1024)

    def lookup(self):
        device = None

        if self._looked_up:
            return

        if self._mount_point is not None:
            self._lookup_by_mountpoint()
        else:
            self._lookup_by_sysfs_path()

        self._looked_up = True

    def __repr__(self):
        if not self._looked_up:
            self.lookup()

        ret = ''
        for part in self._partitions:
            if part.minor == 0:
                main_dev = part
                break

        ret = f'Disk ({main_dev.major}:{main_dev.minor}) {main_dev.name}: \n'
        ret += f'\tBlocks: {main_dev.blocks}\n'
        ret += f'\tSize: {self.size}Gb\n'
        ret += f'\tModel: {self.model}\n'
        ret += f'\tType: {self.type}\n'
        ret += '\n'

        ret += f'Disk has {len(self._partitions) - 1} partition(s): \n'
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
