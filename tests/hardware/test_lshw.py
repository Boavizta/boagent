from unittest import TestCase
from boagent.hardware.lshw import Lshw
from unittest.mock import Mock, patch
from json import load

from tests.mocks.mocks import mock_sudo_lshw_data, mock_lshw_data_disks, mock_nvme_data

with open(mock_sudo_lshw_data) as lshw_json:
    lshw_data = load(lshw_json)
with open(mock_nvme_data) as nvme_json:
    nvme_data = load(nvme_json)

mocked_is_tool = Mock()
mocked_is_tool.return_value = True
mocked_serialized_lshw_output = Mock()
mocked_serialized_lshw_output.return_value = lshw_data
mocked_serialized_nvme_output = Mock()
mocked_serialized_nvme_output.return_value = nvme_data


class LshwTest(TestCase):
    @patch("boagent.hardware.lshw.is_tool", mocked_is_tool)
    @patch(
        "boagent.hardware.lshw.serialized_lshw_output", mocked_serialized_lshw_output
    )
    @patch(
        "boagent.hardware.lshw.serialized_nvme_output", mocked_serialized_nvme_output
    )
    def setUp(self):
        self.lshw = Lshw()
        self.cpu_data = self.lshw.cpus
        self.storage_data = self.lshw.disks
        self.ram_data = self.lshw.memories

    def test_read_get_hw_linux_cpu(self):
        cpu_data = self.lshw.get_hw_linux("cpu")

        assert type(cpu_data) is list

    def test_read_get_hw_linux_storage(self):
        storage_data = self.lshw.get_hw_linux("storage")

        assert type(storage_data) is list

    def test_read_get_hw_linux_memory(self):
        memory_data = self.lshw.get_hw_linux("memory")

        assert type(memory_data) is list

    def test_read_cpus_vendor(self):

        for cpu in self.cpu_data:
            assert "manufacturer" in cpu
            assert type(cpu["manufacturer"]) is str
            assert cpu["manufacturer"] == "Advanced Micro Devices [AMD]"

    def test_read_cpus_name(self):

        for cpu in self.cpu_data:
            assert "name" in cpu
            assert type(cpu["name"]) is str
            assert cpu["name"] == "AMD Ryzen 5 5600H with Radeon Graphics"

    def test_read_cpus_core_units(self):

        for cpu in self.cpu_data:
            assert "core_units" in cpu
            assert type(cpu["core_units"]) is int
            assert cpu["core_units"] == 6

    def test_read_cpus_units(self):

        for cpu in self.cpu_data:
            assert "units" in cpu
            assert type(cpu["units"]) is int
            assert cpu["units"] == 1

    def test_read_check_disk_vendor_with_correct_model(self):

        model = "LENOVO 123456154"
        result = self.lshw.check_disk_vendor(model)

        assert result == "LENOVO"

    def test_read_check_disk_vendor_with_incorrect_model(self):

        model = "12345121 LENOVO"
        result = self.lshw.check_disk_vendor(model)

        assert result == "LENOVO"

    def test_read_check_disk_vendor_with_one_correct_string_in_model(self):

        model = "LENOVO"
        result = self.lshw.check_disk_vendor(model)

        assert result == "LENOVO"

    def test_read_check_disk_vendor_with_one_incorrect_string_in_model(self):

        model = "12345211"
        with self.assertRaises(Exception):
            self.lshw.check_disk_vendor(model)

    def test_read_check_disk_vendor_with_multiple_strings_in_model(self):

        model = "LENOVO 123456 MODEL"
        result = self.lshw.check_disk_vendor(model)

        assert result == "LENOVO"

    def test_read_disks_type(self):

        for disk in self.storage_data:
            assert "type" in disk
            assert type(disk["type"]) is str
            assert disk["type"] == "ssd"

    def test_read_disk_dev_name(self):

        for disk in self.storage_data:
            assert "logicalname" in disk
            assert type(disk["logicalname"]) is str
            assert disk["logicalname"] == "/dev/nvme0n1"

    @patch("boagent.hardware.lshw.Lshw.get_rotational_int")
    def test_check_disk_type_is_ssd(self, mocked_get_rotational):

        dev_logicalname = "/dev/ssdonsata"
        mocked_get_rotational.return_value = 0

        disk_type = self.lshw.get_disk_type(dev_logicalname)
        assert disk_type == "ssd"

    @patch("boagent.hardware.lshw.Lshw.get_rotational_int")
    def test_check_disk_type_is_hdd(self, mocked_get_rotational):

        dev_logicalname = "/dev/sdaex"
        mocked_get_rotational.return_value = 1

        disk_type = self.lshw.get_disk_type(dev_logicalname)
        assert disk_type == "hdd"

    def test_int_for_get_rotational_int_when_file_not_found(self):

        dev_erroneous_name = "/dev/thisnameleadstonorotational"
        rotational_int = self.lshw.get_rotational_int(dev_erroneous_name)

        self.assertEqual(rotational_int, 2)

    def test_read_disk_type_when_dev_path_not_found(self):

        dev_erroneous_name = "/dev/thisnamedoesntexist"
        disk_type = self.lshw.get_disk_type(dev_erroneous_name)
        assert disk_type == "unknown"

    @patch("boagent.hardware.lshw.is_tool")
    def test_check_lshw_is_installed_to_parse_hardware_data_and_raises_error_if_not(
        self, mocked_is_tool
    ):
        mocked_is_tool.return_value = False
        with self.assertRaises(Exception) as context:
            self.lshw.__init__()
        self.assertTrue("lshw does not seem to be installed" in str(context.exception))

    @patch("boagent.hardware.lshw.is_tool")
    def test_check_nvme_cli_is_installed_to_find_storage_and_raises_error_if_not(
        self, mocked_is_tool
    ):
        mocked_is_tool.return_value = False

        with open(mock_lshw_data_disks, "r") as file, self.assertRaises(
            Exception
        ) as nvme_cli_exception:
            data = load(file)
            self.lshw.find_storage(data)

        caught_exception = nvme_cli_exception.exception
        assert str(caught_exception) == "nvme-cli >= 1.0 does not seem to be installed"

    def test_read_disks_manufacturer(self):

        for disk in self.storage_data:
            assert "manufacturer" in disk
            assert type(disk["manufacturer"]) is str
            assert disk["manufacturer"] == "toshiba"

    def test_read_disks_capacity(self):

        for disk in self.storage_data:
            assert "capacity" in disk
            assert type(disk["capacity"]) is int
            assert disk["capacity"] == 238

    def test_read_disks_units(self):

        for disk in self.storage_data:
            assert "units" in disk
            assert type(disk["units"]) is int
            assert disk["units"] == 1

    def test_read_ram_manufacturer(self):

        for ram in self.ram_data:
            assert "manufacturer" in ram
            assert type(ram["manufacturer"]) is str
            assert ram["manufacturer"] == "Samsung"

    def test_read_ram_capacity(self):

        for ram in self.ram_data:
            assert "capacity" in ram
            assert type(ram["capacity"]) is int
            assert ram["capacity"] == 8

    def test_read_ram_units(self):

        for ram in self.ram_data:
            assert "units" in ram
            assert type(ram["units"]) is int
            assert ram["units"] == 1
