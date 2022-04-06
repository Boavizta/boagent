# openapi_client.ComponentApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**case_impact_bottom_up_v1_component_case_post**](ComponentApi.md#case_impact_bottom_up_v1_component_case_post) | **POST** /v1/component/case | Case Impact Bottom Up
[**cpu_impact_bottom_up_v1_component_cpu_post**](ComponentApi.md#cpu_impact_bottom_up_v1_component_cpu_post) | **POST** /v1/component/cpu | Cpu Impact Bottom Up
[**disk_impact_bottom_up_v1_component_hdd_post**](ComponentApi.md#disk_impact_bottom_up_v1_component_hdd_post) | **POST** /v1/component/hdd | Disk Impact Bottom Up
[**disk_impact_bottom_up_v1_component_ssd_post**](ComponentApi.md#disk_impact_bottom_up_v1_component_ssd_post) | **POST** /v1/component/ssd | Disk Impact Bottom Up
[**motherboard_impact_bottom_up_v1_component_motherboard_post**](ComponentApi.md#motherboard_impact_bottom_up_v1_component_motherboard_post) | **POST** /v1/component/motherboard | Motherboard Impact Bottom Up
[**power_supply_impact_bottom_up_v1_component_power_supply_post**](ComponentApi.md#power_supply_impact_bottom_up_v1_component_power_supply_post) | **POST** /v1/component/power_supply | Power Supply Impact Bottom Up
[**ram_impact_bottom_up_v1_component_ram_post**](ComponentApi.md#ram_impact_bottom_up_v1_component_ram_post) | **POST** /v1/component/ram | Ram Impact Bottom Up


# **case_impact_bottom_up_v1_component_case_post**
> bool, date, datetime, dict, float, int, list, str, none_type case_impact_bottom_up_v1_component_case_post()

Case Impact Bottom Up

# ✔️Case impacts from configuration ### 💡 Smart complete All missing data are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the the values used for each attribute*Components have no units since they represent a single instance of a component.* ### 🧮 Measure The impacts values are set by default

### Example


```python
import time
import openapi_client
from openapi_client.api import component_api
from openapi_client.model.case import Case
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
    api_instance = component_api.ComponentApi(api_client)
    verbose = True # bool |  (optional) if omitted the server will use the default value of True
    case = Case(
        units=1,
        case_type="case_type_example",
    ) # Case |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Case Impact Bottom Up
        api_response = api_instance.case_impact_bottom_up_v1_component_case_post(verbose=verbose, case=case)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->case_impact_bottom_up_v1_component_case_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **case** | [**Case**](Case.md)|  | [optional]

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

# **cpu_impact_bottom_up_v1_component_cpu_post**
> bool, date, datetime, dict, float, int, list, str, none_type cpu_impact_bottom_up_v1_component_cpu_post()

Cpu Impact Bottom Up

# ✔️CPU impacts from configuration ### 💡 Smart complete All missing data are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the the values used for each attribute*Components have no units since they represent a single instance of a component.* ### 🧮 Measure <h3>cpu<sub>manuf<sub><em>criteria</em></sub></sub> = ( cpu<sub>core<sub>units</sub></sub> x cpu<sub>diesize</sub> + 0,491 ) x cpu<sub>manuf_die<sub><em>criteria</em></sub></sub> + cpu<sub>manuf_base<sub><em>criteria</em></sub></sub></h3> 

### Example


```python
import time
import openapi_client
from openapi_client.api import component_api
from openapi_client.model.http_validation_error import HTTPValidationError
from openapi_client.model.cpu import Cpu
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = component_api.ComponentApi(api_client)
    verbose = True # bool |  (optional) if omitted the server will use the default value of True
    cpu = Cpu(
        units=1,
        core_units=1,
        die_size=3.14,
        die_size_per_core=3.14,
        process=3.14,
        manufacturer="manufacturer_example",
        manufacture_date="manufacture_date_example",
        model="model_example",
        family="family_example",
    ) # Cpu |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Cpu Impact Bottom Up
        api_response = api_instance.cpu_impact_bottom_up_v1_component_cpu_post(verbose=verbose, cpu=cpu)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->cpu_impact_bottom_up_v1_component_cpu_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **cpu** | [**Cpu**](Cpu.md)|  | [optional]

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

# **disk_impact_bottom_up_v1_component_hdd_post**
> bool, date, datetime, dict, float, int, list, str, none_type disk_impact_bottom_up_v1_component_hdd_post()

Disk Impact Bottom Up

# ✔️HDD impacts from configuration ### 💡 Smart complete All missing data are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the the values used for each attribute*Components have no units since they represent a single instance of a component.* ### 🧮 Measure The impacts values are set by default

### Example


```python
import time
import openapi_client
from openapi_client.api import component_api
from openapi_client.model.disk import Disk
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
    api_instance = component_api.ComponentApi(api_client)
    verbose = True # bool |  (optional) if omitted the server will use the default value of True
    disk = Disk(
        units=1,
        type="type_example",
        capacity=1,
        density=3.14,
        manufacturer="manufacturer_example",
        manufacture_date="manufacture_date_example",
        model="model_example",
    ) # Disk |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Disk Impact Bottom Up
        api_response = api_instance.disk_impact_bottom_up_v1_component_hdd_post(verbose=verbose, disk=disk)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->disk_impact_bottom_up_v1_component_hdd_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **disk** | [**Disk**](Disk.md)|  | [optional]

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

# **disk_impact_bottom_up_v1_component_ssd_post**
> bool, date, datetime, dict, float, int, list, str, none_type disk_impact_bottom_up_v1_component_ssd_post()

Disk Impact Bottom Up

# ✔️SSD impacts from configuration ### 💡 Smart complete All missing data are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the the values used for each attribute*Components have no units since they represent a single instance of a component.* ### 🧮 Measure <h3>ssd<sub>manuf<sub><em>criteria</em></sub></sub> =  ( ssd<sub>size</sub> ssd<sub>density</sub> ) x ssd<sub>manuf_die<sub><em>criteria</em></sub></sub> + ssd<sub>manuf_base<sub><em>criteria</em></sub></sub></h3> 

### Example


```python
import time
import openapi_client
from openapi_client.api import component_api
from openapi_client.model.disk import Disk
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
    api_instance = component_api.ComponentApi(api_client)
    verbose = True # bool |  (optional) if omitted the server will use the default value of True
    disk = Disk(
        units=1,
        type="type_example",
        capacity=1,
        density=3.14,
        manufacturer="manufacturer_example",
        manufacture_date="manufacture_date_example",
        model="model_example",
    ) # Disk |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Disk Impact Bottom Up
        api_response = api_instance.disk_impact_bottom_up_v1_component_ssd_post(verbose=verbose, disk=disk)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->disk_impact_bottom_up_v1_component_ssd_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **disk** | [**Disk**](Disk.md)|  | [optional]

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

# **motherboard_impact_bottom_up_v1_component_motherboard_post**
> bool, date, datetime, dict, float, int, list, str, none_type motherboard_impact_bottom_up_v1_component_motherboard_post()

Motherboard Impact Bottom Up

# ✔️Motherboard impacts from configuration ### 💡 Smart complete All missing data are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the the values used for each attribute*Components have no units since they represent a single instance of a component.* ### 🧮 Measure The impacts values are set by default

### Example


```python
import time
import openapi_client
from openapi_client.api import component_api
from openapi_client.model.http_validation_error import HTTPValidationError
from openapi_client.model.mother_board import MotherBoard
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = component_api.ComponentApi(api_client)
    verbose = True # bool |  (optional) if omitted the server will use the default value of True
    mother_board = MotherBoard(
        units=1,
    ) # MotherBoard |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Motherboard Impact Bottom Up
        api_response = api_instance.motherboard_impact_bottom_up_v1_component_motherboard_post(verbose=verbose, mother_board=mother_board)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->motherboard_impact_bottom_up_v1_component_motherboard_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **mother_board** | [**MotherBoard**](MotherBoard.md)|  | [optional]

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

# **power_supply_impact_bottom_up_v1_component_power_supply_post**
> bool, date, datetime, dict, float, int, list, str, none_type power_supply_impact_bottom_up_v1_component_power_supply_post()

Power Supply Impact Bottom Up

# ✔️Power supply impacts from configuration ### 💡 Smart complete All missing data are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the the values used for each attribute*Components have no units since they represent a single instance of a component.* ### 🧮 Measure <h3>psu<sub>manuf<sub><em>criteria</em></sub></sub> = psu<sub>unit<sub>weight</sub></sub> x psu<sub>manuf_weight<sub><em>criteria</em></sub></sub></h3> 

### Example


```python
import time
import openapi_client
from openapi_client.api import component_api
from openapi_client.model.http_validation_error import HTTPValidationError
from openapi_client.model.power_supply import PowerSupply
from pprint import pprint
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = component_api.ComponentApi(api_client)
    verbose = True # bool |  (optional) if omitted the server will use the default value of True
    power_supply = PowerSupply(
        units=1,
        unit_weight=3.14,
    ) # PowerSupply |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Power Supply Impact Bottom Up
        api_response = api_instance.power_supply_impact_bottom_up_v1_component_power_supply_post(verbose=verbose, power_supply=power_supply)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->power_supply_impact_bottom_up_v1_component_power_supply_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **power_supply** | [**PowerSupply**](PowerSupply.md)|  | [optional]

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

# **ram_impact_bottom_up_v1_component_ram_post**
> bool, date, datetime, dict, float, int, list, str, none_type ram_impact_bottom_up_v1_component_ram_post()

Ram Impact Bottom Up

# ✔️RAM impacts from configuration ### 💡 Smart complete All missing data are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the the values used for each attribute*Components have no units since they represent a single instance of a component.* ### 🧮 Measure <h3>ram<sub>manuf<sub><em>criteria</em></sub></sub> =( ram<sub>size</sub> / ram<sub>density</sub> ) x ram<sub>manuf_die<sub><em>criteria</em></sub></sub> + ram<sub>manuf_base<sub><em>criteria</em></sub></sub> </h3> 

### Example


```python
import time
import openapi_client
from openapi_client.api import component_api
from openapi_client.model.ram import Ram
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
    api_instance = component_api.ComponentApi(api_client)
    verbose = True # bool |  (optional) if omitted the server will use the default value of True
    ram = Ram(
        units=1,
        capacity=1,
        density=3.14,
        process=3.14,
        manufacturer="manufacturer_example",
        manufacture_date="manufacture_date_example",
        model="model_example",
        integrator="integrator_example",
    ) # Ram |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Ram Impact Bottom Up
        api_response = api_instance.ram_impact_bottom_up_v1_component_ram_post(verbose=verbose, ram=ram)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->ram_impact_bottom_up_v1_component_ram_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **ram** | [**Ram**](Ram.md)|  | [optional]

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

