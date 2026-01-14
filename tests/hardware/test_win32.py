import os
import sys
from unittest import TestCase
from unittest.mock import Mock, patch

if os.name == "posix":
    sys.modules["win32com"] = Mock()
    sys.modules["win32com.client"] = Mock()

from boagent.hardware.win32 import Hardware

mock_win32_processor_name = "AMD Ryzen 5 5600H with Radeon Graphics"
mock_win32_processor_manufacturer = "Advanced Micro Devices [AMD]"
mock_win32_processor_core_units = 6


class HardwareTest(TestCase):
    def setUp(self) -> None:
        self.hardware = Hardware()
        self.cpu_data = self.hardware.cpus

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    def test_find_cpu_name(self, mocked_get_property, mocked_win32_instances):
        mocked_win32_instances.return_value = [1]
        mocked_get_property.return_value = mock_win32_processor_name
        cpus = self.hardware.find_cpus()
        cpu_name = cpus["cpus"][0]["name"]
        assert cpu_name == "AMD Ryzen 5 5600H with Radeon Graphics"

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    def test_find_cpu_manufacturer(self, mocked_get_property, mocked_win32_instances):
        mocked_win32_instances.return_value = [1]
        mocked_get_property.return_value = mock_win32_processor_manufacturer
        cpus = self.hardware.find_cpus()
        cpu_manufacturer = cpus["cpus"][0]["manufacturer"]
        assert cpu_manufacturer == "Advanced Micro Devices [AMD]"

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    def test_find_cpu_core_units(self, mocked_get_property, mocked_win32_instances):
        mocked_win32_instances.return_value = [1]
        mocked_get_property.return_value = mock_win32_processor_core_units
        cpus = self.hardware.find_cpus()
        cpu_core_units = cpus["cpus"][0]["core_units"]
        assert cpu_core_units == 6
