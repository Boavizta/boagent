import os
import json

from unittest import TestCase, TestSuite, TestLoader
from unittest.mock import patch

from boagent.api.api import (
    build_hardware_data,
    read_hardware_data,
    get_hardware_data,
    # query_machine_impact_data,
    format_usage_request,
    compute_average_consumption,
    get_power_data,
    get_metrics,
)
from boagent.api.utils import format_prometheus_output

# from boagent.api.utils import format_scaphandre_json


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
mock_get_metrics_not_verbose = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_not_verbose.json"
)
mock_get_metrics_verbose = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_verbose.json"
)
hardware_cli = os.path.join(f"{current_dir}", "../../boagent/hardware/hardware_cli.py")
hardware_data = os.path.join(f"{current_dir}", "../../boagent/api/hardware_data.json")


@patch("boagent.api.api.HARDWARE_FILE_PATH", hardware_data)
class ReadHardwareDataTest(TestCase):
    def test_build_hardware_data(self):

        build_hardware_data()
        assert os.path.exists(hardware_data) is True

    def test_read_hardware_data(self):

        build_hardware_data()
        data = read_hardware_data()
        assert type(data["cpus"]) is list
        assert type(data["rams"]) is list
        assert type(data["disks"]) is list

    @patch("boagent.api.api.build_hardware_data")
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
        os.remove(hardware_data)


class FormatUsageRequestTest(TestCase):
    def setUp(self) -> None:
        self.start_time = 1710837858
        self.end_time = 1710841458

    def test_format_usage_request_with_start_and_end_times(self):

        formatted_request = format_usage_request(
            start_time=self.start_time,
            end_time=self.end_time,
        )

        assert type(formatted_request) is dict
        assert "hours_use_time" in formatted_request

    def test_format_usage_request_with_host_avg_consumption_and_location(
        self,
    ):

        location = "FRA"
        avg_power = 120

        formatted_request = format_usage_request(
            start_time=self.start_time,
            end_time=self.end_time,
            location=location,
            avg_power=avg_power,
        )
        assert type(formatted_request) is dict
        assert "avg_power" in formatted_request
        assert "usage_location" in formatted_request

    def test_format_usage_request_with_time_workload_as_percentage(self):

        time_workload = {"time_workload": 50.0}

        formatted_request = format_usage_request(
            start_time=self.start_time,
            end_time=self.end_time,
            time_workload=time_workload,
        )

        assert type(formatted_request) is dict
        assert "time_workload" in formatted_request


class ComputeAvgConsumptionTest(TestCase):
    def test_compute_average_consumption(self):

        with open(mock_power_data, "r") as power_data_file:
            power_data = f"[{power_data_file.read()}]"
        data = json.loads(power_data)
        avg_host = compute_average_consumption(data)

        assert type(avg_host) is float


class FormatPrometheusOutput(TestCase):

    def setUp(self):
        self.get_metrics_response_not_verbose_path = mock_get_metrics_not_verbose
        self.get_metrics_response_verbose_path = mock_get_metrics_verbose

    def test_format_prometheus_output_with_get_metrics_not_verbose(self):

        with open(mock_get_metrics_not_verbose, "r") as json_response:
            response_to_format = json.load(json_response)

        prometheus_output = format_prometheus_output(response_to_format)

        assert type(prometheus_output) is str
        assert len(prometheus_output) > 1
        assert "TYPE" in prometheus_output
        assert "HELP" in prometheus_output

    def test_format_prometheus_output_with_get_metrics_verbose(self):

        with open(mock_get_metrics_verbose, "r") as json_response:
            response_to_format = json.load(json_response)

        prometheus_output = format_prometheus_output(response_to_format)

        assert type(prometheus_output) is str
        assert len(prometheus_output) > 1
        assert "TYPE" in prometheus_output
        assert "HELP" in prometheus_output


class GetPowerDataTest(TestCase):
    def setUp(self) -> None:
        # One-hour interval
        self.start_time = 1713776733
        self.end_time = 1713780333
        # Ten minutes interval
        self.short_interval_start_time = 1713776733
        self.short_interval_end_time = 1713777333

        self.formatted_scaphandre = f"{mock_formatted_scaphandre}"

    @patch("boagent.api.api.format_scaphandre_json")
    def test_get_power_data(self, mocked_format_scaphandre_json):

        mocked_format_scaphandre_json.return_value = open(
            mock_formatted_scaphandre, "r"
        ).read()

        power_data = get_power_data(self.start_time, self.end_time)

        assert type(power_data) is dict
        assert "raw_data" in power_data
        assert "avg_power" in power_data
        assert type(power_data["avg_power"]) is float
        assert power_data["avg_power"] > 0

    @patch("boagent.api.api.format_scaphandre_json")
    def test_get_power_data_with_short_time_interval(
        self, mocked_format_scaphandre_json
    ):

        mocked_format_scaphandre_json.return_value = open(
            mock_formatted_scaphandre, "r"
        ).read()

        power_data = get_power_data(
            self.short_interval_start_time, self.short_interval_end_time
        )

        assert type(power_data) is dict
        assert "raw_data" in power_data
        assert "avg_power" in power_data
        assert "warning" in power_data


