from pathlib import Path
from unittest.mock import patch

from soft_spot.implementations.scripts import execute_scripts, _prepare_connection


def test__prepare_connection(configuration):
    with patch(
        "soft_spot.implementations.scripts.get_connection", autospec=True
    ) as get_conn_mock:
        _prepare_connection("192.168.0.1", configuration)
        get_conn_mock.assert_called_once_with(
            "192.168.0.1", "ubuntu", str(Path("~/.ssh/key.pem").expanduser())
        )


@patch("soft_spot.implementations.scripts._prepare_connection", autospec=True)
def test_execute_scripts(_, configuration, commands):
    expected_results = [(c, f"{c}_result") for c in commands]

    def execute_substitute(connection, command):
        return f"{command}_result"

    with patch(
        "soft_spot.implementations.scripts.execute", side_effect=execute_substitute
    ):
        result = execute_scripts("192.168.0.1", configuration)

        assert expected_results == result
