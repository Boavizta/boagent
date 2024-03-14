from unittest import TestCase
from .api import build_hardware_data, read_hardware_data
import os


class ApiUnitTest(TestCase):

    def test_read_build_hardware_data(self):

        build_hardware_data()
        assert os.path.exists("./hardware_data.json") is True

    def test_read_read_hardware_data(self):

        data = read_hardware_data()
        assert type(data) is dict
        assert type(data["cpu"]) is list
        assert type(data["ram"]) is list
        assert type(data["disk"]) is list
