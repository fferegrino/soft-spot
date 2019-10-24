from datetime import datetime
from unittest.mock import ANY, MagicMock, patch

from freezegun import freeze_time
import pytest


@pytest.fixture
def invoke(invoke, config_file):
    with patch("soft_spot.__main__.get_client", autospec=True) as cli, patch(
        "soft_spot.__main__.read_instance_configuration", autospec=True
    ) as config:
        yield invoke
        config.assert_called_once_with(config_file)
        cli.assert_called_once()


@pytest.mark.parametrize("attach_volumes", [True, False])
@pytest.mark.parametrize("execute_scripts", [True, False])
@patch("soft_spot.__main__.request_instance", autospec=True)
@patch("soft_spot.__main__.attach_device", autospec=True)
@patch("soft_spot.__main__.execute_scripts", autospec=True)
@patch("soft_spot.__main__.get_public_ip", return_value="192.168.0.1", autospec=True)
def test_request(
    get_public_ip_mock,
    execute_scripts_mock,
    attach_device_mock,
    request_instance_mock,
    invoke,
    config_file,
    attach_volumes,
    execute_scripts,
):
    parameters = [config_file]
    if not attach_volumes:
        parameters.append("--no-volumes")
    if not execute_scripts:
        parameters.append("--no-scripts")

    result = invoke("request", *parameters)

    assert result.exit_code == 0
    get_public_ip_mock.assert_called_once()
    request_instance_mock.assert_called_once()
    assert attach_volumes == attach_device_mock.called
    assert execute_scripts == execute_scripts_mock.called


@freeze_time("2012-01-14")
@pytest.mark.parametrize(
    ["start_time", "end_time", "start_time_expected", "end_time_expected"],
    [
        (None, None, datetime(2012, 1, 13), datetime(2012, 1, 14)),
        ("2019-01-01", "2019-10-11", datetime(2019, 1, 1), datetime(2019, 10, 11)),
    ],
)
@patch("soft_spot.__main__.get_prices", autospec=True)
@patch("soft_spot.__main__.tabulate", autospec=True)
def test_price(
    tabulate_mock,
    get_prices_mock,
    start_time,
    end_time,
    start_time_expected,
    end_time_expected,
    invoke,
    config_file,
):
    prices, headers = MagicMock(), MagicMock()
    get_prices_mock.return_value = (headers, prices)

    arguments = [config_file]
    if start_time:
        arguments.extend(["--start-time", start_time])
    if end_time:
        arguments.extend(["--end-time", end_time])

    result = invoke("price", *arguments)

    assert result.exit_code == 0
    get_prices_mock.assert_called_once_with(
        ANY, ANY, start_time_expected, end_time_expected
    )
    tabulate_mock.assert_called_once_with(prices, headers=headers)
