#!/usr/bin/env python3

from openapi_client import ApiClient, Configuration
from openapi_client.api.component_api import ComponentApi
from openapi_client.model.component_cpu import ComponentCPU

from pprint import pprint

def main():
    config = Configuration(
        host="http://localhost:5000",
    )
    client = openapi_client = ApiClient(
        configuration=config, pool_threads=2
    )

    component_api = ComponentApi(client)

    kwargs={
        "core_units": 24,
        "family": "Skylake",
        "manufacture_date": "2017"
    }

    cpu = ComponentCPU(
        **kwargs
    )

    res = component_api.cpu_impact_bottom_up_v1_component_cpu_post(
        component_cpu=cpu
    )

    pprint(res)

    #client.call_api(
    #    resource_path="v1/component/cpu",
    #    method="POST",
    #    path_params=None,
    #    query_params=[("verbose", "true")],
    #    post_params={
    #        "core_units": 24,
    #        "family": "Skylake",
    #        "manufacture_date": 2017
    #    }
    #    #post_params=[
    #    #    ("core_units", 24),
    #    #    ("family", "Skylake"),
    #    #    ("manufacture_date", 2017)
    #    #]
    #)

if __name__ == '__main__':
    main()
