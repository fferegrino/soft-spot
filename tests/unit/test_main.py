from datetime import datetime
from unittest.mock import ANY, MagicMock, patch

from freezegun import freeze_time
import pytest


@pytest.fixture
def invoke(invoke):
    with patch("soft_spot.__main__.get_client", autospec=True) as cli:
        yield invoke
        assert cli.called


@patch("soft_spot.__main__.configparser.ConfigParser", autospec=True)
@patch("soft_spot.__main__.request_instance", autospec=True)
def test_request(request_instance_mock, config_parser, invoke, config_file):
    result = invoke("request", config_file)
    assert result.exit_code == 0
    config_parser.return_value.read.assert_called_once_with(config_file)
    request_instance_mock.assert_called_once_with(ANY, config_parser.return_value)


@freeze_time("2012-01-14")
@pytest.mark.parametrize(
    ["start_time", "end_time", "start_time_expected", "end_time_expected"],
    [
        (None, None, datetime(2012, 1, 13), datetime(2012, 1, 14)),
        ("2019-01-01", "2019-10-11", datetime(2019, 1, 1), datetime(2019, 10, 11)),
    ],
)
@patch("soft_spot.__main__.configparser.ConfigParser", autospec=True)
@patch("soft_spot.__main__.get_prices", autospec=True)
@patch("soft_spot.__main__.tabulate", autospec=True)
def test_price(
    tabulate_mock,
    get_prices_mock,
    config_parser,
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
    config_parser.return_value.read.assert_called_once_with(config_file)
    get_prices_mock.assert_called_once_with(
        ANY, config_parser.return_value, start_time_expected, end_time_expected
    )
    tabulate_mock.assert_called_once_with(prices, headers=headers)
