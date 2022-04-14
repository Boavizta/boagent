from dataclasses import dataclass
from os import stat, path, major as _major


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
        self._looked_up = False

    def __get_type(self):
        name = self._partitions[0].name.split('0')[0]

        disk_type = "not sure"
        type_path = "/sys/block/{}/queue/rotational".format(name)
        if path.exists(type_path):
            with open(type_path, 'r') as fd:
                res = fd.read()
                if int(res) == 0:
                    disk_type = "ssd"
                elif int(res) == 1:
                    disk_type = "hdd"

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

    def lookup(self):
        device = None

        if self._looked_up:
            return

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
