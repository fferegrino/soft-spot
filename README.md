# soft-spot

Do you have a soft spot for cheap cloud computing (**a.k.a. AWS Spot instances**)? Me too, no shame on that.

However, what is a shame is having to go through that clunky UI and click here and there to get one; `soft-spot` makes it dead easy to launch an instance:

## How?
Just define a file with the specifications of the machine you want to launch:  

```ini
[INSTANCE]
ami = ami-06f2f779464715dc5
type = t2.micro
security_group = wizard-launch
key_pair = a_secret_key
spot_price = 0.0035

[ACCOUNT]
user = unbuntu

[VOLUME]
id = vol-volume123
device = /dev/sda2
mount_point = /data/
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
region_name = us-west-1
```

And then pass it on to the `spot` command:

```bash
sspot -a ~/aws_credentials.txt request <<instance_config_file>> 
```
