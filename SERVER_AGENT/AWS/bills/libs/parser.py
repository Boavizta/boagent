

#%%
import re
import pandas as pd

# #%%
# INPUT_FILE = "Exemple.Cost.Explorer.-.Usage.Type.Group.EC2.Running.Hours.-.Group.By.Instance.Type.csv"

# #%%
# bill = pd.read_csv(INPUT_FILE, header=None)

# # %%
# usage = bill.loc[[0, 1], :]
# # usage = usage.set_index("Instance Type")

# usage_hours_columns = [
#     ("(hrs)" in name and not name.startswith("total"))
#     for name in usage.loc[0, :].str.lower()
# ]
# instance_types = usage.loc[0, usage_hours_columns].apply(
#     lambda x: re.sub(r"\s*\(hrs\)", "", x, flags=re.I)
# )
# # usage = usage.loc[:, usage_hours_columns]
# # usage.loc[:, usage_hours_columns]
# instance_types

# #%%

# usage_and_name = pd.DataFrame(
#     {"instance_type": instance_types, "total_usage": usage.loc[1, usage_hours_columns]}
# ).reset_index(drop=True)
# usage_and_name


#%%
# inferred from the sample file provided
HEADERS_ROW = 0
TOTAL_USAGE_ROW = 1

def get_usage_by_instance_type(bill: pd.DataFrame):
    """
    take a bill as a dataframe and extract the usage info for each instance type
    """
    # keep only the headers and total usage
    usage = bill.loc[[HEADERS_ROW, TOTAL_USAGE_ROW], :]
    # keep only columns that give values in hours except for the total
    usage_hours_columns = [
        ("(hrs)" in name and not name.startswith("total"))
        for name in usage.loc[HEADERS_ROW, :].str.lower()
    ]
    # build a new dataframe
    usage_by_type = pd.DataFrame(
        {
            "instance_type": usage.loc[HEADERS_ROW, usage_hours_columns],
            "hours_use_time": usage.loc[TOTAL_USAGE_ROW, usage_hours_columns],
        }
    ).reset_index(drop=True)
    # rename instances to remove 'Hrs'
    usage_by_type = usage_by_type.assign(
        instance_type=usage_by_type.instance_type.apply(
            lambda x: re.sub(r"\s*\(hrs\)", "", x, flags=re.I)
        )
    )
    return usage_by_type