@patch("boagent.api.api.read_hardware_data")
@patch("boagent.api.api.query_machine_impact_data")
class GetMetricsNotVerboseNoScaphandreTest(TestCase):
    def setUp(self) -> None:
        self.time_workload_as_percentage = {"time_workload": 70.0}
        self.time_workload_as_list_of_dicts = {
            "time_workload": [
                {"time_percentage": 50, "load_percentage": 0},
                {"time_percentage": 25, "load_percentage": 60},
                {"time_percentage": 25, "load_percentage": 100},
            ]
        }
        self.start_time = 1710837858
        self.end_time = 1710841458
        self.verbose = False
        self.location = "FRA"
        self.measure_power = False
        self.lifetime = 5.0
        self.fetch_hardware = False

        with open(mock_boaviztapi_response_not_verbose, "r") as file:
            self.boaviztapi_data = json.load(file)

        with open(mock_hardware_data, "r") as file:
            self.hardware_data = json.load(file)

    def test_get_metrics_with_time_workload_as_percentage(
        self, mocked_read_hardware_data, mocked_query_machine_impact_data
    ):

        metrics = get_metrics(
            self.start_time,
            self.end_time,
            self.verbose,
            self.location,
            self.measure_power,
            self.lifetime,
            self.fetch_hardware,
            self.time_workload_as_percentage,
        )

        mocked_read_hardware_data.return_value = self.hardware_data
        mocked_query_machine_impact_data.return_value = self.boaviztapi_data

        assert type(metrics) is dict
        assert "emissions_calculation_data" in metrics
        assert "embedded_emissions" in metrics
        assert "embedded_abiotic_resources_depletion" in metrics
        assert "embedded_primary_energy" in metrics

    def test_get_metrics_with_time_workload_as_list_of_dicts(
        self, mocked_read_hardware_data, mocked_query_machine_impact_data
    ):

        metrics = get_metrics(
            self.start_time,
            self.end_time,
            self.verbose,
            self.location,
            self.measure_power,
            self.lifetime,
            self.fetch_hardware,
            self.time_workload_as_list_of_dicts,
        )

        mocked_read_hardware_data.return_value = self.hardware_data
        mocked_query_machine_impact_data.return_value = self.boaviztapi_data

        assert type(metrics) is dict
        assert "emissions_calculation_data" in metrics
        assert "embedded_emissions" in metrics
        assert "embedded_abiotic_resources_depletion" in metrics
        assert "embedded_primary_energy" in metrics

    def test_get_metrics_with_default_location(
        self, mocked_read_hardware_data, mocked_query_machine_impact_data
    ):

        metrics = get_metrics(
            self.start_time,
            self.end_time,
            self.verbose,
            "EEE",
            self.measure_power,
            self.lifetime,
            self.fetch_hardware,
            self.time_workload_as_list_of_dicts,
        )

        mocked_read_hardware_data.return_value = self.hardware_data
        mocked_query_machine_impact_data.return_value = self.boaviztapi_data

        assert type(metrics) is dict
        assert "location_warning" in metrics

    def test_get_metrics_with_no_set_location(
        self, mocked_read_hardware_data, mocked_query_machine_impact_data
    ):

        empty_location = ""

        metrics = get_metrics(
            self.start_time,
            self.end_time,
            self.verbose,
            empty_location,
            self.measure_power,
            self.lifetime,
            self.fetch_hardware,
            self.time_workload_as_list_of_dicts,
        )

        mocked_read_hardware_data.return_value = self.hardware_data
        mocked_query_machine_impact_data.return_value = self.boaviztapi_data

        print(len(empty_location))
        assert type(metrics) is dict
        assert "location_warning" in metrics


