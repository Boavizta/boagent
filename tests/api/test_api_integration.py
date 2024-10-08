import json

from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest import TestCase
from unittest.mock import patch
from pytest import mark
from boagent.api.config import Settings
from tests.mocks.mocks import (
    mock_boaviztapi_response_not_verbose,
    mock_get_metrics_verbose,
    mock_get_metrics_not_verbose,
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

        with open(mock_get_metrics_not_verbose, "r") as get_metrics_not_verbose_file:
            self.get_metrics_not_verbose = json.load(get_metrics_not_verbose_file)
        with open(mock_get_metrics_verbose, "r") as get_metrics_verbose_file:
            self.get_metrics_verbose = json.load(get_metrics_verbose_file)

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
        assert response.status_code == 400
        assert (
            response.text
            == "Process_id 1234 has not been found in metrics data. Check the queried PID"
        )
