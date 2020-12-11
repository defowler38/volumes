import boto3
import os
import yaml


def import_yaml(file):
    stream = open(file, 'r')
    docs=yaml.load_all(stream,Loader=yaml.FullLoader)
    l = list(docs)
    return l

def create_ec2_from_file(filepath):
    data = import_yaml(filepath)
    server = data[0]['server']
    ec2_client = boto3.client('ec2')
    response = ec2_client.run_instances(
        ImageID=server['ami_type'],
        InstanceType=server['instance_type'],
    )
    instanceID = response['Instances'][0]['InstanceId']
    for v in server['volumes']:
        vid = build_volumes(v)
        ec2_client.attach_volume(
            Device=v['device'],
            InstanceId=instanceID,
            VolumeId=vid
        )


def build_volumes(volume):
    ec2 = boto3.client('ec2')
    response = ec2.create_volume(
        AvailabilityZone='az1',
        Size=volume['size_gb'],
        VolumeType=volume['type']
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return response['VolumeId']

def run():
    create_ec2_from_file("./config.yaml")


if __name__ == '__main__':
    run()