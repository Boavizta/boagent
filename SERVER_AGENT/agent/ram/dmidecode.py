import re
import subprocess

from typing import Optional, Mapping, List

from .model import MemoryDevice


class DMIDecodeError(Exception):
    pass


def get_dmidecode_info() -> List[MemoryDevice]:
    try:
        cmd_output = execute_dmidecode()
        return parse_dmidecode(cmd_output)
    except Exception as e:
        raise DMIDecodeError('cannot extract ram info from dmidecode.') from e


def execute_dmidecode() -> Optional[str]:
    proc = subprocess.Popen(['dmidecode', '-t', '17'], stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode > 0:
        raise RuntimeError(f'failed to run dmidecode command.')
    else:
        return stdout.decode()


def parse_dmidecode(dmidecode_dump: str) -> List[MemoryDevice]:
    memory_devices = []
    for record in dmidecode_dump.split('\n\n'):
        if skip_record(record):
            continue

        record_lines = record.split('\n')
        record_map = build_record_map(record_lines)

        if not is_record_map_valid(record_map):
            continue

        memory_devices.append(parse_record_map_to_memory_device(record_map))
    return memory_devices


def skip_record(record) -> bool:
    if len(record.split('\n')) < 4:
        return True
    return False


def build_record_map(record_lines: List[str]) -> Mapping[str, str]:
    record_map = {}
    for raw_line in record_lines:
        if skip_record_line(raw_line):
            continue
        line = raw_line.replace('\t', '')
        line = line.strip()
        key, value = line.split(':')
        value = value.strip()
        record_map[key] = value
    return record_map


def skip_record_line(line: str) -> bool:
    if not line.startswith('\t'):
        return True
    return False


def is_record_map_valid(record_map: Mapping) -> bool:
    if re.search(r'empty', record_map['Manufacturer'], re.IGNORECASE):
        return False
    return True


def parse_record_map_to_memory_device(record_map: Mapping[str, str]):
    size = record_map.get('Size')
    if size:
        size = parse_size_to_gb(size)

    speed = record_map.get('Speed')
    if speed:
        speed = parse_speed_to_mt_s(speed)

    return MemoryDevice(
        manufacturer=record_map.get('Manufacturer'),
        model=record_map.get('Part Number'),
        size_gb=size,
        type_=record_map.get('Type'),
        speed_mt_s=speed,
        form_factor=record_map.get('Form Factor')
    )


def parse_size_to_gb(size_str: str) -> int:
    size = re.search(r'[0-9]+', size_str)
    if size:
        size = int(size[0])
        if 'MB' in size_str:
            size = int(size / 1024)
        return size
    return 0


def parse_speed_to_mt_s(speed_str: str) -> int:
    speed = re.search(r'[0-9]+', speed_str)
    if speed:
        return int(speed[0])
    return 0
