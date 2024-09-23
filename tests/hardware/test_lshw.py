from unittest import TestCase
from boagent.hardware.lshw import Lshw
from unittest.mock import patch
from json import load
from os import path

current_dir = path.dirname(__file__)
mock_lshw_data = path.join(f"{current_dir}", "../mocks/sudo_lshw_data")

hw = Lshw()

lshw_cpus_data = hw.cpus
lshw_disks_data = hw.disks
lshw_ram_data = hw.memories


class LshwTest(TestCase):
    def test_read_get_hw_linux_cpu(self):
        cpu_data = hw.get_hw_linux("cpu")

        assert type(cpu_data) is list

    def test_read_get_hw_linux_storage(self):
        storage_data = hw.get_hw_linux("storage")

        assert type(storage_data) is list

    def test_read_get_hw_linux_memory(self):
        memory_data = hw.get_hw_linux("memory")

        assert type(memory_data) is list

    def test_read_cpus_vendor(self):

        for cpu in lshw_cpus_data:
            assert "manufacturer" in cpu
            assert type(cpu["manufacturer"]) is str

    def test_read_cpus_name(self):

        for cpu in lshw_cpus_data:
            assert "name" in cpu
            assert type(cpu["name"]) is str

    def test_read_cpus_core_units(self):

        for cpu in lshw_cpus_data:
            assert "core_units" in cpu
            assert type(cpu["core_units"]) is int

    def test_read_cpus_units(self):

        for cpu in lshw_cpus_data:
            assert "units" in cpu
            assert type(cpu["units"]) is int

    def test_read_check_disk_vendor_with_correct_model(self):

        model = "LENOVO 123456154"
        result = hw.check_disk_vendor(model)

        assert result == "LENOVO"

    def test_read_check_disk_vendor_with_incorrect_model(self):

        model = "12345121 LENOVO"
        result = hw.check_disk_vendor(model)

        assert result == "LENOVO"

    def test_read_check_disk_vendor_with_one_correct_string_in_model(self):

        model = "LENOVO"
        result = hw.check_disk_vendor(model)

        assert result == "LENOVO"

    def test_read_check_disk_vendor_with_one_incorrect_string_in_model(self):

        model = "12345211"
        with self.assertRaises(Exception):
            hw.check_disk_vendor(model)

    def test_read_check_disk_vendor_with_multiple_strings_in_model(self):

        model = "LENOVO 123456 MODEL"
        result = hw.check_disk_vendor(model)

        assert result == "LENOVO"

    def test_read_disks_type(self):

        for disk in lshw_disks_data:
            assert "type" in disk
            assert type(disk["type"]) is str
            assert (
                disk["type"] == "ssd"
                or disk["type"] == "hdd"
                or disk["type"] == "usb"
                or disk["type"] == "unknown"
            )

    def test_read_disk_dev_name(self):

        for disk in lshw_disks_data:
            assert "logicalname" in disk
            assert type(disk["logicalname"]) is str

    @patch("boagent.hardware.lshw.Lshw.get_rotational_int")
    def test_check_disk_type_is_ssd(self, mocked_get_rotational):

        dev_logicalname = "/dev/ssdonsata"
        mocked_get_rotational.return_value = 0

        disk_type = hw.get_disk_type(dev_logicalname)
        assert disk_type == "ssd"

    @patch("boagent.hardware.lshw.Lshw.get_rotational_int")
    def test_check_disk_type_is_hdd(self, mocked_get_rotational):

        dev_logicalname = "/dev/sdaex"
        mocked_get_rotational.return_value = 1

        disk_type = hw.get_disk_type(dev_logicalname)
        assert disk_type == "hdd"

    def test_int_for_get_rotational_int_when_file_not_found(self):

        dev_erroneous_name = "/dev/thisnameleadstonorotational"
        rotational_int = hw.get_rotational_int(dev_erroneous_name)

        self.assertEqual(rotational_int, 2)

    def test_read_disk_type_when_dev_path_not_found(self):

        dev_erroneous_name = "/dev/thisnamedoesntexist"
        disk_type = hw.get_disk_type(dev_erroneous_name)
        assert disk_type == "unknown"

    @patch("boagent.hardware.lshw.is_tool")
    def test_check_lshw_is_installed_to_parse_hardware_data_and_raises_error_if_not(
        self, mocked_is_tool
    ):
        another_lshw = Lshw()
        mocked_is_tool.return_value = False
        with self.assertRaises(Exception) as context:
            another_lshw.__init__()
        self.assertTrue("lshw does not seem to be installed" in str(context.exception))

    @patch("boagent.hardware.lshw.is_tool")
    def test_check_nvme_cli_is_installed_to_find_storage_and_raises_error_if_not(
        self, mocked_is_tool
    ):
        mocked_is_tool.return_value = False

        with open(f"{mock_lshw_data}_disks.json", "r") as file, self.assertRaises(
            Exception
        ) as nvme_cli_exception:
            data = load(file)
            hw.find_storage(data)

        caught_exception = nvme_cli_exception.exception
        assert str(caught_exception) == "nvme-cli >= 1.0 does not seem to be installed"

    def test_read_disks_manufacturer(self):

        for disk in lshw_disks_data:
            assert "manufacturer" in disk
            assert type(disk["manufacturer"]) is str

    def test_read_disks_capacity(self):

        for disk in lshw_disks_data:
            assert "capacity" in disk
            assert type(disk["capacity"]) is int

    def test_read_disks_units(self):

        for disk in lshw_disks_data:
            assert "units" in disk
            assert type(disk["units"]) is int

    def test_read_ram_manufacturer(self):

        for ram in lshw_ram_data:
            assert "manufacturer" in ram
            assert type(ram["manufacturer"]) is str

    def test_read_ram_capacity(self):

        for ram in lshw_ram_data[1:]:
            assert "capacity" in ram
            assert type(ram["capacity"]) is int

    def test_read_ram_units(self):

        assert "units" in lshw_ram_data[0]
        assert type(lshw_ram_data[0]["units"]) is int
