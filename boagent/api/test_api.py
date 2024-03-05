from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest import TestCase
import config
from config import Settings

# Mocks for testing environment
config.settings = Settings(
    hardware_file_path="./mocks/hardware_data.json",
    db_path="./mocks/boagent.db",
    power_file_path="./mocks/power_data.json",
)

from .api import app  # noqa

NOW_ISO8601 = datetime.now().isoformat()
NOW_ISO8601_MINUS_ONE_MINUTE = datetime.fromisoformat(NOW_ISO8601) - timedelta(
    minutes=1
)

client = TestClient(app)


class ApiTest(TestCase):

    def test_read_info(self):
        response = client.get("/info")
        assert response.status_code == 200

    def test_read_web(self):
        response = client.get("/web")
        assert response.status_code == 200

    def test_read_metrics(self):

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

    def test_read_query_without_measure_power_and_fetch_hardware(self):

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

    def test_read_query_with_measure_power(self):

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

    def test_read_query_with_fetch_hardware(self):

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

    def test_read_query_with_measure_power_and_fetch_hardware(self):

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

    def test_read_query_with_measure_power_and_fetch_hardware_verbose(self):

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


class DatabaseTest(TestCase):
    """ROUTES DEPENDENT ON DATABASE"""

    def test_read_last_info(self):
        response = client.get("/last_info")
        assert response.status_code == 200

    def test_read_max_info(self):
        response = client.get("/max_info")
        assert response.status_code == 200

    def test_read_yearly_operational(self):
        response = client.get("/yearly_operational")
        assert response.status_code == 200

    def test_read_last_data(self):
        response = client.get("/last_data")
        assert response.status_code == 200

    def test_read_update(self):
        response = client.get("/update")
        assert response.status_code == 200

    def test_read_carbon_intensity_forecast(self):
        params = {"since": "now", "until": "24h"}
        response = client.get("/carbon_intensity_forecast", params=params)
        assert response.status_code == 200

    def test_read_carbon_intensity(self):
        params = {"since": "now", "until": "24h"}
        response = client.get("/carbon_intensity", params=params)
        assert response.status_code == 200

    def test_impact(self):
        response = client.get("/impact")
        assert response.status_code == 200

    def test_read_csv(self):
        """ROUTE NOT IMPLEMENTED YET"""
        params = {"data": "power"}

        response = client.get("/csv", params=params)
        assert response.status_code == 200
