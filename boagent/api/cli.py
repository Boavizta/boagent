import click
import requests
import json
from boagent.api.api import get_metrics, DEFAULT_LIFETIME
from boagent.api.utils import iso8601_or_timestamp_as_timestamp, format_prometheus_metric, format_prometheus_output

@click.command("prometheus-push")
@click.option('--push-url', default='http://localhost:9091',  help='Push Gateway URL.')
@click.option('--push-job', default='boagent', help='Push Gateway job to attach metrics to.')
@click.option('--push-suffix', default='metrics', help='Push Gateway job to attach metrics to.')
@click.option('--start-time', default = "0.0", help='')
@click.option('--end-time', default="0.0", help='')
@click.option('--verbose', default=False, help='')
@click.option('--location', default="EEE", help='')
@click.option('--measure-power', default=True, help='')
@click.option('--lifetime', default=DEFAULT_LIFETIME, help='')
@click.option('--fetch-hardware', default=False, help='')
@click.option('--no-certificate-check', default=False, help='Disables TLS certificate check')
def prometheus_push(push_url, push_job, push_suffix,
    start_time, end_time, verbose, location, measure_power, lifetime,
    fetch_hardware, no_certificate_check
):
    metrics = get_metrics(
        iso8601_or_timestamp_as_timestamp(start_time),
        iso8601_or_timestamp_as_timestamp(end_time),
        verbose,
        location,
        measure_power,
        lifetime,
        fetch_hardware,
    )
    labels = {
        "hostname": "oden"
    }
    body = format_prometheus_output(metrics, verbose, labels=labels)
    body += format_prometheus_metric(
        metric_name="boagent_hardware_lifetime",
        metric_description="Hardware lifetime hypothesis for calculation. In Years.",
        metric_type="GAUGE",
        metric_value=lifetime,
        labels=labels
    )
    url = "{}/{}/job/{}/hostname/{}".format(push_url, push_suffix, push_job, "oden")
    p = requests.post(url, data=body, verify=True if not no_certificate_check else False)

if __name__ == '__main__':
    prometheus_push()
