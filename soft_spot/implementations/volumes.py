import click


def attach_device(client, instance_id, config):
    volume_id = config.get("VOLUME", "id")
    device = config.get("VOLUME", "device")
    click.echo(f"Will attach the volume {volume_id} to {instance_id} at {device}")
    attachment_result = client.attach_volume(
        VolumeId=volume_id, InstanceId=instance_id, Device=device
    )
    return attachment_result
