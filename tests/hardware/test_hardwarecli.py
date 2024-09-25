from json import load
from unittest import TestCase
from os import path
from os.path import exists
from unittest.mock import Mock, patch
from hardware_cli import main
from click.testing import CliRunner

current_dir = path.dirname(__file__)
mock_lshw_data = path.join(f"{current_dir}", "../mocks/sudo_lshw_data")
with open(f"{mock_lshw_data}.json") as lshw_json:
    data = load(lshw_json)


class MockLshw:
    def __init__(self):
        self.cpus = {
            "cpus": [
                {
                    "units": 1,
                    "name": "AMD Ryzen 5 5600H with Radeon Graphics",
                    "manufacturer": "Advanced Micro Devices [AMD]",
                    "core_units": 6,
                }
            ]
        }
        self.memories = {
            "rams": [
                {"units": 1, "manufacturer": "Samsung", "capacity": 8},
                {"units": 1, "manufacturer": "Kingston", "capacity": 16},
            ]
        }
        self.disks = {
            "disks": [
                {
                    "units": 1,
                    "logicalname": "/dev/nvme0n1",
                    "manufacturer": "samsung",
                    "type": "ssd",
                    "capacity": 476,
                }
            ],
        }


mocked_lshw = Mock()
mocked_lshw.return_value = MockLshw()


class HardwarecliTest(TestCase):
    @patch("hardware_cli.Lshw", mocked_lshw)
    def test_write_hardware_json_file_from_hardware_cli_with_output_file_flag_on(self):

        runner = CliRunner()
        with runner.isolated_filesystem():
            result_file_path = "hardware_data.json"

            result = runner.invoke(main, ["--output-file", f"./{result_file_path}"])
            assert exists(f"./{result_file_path}") is True

        assert result.exit_code == 0

    @patch("hardware_cli.Lshw", mocked_lshw)
    def test_read_stdout_from_hardware_cli(self):

        runner = CliRunner()

        result = runner.invoke(main)

        assert result.exit_code == 0
        assert result.output.count("disk") >= 1
        assert result.output.count("ram") >= 1
        assert result.output.count("cpu") >= 1

    def test_hardware_cli_returns_error_is_not_executed_with_sudo(self):
        runner = CliRunner()
        result = runner.invoke(main)
        assert (
            result.output.__contains__(
                "Hardware_cli was not executed with privileges, try `sudo ./hardware_cli.py`"
            )
        ) is True
