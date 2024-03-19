from unittest import TestCase, TestSuite, TestLoader
from unittest.mock import patch

from api import (
    build_hardware_data,
    read_hardware_data,
    get_hardware_data,
    # query_machine_impact_data,
    format_usage_request,
    compute_average_consumption,
)

from utils import format_scaphandre_json
import os
import json


class ReadHardwareDataTest(TestCase):
    def test_build_hardware_data(self):

        build_hardware_data()
        assert os.path.exists("./hardware_data.json") is True

    def test_read_hardware_data(self):

        build_hardware_data()
        data = read_hardware_data()
        assert type(data["cpus"]) is list
        assert type(data["rams"]) is list
        assert type(data["disks"]) is list

    @patch("api.build_hardware_data")
    def test_get_hardware_data_with_fetch_hardware_false(self, mocked_build_hardware):

        # Test case where hardware_data.json is already present on the
        # filesystem through previous call to build_hardware_data

        build_hardware_data()
        data = get_hardware_data(fetch_hardware=False)
        assert type(data) is dict
        mocked_build_hardware.assert_not_called()

    def test_get_hardware_data_with_fetch_hardware_true(self):

        data = get_hardware_data(fetch_hardware=True)
        assert type(data) is dict

    # def test_read_query_machine_impact_data(self):
    #    server_impact = query_machine_impact_data()
    #    print(server_impact)
    #    pass

    def tearDown(self) -> None:
        os.remove("./hardware_data.json")


class FormatUsageRequestTest(TestCase):
    def test_format_usage_request_with_start_and_end_times(self):

        start_time = 1710837858
        end_time = 1710841458

        formatted_request = format_usage_request(
            start_time=start_time,
            end_time=end_time,
        )

        assert type(formatted_request) is dict
        assert "hours_use_time" in formatted_request

    def test_format_usage_request_with_host_avg_consumption_use_time_ratio_and_location(
        self,
    ):

        start_time = 1710837858
        end_time = 1710841458
        location = "FRA"
        host_avg_consumption = 120
        use_time_ratio = 1

        formatted_request = format_usage_request(
            start_time=start_time,
            end_time=end_time,
            location=location,
            host_avg_consumption=host_avg_consumption,
            use_time_ratio=use_time_ratio,
        )
        assert type(formatted_request) is dict
        assert "avg_power" in formatted_request
        assert "use_time_ratio" in formatted_request
        assert "usage_location" in formatted_request


class ComputeAvgConsumptionTest(TestCase):
    def test_compute_average_consumption(self):

        power_data = format_scaphandre_json("./tests/mocks/power_data.json")
        data = json.loads(power_data)
        avg_host = compute_average_consumption(data)

        assert type(avg_host) is float


loader = TestLoader()
suite = TestSuite()

suite.addTests(loader.loadTestsFromTestCase(ReadHardwareDataTest))
suite.addTests(loader.loadTestsFromTestCase(FormatUsageRequestTest))
suite.addTests(loader.loadTestsFromTestCase(ComputeAvgConsumptionTest))
