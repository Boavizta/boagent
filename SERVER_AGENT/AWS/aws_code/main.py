import boto3
from datetime import datetime, timedelta
import requests
from requests.structures import CaseInsensitiveDict

client = boto3.client('cloudwatch')

ec2 = boto3.resource('ec2')

def get_cpu_utilisation(cw_cli, ec2_id):
    response = cw_cli.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': ec2_id
            },
        ],
        StartTime=datetime(2022, 1, 1) - timedelta(seconds=600),
        EndTime=datetime(2022, 3, 18),
        Period=86400,
        Statistics=[
            'Maximum',
        ],
        Unit='Percent'
    )
    print("response is ; ", response)
    # for cpu in response:
    #     if cpu['Key'] == 'Average':
    #         k = cpu['Value']
    # print("k : ", k)   




def get_ec2_instance_ids(ec2_cli):
    # list de dict :  InstanceId, InstanceType
    instance_ids_types = []
    response = ec2_cli.describe_instances()
    if response and "Reservations" in response:
        for reservation in response['Reservations']:
            instances = reservation['Instances']
            for instance in instances: 
                instance_ids_types.append({'instanceId': instance['InstanceId'], 'instanceType':instance['InstanceType']})
    return instance_ids_types
                


def get_boavizta_supported_instances():
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    
    x = requests.get('http://hackaton.boavizta.org:5000/v1/cloud/aws/all_instances', headers=headers, json={} )
    # print(x.text) 
    return x.text

def is_supported_instance(instance, supported_instances):
    return instance in supported_instances

def get_boavizta_default_data(instance_type):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["accept"] = "application/json"

    x = requests.post(f'http://hackaton.boavizta.org:5000/v1/cloud/aws?instance_type={instance_type}&verbose=false', headers=headers, json={} )
    return x.text

def get_boavizta_data(instance_type, hours_use_time, usage_location):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["accept"] = "application/json"

    x = requests.post(f'http://api.boavizta.org:5000/v1/cloud/aws?instance_type={instance_type}&verbose=false', headers=headers, json={"hours_use_time": hours_use_time, "usage_location": usage_location} )
    return x.text



if __name__ == "__main__":
    """
    1er scénario : 
    - On se connecte à AWS 
    - On liste les VM EC2
    - On récupère l'instance type d'une EC2
    - On récupère 
    """

    # Get aws instances
    instances = ec2.instances.all()



    # Getting Boavizta data
    supported_instances = get_boavizta_supported_instances()
    
    for ec2 in instances:
        if is_supported_instance(ec2.instance_type, supported_instances):
            print(f'Default impacts of {ec2.id} with type {ec2.instance_type}')
            print(get_boavizta_default_data(ec2.instance_type))
        else:
            print(f'⚠ Skipping instance {ec2.id} because {ec2.instance_type} is not (yet) in the Boavizta dataset')

    print("⚠ Is m1.small supported ?")
    print( is_supported_instance('m1.small', supported_instances))

    print("⚠ Is t2.xlarge supported ?")
    print( is_supported_instance('t2.xlarge', supported_instances))

    print("Is 'a1.4xlarge' supported ?")
    print(is_supported_instance('a1.4xlarge', supported_instances))
    print("Getting default impacts of a supported instance:")
    print(get_boavizta_default_data('a1.4xlarge'))

    get_boavizta_default_data('a1.4xlarge')
    
    get_boavizta_data(
        instance_type="a1.4xlarge",
        hours_use_time=50,
        usage_location="FRA"
    )