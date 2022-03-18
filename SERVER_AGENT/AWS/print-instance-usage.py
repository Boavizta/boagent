import boto3
import sys
from datetime import datetime, timedelta
  
client = boto3.client('cloudwatch')

ec2 = boto3.resource('ec2')

print("All instances of the account")
print("----------------------------")
for instance in ec2.instances.all():
  print(
    "Id: {0}\nPlatform: {1}\nType: {2}\nPublic IPv4: {3}\nAMI: {4}\nState: {5}\n".format(
    instance.id, instance.platform, instance.instance_type, instance.public_ip_address, instance.image.id, instance.state
  )
)





print("Example CPU usage query")
print("----------------------------")
metrics = client.get_metric_statistics(
  Namespace='AWS/EC2',
  MetricName='CPUUtilization',
  Dimensions=[
    {
    'Name': 'InstanceId',
    'Value': 'i-1234abcd'
    },
  ],
  StartTime=datetime(2018, 4, 23) - timedelta(seconds=600),
  EndTime=datetime(2018, 4, 24),
  Period=86400,
  Statistics=[
    'Average',
  ],
  Unit='Percent'
)
print(metrics)  
  # for cpu in response['Datapoints']:
  #   if 'Average' in cpu:
  #   print(cpu['Average'])
