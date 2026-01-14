import win32com.client


def get_property(com_object, field: str) -> str:
    property = com_object.Properties_(field).Value
    return property


def get_win32_instances(class_name: str):
    instances = win32com.client.GetObject("winmgmts:").InstancesOf(class_name)
    return instances


class Hardware:
    def __init__(self) -> None:
        self.cpus = []

    def find_cpus(self) -> dict:
        cpus = {"cpus": []}
        processors = get_win32_instances("Win32_Processor")
        for processor in processors:
            cpu_name = get_property(processor, "Name")
            cpu_manufacturer = get_property(processor, "Manufacturer")
            cpu_core_units = get_property(processor, "NumberOfCores")
            cpu = {
                "name": cpu_name,
                "manufacturer": cpu_manufacturer,
                "core_units": cpu_core_units,
            }
            cpus["cpus"].append(cpu)

        return cpus
