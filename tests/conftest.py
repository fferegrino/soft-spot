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
def configuration():
    config = configparser.ConfigParser()
    config["INSTANCE"] = {
        # ami-1e749f67 - ubuntu/images/hvm-ssd/ubuntu-trusty-14.04-amd64-server-20170727
        "ami": "ami-1e749f67",
        "type": "t2.micro",
        "security_group": "a_sec_group",
        "key_pair": "key_pair",
        "spot_price": 0.0035,
    }
    config["VOLUME"] = {"id": "vol-volume123", "device": "/dev/sdf"}
    config["ACCOUNT"] = {"user": "ubuntu"}
    return config


@pytest.fixture
def config_file(tmpdir, configuration):
    _, file_name = mkstemp(suffix=".spot", dir=tmpdir)

    with open(file_name, "w") as configfile:
        configuration.write(configfile)
    return file_name
