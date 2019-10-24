import backoff
from fabric.connection import Connection
from paramiko.ssh_exception import NoValidConnectionsError


@backoff.on_exception(backoff.expo, NoValidConnectionsError, max_time=90)
def get_connection(host, user, private_key_path):
    conn = Connection(
        host=host, user=user, connect_kwargs={"key_filename": private_key_path}
    )
    conn.sudo("whoami", hide=True)

    return conn


def has_fs(conn, device):
    result = conn.sudo(f"file -s {device}", hide=True)
    not_relevant_data = len(device) + 1
    return result.stdout[not_relevant_data:].strip() != "data"


def mount_drive(conn, location, device):
    conn.sudo(f"mkdir {location}", hide=True)
    if not has_fs(conn, device):
        conn.sudo(f"mkfs -t xfs {device}", hide=True)
    conn.sudo(f"mount {device} {location}", hide=True)
    conn.sudo(f"chown {conn.user} {location}", hide=True)


def execute(conn, command):
    cmd_result = conn.run(command, hide=True)
    return cmd_result.stdout.strip()
