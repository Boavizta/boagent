# openapi_client.CloudApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**instance_cloud_impact_v1_cloud_aws_post**](CloudApi.md#instance_cloud_impact_v1_cloud_aws_post) | **POST** /v1/cloud/aws | Instance Cloud Impact
[**server_get_all_archetype_name_v1_cloud_aws_all_instances_get**](CloudApi.md#server_get_all_archetype_name_v1_cloud_aws_all_instances_get) | **GET** /v1/cloud/aws/all_instances | Server Get All Archetype Name


# **instance_cloud_impact_v1_cloud_aws_post**
> bool, date, datetime, dict, float, int, list, str, none_type instance_cloud_impact_v1_cloud_aws_post()

Instance Cloud Impact

# ✔️AWS instance impacts from instance type and usage  ### 📋 Instance type  AWS name of the chosen instance. You can retrieve the [list here](#/cloud/server_get_all_archetype_name_v1_cloud_all_aws_instances_get). ### 👄 Verbose If set at true, shows the impacts of each components and the value used for each attributes    ### ⏲ Duration Usage impacts are given for a specific time duration. Duration can be given : | time unit | Usage parameter | |------|-----| | HOURS | ```hours_use_time``` | | DAYS | ```days_use_time``` | | YEARS | ```years_use_time``` | *Note* : units are cumulative ### 🧮 Measure  🔨 Manufacture impacts are the sum of the pre-registered components impacts divided by the number of instances host in the physicall server  🔌 Usage impacts are measured by multiplying : * a **duration**  * an **impact factor** (```gwp_factor```, ```pe_factor```, ```adp_factor```) - retrieve with ```usage_location``` if not given  * The ```time``` per load in ```workload``` object. The ```power``` per load is retreive from the ```instance_type```

### Example


```python
import time
import openapi_client
from openapi_client.api import cloud_api
from openapi_client.model.usage_cloud import UsageCloud
from openapi_client.model.http_validation_error import HTTPValidationError
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = cloud_api.CloudApi(api_client)
    instance_type = "a1.4xlarge" # str |  (optional)
    verbose = True # bool |  (optional) if omitted the server will use the default value of True
    usage_cloud = UsageCloud(
        hash="hash_example",
        type="USAGE",
        years_use_time=3.14,
        days_use_time=3.14,
        hours_use_time=3.14,
        hours_electrical_consumption=3.14,
        usage_location="usage_location_example",
        gwp_factor=3.14,
        pe_factor=3.14,
        adp_factor=3.14,
        max_power=3.14,
        workload={
            "key": {
                "key": 3.14,
            },
        },
        instance_per_server=3.14,
    ) # UsageCloud |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Instance Cloud Impact
        api_response = api_instance.instance_cloud_impact_v1_cloud_aws_post(instance_type=instance_type, verbose=verbose, usage_cloud=usage_cloud)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CloudApi->instance_cloud_impact_v1_cloud_aws_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **instance_type** | **str**|  | [optional]
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **usage_cloud** | [**UsageCloud**](UsageCloud.md)|  | [optional]

### Return type

**bool, date, datetime, dict, float, int, list, str, none_type**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **server_get_all_archetype_name_v1_cloud_aws_all_instances_get**
> bool, date, datetime, dict, float, int, list, str, none_type server_get_all_archetype_name_v1_cloud_aws_all_instances_get()

Server Get All Archetype Name

# ✔️Get all the available aws instances Return the name of all pre-registered aws instances

### Example


```python
import time
import openapi_client
from openapi_client.api import cloud_api
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = cloud_api.CloudApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Server Get All Archetype Name
        api_response = api_instance.server_get_all_archetype_name_v1_cloud_aws_all_instances_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling CloudApi->server_get_all_archetype_name_v1_cloud_aws_all_instances_get: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

**bool, date, datetime, dict, float, int, list, str, none_type**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

