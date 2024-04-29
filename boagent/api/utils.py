from datetime import datetime
from boaviztapi_sdk import ApiClient, Configuration
from dateutil import parser
from .config import Settings
from os import PathLike

settings = Settings()
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
                    "capacity": r["capacity"],
                }
        else:
            hash_map["{}".format(r["capacity"])] = {
                "units": 1,
                "capacity": r["capacity"],
            }
    return [v for k, v in hash_map.items()]


def sort_disks(items: list):
    hash_map = {}
    for r in items:
        if "{}:{}:{}".format(r["capacity"], r["manufacturer"], r["type"]) in hash_map:
            hash_map["{}:{}:{}".format(r["capacity"], r["manufacturer"], r["type"])][
                "units"
            ] += 1
        else:
            hash_map["{}:{}:{}".format(r["capacity"], r["manufacturer"], r["type"])] = {
                "units": 1,
                "manufacturer": r["manufacturer"],
                "capacity": r["capacity"],
                "type": r["type"],
            }
    return [v for k, v in hash_map.items()]


def get_boavizta_api_client():
    config = Configuration(
        host=BOAVIZTAPI_ENDPOINT,
    )
    client = ApiClient(configuration=config)
    return client


def iso8601_or_timestamp_as_timestamp(iso_time: str) -> float:
    """
    Takes an str that's either a timestamp or an iso8601
    time. Returns a float that represents a timestamp.
    """
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


def format_prometheus_output(res, verbose: bool):
    response = ""
    for k, v in res.items():
        if "value" in v and "type" in v:
            if "description" not in v:
                v["description"] = "TODO: define me"
            if type(v["value"]) is float:
                response += format_prometheus_metric(
                    k,
                    "{}. {}".format(
                        v["description"],
                        "In {} ({}).".format(v["long_unit"], v["unit"]),
                    ),
                    v["type"],
                    v["value"],
                )
            if type(v["value"]) is dict:
                response += format_prometheus_metric(
                    k,
                    "{}. {}".format(
                        v["description"],
                        "In {} ({}).".format(v["long_unit"], v["unit"]),
                    ),
                    v["type"],
                    v["value"]["value"],
                )

        else:
            for x, y in v.items():
                if type(y) is float:
                    pass
                else:
                    if "value" in y and "type" in y:
                        if "description" not in y:
                            y["description"] = "TODO: define me"
                        response += format_prometheus_metric(
                            "{}_{}".format(k, x),
                            "{}. {}".format(
                                y["description"],
                                "In {} ({}).".format(y["long_unit"], y["unit"]),
                            ),
                            y["type"],
                            y["value"],
                        )
        if verbose:
            if "boaviztapi_data" in v:
                for impact_name, impact_items in v["boaviztapi_data"][
                    "impacts"
                ].items():
                    if "unit" in impact_items:
                        embedded_impact_values = f"{{value={impact_items['embedded']['value']},min={impact_items['embedded']['min']},max={impact_items['embedded']['max']}}}"
                        response += format_prometheus_metric(
                            "{}".format(f"{impact_name}_total_impact"),
                            "{}. {}".format(
                                impact_items["description"],
                                "In {}".format(impact_items["unit"]),
                            ),
                            "{}".format("gauge"),
                            "{}".format(
                                f"{impact_items['embedded']['value']}",
                            ),
                            embedded_impact_values,
                        )

                for component_name, component_impacts in v["boaviztapi_data"][
                    "verbose"
                ].items():
                    print(f"COMPONENT: {component_name}")
                    formatted_component_name = component_name.lower().replace("-", "_")
                    if "impacts" in component_impacts:
                        for impact, items in component_impacts["impacts"].items():
                            component_embedded_impact_values = f"{{value={items['embedded']['value']},min={items['embedded']['min']},max={items['embedded']['max']}}}"
                            response += format_prometheus_metric(
                                "{}".format(
                                    f"{formatted_component_name}_{impact}_embedded_impact"
                                ),
                                "{}. {}".format(
                                    items["description"],
                                    "In {}".format(items["unit"]),
                                ),
                                "{}".format("gauge"),
                                "{}".format(
                                    f"{items['embedded']['value']}",
                                ),
                                component_embedded_impact_values,
                            )

    return response


def format_prometheus_metric(
    metric_name, metric_description, metric_type, metric_value, metric_label=""
):
    response = """# HELP {} {}
# TYPE {} {}
{}{} {}
""".format(
        metric_name,
        metric_description,
        metric_name,
        metric_type,
        metric_name,
        metric_label,
        metric_value,
    )
    return response


def filter_date_range(data: list, start_date: datetime, stop_date: datetime) -> list:

    lower_index = 0
    upper_index = 0

    start = datetime.timestamp(start_date)
    end = datetime.timestamp(stop_date)

    for d in data:
        if d["timestamp"] < start:
            lower_index += 1
        if d["timestamp"] < end:
            upper_index += 1

    return data[lower_index:upper_index]


def format_scaphandre_json(file: str | PathLike) -> str:
    with open(file, "r") as fd:
        formatted_scaphandre_json = f"[{fd.read()}]".replace(
            '{"host"', ',{"host"'
        ).replace(',{"host"', '{"host"', 1)
    return formatted_scaphandre_json
