import json
import os

from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest import TestCase
from unittest.mock import patch
from pytest import mark
from boagent.api.config import Settings

# Mocks for testing environment
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

current_dir = os.path.dirname(__file__)
mock_boaviztapi_response_not_verbose = os.path.join(
    f"{current_dir}", "../mocks/boaviztapi_response_not_verbose.json"
)
mock_get_metrics_not_verbose = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_not_verbose.json"
)
mock_get_metrics_verbose = os.path.join(
    f"{current_dir}", "../mocks/get_metrics_verbose.json"
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

    def test_read_yearly_embedded(self):
        response = client.get("/yearly_embedded")
        assert response.status_code == 200

    def test_read_last_info(self):
        response = client.get("/last_info")
        assert response.status_code == 200

    def test_read_max_info(self):
        response = client.get("/max_info")
        assert response.status_code == 200

    def test_read_yearly_operational(self):
        """ROUTE NOT IMPLEMENTED YET"""
        response = client.get("/yearly_operational")
        assert response.status_code == 501

    @mark.database
    def test_read_last_data(self):
        """ROUTE NOT IMPLEMENTED YET"""

        params = {"table_name": "cpu"}
        response = client.get("/last_data", params=params)
        assert response.status_code == 501

    @mark.database
    def test_read_update(self):
        """ROUTE NOT IMPLEMENTED YET"""
        response = client.get("/update")
        assert response.status_code == 501

    @mark.database
    def test_read_carbon_intensity_forecast(self):
        """ROUTE NOT IMPLEMENTED YET"""
        params = {"since": "now", "until": "24h"}
        response = client.get("/carbon_intensity_forecast", params=params)
        assert response.status_code == 501

    @mark.database
    def test_read_carbon_intensity(self):
        """ROUTE NOT IMPLEMENTED YET"""
        params = {"since": "now", "until": "24h"}
        response = client.get("/carbon_intensity", params=params)
        assert response.status_code == 501

    @mark.database
    def test_impact(self):
        """ROUTE NOT IMPLEMENTED YET"""
        response = client.get("/impact")
        assert response.status_code == 501

    @mark.database
    def test_read_csv(self):
        """ROUTE NOT IMPLEMENTED YET"""
        params = {"data": "power"}

        response = client.get("/csv", params=params)
        assert response.status_code == 501
