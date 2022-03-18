"""
Script that will parse an AWS bill and extract the usage info for each resource type
The GWP can then be computed
"""

#%%
import pandas as pd

from libs.api import get_aws_instance_gwp
from libs.parser import get_usage_by_instance_type

from argparse import ArgumentParser

parser = ArgumentParser(description="Program that retrives GWP of an instance from its usage")

parser.add_argument("-i", "--input_file", help="Path to the csv file.", type=str, required=True)

args = parser.parse_args()

input_file = args.input_file



#%%
# read input file
bill = pd.read_csv(input_file, header=None)

# extract usage info
usage_by_type = get_usage_by_instance_type(bill)

# call api for each instance type
gwp = usage_by_type.apply(
    lambda row: get_aws_instance_gwp(row.instance_type, row.hours_use_time, "FRA"),
    axis=1,
)

# format result
result = pd.concat([usage_by_type, pd.DataFrame(gwp.tolist(), index=usage_by_type.index)], axis=1)

print(result)
# %%
