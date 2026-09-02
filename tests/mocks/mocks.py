import os

from boaviztapi_sdk.models.configuration_server import ConfigurationServer

current_dir = os.path.dirname(__file__)
mock_power_data = os.path.join(f"{current_dir}", "../mocks/power_data.json")
mock_hardware_data = os.path.join(f"{current_dir}", "../mocks/hardware_data.json")
mock_boaviztapi_response_not_verbose = os.path.join(
    f"{current_dir}", "../mocks/boaviztapi_response_not_verbose.json"
)
mock_boaviztapi_response_verbose = os.path.join(
    f"{current_dir}", "../mocks/boaviztapi_response_verbose.json"
)
mock_boaviztapi_response_verbose_all_criteria = os.path.join(
    f"{current_dir}", "../mocks/boaviztapi_response_verbose_all_criteria.json"
)
mock_boavizta_response_not_verbose_all_criteria = os.path.join(
    f"{current_dir}", "../mocks/boaviztapi_response_not_verbose_all_criteria.json"
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
mock_get_metrics_not_verbose_all_criteria = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_not_verbose_all_criteria.json"
)
mock_get_metrics_verbose = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_verbose.json"
)
mock_get_metrics_verbose_no_hdd = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_verbose_no_hdd.json"
)
mock_get_metrics_all_criteria_verbose = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_all_criteria_verbose.json"
)
mock_lshw_data = os.path.join(f"{current_dir}", "../mocks/lshw_data.json")
mock_lshw_data_disks = os.path.join(
    f"{current_dir}", "../mocks/sudo_lshw_data_disks.json"
)
mock_sudo_lshw_data = os.path.join(f"{current_dir}", "../mocks/sudo_lshw_data.json")
mock_nvme_data = os.path.join(f"{current_dir}", "../mocks/nvme_data_sudo.json")
hardware_cli = os.path.join(f"{current_dir}", "../../boagent/hardware/hardware_cli.py")
hardware_data = os.path.join(f"{current_dir}", "../../boagent/api/hardware_data.json")


def generate_configuration_server() -> ConfigurationServer:
    hardware_data = {
        "disk": [
            {
                "units": 1,
                "logicalname": "/dev/nvme0n1",
                "manufacturer": "toshiba",
                "type": "ssd",
                "capacity": 238,
            }
        ],
        "cpu": {
            "units": 1,
            "name": "Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz",
            "vendor": "Intel Corp.",
            "core_units": 4,
        },
        "ram": [
            {"units": 1, "manufacturer": "Micron", "capacity": 4},
            {"units": 1, "manufacturer": "Micron", "capacity": 4},
        ],
    }
    configuration_server = ConfigurationServer.model_validate(hardware_data)
    return configuration_server


class MockLshw:
    def __init__(self):
        self.cpu = {
            "cpu": {
                "name": "AMD Ryzen 5 5600H with Radeon Graphics",
                "manufacturer": "Advanced Micro Devices [AMD]",
                "core_units": 6,
                "threads": 8,
            }
        }
        self.memories = [
            {"units": 1, "manufacturer": "Samsung", "capacity": 8},
            {"units": 1, "manufacturer": "Kingston", "capacity": 16},
        ]

        self.disks = [
            {
                "units": 1,
                "logicalname": "/dev/nvme0n1",
                "manufacturer": "samsung",
                "type": "ssd",
                "capacity": 476,
            }
        ]
