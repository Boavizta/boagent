import json
from unittest import TestCase
from tempfile import TemporaryDirectory
from boagent.api.hypervisor import (
    Hypervisor,
    deserialize_virtual_machines_metrics,
)
from tests.mocks.mocks import generate_mock_file_system, mock_get_metrics_verbose


class HypervisorTest(TestCase):
    def setUp(self):
        temp_mount_path = self.enterContext(TemporaryDirectory())
        generate_mock_file_system(temp_mount_path)
        with open(f"{mock_get_metrics_verbose}", "r") as hypervisor_metrics_file:
            deserialized_hypervisor_metrics = json.load(hypervisor_metrics_file)
            hypervisor_hardware_data = deserialized_hypervisor_metrics["raw_data"][
                "hardware_data"
            ]

        vms_metrics = deserialize_virtual_machines_metrics(temp_mount_path)

        self.hardware_data = hypervisor_hardware_data
        self.vms_metrics = vms_metrics
        self.hypervisor = Hypervisor(self.hardware_data, self.vms_metrics)

    def test_calculate_total_memory(self):
        assert self.hypervisor.total_memory == 8589934592

    def test_evaluate_virtual_machines(self):
        evaluated_virtual_machines = self.hypervisor.evaluated_virtual_machines

        assert (
            round(
                evaluated_virtual_machines["virtual_machines"][0]["processes"][0][
                    "memory_ratio"
                ],
                1,
            )
            == 0.6
        )
        assert (
            round(
                evaluated_virtual_machines["virtual_machines"][0]["processes"][0][
                    "cpu_usage"
                ],
                3,
            )
            == 0.025
        )
        assert (
            round(
                evaluated_virtual_machines["virtual_machines"][1]["processes"][0][
                    "memory_ratio"
                ],
                1,
            )
            == 0.6
        )
        assert (
            round(
                evaluated_virtual_machines["virtual_machines"][1]["processes"][0][
                    "cpu_usage"
                ],
                3,
            )
            == 0.025
        )


class ReadingMountPathTest(TestCase):
    def setUp(self):
        temp_mount_path = self.enterContext(TemporaryDirectory())
        generate_mock_file_system(temp_mount_path)
        self.mount_path = temp_mount_path

        with open(f"{mock_get_metrics_verbose}", "r") as hypervisor_metrics_file:
            deserialized_hypervisor_metrics = json.load(hypervisor_metrics_file)
            hypervisor_hardware_data = deserialized_hypervisor_metrics["raw_data"][
                "hardware_data"
            ]

        self.hardware_data = hypervisor_hardware_data

    def test_deserialize_virtual_machines_metrics(self):
        vms_metrics = deserialize_virtual_machines_metrics(self.mount_path)

        assert len(vms_metrics) == 2
