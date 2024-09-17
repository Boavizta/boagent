import os
import json
from unittest import TestCase, TestSuite, TestLoader
from unittest.mock import patch
from boagent.api.api import (
    get_metrics,
)
from boagent.api.process import Process, InvalidPIDException

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
hardware_cli = os.path.join(f"{current_dir}", "../../boagent/hardware/hardware_cli.py")
hardware_data = os.path.join(f"{current_dir}", "../../boagent/api/hardware_data.json")


class AllocateEmbeddedImpactForProcess(TestCase):
    def setUp(self):

        self.start_time = 1710837858
        self.end_time = 1710841458
        self.verbose = False
        self.location = "EEE"
        self.measure_power = False
        self.lifetime = 5.0
        self.fetch_hardware = False
        self.pid = 3099

        with open(mock_boaviztapi_response_not_verbose, "r") as boaviztapi_data:
            self.boaviztapi_data = json.load(boaviztapi_data)

        with open(mock_get_metrics_verbose) as get_metrics_verbose:
            self.get_metrics_verbose = json.load(get_metrics_verbose)

        self.process = Process(mock_get_metrics_verbose, self.pid)

    @patch("boagent.api.api.query_machine_impact_data")
    def test_get_total_embedded_impacts_for_host(
        self, mocked_query_machine_impact_data
    ):

        total_embedded_impacts_host = get_metrics(
            self.start_time,
            self.end_time,
            self.verbose,
            self.location,
            self.measure_power,
            self.lifetime,
            self.fetch_hardware,
        )

        mocked_query_machine_impact_data.return_value = self.boaviztapi_data

        assert "embedded_emissions" in total_embedded_impacts_host
        assert "embedded_abiotic_resources_depletion" in total_embedded_impacts_host
        assert "embedded_primary_energy" in total_embedded_impacts_host

    def test_get_process_info(self):

        process_details = self.process.process_info
        for process in process_details:
            assert type(process) is dict
            self.assertEqual(process["pid"], 3099)
            self.assertEqual(
                process["exe"], "/snap/firefox/4336/usr/lib/firefox/firefox"
            )
        assert type(process_details) is list

    def test_get_process_name(self):

        expected_process_name = "firefox"
        process_name = self.process.process_name

        self.assertEqual(expected_process_name, process_name)

    def test_get_process_exe(self):

        expected_process_exe = "/snap/firefox/4336/usr/lib/firefox/firefox"
        process_exe = self.process.process_exe

        self.assertEqual(expected_process_exe, process_exe)

    def test_validate_pid_with_error_if_process_id_not_in_metrics(self):

        expected_error_message = (
            "Process_id 1234 has not been found in metrics data. Check the queried PID"
        )

        with self.assertRaises(InvalidPIDException) as context_manager:
            self.process = Process(mock_get_metrics_verbose, 1234)

        self.assertEqual(context_manager.exception.message, expected_error_message)

        with self.assertRaises(InvalidPIDException) as context_manager:
            self.process.pid = 1234

        self.assertEqual(context_manager.exception.message, expected_error_message)

    def test_get_total_ram_in_bytes(self):

        expected_ram_total = 8589934592
        total_ram_in_bytes = self.process.get_total_ram_in_bytes()
        assert type(total_ram_in_bytes) is int
        self.assertEqual(total_ram_in_bytes, expected_ram_total)

    def test_get_process_ram_share_by_timestamp(self):

        expected_ram_shares = [5.918979644775391, 0.0, 5.9177398681640625]
        process_ram_shares = self.process.ram_shares
        for index, ram_share in enumerate(process_ram_shares):
            assert type(ram_share) is float
            self.assertEqual(ram_share, expected_ram_shares[index])
        assert type(process_ram_shares) is list

    def test_get_disk_usage_in_bytes(self):
        disk_total_bytes = int(
            self.get_metrics_verbose["raw_data"]["power_data"]["raw_data"][1]["host"][
                "components"
            ]["disks"][0]["disk_total_bytes"]
        )
        disk_available_bytes = int(
            self.get_metrics_verbose["raw_data"]["power_data"]["raw_data"][1]["host"][
                "components"
            ]["disks"][0]["disk_available_bytes"]
        )
        expected_disk_usage = disk_total_bytes - disk_available_bytes
        disk_usage = self.process.get_disk_usage_in_bytes()
        assert type(disk_usage) is int
        self.assertEqual(expected_disk_usage, disk_usage)

    def test_get_process_storage_share_by_timestamp(self):

        expected_storage_shares = [0.0, 0.0, 0.0]
        process_storage_shares = self.process.storage_shares
        for index, storage_share in enumerate(process_storage_shares):
            assert type(storage_share) is float
            self.assertEqual(storage_share, expected_storage_shares[index])
        assert type(process_storage_shares) is list

    def test_get_embedded_impact_share_for_storage_by_timestamp(self):

        storage_embedded_impact_shares = (
            self.process.get_component_embedded_impact_shares(
                "SSD", self.process.storage_shares
            )
        )

        for storage_embedded_impact_share in storage_embedded_impact_shares:
            assert type(storage_embedded_impact_share) is tuple
            for value in storage_embedded_impact_share:
                assert type(storage_embedded_impact_share[1]) is float
            assert type(storage_embedded_impact_shares)

    def test_get_embedded_impact_share_for_ram_by_timestamp(self):

        ram_embedded_impact_shares = self.process.get_component_embedded_impact_shares(
            "RAM", self.process.ram_shares
        )

        for ram_embedded_impact_share in ram_embedded_impact_shares:
            assert type(ram_embedded_impact_share) is tuple
            for value in ram_embedded_impact_share:
                assert type(ram_embedded_impact_share[1]) is float
        assert type(ram_embedded_impact_shares) is list

    def test_get_process_cpu_load_shares_by_timestamp(self):

        expected_cpu_load_shares = [5.9772415, 5.2776732, 2.9987452]
        process_cpu_load_shares = self.process.cpu_load_shares

        for index, cpu_load_share in enumerate(process_cpu_load_shares):
            assert type(cpu_load_share) is float
            self.assertEqual(cpu_load_share, expected_cpu_load_shares[index])
        assert type(process_cpu_load_shares) is list

    def test_get_embedded_impact_share_for_cpu_by_timestamp(self):

        cpu_embedded_impact_shares = self.process.get_component_embedded_impact_shares(
            "CPU", self.process.cpu_load_shares
        )

        for cpu_embedded_impact_share in cpu_embedded_impact_shares:
            assert type(cpu_embedded_impact_share) is tuple
        assert type(cpu_embedded_impact_shares) is list

    def test_get_avg_min_max_embedded_impact_shares_for_cpu_and_ram(self):

        impact_criterias = ["gwp", "adp", "pe"]
        cpu_embedded_impact_values = self.process.get_component_embedded_impact_values(
            "cpu"
        )
        ram_embedded_impact_values = self.process.get_component_embedded_impact_values(
            "ram"
        )

        assert type(cpu_embedded_impact_values) is dict
        assert type(ram_embedded_impact_values) is dict
        for criteria in impact_criterias:
            assert f"{criteria}_cpu_average_impact" in cpu_embedded_impact_values
            assert f"{criteria}_cpu_max_impact" in cpu_embedded_impact_values
            assert f"{criteria}_cpu_min_impact" in cpu_embedded_impact_values
            assert f"{criteria}_ram_average_impact" in ram_embedded_impact_values
            assert f"{criteria}_ram_max_impact" in ram_embedded_impact_values
            assert f"{criteria}_ram_min_impact" in ram_embedded_impact_values

    def test_get_embedded_impact_values_with_error_if_invalid_component_queried(self):

        invalid_component_queried = self.process.get_component_embedded_impact_values(
            "invalid_component"
        )
        assert (
            invalid_component_queried
            == "Queried component is not available for evaluation."
        )

    def test_get_embedded_impact_values_for_ssd(self):

        impact_criterias = ["gwp", "adp", "pe"]
        storage_embedded_impact_values = (
            self.process.get_component_embedded_impact_values("ssd")
        )

        assert type(storage_embedded_impact_values) is dict
        for criteria in impact_criterias:
            assert f"{criteria}_ssd_average_impact" in storage_embedded_impact_values


loader = TestLoader()
suite = TestSuite()

suite.addTests(loader.loadTestsFromTestCase(AllocateEmbeddedImpactForProcess))