from unittest import TestCase

from api import build_hardware_data
import os


class ApiUnitTest(TestCase):

    def test_read_build_hardware_data(self):

        build_hardware_data()
        assert os.path.exists("./hardware_data.json") is True
