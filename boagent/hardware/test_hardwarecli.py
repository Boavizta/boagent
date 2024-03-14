from unittest import TestCase
from os.path import exists
from hardware_cli import main, get_cpus, get_ram, get_disks
from click.testing import CliRunner


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

    def test_write_hardware_json_file_from_hardware_cli_with_output_file_flag_on(self):

        runner = CliRunner()
        with runner.isolated_filesystem():
            result_file_path = "hardware_data.json"

            result = runner.invoke(main, ["--output-file", f"./{result_file_path}"])
            assert exists(f"./{result_file_path}") is True

        assert result.exit_code == 0

    def test_read_stdout_from_hardware_cli(self):

        runner = CliRunner()

        result = runner.invoke(main)

        assert result.exit_code == 0
        assert result.output.count("disk") >= 1
        assert result.output.count("ram") >= 1
        assert result.output.count("cpu") >= 1
