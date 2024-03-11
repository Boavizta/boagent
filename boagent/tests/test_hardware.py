from unittest import TestCase

# import hardware.cpu as cpu
import hardware.lshw as lshw
# import hardware.hardware_cli as hwcli

hw = lshw.Lshw()


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

    def test_read_cpus_properties(self):
        cpu_data = hw.cpus

        for cpu in cpu_data:
            assert "vendor" in cpu
            assert "name" in cpu
            assert "core_units" in cpu
            assert "units" in cpu
            assert cpu["vendor"] is not None
            assert cpu["name"] is not None
            assert cpu["core_units"] is not None
            assert cpu["units"] is not None

    def test_read_disks_properties(self):
        disks_data = hw.disks

        for disk in disks_data:
            assert "type" in disk
            assert "model" in disk
            assert "manufacturer" in disk
            assert "capacity" in disk
            assert disk["type"] == "ssd" or disk["type"] == "hdd" or disk["type"] == "unknown"


""" class CpuTest(TestCase):
    def test_read_get_cpus(self):
        cpu_data = cpu.get_cpus()

        assert type(cpu_data) is list
        assert "vendor" in cpu_data[0]
        assert "name" in cpu_data[0]
 """


class HardwarecliTest(TestCase):

    def test_read_hardware_cli_cpus(self):
        pass
