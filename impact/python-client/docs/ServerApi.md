# openapi_client.ServerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**server_get_all_archetype_name_v1_server_all_default_models_get**](ServerApi.md#server_get_all_archetype_name_v1_server_all_default_models_get) | **GET** /v1/server/all_default_models | Server Get All Archetype Name
[**server_impact_by_config_v1_server_post**](ServerApi.md#server_impact_by_config_v1_server_post) | **POST** /v1/server/ | Server Impact By Config
[**server_impact_by_model_v1_server_model_get**](ServerApi.md#server_impact_by_model_v1_server_model_get) | **GET** /v1/server/model | Server Impact By Model


# **server_get_all_archetype_name_v1_server_all_default_models_get**
> bool, date, datetime, dict, float, int, list, str, none_type server_get_all_archetype_name_v1_server_all_default_models_get()

Server Get All Archetype Name

# ✔️Get all the available server models Return the name of all pre-registered server models

### Example


```python
import time
import openapi_client
from openapi_client.api import server_api
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = server_api.ServerApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Server Get All Archetype Name
        api_response = api_instance.server_get_all_archetype_name_v1_server_all_default_models_get()
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServerApi->server_get_all_archetype_name_v1_server_all_default_models_get: %s\n" % e)
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

# **server_impact_by_config_v1_server_post**
> bool, date, datetime, dict, float, int, list, str, none_type server_impact_by_config_v1_server_post()

Server Impact By Config

# ✔️Server impacts from configuration Retrieve the impacts of a given server configuration. ### 💡 Smart complete All missing components and components attributes are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the impacts of each components and the value used for each attributes   ### 📋 Archetype An archetype is a pre-registered server model. An ```archetype``` can be specify in the model object. In case an archetype is specified, all missing data are retrieve from the archetype. You can have a list of available archetype's server models [here](#/server/server_get_all_archetype_name_v1_server_all_default_models_get)   ### ⏲ Duration Usage impacts are given for a specific time duration. Duration can be given in : | time unit | Usage parameter | |------|-----| | HOURS | ```hours_use_time``` | | DAYS | ```days_use_time``` | | YEARS | ```years_use_time``` | If no duration is given, **the impact is measured for a year**. *Note* : units are cumulative ### 🧮 Measure 🔨 Manufacture impacts are the sum of the components impacts  🔌 Usage impacts are measured by multiplying : * a **duration**  * an **impact factor** (```gwp_factor```, ```pe_factor```, ```adp_factor```) - retrieve with ```usage_location``` if not given  * an **electrical consumption** (```hours_electrical_consumption```) - retrieve with ```workload``` if not given

### Example


```python
import time
import openapi_client
from openapi_client.api import server_api
from openapi_client.model.server_dto import ServerDTO
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
    api_instance = server_api.ServerApi(api_client)
    verbose = True # bool |  (optional) if omitted the server will use the default value of True
    server_dto = ServerDTO(
        model=ModelServer(
            manufacturer="manufacturer_example",
            name="name_example",
            type="type_example",
            year="year_example",
            archetype="archetype_example",
        ),
        configuration=ConfigurationServer(
            cpu=Cpu(
                units=1,
                core_units=1,
                die_size=3.14,
                die_size_per_core=3.14,
                process=3.14,
                manufacturer="manufacturer_example",
                manufacture_date="manufacture_date_example",
                model="model_example",
                family="family_example",
            ),
            ram=[
                Ram(
                    units=1,
                    capacity=1,
                    density=3.14,
                    process=3.14,
                    manufacturer="manufacturer_example",
                    manufacture_date="manufacture_date_example",
                    model="model_example",
                    integrator="integrator_example",
                ),
            ],
            disk=[
                Disk(
                    units=1,
                    type="type_example",
                    capacity=1,
                    density=3.14,
                    manufacturer="manufacturer_example",
                    manufacture_date="manufacture_date_example",
                    model="model_example",
                ),
            ],
            power_supply=PowerSupply(
                units=1,
                unit_weight=3.14,
            ),
        ),
        usage=UsageServer(
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
        ),
        add_method="add_method_example",
        add_date="add_date_example",
    ) # ServerDTO |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Server Impact By Config
        api_response = api_instance.server_impact_by_config_v1_server_post(verbose=verbose, server_dto=server_dto)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServerApi->server_impact_by_config_v1_server_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **server_dto** | [**ServerDTO**](ServerDTO.md)|  | [optional]

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

# **server_impact_by_model_v1_server_model_get**
> bool, date, datetime, dict, float, int, list, str, none_type server_impact_by_model_v1_server_model_get()

Server Impact By Model

# ✔️Server impacts from model name Retrieve the impacts of a given server name (archetype). ### 📋 Model Uses the [classic server impacts router](#/server/server_impact_by_config_v1_server__post) with a pre-registered model  ### 👄 Verbose If set at true, shows the impacts of each components and the value used for each attributes   ### 📋 Model name You can have a list of available server models names [here](#/server/server_get_all_archetype_name_v1_server_all_default_models_get)   ### 🧮 Measure 🔨 Manufacture impacts are the sum of the pre-registered components impacts  🔌 Usage impacts are measured based on the electrical consumption of the pre-registered model for a year 

### Example


```python
import time
import openapi_client
from openapi_client.api import server_api
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
    api_instance = server_api.ServerApi(api_client)
    archetype = "dellR740" # str |  (optional)
    verbose = True # bool |  (optional) if omitted the server will use the default value of True

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Server Impact By Model
        api_response = api_instance.server_impact_by_model_v1_server_model_get(archetype=archetype, verbose=verbose)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ServerApi->server_impact_by_model_v1_server_model_get: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **archetype** | **str**|  | [optional]
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

