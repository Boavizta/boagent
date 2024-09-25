from json import load
from unittest import TestCase
from os import path
from os.path import exists
from unittest.mock import Mock, patch
from hardware_cli import main
from click.testing import CliRunner
from tests.mocks.mocks import MockLshw

current_dir = path.dirname(__file__)

# Need to use a mock of `lshw` run without `sudo` to reproduce the error case
# where hardware_cli is run without `sudo`.
mock_lshw_data = path.join(f"{current_dir}", "../mocks/lshw_data.json")
with open(mock_lshw_data) as lshw_json:
    lshw_data = load(lshw_json)

mocked_lshw = Mock()
mocked_lshw.return_value = MockLshw()
mocked_is_tool = Mock()
mocked_is_tool.return_value = True
mocked_serialized_lshw_output = Mock()
mocked_serialized_lshw_output.return_value = lshw_data


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

    @patch("boagent.hardware.lshw.is_tool", mocked_is_tool)
    @patch(
        "boagent.hardware.lshw.serialized_lshw_output", mocked_serialized_lshw_output
    )
    def test_hardware_cli_returns_error_if_not_executed_with_sudo(self):
        runner = CliRunner()
        result = runner.invoke(main)
        assert (
            result.output.__contains__(
                "Hardware_cli was not executed with privileges, try `sudo ./hardware_cli.py`"
            )
        ) is True
