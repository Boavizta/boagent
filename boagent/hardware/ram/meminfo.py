import re

from typing import List

from .model import MemoryDevice

CONVERT_KB_IN_GB = 9.536e-7


class MemInfoError(Exception):
    pass


def get_meminfo() -> List[MemoryDevice]:
    try:
        memory_size_kb = get_total_memory_in_kb()
        memory_size_gb = convert_kb_in_gb(memory_size_kb)
        return [MemoryDevice(size_gb=memory_size_gb)]
    except Exception as e:
        raise MemInfoError('cannot extract ram info from meminfo.') from e


def get_total_memory_in_kb() -> int:
    with open('/proc/meminfo', 'r') as f:
        for line in f.readlines():
            if 'MemTotal' in line:
                mem_total_line = line.strip()
                break
    total_size_kb = int(re.search(r'[0-9]+', mem_total_line)[0])
    return total_size_kb


def convert_kb_in_gb(value: int) -> int:
    return int(value * CONVERT_KB_IN_GB)
