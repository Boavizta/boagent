import os
import json
from unittest import TestCase
from tempfile import TemporaryDirectory
from boagent.api.hypervisor import (
    deserialize_virtual_machines_metrics,
    evaluate_virtual_machines,
)
from tests.mocks.mocks import mock_get_metrics_verbose


class ReadMountPath(TestCase):
    def setUp(self):
        temp_mount_path = self.enterContext(TemporaryDirectory())
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

        self.mount_path = temp_mount_path

    def test_deserialize_virtual_machines_metrics(self):
        vms_metrics = deserialize_virtual_machines_metrics(self.mount_path)

        assert len(vms_metrics) == 2

    def test_evaluate_virtual_machines(self):
        vms_metrics = deserialize_virtual_machines_metrics(self.mount_path)

        with open(f"{mock_get_metrics_verbose}", "r") as hypervisor_metrics_file:
            deserialized_hypervisor_metrics = json.load(hypervisor_metrics_file)
            hypervisor_hardware_data = deserialized_hypervisor_metrics["raw_data"][
                "hardware_data"
            ]

        evaluated_virtual_machines = evaluate_virtual_machines(
            vms_metrics, hypervisor_hardware_data
        )

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
