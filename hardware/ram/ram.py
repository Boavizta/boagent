from typing import List, Optional

from .dmidecode import get_dmidecode_info, DMIDecodeError
from .meminfo import get_meminfo, MemInfoError
from .model import MemoryDevice


def get_ram_info() -> Optional[List[MemoryDevice]]:
    try:
        return get_dmidecode_info()
    except DMIDecodeError:
        pass

    try:
        return get_meminfo()
    except MemInfoError:
        pass
