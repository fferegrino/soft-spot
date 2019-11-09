import datetime
from copy import deepcopy

import pytest
from dateutil.tz import tzutc
from mock import MagicMock

from soft_spot.implementations.request import (
    get_active_spot_requests,
    cancel_spot_requests,
)


@pytest.fixture
def active_requests():
    return [
        {
            "CreateTime": datetime.datetime(2019, 11, 9, 11, 54, 24, tzinfo=tzutc()),
            "InstanceId": "i-079f00718d8935af2",
            "LaunchSpecification": {
                "SecurityGroups": [
                    {"GroupName": "sec-1", "GroupId": "sg-03c5e63e7f2718546"}
                ],
                "ImageId": "ami-0be057a22c63962cb",
                "InstanceType": "t2.micro",
                "KeyName": "kp_aws_mac_1",
                "Placement": {"AvailabilityZone": "eu-west-2c"},
                "SubnetId": "subnet-330e685a",
                "Monitoring": {"Enabled": False},
            },
            "LaunchedAvailabilityZone": "eu-west-2c",
            "ProductDescription": "Linux/UNIX",
            "SpotInstanceRequestId": "sir-2648y2kj",
            "SpotPrice": "0.005000",
            "State": "active",
            "Status": {
                "Code": "fulfilled",
                "Message": "Your spot request is fulfilled.",
                "UpdateTime": datetime.datetime(
                    2019, 11, 9, 11, 54, 26, tzinfo=tzutc()
                ),
            },
            "Tags": [],
            "Type": "one-time",
            "ValidUntil": datetime.datetime(2019, 11, 16, 11, 54, 24, tzinfo=tzutc()),
            "InstanceInterruptionBehavior": "terminate",
        }
    ]


@pytest.fixture
def active_requests_ids(active_requests):
    return [req["SpotInstanceRequestId"] for req in active_requests]


@pytest.fixture
def active_instance_ids(active_requests):
    return [req["InstanceId"] for req in active_requests]


@pytest.fixture
def spot_instances_describe(active_requests):
    return {
        "SpotInstanceRequests": [
            {
                "CreateTime": datetime.datetime(2019, 11, 9, 9, 59, 23, tzinfo=tzutc()),
                "InstanceId": "i-0977dc92c1597b2a9",
                "LaunchSpecification": {
                    "SecurityGroups": [
                        {"GroupName": "sec-1", "GroupId": "sg-03c5e63e7f2718546"}
                    ],
                    "ImageId": "ami-0be057a22c63962cb",
                    "InstanceType": "t2.micro",
                    "KeyName": "kp_aws_mac_1",
                    "Placement": {"AvailabilityZone": "eu-west-2b"},
                    "SubnetId": "subnet-ca3fce86",
                    "Monitoring": {"Enabled": False},
                },
                "LaunchedAvailabilityZone": "eu-west-2b",
                "ProductDescription": "Linux/UNIX",
                "SpotInstanceRequestId": "sir-epqgxnjj",
                "SpotPrice": "0.005000",
                "State": "closed",
                "Status": {
                    "Code": "instance-terminated-by-user",
                    "Message": "Spot Instance terminated due to user-initiated termination.",
                    "UpdateTime": datetime.datetime(
                        2019, 11, 9, 10, 9, 29, tzinfo=tzutc()
                    ),
                },
                "Tags": [],
                "Type": "one-time",
                "ValidUntil": datetime.datetime(
                    2019, 11, 16, 9, 59, 23, tzinfo=tzutc()
                ),
                "InstanceInterruptionBehavior": "terminate",
            },
            *active_requests,
            {
                "CreateTime": datetime.datetime(2019, 11, 9, 9, 54, 36, tzinfo=tzutc()),
                "InstanceId": "i-0ab8ac0a5104df2ae",
                "LaunchSpecification": {
                    "SecurityGroups": [
                        {"GroupName": "sec-1", "GroupId": "sg-03c5e63e7f2718546"}
                    ],
                    "ImageId": "ami-0be057a22c63962cb",
                    "InstanceType": "t2.micro",
                    "KeyName": "kp_aws_mac_1",
                    "Placement": {"AvailabilityZone": "eu-west-2b"},
                    "SubnetId": "subnet-ca3fce86",
                    "Monitoring": {"Enabled": False},
                },
                "LaunchedAvailabilityZone": "eu-west-2b",
                "ProductDescription": "Linux/UNIX",
                "SpotInstanceRequestId": "sir-n6zry68h",
                "SpotPrice": "0.005000",
                "State": "cancelled",
                "Status": {
                    "Code": "instance-terminated-by-user",
                    "Message": "Spot Instance terminated due to user-initiated termination.",
                    "UpdateTime": datetime.datetime(
                        2019, 11, 9, 9, 59, 57, tzinfo=tzutc()
                    ),
                },
                "Tags": [],
                "Type": "one-time",
                "ValidUntil": datetime.datetime(
                    2019, 11, 16, 9, 54, 36, tzinfo=tzutc()
                ),
                "InstanceInterruptionBehavior": "terminate",
            },
        ],
        "ResponseMetadata": {
            "RequestId": "d6d7bfbc-ac74-464a-9401-0edba865762f",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "content-type": "text/xml;charset=UTF-8",
                "transfer-encoding": "chunked",
                "vary": "accept-encoding",
                "date": "Sat, 09 Nov 2019 11:58:47 GMT",
                "server": "AmazonEC2",
            },
            "RetryAttempts": 0,
        },
    }


def test_get_active_spot_requests(active_requests, spot_instances_describe):
    client = MagicMock()
    client.describe_spot_instance_requests.return_value = spot_instances_describe
    actual = get_active_spot_requests(client)

    expected = deepcopy(active_requests)

    assert actual == expected


def test_cancel_spot_requests(
    active_requests, active_requests_ids, active_instance_ids
):
    client = MagicMock()
    cancel_spot_requests(client, active_requests)
    client.cancel_spot_instance_requests.assert_called_once_with(
        SpotInstanceRequestIds=active_requests_ids
    )
    client.terminate_instances.assert_called_once_with(InstanceIds=active_instance_ids)
