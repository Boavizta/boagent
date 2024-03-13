from unittest import TestCase
from hardware_cli import get_cpus, get_ram, get_disks


class HardwarecliTest(TestCase):

    def test_read_hardware_cli_cpus(self):

        cpus = get_cpus()
        assert type(cpus) is list

    def test_read_hardware_cli_ram(self):

        ram = get_ram()
        assert type(ram) is list

    def test_read_hardware_cli_disks(self):

        disks = get_disks()
        assert type(disks) is list
