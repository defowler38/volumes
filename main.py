import boto3
import yaml


def import_yaml(file):
    stream = open(file, 'r')
    docs=yaml.load_all(stream,Loader=yaml.FullLoader)
    l = list(docs)
    return l

def run_ec2_from_file(filepath):
    data = import_yaml(filepath)
    server = data[0]['server']
    ec2_client = boto3.client('ec2')
    #create default key pair for other user to ssh
    response = ec2_client.create_key_pair(KeyName='ec2Key')
    with open('./my_key.pem', 'w') as file:
        file.write(response['key_material'])
    ##user data for ssh
    ud = build_userdata(server['users'])
    response = ec2_client.run_instances(
        ImageID=server['ami_type'],
        InstanceType=server['instance_type'],
        KeyName='ec2Key',
        UserData=ud
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

def build_userdata(users):
    ud = "#!/bin/bash " \
         "echo "+ users[0]['ssh_key'] + " > /home/"+users[0]['login']+"/.ssh/authorized_keys" \
         "chown "+ users[0]['login']+": /home/"+users[0]['login']+"/.ssh/authorized_keys" \
         "chmod 0600 /home"+users[0]['login']+"/.ssh/authorized_keys" \
         "echo "+ users[1]['ssh_key'] + " > /home/"+users[1]['login']+"/.ssh/authorized_keys" \
         "chown "+ users[1]['login']+": /home/"+users[1]['login']+"/.ssh/authorized_keys" \
         "chmod 0600 /home"+users[1]['login']+"/.ssh/authorized_keys"
    return ud



def run():
    run_ec2_from_file("./config.yaml")


if __name__ == '__main__':
    run()
