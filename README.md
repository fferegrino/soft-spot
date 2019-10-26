# soft-spot

[![Build Status](https://dev.azure.com/messier-16/soft-spot/_apis/build/status/fferegrino.soft-spot?branchName=master)](https://dev.azure.com/messier-16/soft-spot/_build/latest?definitionId=1&branchName=master) [![PyPI version](https://badge.fury.io/py/soft-spot.svg)](https://pypi.org/project/soft-spot/)

Do you have a soft spot for cheap cloud computing (**a.k.a. AWS Spot instances**)? Me too, no shame on that.

However, what is a shame is having to go through that clunky UI and click here and there to get one; `soft-spot` makes it dead easy to launch an instance:

## How?
Just define a file with the specifications of the machine you want to launch:  

```ini
[INSTANCE]
ami = ami-06d51e91cea0dac8d
type = t2.micro
security_group = SecurityGroupName
key_pair = some-key
spot_price = 0.005
availability_zone = us-west-2c

[VOLUME]
id = vol-00a56acb10f11b0e3
device = /dev/sdf

[ACCOUNT]
user = ubuntu
key_location = ~/.ssh/some-key.pem

[SCRIPT]
commands = ["sudo mkdir /data", "sudo mount /dev/xvdf /data", "sudo chown ubuntu /data"]
```

Then just execute the `sspot request` command:  

```bash
sspot request <<instance_config_file>>
```

### Credentials  
This script uses `boto3` so I strongly recommend heading over to [its documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) to learn more.  

Alternatively, you could create a tiny configuration file like this:  

```ini
[DEFAULT]
aws_access_key_id = an_acces_key
aws_secret_access_key = a_secret_key
region_name = us-west-2
```

And then pass it on to the `spot` command:

```bash
sspot -a ~/aws_credentials.txt request <<instance_config_file>> 
```