@patch("boagent.api.api.read_hardware_data")
@patch("boagent.api.api.query_machine_impact_data")
class GetMetricsVerboseNoScaphandreTest(TestCase):
    def setUp(self) -> None:
        self.time_workload_as_percentage = {"time_workload": 70.0}
        self.time_workload_as_list_of_dicts = {
            "time_workload": [
                {"time_percentage": 50, "load_percentage": 0},
                {"time_percentage": 25, "load_percentage": 60},
                {"time_percentage": 25, "load_percentage": 100},
            ]
        }

        self.start_time = 1710837858
        self.end_time = 1710841458
        self.verbose = True
        self.location = "FRA"
        self.measure_power = False
        self.lifetime = 5.0
        self.fetch_hardware = False

        with open(mock_boaviztapi_response_verbose, "r") as file:
            self.boaviztapi_data = json.load(file)

        with open(mock_hardware_data, "r") as file:
            self.hardware_data = json.load(file)

    def test_get_metrics_verbose_with_time_workload_percentage(
        self, mocked_read_hardware_data, mocked_query_machine_impact_data
    ):

        metrics = get_metrics(
            self.start_time,
            self.end_time,
            self.verbose,
            self.location,
            self.measure_power,
            self.lifetime,
            self.fetch_hardware,
            self.time_workload_as_percentage,
        )

        mocked_read_hardware_data.return_value = self.hardware_data
        mocked_query_machine_impact_data.return_value = self.boaviztapi_data

        assert type(metrics) is dict
        assert "emissions_calculation_data" in metrics
        assert "embedded_emissions" in metrics
        assert "embedded_abiotic_resources_depletion" in metrics
        assert "embedded_primary_energy" in metrics
        assert "raw_data" in metrics
        assert "electricity_carbon_intensity" in metrics

    def test_get_metrics_verbose_with_time_workload_as_list_of_dicts(
        self, mocked_read_hardware_data, mocked_query_machine_impact_data
    ):

        metrics = get_metrics(
            self.start_time,
            self.end_time,
            self.verbose,
            self.location,
            self.measure_power,
            self.lifetime,
            self.fetch_hardware,
            self.time_workload_as_list_of_dicts,
        )

        mocked_read_hardware_data.return_value = self.hardware_data
        mocked_query_machine_impact_data.return_value = self.boaviztapi_data

        assert type(metrics) is dict
        assert "emissions_calculation_data" in metrics
        assert "embedded_emissions" in metrics
        assert "embedded_abiotic_resources_depletion" in metrics
        assert "embedded_primary_energy" in metrics
        assert "raw_data" in metrics
        assert "electricity_carbon_intensity" in metrics


class GetMetricsVerboseWithScaphandreTest(TestCase):
    def setUp(self) -> None:
        self.start_time = 1710837858
        self.end_time = 1710841458
        self.verbose = True
        self.location = "FRA"
        self.measure_power = True
        self.lifetime = 5.0
        self.fetch_hardware = False

        with open(mock_boaviztapi_response_verbose, "r") as file:
            self.boaviztapi_data = json.load(file)

        with open(mock_formatted_scaphandre, "r") as file:
            power_data = {}
            power_data["raw_data"] = file.read()
            power_data["avg_power"] = 11.86
            self.power_data = power_data

        with open(mock_hardware_data, "r") as file:
            self.hardware_data = json.load(file)

    @patch("boagent.api.api.query_machine_impact_data")
    @patch("boagent.api.api.get_power_data")
    @patch("boagent.api.api.read_hardware_data")
    def test_get_metrics_verbose_with_scaphandre(
        self,
        mocked_read_hardware_data,
        mocked_query_machine_impact_data,
        mocked_power_data,
    ):

        metrics = get_metrics(
            self.start_time,
            self.end_time,
            self.verbose,
            self.location,
            self.measure_power,
            self.lifetime,
            self.fetch_hardware,
        )

        mocked_read_hardware_data.return_value = self.hardware_data
        mocked_query_machine_impact_data.return_value = self.boaviztapi_data
        mocked_power_data.return_value = self.power_data

        assert type(metrics) is dict
        assert "total_operational_emissions" in metrics
        assert "total_operational_abiotic_resources_depletion" in metrics
        assert "total_operational_primary_energy_consumed" in metrics
        assert "start_time" in metrics
        assert "end_time" in metrics
        assert "average_power_measured" in metrics
        assert "raw_data" in metrics
        assert "electricity_carbon_intensity" in metrics
        assert "power_data" in metrics["raw_data"]


loader = TestLoader()
suite = TestSuite()

suite.addTests(loader.loadTestsFromTestCase(ReadHardwareDataTest))
suite.addTests(loader.loadTestsFromTestCase(FormatUsageRequestTest))
suite.addTests(loader.loadTestsFromTestCase(ComputeAvgConsumptionTest))
suite.addTests(loader.loadTestsFromTestCase(GetPowerDataTest))
suite.addTests(loader.loadTestsFromTestCase(GetMetricsNotVerboseNoScaphandreTest))
suite.addTests(loader.loadTestsFromTestCase(GetMetricsVerboseNoScaphandreTest))
suite.addTests(loader.loadTestsFromTestCase(GetMetricsVerboseWithScaphandreTest))
