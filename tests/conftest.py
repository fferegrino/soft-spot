import configparser
from tempfile import mkstemp

from click.testing import CliRunner
import pytest

from soft_spot.__main__ import cli


@pytest.fixture
def aws_region():
    return "eu-west-1"


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
