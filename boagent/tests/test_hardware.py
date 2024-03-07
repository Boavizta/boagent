from unittest import TestCase
import hardware.cpu as cpu
import hardware.lshw as lshw

hw = lshw.LSHW()


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


class CpuTest(TestCase):
    def test_read_get_cpus(self):
        cpu_data = cpu.get_cpus()

        assert type(cpu_data) is list
        assert "vendor" in cpu_data[0]
        assert "name" in cpu_data[0]


class DiskTest(TestCase):
    pass


class RamTest(TestCase):
    pass
