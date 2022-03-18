import moto
import main
import boto3
from datetime import datetime, timedelta

mock_ec2 = moto.mock_ec2()
mock_ec2.start()

mock_cw = moto.mock_cloudwatch()
mock_cw.start()

def put_metrics_data(client, ec2_id):
    response = client.put_metric_data(
        Namespace='AWS/EC2',
        MetricData=[
            {
                'MetricName': 'CPUUtilization',
                'Dimensions': [
                    {
                    'Name': 'InstanceId',
                    'Value': ec2_id
                    }
                ],
                'Timestamp': datetime(2022, 3, 11),
                'StatisticValues': {
                    'SampleCount': 123.0,
                    'Sum': 123.0,
                    'Minimum': 10.0,
                    'Maximum': 70.0,
                },
                'Unit': 'Percent'
            },
        ]
    )
    print("the response is : ", response)


if __name__ == "__main__":
    # Check if instances are supported
    supported_instances = main.get_boavizta_supported_instances()
    print("⚠ Is m1.small supported ?")
    print( main.is_supported_instance('m1.small', supported_instances))

    print("Is 'a1.4xlarge' supported ?")
    print( main.is_supported_instance('a1.4xlarge', supported_instances))

    # Set up mock "AWS Account"
    ec2_cli = boto3.client("ec2", region_name="eu-west-3")
    cw_cli = boto3.client("cloudwatch", region_name="eu-west-3")

    ec2_cli.run_instances(ImageId="boaviztaImage", MinCount=3, MaxCount=3, InstanceType='a1.medium')

    toto = main.get_ec2_instance_ids(ec2_cli)

    for instance in toto: 
        put_metrics_data(cw_cli, instance['instanceId'])
        main.get_cpu_utilisation(cw_cli, instance['instanceId'])
        # main.get_boavizta_data(instance['instanceType'], hours_use_time=50, usage_location="FRA")