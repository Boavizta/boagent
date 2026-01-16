import win32com.client
from enum import Enum

NUMBER_OF_BYTES_IN_A_GIGABYTE = 1073741824
Win32_WMI_Class = Enum(
    "Win32_WMI_Class",
    [
        ("PROCESSOR", "Win32_Processor"),
        ("MEMORY", "Win32_PhysicalMemory"),
        ("DRIVE", "Win32_DiskDrive"),
        ("LOGICAL_DRIVE", "Win32_LogicalDrive"),
    ],
)

Win32_WMI_Class_Property = Enum(
    "Win32_WMI_Class_Property",
    [
        ("NAME", "Name"),
        ("MANUFACTURER", "Manufacturer"),
        ("CORE_NUMBER", "NumberOfCores"),
        ("CAPACITY", "Capacity"),
    ],
)


def get_property(com_object, field: Win32_WMI_Class_Property) -> str | int:
    property = com_object.Properties_(field.value).Value
    return property


def get_win32_instances(class_name: Win32_WMI_Class):
    instances = win32com.client.GetObject("winmgmts:").InstancesOf(class_name)
    return instances


def convert_to_gigabytes(capacity: int):
    capacity_to_gigabytes = capacity // 2**20 // 1024
    return capacity_to_gigabytes


class Hardware:
    def __init__(self) -> None:
        self.cpus = []
        self.memories = []
        self.disks = []

    def find_cpus(self) -> dict:
        cpus = {"cpus": []}
        processors = get_win32_instances(Win32_WMI_Class.PROCESSOR)
        total_units = len(processors)
        for processor in processors:
            cpu_name = get_property(processor, Win32_WMI_Class_Property.NAME)
            cpu_manufacturer = get_property(
                processor, Win32_WMI_Class_Property.MANUFACTURER
            )
            cpu_core_units = get_property(
                processor, Win32_WMI_Class_Property.CORE_NUMBER
            )
            cpu = {
                "units": total_units,
                "name": cpu_name,
                "manufacturer": cpu_manufacturer,
                "core_units": cpu_core_units,
            }
            cpus["cpus"].append(cpu)

        return cpus

    def find_memories(self) -> dict:
        memories = {"rams": []}
        rams = get_win32_instances(Win32_WMI_Class.MEMORY)
        total_units = len(rams)
        for ram in rams:
            ram_manufacturer = get_property(ram, Win32_WMI_Class_Property.MANUFACTURER)
            ram_capacity = get_property(ram, Win32_WMI_Class_Property.CAPACITY)
            capacity_converted_to_gigabytes = convert_to_gigabytes(ram_capacity)
            ram = {
                "units": total_units,
                "manufacturer": ram_manufacturer,
                "capacity": capacity_converted_to_gigabytes,
            }
            memories["rams"].append(ram)

        return memories

    def find_storage(self) -> dict:
        disks = {"disks": []}
        storage = get_win32_instances(Win32_WMI_Class.DRIVE)
        total_units = len(storage)
        for disk in storage:
            disk_manufacturer = get_property(
                disk, Win32_WMI_Class_Property.MANUFACTURER
            )
            disk_capacity = get_property(disk, Win32_WMI_Class_Property.CAPACITY)
            converted_to_gigabytes = disk_capacity // NUMBER_OF_BYTES_IN_A_GIGABYTE
            disk = {
                "units": total_units,
                "manufacturer": disk_manufacturer,
                "capacity": converted_to_gigabytes,
            }
            disks["disks"].append(disk)

        return disks
