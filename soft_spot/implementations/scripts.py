import ast
from pathlib import Path

from soft_spot.fab import execute, get_connection


def _prepare_connection(ip_address, instance_configuration):
    account = instance_configuration["ACCOUNT"]
    user = account.get("user")
    key_location = str(Path(account.get("key_location")).expanduser())
    return get_connection(ip_address, user, key_location)


def execute_scripts(ip_address, instance_configuration):
    scripts = instance_configuration["SCRIPT"]
    commands = ast.literal_eval(scripts.get("commands"))
    conn = _prepare_connection(ip_address, instance_configuration)

    command_results = []
    for command in commands:
        command_results.append((command, execute(conn, command)))

    return command_results
