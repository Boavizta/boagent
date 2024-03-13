from unittest import TestCase
from hardware.lshw.lshw import Lshw, get_disk_type, get_rotational_int
from unittest.mock import patch


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

        for cpu in lshw_cpus_data[1:]:
            assert "vendor" in cpu
            assert type(cpu["vendor"]) is str

    def test_read_cpus_name(self):

        for cpu in lshw_cpus_data[1:]:
            assert "name" in cpu
            assert type(cpu["name"]) is str

    def test_read_cpus_core_units(self):

        for cpu in lshw_cpus_data[1:]:
            assert "core_units" in cpu
            assert type(cpu["core_units"]) is str

    def test_read_cpus_units(self):

        assert "units" in lshw_cpus_data[0]
        assert type(lshw_cpus_data[0]["units"]) is int

    def test_read_disks_type(self):

        for disk in lshw_disks_data[1:]:
            assert "type" in disk
            assert type(disk["type"]) is str
            assert (
                disk["type"] == "ssd"
                or disk["type"] == "hdd"
                or disk["type"] == "usb"
                or disk["type"] == "unknown"
            )

    def test_read_disk_dev_name(self):

        for disk in lshw_disks_data[1:]:
            assert "logicalname" in disk
            assert type(disk["logicalname"]) is str

    @patch("hardware.lshw.lshw.get_rotational_int")
    def test_check_disk_type_is_ssd(self, mocked_get_rotational):

        dev_logicalname = "/dev/nvmeex"
        mocked_get_rotational.return_value = 0

        disk_type = get_disk_type(dev_logicalname)
        assert disk_type == "ssd"

    @patch("hardware.lshw.lshw.get_rotational_int")
    def test_check_disk_type_is_hdd(self, mocked_get_rotational):

        dev_logicalname = "/dev/sdaex"
        mocked_get_rotational.return_value = 1

        disk_type = get_disk_type(dev_logicalname)
        assert disk_type == "hdd"

    def test_int_for_get_rotational_int_when_file_not_found(self):

        dev_erroneous_name = "/dev/thisnameleadstonorotational"
        rotational_int = get_rotational_int(dev_erroneous_name)

        self.assertEqual(rotational_int, 2)

    def test_read_disk_type_when_dev_path_not_found(self):

        dev_erroneous_name = "/dev/thisnamedoesntexist"
        disk_type = get_disk_type(dev_erroneous_name)
        assert disk_type == "unknown"

    def test_read_disks_manufacturer(self):

        for disk in lshw_disks_data[1:]:
            assert "manufacturer" in disk
            assert type(disk["manufacturer"]) is str

    def test_read_disks_capacity(self):

        for disk in lshw_disks_data[1:]:
            assert "capacity" in disk
            assert type(disk["capacity"]) is int

    def test_read_disks_units(self):

        assert "units" in lshw_disks_data[0]
        assert type(lshw_disks_data[0]["units"]) is int

    def test_read_ram_manufacturer(self):

        for ram in lshw_ram_data[1:]:
            assert "manufacturer" in ram
            assert type(ram["manufacturer"]) is str

    def test_read_ram_capacity(self):

        print(lshw_ram_data)

        for ram in lshw_ram_data[1:]:
            assert "capacity" in ram
            assert type(ram["capacity"]) is int

    def test_read_ram_units(self):

        assert "units" in lshw_ram_data[0]
        assert type(lshw_ram_data[0]["units"]) is int