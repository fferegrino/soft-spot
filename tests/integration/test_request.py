import threading

from moto.backends import get_model


def test_full_request(ec2, invoke, config_file, aws_region):
    def start_responding():
        requests = get_model("SpotInstanceRequest", aws_region)
        while not requests:
            requests = get_model("SpotInstanceRequest", aws_region)
        [request] = requests
        [instance] = ec2.run_instances(ImageId="ami-1e749f67", MaxCount=1, MinCount=1)[
            "Instances"
        ]
        request.state = "active"
        request.instance_id = instance["InstanceId"]

    t = threading.Timer(3.0, start_responding)
    t.start()

    result = invoke("request", config_file, "--no-volumes", "--no-scripts")
    assert result.exit_code == 0
