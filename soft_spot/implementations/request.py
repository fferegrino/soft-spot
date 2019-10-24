from functools import partial
from time import sleep

import click

DELAY = 10


class SpotRequestError(Exception):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message


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
    return client.describe_instances(InstanceIds=[instance_id])["Reservations"][0][
        "Instances"
    ][0]


def get_spot_request(client, instance_config):
    request_response = client.request_spot_instances(**instance_config)
    current_request = request_response["SpotInstanceRequests"][0]
    request_id = current_request["SpotInstanceRequestId"]
    click.echo(f"Spot request {request_id} created, status: {current_request['State']}")
    spot_request = wait_for_spot_request(client, request_id)
    return spot_request


def request_instance(client, config):
    instance_config = get_instance_configuration(config)
    spot_request = get_spot_request(client, instance_config)

    if spot_request["State"] != "active":
        raise SpotRequestError(
            f"The spot request has failed, the state is {spot_request['State']}"
        )

    instance = get_instance_from(client, spot_request)
    instance_state = instance["State"]["Name"]
    if instance_state != "running":
        raise SpotRequestError(
            f"The request was fullified but the instance state is {instance_state}"
        )
    return instance


def get_instance_from(client, spot_request):
    instances = client.describe_instances(InstanceIds=[spot_request["InstanceId"]])
    [instance] = instances["Reservations"][0]["Instances"]
    client.create_tags(
        Resources=[instance["InstanceId"]],
        Tags=[{"Key": "CreatedBy", "Value": "SoftSpot"}],
    )

    instance_id = instance["InstanceId"]
    click.echo(f"Instance {instance_id} started")
    return wait_until_instance_ready(client, instance_id)


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


def get_public_ip(instance):
    return instance["NetworkInterfaces"][0]["Association"]["PublicIp"]
