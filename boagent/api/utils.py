from datetime import datetime
from boaviztapi_sdk import ApiClient, Configuration
from dateutil import parser
from boagent.api.config import Settings
from os import PathLike
import logging

settings = Settings()
BOAVIZTAPI_ENDPOINT = settings.boaviztapi_endpoint


def configure_logger():
    logger = logging.getLogger("boagent")
    formatter = logging.Formatter(settings.logging_formatter)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


logger = configure_logger()


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
    return [v for v in hash_map.values()]


def sort_disks(items: list):
    hash_map = {}
    for r in items:
        capacity = r["capacity"]
        manufacturer = r["manufacturer"]
        disk_type = r["type"]
        disk = f"{capacity}:{manufacturer}:{disk_type}"
        if disk in hash_map:
            hash_map[disk]["units"] += 1
        else:
            hash_map[disk] = {
                "units": 1,
                "manufacturer": r["manufacturer"],
                "capacity": r["capacity"],
                "type": r["type"],
            }
    return [v for v in hash_map.values()]


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
            logger.debug(f"{iso_time} is an iso 8601 datetime")
        except Exception as e:
            logger.debug(f"{iso_time} is not an iso 8601 datetime")
            logger.debug(f"Exception : {e}")
            try:
                dt = datetime.fromtimestamp(int(round(float(iso_time))))
                logger.debug(f"{iso_time} is a timestamp")
            except Exception as e:
                logger.debug(f"{iso_time} is not a timestamp")
                logger.debug(f"Exception : {e}")
                logger.debug(f"Parser would give : {parser.parse(iso_time)}")
        finally:
            if dt:
                return dt.timestamp()
            else:
                return float(iso_time)


def format_prometheus_output(res, verbose: bool, labels: dict = {}):
    response = ""
    for k, v in res.items():
        if "value" in v and "type" in v:
            if "description" not in v:
                v["description"] = "TODO: define me"
            value_type = type(v["value"])
            if value_type is float or value_type is int or value_type is str:
                response += format_prometheus_metric(
                    f"boagent_{k}",
                    f"{v['description']}. In {v['long_unit']} ({v['unit']})",
                    v["type"],
                    v["value"],
                    labels,
                )
            if value_type is dict:
                response += format_prometheus_metric(
                    f"boagent_{k}",
                    f"{v['description']}. In {v['long_unit']} ({v['unit']})",
                    v["type"],
                    v["value"]["value"],
                    labels,
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
                            f"boagent_{k}_{x}",
                            f"{y['description']}. In {y['long_unit']} ({y['unit']})",
                            y["type"],
                            y["value"],
                            labels,
                        )
        if verbose:
            if "boaviztapi_data" in v:
                for impact_name, impact_items in v["boaviztapi_data"][
                    "impacts"
                ].items():
                    if "unit" in impact_items:
                        for value in impact_items["embedded"]:
                            if value == "warnings":
                                pass
                            else:
                                # Embedded impact might not be implemented in BoaviztAPI for an impact criterion.
                                if "value" in impact_items["embedded"]:
                                    response += format_prometheus_metric(
                                        f"boaviztapi_{impact_name}_total_impact_{value}",
                                        f"{impact_items['description']}. In {impact_items['unit']}",
                                        "gauge",
                                        f"{impact_items['embedded']['value']}",
                                        labels,
                                    )
                                else:
                                    response += format_prometheus_metric(
                                        f"boaviztapi_{impact_name}_total_impact_{value}",
                                        f"{impact_items['description']}. In {impact_items['unit']}",
                                        "gauge",
                                        f"{impact_items['embedded']}",
                                        labels,
                                    )

                for component_name, component_impacts in v["boaviztapi_data"][
                    "verbose"
                ].items():
                    formatted_component_name = component_name.lower().replace("-", "_")
                    if "impacts" in component_impacts:
                        for impact, items in component_impacts["impacts"].items():
                            if "value" in items["embedded"]:
                                for component_embedded_impact_metric, value in items[
                                    "embedded"
                                ].items():
                                    if component_embedded_impact_metric == "warnings":
                                        pass
                                    else:
                                        response += format_prometheus_metric(
                                            f"boaviztapi_{formatted_component_name}_{impact}_embedded_impact_{component_embedded_impact_metric}"
                                            f"{items['description']}. In {items['unit']}",
                                            "gauge",
                                            f"{value}",
                                            labels,
                                        )

    return response


def format_prometheus_metric(
    metric_name, metric_description, metric_type, metric_value, labels: dict = {}
):

    labels_str = "{"
    for k, v in labels.items():
        labels_str += f'{k}="{v}"'
    labels_str += "}"
    response = f"""# HELP {metric_name} {metric_description}
               # TYPE {metric_name} {metric_type}
               {metric_name}{labels_str} {metric_value}
               """
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


def ratio(value: int | float, ratio: int | float):
    ratioed_value = value * ratio
    return ratioed_value
