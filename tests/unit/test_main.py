from tempfile import NamedTemporaryFile, mkstemp
from unittest.mock import MagicMock, patch
import configparser

import pytest
from click.testing import CliRunner

from soft_spot.__main__ import cli


@pytest.fixture
def invoke():
    def inner(subcommand, *args):
        runner = CliRunner()
        arguments = [subcommand] + list(args)
        return runner.invoke(cli, arguments)

    return inner


@pytest.fixture
def config_file(tmpdir):
    _, file_name = mkstemp(suffix=".spot", dir=tmpdir)
    config = configparser.ConfigParser()
    config["INSTANCE"] = {
        "ami": "ami-0be057a22c63962cb",
        "type": "t2.micro",
        "security_group": "a_sec_group",
        "key_pair": "key_pair",
        "spot_price": 0.0035,
    }
    with open(file_name, "w") as configfile:
        config.write(configfile)
    return file_name


@patch("soft_spot.__main__.configparser.ConfigParser", autospec=True)
@patch("soft_spot.__main__.request_instance", autospec=True)
def test_request(request_instance_mock, config_parser, invoke, config_file):
    result = invoke("request", config_file)
    assert result.exit_code == 0
    config_parser.return_value.read.assert_called_once_with(config_file)
    request_instance_mock.assert_called_once_with({}, config_parser.return_value)
