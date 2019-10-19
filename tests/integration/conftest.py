import os

import boto3
from moto import mock_ec2
import pytest


@pytest.fixture
def aws_credentials(aws_region):
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_REGION"] = aws_region
    os.environ["AWS_DEFAULT_REGION"] = aws_region


@pytest.fixture
def ec2(aws_credentials, aws_region):
    with mock_ec2():
        yield boto3.client("ec2", region_name=aws_region)
