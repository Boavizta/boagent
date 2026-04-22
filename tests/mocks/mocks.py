import os

current_dir = os.path.dirname(__file__)
mock_power_data = os.path.join(f"{current_dir}", "../mocks/power_data.json")
mock_hardware_data = os.path.join(f"{current_dir}", "../mocks/hardware_data.json")
mock_boaviztapi_response_not_verbose = os.path.join(
    f"{current_dir}", "../mocks/boaviztapi_response_not_verbose.json"
)
mock_boaviztapi_response_verbose = os.path.join(
    f"{current_dir}", "../mocks/boaviztapi_response_verbose.json"
)
mock_formatted_scaphandre = os.path.join(
    f"{current_dir}", "../mocks/formatted_power_data_one_hour.json"
)
mock_formatted_scaphandre_with_processes = os.path.join(
    f"{current_dir}", "../mocks/formatted_scaphandre.json"
)
mock_get_metrics_not_verbose = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_not_verbose.json"
)
mock_get_metrics_verbose = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_verbose.json"
)
mock_get_metrics_verbose_no_hdd = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_verbose_no_hdd.json"
)
mock_lshw_data = os.path.join(f"{current_dir}", "../mocks/lshw_data.json")
mock_lshw_data_disks = os.path.join(
    f"{current_dir}", "../mocks/sudo_lshw_data_disks.json"
)
mock_sudo_lshw_data = os.path.join(f"{current_dir}", "../mocks/sudo_lshw_data.json")
mock_nvme_data = os.path.join(f"{current_dir}", "../mocks/nvme_data_sudo.json")
hardware_cli = os.path.join(f"{current_dir}", "../../boagent/hardware/hardware_cli.py")
hardware_data = os.path.join(f"{current_dir}", "../../boagent/api/hardware_data.json")


class MockLshw:
    def __init__(self):
        self.cpus = {
            "cpus": [
                {
                    "units": 1,
                    "name": "AMD Ryzen 5 5600H with Radeon Graphics",
                    "manufacturer": "Advanced Micro Devices [AMD]",
                    "core_units": 6,
                }
            ]
        }
        self.memories = {
            "rams": [
                {"units": 1, "manufacturer": "Samsung", "capacity": 8},
                {"units": 1, "manufacturer": "Kingston", "capacity": 16},
            ]
        }
        self.disks = {
            "disks": [
                {
                    "units": 1,
                    "logicalname": "/dev/nvme0n1",
                    "manufacturer": "samsung",
                    "type": "ssd",
                    "capacity": 476,
                }
            ],
        }


def generate_mock_file_system(temp_mount_path):
    volumes_path = temp_mount_path + "/volumes"
    first_vm_path = volumes_path + "/vm1"
    second_vm_path = volumes_path + "/vm2"

    os.mkdir(volumes_path)
    os.mkdir(first_vm_path)
    os.mkdir(second_vm_path)

    # Virtual machine metrics file format is not established yet. This might need to be modified.
    first_mock_metrics_content = r'{"name": "virtual-machine-1", "processes":[{"exe": "/usr/bin/containerd","cmdline": "/usr/bin/containerd","pid": 685,"resources_usage":{"cpu_usage": "0.025018765","cpu_usage_unit": "%","memory_usage": "51855360","memory_usage_unit": "Bytes","memory_virtual_usage": "0","memory_virtual_usage_unit": "Bytes","disk_usage_write": "2097152","disk_usage_write_unit": "Bytes","disk_usage_read": "0","disk_usage_read_unit": "Bytes"},"consumption": 1978.3303,"timestamp": 1716977654.2153192,"container": null}]}'

    second_mock_metrics_content = r'{"name": "virtual-machine-2", "processes":[{"exe": "/usr/bin/containerd","cmdline": "/usr/bin/containerd","pid": 685,"resources_usage":{"cpu_usage": "0.025018765","cpu_usage_unit": "%","memory_usage": "51855360","memory_usage_unit": "Bytes","memory_virtual_usage": "0","memory_virtual_usage_unit": "Bytes","disk_usage_write": "0","disk_usage_write_unit": "Bytes","disk_usage_read": "0","disk_usage_read_unit": "Bytes"},"consumption": 1978.3303,"timestamp": 1716977654.2153192,"container": null}]}'

    with open(f"{first_vm_path}/metrics.json", "w") as tmp_metrics_file:
        tmp_metrics_file.write(first_mock_metrics_content)

    with open(f"{second_vm_path}/metrics.json", "w") as tmp_metrics_file:
        tmp_metrics_file.write(second_mock_metrics_content)
