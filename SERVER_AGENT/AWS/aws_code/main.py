import boto3
from datetime import datetime, timedelta
import requests
from requests.structures import CaseInsensitiveDict

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
    for cpu in response:
        if cpu['Key'] == 'Average':
            k = cpu['Value']
    print("k : ", k)   


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
                

def get_boavizta_data(instance_type, hours_use_time, usage_location):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["accept"] = "application/json"

    x = requests.post(f'http://api.boavizta.org:5000/v1/cloud/aws?instance_type={instance_type}&verbose=false', headers=headers, json={"hours_use_time": hours_use_time, "usage_location": usage_location} )
    print(x.text) 



if __name__ == "__main__":
    """
    1er scénario : 
    - On se connecte à AWS 
    - On liste les VM EC2
    - On récupère l'instance type d'une EC2
    - On récupère 
    """
    get_boavizta_data(
        instance_type="m1.small",
        hours_use_time=50,
        usage_location="FRA"
    )