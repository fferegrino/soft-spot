import configparser
from datetime import datetime, timedelta

import boto3
import click
from tabulate import tabulate

from soft_spot.configuration import get_account_info
from soft_spot.implementations.price import get_prices
from soft_spot.implementations.request import request_instance


def get_client(account_info):
    return boto3.client("ec2", **account_info)


@click.group()
@click.option(
    "--account_info_file",
    "-a",
    default=None,
    type=click.Path(exists=True, dir_okay=False),
)
@click.pass_context
def cli(context, account_info_file):
    context.ensure_object(dict)
    context.obj["client"] = get_client(get_account_info(account_info_file))


@cli.command()
@click.pass_context
@click.argument("instance_file", type=click.Path(exists=True, dir_okay=False))
def request(context, instance_file):
    click.echo(f"Requesting from: {instance_file}")

    instance_configuration = configparser.ConfigParser()
    instance_configuration.read(instance_file)

    request_instance(context.obj["client"], instance_configuration)


@cli.command()
@click.pass_context
@click.argument("instance_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--start-time", type=click.DateTime(), default=None)
@click.option("--end-time", type=click.DateTime(), default=None)
def price(context, instance_file, start_time, end_time):
    click.echo(f"Requesting from: {instance_file}")

    instance_configuration = configparser.ConfigParser()
    instance_configuration.read(instance_file)

    if end_time is None:
        end_time = datetime.now()
    if start_time is None:
        start_time = end_time - timedelta(days=1)

    headers, prices = get_prices(
        context.obj["client"],
        instance_configuration,
        end_time=end_time,
        start_time=start_time,
    )
    click.echo(tabulate(prices, headers=headers))


if __name__ == "__main__":
    # pylint: disable=E1120
    cli()
