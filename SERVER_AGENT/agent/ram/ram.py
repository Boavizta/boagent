from dataclasses import dataclass
from typing import List, Optional

from ram.dmidecode import get_dmidecode_info, DMIDecodeError
from ram.meminfo import get_meminfo, MemInfoError


@dataclass()
class MemoryDevice:
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    size_gb: Optional[int] = None
    type_: Optional[str] = None
    speed_mt_s: Optional[int] = None
    form_factor: Optional[str] = None


def get_ram_info() -> Optional[List[MemoryDevice]]:
    try:
        return get_dmidecode_info()
    except DMIDecodeError:
        pass

    try:
        return get_meminfo()
    except MemInfoError:
        pass
