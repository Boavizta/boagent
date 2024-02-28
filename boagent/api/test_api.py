from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest import TestCase
from .api import app

client = TestClient(app)

NOW_ISO8601 = datetime.now().isoformat()
NOW_ISO8601_MINUS_ONE_MINUTE = datetime.fromisoformat(NOW_ISO8601) - timedelta(
    minutes=1
)


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

        # TO IMPLEMENT : mock hardware_data.json with known functional values for Boaviztapi
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

    def test_read_yearly_operational(self):
        response = client.get("/yearly_operational")
        assert response.status_code == 200

    def test_read_last_info(self):
        response = client.get("/last_info")
        assert response.status_code == 200

    def test_read_max_info(self):
        response = client.get("/max_info")
        assert response.status_code == 200


class BoaviztapiTest(TestCase):
    """ROUTES DEPENDENT ON DATABASE AND / OR BOAVIZTAPI QUERIES"""

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

        params = {"data": "power"}

        response = client.get("/csv", params=params)
        assert response.status_code == 200
