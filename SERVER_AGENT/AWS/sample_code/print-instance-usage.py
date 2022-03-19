import boto3
import sys
from datetime import datetime, timedelta
  
client = boto3.client('cloudwatch')

ec2 = boto3.resource('ec2')






def get_instance_cpu_metrics(instance):
  metrics = client.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[
      {
      'Name': 'InstanceId',
      'Value': instance.id
      },
    ],
    # at 10 am 
    StartTime=datetime(2022, 3, 15) + timedelta(hours=10),
    EndTime=datetime(2022, 3, 18) + timedelta(hours=10),
    # 24 hours period
    Period=86400,
    Statistics=[
      'Average',
    ],
    Unit='Percent'
  )
  return metrics




def print_instance_detail(instance):
  metrics = get_instance_cpu_metrics(instance)
  print(
    "\nId: {0}\nType: {1}".format(
      instance.id, instance.instance_type
      )
  )
  print("CPU usage:")
  for cpu in metrics['Datapoints']:
    if 'Average' in cpu:
      print(cpu['Timestamp'], cpu['Average'])



print("List instances of the account")
print("----------------------------")
for instance in ec2.instances.all():
  print(
    "Id: {0}\nPlatform: {1}\nType: {2}\nPublic IPv4: {3}\nAMI: {4}\nState: {5}\n".format(
    instance.id, instance.platform, instance.instance_type, instance.public_ip_address, instance.image.id, instance.state
  )
)

print("List instances of with CPU usage of the account")
print("----------------------------")
for instance in ec2.instances.all():
  print_instance_detail(instance)



