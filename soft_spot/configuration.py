import configparser
from functools import partial


def get_account_info(account_info_file):
    if account_info_file:
        config = configparser.ConfigParser()
        config.read(account_info_file)
        return config["DEFAULT"]
    return {}


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


def get_price_request_configuration(config):
    instance_section = config["INSTANCE"]
    price_request_configuration = {"InstanceTypes": [instance_section["type"]]}
    availability_zone = instance_section.get("availability_zone", None)
    product_description = instance_section.get("product_description", None)
    if availability_zone:
        price_request_configuration["AvailabilityZone"] = availability_zone
    if product_description:
        price_request_configuration["ProductDescriptions"] = [product_description]
    return price_request_configuration
