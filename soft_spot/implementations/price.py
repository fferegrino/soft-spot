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


def get_prices(client, instance_configuration, start_time, end_time):
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
