from dataclasses import asdict
import json

from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest import TestCase
from unittest.mock import patch
from pytest import mark
from boagent.api.config import Settings
from boagent.api.data import impact_criteria
from boagent.api.exceptions import invalid_criteria_choice_error_msg
from tests.mocks.mocks import (
    mock_boaviztapi_response_not_verbose,
    mock_boavizta_response_not_verbose_all_criteria,
    mock_boaviztapi_response_verbose_all_criteria,
    mock_get_metrics_verbose,
    mock_get_metrics_not_verbose,
    mock_get_metrics_not_verbose_all_criteria,
    mock_hardware_data,
    mock_formatted_scaphandre,
)

# Mock settings for testing environment
settings = Settings(
    hardware_file_path="./tests/mocks/hardware_data.json",
    db_path="./tests/mocks/boagent.db",
    power_file_path="./tests/mocks/power_data.json",
)

from boagent.api.api import app  # noqa

NOW_ISO8601 = datetime.now().isoformat()
NOW_ISO8601_MINUS_ONE_MINUTE = datetime.fromisoformat(NOW_ISO8601) - timedelta(
    minutes=1
)

client = TestClient(app)


class ApiEndpointsTest(TestCase):
    def setUp(self):
        with open(
            mock_boaviztapi_response_not_verbose, "r"
        ) as boaviztapi_response_file:
            self.boaviztapi_response_not_verbose = json.load(boaviztapi_response_file)
        with open(
            mock_boavizta_response_not_verbose_all_criteria, "r"
        ) as boaviztapi_response_file:
            self.boaviztapi_response_not_verbose_all_criteria = json.load(
                boaviztapi_response_file
            )
        with open(
            mock_boaviztapi_response_verbose_all_criteria, "r"
        ) as boaviztapi_response_file:
            self.boaviztapi_response_verbose_all_criteria = json.load(
                boaviztapi_response_file
            )
        with open(mock_get_metrics_not_verbose, "r") as get_metrics_not_verbose_file:
            self.get_metrics_not_verbose = json.load(get_metrics_not_verbose_file)
        with open(
            mock_get_metrics_not_verbose_all_criteria, "r"
        ) as get_metrics_not_verbose_all_criteria_file:
            self.get_metrics_not_verbose_all_criteria = json.load(
                get_metrics_not_verbose_all_criteria_file
            )
        with open(mock_get_metrics_verbose, "r") as get_metrics_verbose_file:
            self.get_metrics_verbose = json.load(get_metrics_verbose_file)
        with open(mock_hardware_data, "r") as hardware_data_file:
            self.hardware_data = json.load(hardware_data_file)
        with open(mock_formatted_scaphandre, "r") as file:
            power_data = {}
            power_data["raw_data"] = file.read()
            power_data["avg_power"] = 11.86
            self.power_data = power_data

    def test_read_info(self):
        response = client.get("/info")
        assert response.status_code == 200

    def test_read_web(self):
        response = client.get("/web")
        assert response.status_code == 200

    @patch("boagent.api.api.get_metrics")
    def test_read_metrics_with_success(self, mocked_get_metrics):

        mocked_get_metrics.return_value = self.get_metrics_not_verbose

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "false",
            "lifetime": 5,
            "fetch_hardware": "false",
        }

        response = client.get("/metrics", params=params)
        assert response.status_code == 200

    @patch("boagent.api.api.get_metrics")
    def test_read_metrics_with_verbose_with_success(self, mocked_get_metrics):

        mocked_get_metrics.return_value = self.get_metrics_verbose

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "false",
            "lifetime": 5,
            "fetch_hardware": "false",
        }

        response = client.get("/metrics", params=params)
        assert response.status_code == 200

    @patch("boagent.api.api.query_machine_impact_data")
    @patch("boagent.api.api.read_hardware_data")
    def test_read_metrics_without_measure_power_fetch_hardware_and_all_criteria_with_success(
        self, mocked_hardware_data, mocked_boaviztapi_response
    ):
        mocked_boaviztapi_response.return_value = (
            self.boaviztapi_response_not_verbose_all_criteria
        )
        mocked_hardware_data.return_value = self.hardware_data

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "false",
            "lifetime": 5,
            "fetch_hardware": "false",
            "criteria": "all",
        }

        response = client.get("/metrics", params=params)
        response_prometheus_output = response.text

        for value in asdict(impact_criteria).values():
            embedded_value = f"boagent_{value['boagent_embedded_key']}"
            assert embedded_value in response_prometheus_output

        assert response.status_code == 200

    @patch("boagent.api.api.query_machine_impact_data")
    @patch("boagent.api.api.read_hardware_data")
    @patch("boagent.api.api.get_power_data")
    def test_read_metrics_with_measure_power_and_all_criteria_with_success(
        self, mocked_power_data, mocked_hardware_data, mocked_boaviztapi_response
    ):

        mocked_boaviztapi_response.return_value = (
            self.boaviztapi_response_not_verbose_all_criteria
        )
        mocked_hardware_data.return_value = self.hardware_data
        mocked_power_data.return_value = self.power_data

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "false",
            "criteria": "all",
        }

        response = client.get("/metrics", params=params)
        response_prometheus_output = response.text

        for value in asdict(impact_criteria).values():
            embedded_value = f"boagent_{value['boagent_embedded_key']}"
            assert embedded_value in response_prometheus_output
            use_value = f"boagent_{value['boagent_use_key']}"
            assert use_value in response_prometheus_output

        assert response.status_code == 200

    @patch("boagent.api.api.query_machine_impact_data")
    @patch("boagent.api.api.get_hardware_data")
    @patch("boagent.api.api.get_power_data")
    def test_read_metrics_with_measure_power_fetch_hardware_and_all_criteria_with_success(
        self, mocked_power_data, mocked_hardware_data, mocked_boaviztapi_response
    ):

        mocked_boaviztapi_response.return_value = (
            self.boaviztapi_response_not_verbose_all_criteria
        )
        mocked_hardware_data.return_value = self.hardware_data
        mocked_power_data.return_value = self.power_data

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "true",
            "criteria": "all",
        }

        response = client.get("/metrics", params=params)
        response_prometheus_output = response.text

        for value in asdict(impact_criteria).values():
            embedded_value = f"boagent_{value['boagent_embedded_key']}"
            assert embedded_value in response_prometheus_output
            use_value = f"boagent_{value['boagent_use_key']}"
            assert use_value in response_prometheus_output

        assert response.status_code == 200

    @patch("boagent.api.api.query_machine_impact_data")
    @patch("boagent.api.api.get_hardware_data")
    @patch("boagent.api.api.get_power_data")
    def test_read_metrics_with_measure_power_fetch_hardware_and_all_criteria_verbose_with_success(
        self, mocked_power_data, mocked_hardware_data, mocked_boaviztapi_response
    ):

        mocked_boaviztapi_response.return_value = (
            self.boaviztapi_response_verbose_all_criteria
        )
        mocked_hardware_data.return_value = self.hardware_data
        mocked_power_data.return_value = self.power_data

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "true",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "true",
            "criteria": "all",
        }

        response = client.get("/metrics", params=params)
        response_prometheus_output = response.text

        for value in asdict(impact_criteria).values():
            embedded_value = f"boagent_{value['boagent_embedded_key']}"
            assert embedded_value in response_prometheus_output
            use_value = f"boagent_{value['boagent_use_key']}"
            assert use_value in response_prometheus_output

        assert response.status_code == 200

    @mark.query
    @patch("boagent.api.api.get_metrics")
    def test_read_query_without_measure_power_and_fetch_hardware_with_success(
        self, mocked_get_metrics
    ):

        mocked_get_metrics.return_value = self.boaviztapi_response_not_verbose

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "false",
            "lifetime": 5,
            "fetch_hardware": "false",
        }

        response = client.get("/query", params=params)
        assert response.status_code == 200

    @mark.query
    @patch("boagent.api.api.query_machine_impact_data")
    @patch("boagent.api.api.read_hardware_data")
    def test_read_query_without_measure_power_and_fetch_hardware_with_all_criteria_with_success(
        self, mocked_hardware_data, mocked_boaviztapi_response
    ):

        mocked_boaviztapi_response.return_value = (
            self.boaviztapi_response_not_verbose_all_criteria
        )
        mocked_hardware_data.return_value = self.hardware_data

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "false",
            "lifetime": 5,
            "fetch_hardware": "false",
            "criteria": "all",
        }

        response = client.get("/query", params=params)
        assert response.status_code == 200

        response_data = response.json()

        for value in asdict(impact_criteria).values():
            assert value["boagent_embedded_key"] in response_data

    @mark.query
    @patch("boagent.api.api.get_metrics")
    def test_read_query_with_measure_power_with_success(self, mocked_get_metrics):

        mocked_get_metrics.return_value = self.get_metrics_not_verbose

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "false",
        }

        response = client.get("/query", params=params)
        assert response.status_code == 200

    @mark.query
    @patch("boagent.api.api.query_machine_impact_data")
    @patch("boagent.api.api.read_hardware_data")
    @patch("boagent.api.api.get_power_data")
    def test_read_query_with_measure_power_with_all_criteria_with_success(
        self, mocked_power_data, mocked_hardware_data, mocked_boaviztapi_response
    ):

        mocked_boaviztapi_response.return_value = (
            self.boaviztapi_response_not_verbose_all_criteria
        )
        mocked_hardware_data.return_value = self.hardware_data
        mocked_power_data.return_value = self.power_data

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "false",
            "criteria": "all",
        }

        response = client.get("/query", params=params)
        assert response.status_code == 200

        response_data = response.json()

        for value in asdict(impact_criteria).values():
            assert value["boagent_embedded_key"] in response_data
            assert value["boagent_use_key"] in response_data

    @mark.query
    @patch("boagent.api.api.get_metrics")
    def test_read_query_with_fetch_hardware_with_success(self, mocked_get_metrics):

        mocked_get_metrics.return_value = self.get_metrics_not_verbose

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "false",
            "lifetime": 5,
            "fetch_hardware": "true",
        }

        response = client.get("query", params=params)
        assert response.status_code == 200

    @mark.query
    @patch("boagent.api.api.query_machine_impact_data")
    @patch("boagent.api.api.get_hardware_data")
    @patch("boagent.api.api.get_power_data")
    def test_read_query_with_fetch_hardware_with_all_criteria_with_success(
        self, mocked_power_data, mocked_hardware_data, mocked_boaviztapi_response
    ):

        mocked_boaviztapi_response.return_value = (
            self.boaviztapi_response_not_verbose_all_criteria
        )
        mocked_hardware_data.return_value = self.hardware_data

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "false",
            "lifetime": 5,
            "fetch_hardware": "true",
            "criteria": "all",
        }

        response = client.get("/query", params=params)
        assert response.status_code == 200

        response_data = response.json()

        for value in asdict(impact_criteria).values():
            assert value["boagent_embedded_key"] in response_data

    @mark.query
    @patch("boagent.api.api.get_metrics")
    def test_read_query_with_measure_power_and_fetch_hardware(self, mocked_get_metrics):

        mocked_get_metrics.return_value = self.boaviztapi_response_not_verbose

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "true",
        }

        response = client.get("/query", params=params)
        assert response.status_code == 200

    @mark.query
    @patch("boagent.api.api.query_machine_impact_data")
    @patch("boagent.api.api.get_hardware_data")
    @patch("boagent.api.api.get_power_data")
    def test_read_query_with_measure_power_and_fetch_hardware_with_all_criteria_with_success(
        self, mocked_power_data, mocked_hardware_data, mocked_boaviztapi_response
    ):

        mocked_boaviztapi_response.return_value = (
            self.boaviztapi_response_not_verbose_all_criteria
        )
        mocked_hardware_data.return_value = self.hardware_data
        mocked_power_data.return_value = self.power_data

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "false",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "true",
            "criteria": "all",
        }

        response = client.get("/query", params=params)
        assert response.status_code == 200

        response_data = response.json()

        for value in asdict(impact_criteria).values():
            assert value["boagent_embedded_key"] in response_data
            assert value["boagent_use_key"] in response_data

    @mark.query
    @patch("boagent.api.api.get_metrics")
    def test_read_query_with_measure_power_and_fetch_hardware_verbose(
        self, mocked_get_metrics
    ):

        mocked_get_metrics.return_value = self.get_metrics_verbose

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "true",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "true",
        }

        response = client.get("/query", params=params)
        assert response.status_code == 200

    @mark.query
    @patch("boagent.api.api.query_machine_impact_data")
    @patch("boagent.api.api.get_hardware_data")
    @patch("boagent.api.api.get_power_data")
    def test_read_query_with_measure_power_and_fetch_hardware_verbose_with_all_criteria(
        self, mocked_power_data, mocked_hardware_data, mocked_boaviztapi_response
    ):

        mocked_boaviztapi_response.return_value = (
            self.boaviztapi_response_verbose_all_criteria
        )
        mocked_hardware_data.return_value = self.hardware_data
        mocked_power_data.return_value = self.power_data

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "true",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "true",
            "criteria": "all",
        }

        response = client.get("/query", params=params)
        assert response.status_code == 200

    @patch("boagent.api.api.get_metrics")
    def test_get_process_embedded_impacts_with_success(self, mocked_get_metrics):
        mocked_get_metrics.return_value = self.get_metrics_verbose
        params = {
            "process_id": 3099,
            "start_time": "1717500637.2979465",
            "end_time": "1717504237.2979465",
            "verbose": "true",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "true",
        }
        response = client.get("/process_embedded_impacts", params=params)
        assert response.status_code == 200
        self.assertIn("pid", response.json())
        self.assertEqual(response.json()["pid"], 3099)
        self.assertIn("process_embedded_impacts", response.json())
        self.assertIn(
            "process_cpu_embedded_impact_values",
            response.json()["process_embedded_impacts"],
        )
        self.assertIn(
            "process_ram_embedded_impact_values",
            response.json()["process_embedded_impacts"],
        )
        self.assertIn(
            "process_ssd_embedded_impact_values",
            response.json()["process_embedded_impacts"],
        )
        self.assertIn(
            "process_hdd_embedded_impact_values",
            response.json()["process_embedded_impacts"],
        )

    @patch("boagent.api.api.get_metrics")
    def test_get_process_embedded_impacts_with_error_if_pid_not_found_in_metrics_data(
        self, mocked_get_metrics
    ):

        mocked_get_metrics.return_value = self.get_metrics_verbose
        params = {
            "process_id": 1234,
            "start_time": "1717500637.2979465",
            "end_time": "1717504237.2979465",
            "verbose": "true",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "true",
        }

        response = client.get("/process_embedded_impacts", params=params)
        error_message = (
            "Process_id 1234 has not been found in metrics data. Check the queried PID."
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(error_message in response.text)

    def test_get_process_embedded_impacts_with_error_if_invalid_criteria_choice_is_sent_by_the_client(
        self,
    ):

        params = {
            "start_time": f"{NOW_ISO8601_MINUS_ONE_MINUTE}",
            "end_time": f"{NOW_ISO8601}",
            "verbose": "true",
            "location": "FRA",
            "measure_power": "true",
            "lifetime": 5,
            "fetch_hardware": "true",
            "criteria": "error",
        }

        response = client.get("/query", params=params)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(invalid_criteria_choice_error_msg in response.text)
