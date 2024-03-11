from unittest import TestCase

import hardware.lshw as lshw

hw = lshw.Lshw()

lshw_cpus_data = hw.cpus
lshw_disks_data = hw.disks


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

    def test_read_cpu_vendor(self):

        for cpu in lshw_cpus_data:
            assert "vendor" in cpu
            assert type(cpu["vendor"]) is str

    def test_read_cpu_name(self):

        for cpu in lshw_cpus_data:
            assert "name" in cpu
            assert type(cpu["name"]) is str

    def test_read_cpu_core_units(self):

        for cpu in lshw_cpus_data:
            assert "core_units" in cpu
            assert type(cpu["core_units"]) is str

    def test_read_cpu_units(self):

        for cpu in lshw_cpus_data:
            assert "units" in cpu
            assert type(cpu["units"]) is int

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

    def test_read_disks_manufacturer(self):

        for disk in lshw_disks_data:
            assert "manufacturer" in disk
            assert type(disk["manufacturer"]) is str

    def test_read_disks_capacity(self):

        for disk in lshw_disks_data:
            assert "capacity" in disk
            assert type(disk["capacity"]) is int


class HardwarecliTest(TestCase):

    def test_read_hardware_cli_cpus(self):
        pass
