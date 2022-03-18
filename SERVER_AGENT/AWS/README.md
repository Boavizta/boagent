# AWS

A script to get impacts of all EC2 instances of an AWS account.

## Principle

1. Query AWS apis to list all instances of the account and retrieve average CPU utilization
2. Use theses results to query Boavizta API to get impacts

## Usage

Authenticate against aws using a specific profile with `export AWS_PROFILE=my-custom-profile-name`.

```bash
cd aws_code
python main.py
```

## Sample code to query AWS

See some examples of querying aws api in `sample_code/python print-instance-usage.py`.
