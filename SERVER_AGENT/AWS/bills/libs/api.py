import requests


def get_aws_instance_gwp(instance_type, hours_use_time, usage_location):
    """
    call the api with the given instance type, usage, and location
    if the instance is not found return a dict with null values
    """
    headers = dict()
    headers["Content-Type"] = "application/json"
    headers["accept"] = "application/json"

    x = requests.post(
        f"http://api.boavizta.org:5000/v1/cloud/aws?instance_type={instance_type}&verbose=false",
        headers=headers,
        json={"hours_use_time": hours_use_time, "usage_location": usage_location},
    )
    if x.status_code == 200:
        res = x.json()
        return res['gwp']
    # raise Exception(f"instance {instance_type!r} not found")
    return {'manufacture': None, 'use': None}



