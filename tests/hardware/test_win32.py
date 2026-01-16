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
mock_win32_memory_manufacturer = "Samsung"
mock_win32_memory_capacity = 8589934592
mock_win32_disk_manufacturer = "samsung"
mock_win32_disk_size = 999653638144


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
        assert cpu_name == mock_win32_processor_name

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    def test_find_cpu_manufacturer(self, mocked_get_property, mocked_win32_instances):
        mocked_win32_instances.return_value = [1]
        mocked_get_property.return_value = mock_win32_processor_manufacturer
        cpus = self.hardware.find_cpus()
        cpu_manufacturer = cpus["cpus"][0]["manufacturer"]
        assert cpu_manufacturer == mock_win32_processor_manufacturer

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    def test_find_cpu_core_units(self, mocked_get_property, mocked_win32_instances):
        mocked_win32_instances.return_value = [1]
        mocked_get_property.return_value = mock_win32_processor_core_units
        cpus = self.hardware.find_cpus()
        cpu_core_units = cpus["cpus"][0]["core_units"]
        assert cpu_core_units == mock_win32_processor_core_units

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    def test_find_cpu_units(self, mocked_get_property, mocked_win32_instances):
        mocked_win32_instances.return_value = [1]
        mocked_get_property.return_value = mock_win32_processor_core_units
        cpus = self.hardware.find_cpus()
        cpu_units = cpus["cpus"][0]["units"]
        expected_units = 1
        assert cpu_units == expected_units

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    @patch("boagent.hardware.win32.convert_to_gigabytes")
    def test_find_memory_manufacturer(
        self, mocked_conversion, mocked_get_property, mocked_win32_instances
    ):
        mocked_win32_instances.return_value = [1]
        mocked_get_property.return_value = mock_win32_memory_manufacturer
        mocked_conversion.return_value = 8
        memories = self.hardware.find_memories()
        memory_manufacturer = memories["rams"][0]["manufacturer"]
        assert memory_manufacturer == mock_win32_memory_manufacturer

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    def test_find_memory_capacity(self, mocked_get_property, mocked_win32_instances):
        mocked_win32_instances.return_value = [1]
        mocked_get_property.return_value = mock_win32_memory_capacity
        memories = self.hardware.find_memories()
        memory_capacity = memories["rams"][0]["capacity"]
        expected_capacity_in_gigabytes = 8
        assert memory_capacity == expected_capacity_in_gigabytes

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    @patch("boagent.hardware.win32.convert_to_gigabytes")
    def test_find_memory_units(
        self, mocked_conversion, mocked_get_property, mocked_win32_instances
    ):
        mocked_win32_instances.return_value = [1, 2]
        mocked_get_property.return_value = 1
        mocked_conversion.return_value = 8
        memories = self.hardware.find_memories()
        memory_units = memories["rams"][0]["units"]
        expected_units = 2
        assert memory_units == expected_units

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    def test_find_storage_units(self, mocked_get_property, mocked_win32_instances):
        mocked_win32_instances.return_value = [1, 2]
        mocked_get_property.return_value = 1
        storage = self.hardware.find_storage()
        storage_units = storage["disks"][0]["units"]
        expected_units = 2
        assert storage_units == expected_units

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    def test_find_storage_manufacturer(
        self, mocked_get_property, mocked_win32_instances
    ):
        mocked_win32_instances.return_value = [1]
        mocked_get_property.return_value = mock_win32_disk_manufacturer
        storage = self.hardware.find_storage()
        storage_manufacturer = storage["disks"][0]["manufacturer"]
        assert storage_manufacturer == mock_win32_disk_manufacturer

    @patch("boagent.hardware.win32.get_win32_instances")
    @patch("boagent.hardware.win32.get_property")
    def test_find_storage_capacity(self, mocked_get_property, mocked_win32_instances):
        mocked_win32_instances.return_value = [1]
        mocked_get_property.return_value = mock_win32_disk_size
        storage = self.hardware.find_storage()
        storage_capacity = storage["disks"][0]["capacity"]
        expected_capacity = 931
        assert storage_capacity == expected_capacity
