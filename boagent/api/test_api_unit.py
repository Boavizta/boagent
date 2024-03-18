from unittest import TestCase
from unittest.mock import patch

from api import build_hardware_data, read_hardware_data, get_hardware_data
import os


class ApiUnitTest(TestCase):

    def test_read_build_hardware_data(self):

        build_hardware_data()
        assert os.path.exists("./hardware_data.json") is True

    def test_read_read_hardware_data(self):

        build_hardware_data()
        data = read_hardware_data()
        assert type(data) is dict
        assert type(data) is dict
        assert type(data["cpu"]) is list
        assert type(data["ram"]) is list
        assert type(data["disk"]) is list

    @patch("api.build_hardware_data")
    def test_read_get_hardware_data_with_fetch_hardware_false(
        self, mocked_build_hardware
    ):

        # Test case where hardware_data.json is already present on the
        # filesystem through previous call to build_hardware_data

        build_hardware_data()
        data = get_hardware_data(fetch_hardware=False)
        assert type(data) is dict
        mocked_build_hardware.assert_not_called()

    def test_tead_get_hardware_data_with_fetch_hardware_true(self):

        data = get_hardware_data(fetch_hardware=True)
        assert type(data) is dict

    def tearDown(self) -> None:
        os.remove("./hardware_data.json")
