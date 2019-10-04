import configparser
import logging
from functools import partial
from time import sleep

import boto3

LOGGER = logging.getLogger("soft_spot.main")
DELAY = 10


def get_client(account_info):
    LOGGER.info(f"Creating client with {account_info}")
    return boto3.client("ec2", **account_info)


def get_account_info():
    config = configparser.ConfigParser()
    config.read("aws_account.cfg")
    return config["DEFAULT"]


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


def get_instance_from(request):
    instances = client.describe_instances(InstanceIds=[request["InstanceId"]])
    return instances["Reservations"][0]["Instances"][0]


def wait_for_instance(spot_request_id):
    response = client.describe_spot_instance_requests(
        SpotInstanceRequestIds=[spot_request_id]
    )
    spot_request = response["SpotInstanceRequests"][0]
    while True:
        if spot_request["State"] == "active":
            instance = get_instance_from(spot_request)

            client.create_tags(
                Resources=[spot_request["InstanceId"]],
                Tags=[{"Key": "CreatedBy", "Value": "SoftSpot"}],
            )
            return instance

        response = client.describe_spot_instance_requests(
            SpotInstanceRequestIds=[spot_request_id]
        )
        spot_request = response["SpotInstanceRequests"][0]

        print("Waiting...")
        sleep(DELAY)


def attach_device(instance_id, config):
    volume_id = config.get("VOLUME", "id")
    device = config.get("VOLUME", "device")
    print(f"Will attach the volume {volume_id} to {instance_id} at {device}")
    attachment_result = client.attach_volume(
        VolumeId=volume_id, InstanceId=instance_id, Device=device
    )
    return attachment_result


def get_public_ip(instance):
    return instance["NetworkInterfaces"][0]["Association"]["PublicIp"]


if __name__ == "__main__":
    account_info = get_account_info()
    client = get_client(account_info)

    config = configparser.ConfigParser()
    config.read("mini.spot")

    instance_config = get_instance_configuration(config)
    request = client.request_spot_instances(**instance_config)
    current_request = request["SpotInstanceRequests"][0]
    request_id = current_request["SpotInstanceRequestId"]
    print(f"Spot request {request_id} created, status: {current_request['State']}")
    instance = wait_for_instance(request_id)
    instance_id = instance["InstanceId"]
    public_ip = get_public_ip(instance)
    print(f"Instance {instance_id} started, IP: {public_ip}")
    if config.has_section("VOLUME"):
        attach_device(instance_id, config)
