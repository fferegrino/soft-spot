import configparser
from datetime import datetime, timedelta
from time import sleep

import boto3
import click
from tabulate import tabulate

from soft_spot.configuration import (
    get_account_info,
    get_instance_configuration,
    get_price_request_configuration,
)

DELAY = 10


def get_client(account_info):
    return boto3.client("ec2", **account_info)


def get_instance_from(client, spot_request):
    instances = client.describe_instances(InstanceIds=[spot_request["InstanceId"]])
    return instances["Reservations"][0]["Instances"][0]


def wait_for_instance(client, spot_request_id):
    response = client.describe_spot_instance_requests(
        SpotInstanceRequestIds=[spot_request_id]
    )
    spot_request = response["SpotInstanceRequests"][0]
    while True:
        if spot_request["State"] == "active":
            instance = get_instance_from(client, spot_request)

            client.create_tags(
                Resources=[spot_request["InstanceId"]],
                Tags=[{"Key": "CreatedBy", "Value": "SoftSpot"}],
            )
            return instance

        response = client.describe_spot_instance_requests(
            SpotInstanceRequestIds=[spot_request_id]
        )
        spot_request = response["SpotInstanceRequests"][0]

        click.echo("Waiting...")
        sleep(DELAY)


def attach_device(client, instance_id, config):
    volume_id = config.get("VOLUME", "id")
    device = config.get("VOLUME", "device")
    click.echo(f"Will attach the volume {volume_id} to {instance_id} at {device}")
    attachment_result = client.attach_volume(
        VolumeId=volume_id, InstanceId=instance_id, Device=device
    )
    return attachment_result


def get_public_ip(instance):
    return instance["NetworkInterfaces"][0]["Association"]["PublicIp"]


def request_instance(account_info, config):
    client = get_client(account_info)

    instance_config = get_instance_configuration(config)
    request_response = client.request_spot_instances(**instance_config)
    current_request = request_response["SpotInstanceRequests"][0]
    request_id = current_request["SpotInstanceRequestId"]
    click.echo(f"Spot request {request_id} created, status: {current_request['State']}")
    instance = wait_for_instance(client, request_id)
    instance_id = instance["InstanceId"]
    public_ip = get_public_ip(instance)
    click.echo(f"Instance {instance_id} started, IP: {public_ip}")
    if config.has_section("VOLUME"):
        attach_device(client, instance_id, config)
    click.echo(
        click.style(f"Done! the IP of the image is {public_ip}", bg="blue", fg="white")
    )


def get_prices(account_info, instance_configuration, start_time, end_time):
    client = get_client(account_info)
    conf = get_price_request_configuration(instance_configuration)
    conf["EndTime"] = end_time
    conf["StartTime"] = start_time
    response = client.describe_spot_price_history(**conf)

    headers = [
        "Timestamp",
        "SpotPrice",
        "AvailabilityZone",
        "InstanceType",
        "ProductDescription",
    ]
    spot_price_history = [
        [p[key] for key in headers] for p in response["SpotPriceHistory"]
    ]

    spot_price_history = sorted(spot_price_history, key=lambda prc: prc[0])
    return headers, spot_price_history


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
    context.obj["account_info"] = get_account_info(account_info_file)


@cli.command()
@click.pass_context
@click.argument("instance_file", type=click.Path(exists=True, dir_okay=False))
def request(context, instance_file):
    account_info = context.obj["account_info"]
    click.echo(f"Requesting from: {instance_file}")

    instance_configuration = configparser.ConfigParser()
    instance_configuration.read(instance_file)

    request_instance(account_info, instance_configuration)


@cli.command()
@click.pass_context
@click.argument("instance_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--start-time", type=click.DateTime(), default=None)
@click.option("--end-time", type=click.DateTime(), default=None)
def price(context, instance_file, start_time, end_time):
    account_info = context.obj["account_info"]
    click.echo(f"Requesting from: {instance_file}")

    instance_configuration = configparser.ConfigParser()
    instance_configuration.read(instance_file)

    if end_time is None:
        end_time = datetime.now()
    if start_time is None:
        start_time = end_time - timedelta(days=1)

    headers, prices = get_prices(
        account_info, instance_configuration, end_time=end_time, start_time=start_time
    )
    click.echo(tabulate(prices, headers=headers))


if __name__ == "__main__":
    # pylint: disable=E1120
    cli()
