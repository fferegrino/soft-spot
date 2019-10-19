from functools import partial
from time import sleep

import click

DELAY = 10


def get_instance_configuration(config):
    instance = partial(config.get, "INSTANCE")

    return {
        "InstanceCount": 1,
        "Type": "one-time",
        "InstanceInterruptionBehavior": "terminate",
        "LaunchSpecification": {
            "SecurityGroups": [instance("security_group")],
            "ImageId": instance("ami"),
            "InstanceType": instance("type"),
            "KeyName": instance("key_pair"),
        },
        "SpotPrice": instance("spot_price"),
    }


def wait_until_instance_ready(client, instance_id):
    response = client.describe_instance_status(InstanceIds=[instance_id])
    status = response["InstanceStatuses"][0]["InstanceState"]["Name"]
    while status == "pending":
        response = client.describe_instance_status(InstanceIds=[instance_id])
        status = response["InstanceStatuses"][0]["InstanceState"]["Name"]
        sleep(1)
    return response["InstanceStatuses"][0]["InstanceState"]["Name"]


def request_instance(client, config):

    instance_config = get_instance_configuration(config)
    request_response = client.request_spot_instances(**instance_config)
    current_request = request_response["SpotInstanceRequests"][0]
    request_id = current_request["SpotInstanceRequestId"]
    click.echo(f"Spot request {request_id} created, status: {current_request['State']}")
    spot_request = wait_for_spot_request(client, request_id)

    if spot_request["State"] == "active":
        instance = get_instance_from(client, spot_request)

        client.create_tags(
            Resources=[spot_request["InstanceId"]],
            Tags=[{"Key": "CreatedBy", "Value": "SoftSpot"}],
        )

        instance_id = instance["InstanceId"]
        public_ip = get_public_ip(instance)
        click.echo(f"Instance {instance_id} started, IP: {public_ip}")
        instance_status = wait_until_instance_ready(client, instance_id)
        if instance_status == "running":
            if config.has_section("VOLUME"):
                attach_device(client, instance_id, config)
            click.echo(
                click.style(
                    f"Done! the IP of the image is {public_ip}", bg="blue", fg="white"
                )
            )
        else:
            click.echo(
                f"The instance created changed to a non-running state: {instance_status}"
            )
    else:
        click.echo(f"The request failed, status {spot_request['State']}")


def get_instance_from(client, spot_request):
    instances = client.describe_instances(InstanceIds=[spot_request["InstanceId"]])
    return instances["Reservations"][0]["Instances"][0]


def wait_for_spot_request(client, spot_request_id):
    response = client.describe_spot_instance_requests(
        SpotInstanceRequestIds=[spot_request_id]
    )
    spot_request = response["SpotInstanceRequests"][0]
    while spot_request["State"] == "open":

        response = client.describe_spot_instance_requests(
            SpotInstanceRequestIds=[spot_request_id]
        )
        spot_request = response["SpotInstanceRequests"][0]

        click.echo("Waiting...")
        sleep(DELAY)
    return spot_request


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
