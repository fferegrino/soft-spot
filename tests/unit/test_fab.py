import pytest
from fabric import Connection
from mock import patch, MagicMock, call

from soft_spot.fab import get_connection, has_fs, mount_drive


@pytest.fixture
def connection():
    conn = MagicMock(spec=Connection)
    conn.user = "ubuntu"
    return conn


def test_get_connection():
    host = "192.168.0.1"
    user = "ubuntu"
    key = "/home/key.pem"
    with patch("soft_spot.fab.Connection", spec=Connection) as conn_mock:
        val = get_connection(host, user, key)
        conn_mock.assert_called_with(
            host=host, user=user, connect_kwargs={"key_filename": key}
        )
        val.sudo.assert_called_once_with("whoami", hide=True)


@pytest.mark.parametrize(
    ["device", "response", "result"],
    [
        ("/dev/xvdf", "/dev/xvdf: data", False),
        (
            "/dev/xvda1",
            "/dev/xvda1: SGI XFS filesystem data (blksz 4096, inosz 512, v2 dirs)",
            True,
        ),
    ],
)
def test_has_fs(device, response, result, connection):
    connection.sudo.return_value.stdout = response
    actual = has_fs(connection, device)
    connection.sudo.assert_called_with(f"file -s {device}", hide=True)
    assert actual == result


@pytest.mark.parametrize(["has_file_system"], [(True,), (False,)])
def test_mount_drive(connection, has_file_system):
    location = "/data"
    device = "/dev/xvdf"
    has_file_system = True
    with patch("soft_spot.fab.has_fs", return_value=has_file_system):
        mount_drive(connection, location, device)

    commands = [
        f"mkdir {location}",
        f"mount {device} {location}",
        f"chown ubuntu {location}",
    ]
    if not has_file_system:
        commands.insert(1, f"mkfs -t xfs {device}")

    calls = [call(command, hide=True) for command in commands]
    connection.sudo.assert_has_calls(calls, any_order=False)
