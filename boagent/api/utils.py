from datetime import datetime
from boaviztapi_sdk import ApiClient, Configuration
from dateutil import parser
from config import settings

BOAVIZTAPI_ENDPOINT = settings.boaviztapi_endpoint

def sort_ram(items: list):
    hash_map = {}
    for r in items:
        if "manufacturer" in r:
            if "{}:{}".format(r["capacity"], r["manufacturer"]) in hash_map:
                hash_map["{}:{}".format(r["capacity"], r["manufacturer"])]["units"] += 1
            else:
                hash_map["{}:{}".format(r["capacity"], r["manufacturer"])] = {
                    "units": 1,
                    "manufacturer": r["manufacturer"],
                    "capacity": r["capacity"]
                }
        else:
            hash_map["{}".format(r["capacity"])] = {
                "units": 1,
                "capacity": r["capacity"]
            }
    return [v for k, v in hash_map.items()]

def sort_disks(items: list):
    hash_map = {}
    for r in items:
        if "{}:{}:{}".format(r["capacity"], r["manufacturer"], r["type"]) in hash_map:
            hash_map["{}:{}:{}".format(r["capacity"], r["manufacturer"], r["type"])]["units"] += 1
        else:
            hash_map["{}:{}:{}".format(r["capacity"], r["manufacturer"], r["type"])] = {
                "units": 1,
                "manufacturer": r["manufacturer"],
                "capacity": r["capacity"],
                "type": r["type"]
            }
    return [v for k, v in hash_map.items()]

def get_boavizta_api_client():
    config = Configuration(
        host=BOAVIZTAPI_ENDPOINT,
    )
    client = ApiClient(
        configuration=config, pool_threads=2
    )
    return client

def iso8601_or_timestamp_as_timestamp(iso_time: str):
    '''
    Takes an str that's either a timestamp or an iso8601
    time. Returns a float that represents a timestamp.
    '''
    if iso_time == "0.0" or iso_time == "0":
        return float(iso_time)
    else:
        dt = None
        try:
            dt = parser.parse(iso_time)
            print("{} is an iso 8601 datetime".format(iso_time))
        except Exception as e:
            print("{} is not an iso 8601 datetime".format(iso_time))
            print("Exception : {}".format(e))
            try:
                dt = datetime.fromtimestamp(int(round(float(iso_time))))
                print("{} is a timestamp".format(iso_time))
            except Exception as e:
                print("{} is not a timestamp".format(iso_time))
                print("Exception : {}".format(e))
                print("Parser would give : {}".format(parser.parse(iso_time)))
        finally:
            if dt:
                return dt.timestamp()
            else:
                return float(iso_time)

def format_prometheus_output(res):
    response = ""
    for k, v in res.items():
        if "value" in v and "type" in v:
            if "description" not in v:
                v["description"] = "TODO: define me"
            response += format_prometheus_metric(k, "{}. {}".format(v["description"], "In {} ({}).".format(v["long_unit"], v["unit"])), v["type"], v["value"])
    #response += format_prometheus_metric("energy_consumption", "Energy consumed in the evaluation time window (evaluated at least for an hour, be careful if the time windows is lower than 1 hour), in Wh", "counter", res["emissions_calculation_data"]["energy_consumption"])
        else:
            for x, y in v.items():
                if "value" in y and "type" in y:
                    if "description" not in y:
                        y["description"] = "TODO: define me"
                    response += format_prometheus_metric("{}_{}".format(k,x), "{}. {}".format(y["description"], "In {} ({}).".format(y["long_unit"], y["unit"])), y["type"], y["value"])

    return response

def format_prometheus_metric(metric_name, metric_description, metric_type, metric_value):
    response = """# HELP {} {}
# TYPE {} {}
{} {}
""".format(metric_name, metric_description, metric_name, metric_type, metric_name, metric_value)
    return response

def filter_date_range(data: list, start_date: datetime, stop_date: datetime) -> list:

    lower_index = 0
    upper_index = 0

    start = datetime.timestamp(start_date)
    end   = datetime.timestamp(stop_date)

    for d in data:
        if d["timestamp"] < start: lower_index+=1
        if d["timestamp"] < end: upper_index+=1

    return data[lower_index : upper_index]
