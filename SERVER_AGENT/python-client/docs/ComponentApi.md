# openapi_client.ComponentApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**case_impact_bottom_up_v1_component_case_post**](ComponentApi.md#case_impact_bottom_up_v1_component_case_post) | **POST** /v1/component/case | Case Impact Bottom Up
[**cpu_impact_bottom_up_v1_component_cpu_post**](ComponentApi.md#cpu_impact_bottom_up_v1_component_cpu_post) | **POST** /v1/component/cpu | Cpu Impact Bottom Up
[**hdd_impact_bottom_up_v1_component_hdd_post**](ComponentApi.md#hdd_impact_bottom_up_v1_component_hdd_post) | **POST** /v1/component/hdd | Hdd Impact Bottom Up
[**motherboard_impact_bottom_up_v1_component_motherboard_post**](ComponentApi.md#motherboard_impact_bottom_up_v1_component_motherboard_post) | **POST** /v1/component/motherboard | Motherboard Impact Bottom Up
[**power_supply_impact_bottom_up_v1_component_power_supply_post**](ComponentApi.md#power_supply_impact_bottom_up_v1_component_power_supply_post) | **POST** /v1/component/power_supply | Power Supply Impact Bottom Up
[**ram_impact_bottom_up_v1_component_ram_post**](ComponentApi.md#ram_impact_bottom_up_v1_component_ram_post) | **POST** /v1/component/ram | Ram Impact Bottom Up
[**ssd_impact_bottom_up_v1_component_ssd_post**](ComponentApi.md#ssd_impact_bottom_up_v1_component_ssd_post) | **POST** /v1/component/ssd | Ssd Impact Bottom Up


# **case_impact_bottom_up_v1_component_case_post**
> bool, date, datetime, dict, float, int, list, str, none_type case_impact_bottom_up_v1_component_case_post()

Case Impact Bottom Up

# ✔️Case impacts from configuration ### 💡 Smart complete All missing data are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the the values used for each attribute*Components have no units since they represent a single instance of a component.* ### 🧮 Measure The impacts values are set by default

### Example


```python
import time
import openapi_client
from openapi_client.api import component_api
from openapi_client.model.component_case import ComponentCase
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
    component_case = ComponentCase(
        hash="hash_example",
        type="CASE",
        case_type="case_type_example",
    ) # ComponentCase |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Case Impact Bottom Up
        api_response = api_instance.case_impact_bottom_up_v1_component_case_post(verbose=verbose, component_case=component_case)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->case_impact_bottom_up_v1_component_case_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **component_case** | [**ComponentCase**](ComponentCase.md)|  | [optional]

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
from openapi_client.model.component_cpu import ComponentCPU
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
    component_cpu = ComponentCPU(
        hash="hash_example",
        type="CPU",
        core_units=1,
        die_size=3.14,
        die_size_per_core=3.14,
        process=3.14,
        manufacturer="manufacturer_example",
        manufacture_date="manufacture_date_example",
        model="model_example",
        family="family_example",
    ) # ComponentCPU |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Cpu Impact Bottom Up
        api_response = api_instance.cpu_impact_bottom_up_v1_component_cpu_post(verbose=verbose, component_cpu=component_cpu)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->cpu_impact_bottom_up_v1_component_cpu_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **component_cpu** | [**ComponentCPU**](ComponentCPU.md)|  | [optional]

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

# **hdd_impact_bottom_up_v1_component_hdd_post**
> bool, date, datetime, dict, float, int, list, str, none_type hdd_impact_bottom_up_v1_component_hdd_post()

Hdd Impact Bottom Up

# ✔️HDD impacts from configuration ### 💡 Smart complete All missing data are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the the values used for each attribute*Components have no units since they represent a single instance of a component.* ### 🧮 Measure The impacts values are set by default

### Example


```python
import time
import openapi_client
from openapi_client.api import component_api
from openapi_client.model.http_validation_error import HTTPValidationError
from openapi_client.model.component_hdd import ComponentHDD
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
    component_hdd = ComponentHDD(
        hash="hash_example",
        type="HDD",
        capacity=1,
        manufacturer="manufacturer_example",
        manufacture_date="manufacture_date_example",
        model="model_example",
    ) # ComponentHDD |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Hdd Impact Bottom Up
        api_response = api_instance.hdd_impact_bottom_up_v1_component_hdd_post(verbose=verbose, component_hdd=component_hdd)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->hdd_impact_bottom_up_v1_component_hdd_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **component_hdd** | [**ComponentHDD**](ComponentHDD.md)|  | [optional]

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
from openapi_client.model.component_mother_board import ComponentMotherBoard
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
    component_mother_board = ComponentMotherBoard(
        hash="hash_example",
        type="MOTHERBOARD",
    ) # ComponentMotherBoard |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Motherboard Impact Bottom Up
        api_response = api_instance.motherboard_impact_bottom_up_v1_component_motherboard_post(verbose=verbose, component_mother_board=component_mother_board)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->motherboard_impact_bottom_up_v1_component_motherboard_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **component_mother_board** | [**ComponentMotherBoard**](ComponentMotherBoard.md)|  | [optional]

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
from openapi_client.model.component_power_supply import ComponentPowerSupply
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
    component_power_supply = ComponentPowerSupply(
        hash="hash_example",
        type="POWER_SUPPLY",
        unit_weight=3.14,
    ) # ComponentPowerSupply |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Power Supply Impact Bottom Up
        api_response = api_instance.power_supply_impact_bottom_up_v1_component_power_supply_post(verbose=verbose, component_power_supply=component_power_supply)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->power_supply_impact_bottom_up_v1_component_power_supply_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **component_power_supply** | [**ComponentPowerSupply**](ComponentPowerSupply.md)|  | [optional]

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
from openapi_client.model.component_ram import ComponentRAM
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
    component_ram = ComponentRAM(
        hash="hash_example",
        type="RAM",
        capacity=1,
        density=3.14,
        process=3.14,
        manufacturer="manufacturer_example",
        manufacture_date="manufacture_date_example",
        model="model_example",
        integrator="integrator_example",
    ) # ComponentRAM |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Ram Impact Bottom Up
        api_response = api_instance.ram_impact_bottom_up_v1_component_ram_post(verbose=verbose, component_ram=component_ram)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->ram_impact_bottom_up_v1_component_ram_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **component_ram** | [**ComponentRAM**](ComponentRAM.md)|  | [optional]

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

# **ssd_impact_bottom_up_v1_component_ssd_post**
> bool, date, datetime, dict, float, int, list, str, none_type ssd_impact_bottom_up_v1_component_ssd_post()

Ssd Impact Bottom Up

# ✔️SSD impacts from configuration ### 💡 Smart complete All missing data are retrieve with the closest available values. If no data are available default maximizing data are used  ### 👄 Verbose If set at true, shows the the values used for each attribute*Components have no units since they represent a single instance of a component.* ### 🧮 Measure <h3>ssd<sub>manuf<sub><em>criteria</em></sub></sub> =  ( ssd<sub>size</sub> ssd<sub>density</sub> ) x ssd<sub>manuf_die<sub><em>criteria</em></sub></sub> + ssd<sub>manuf_base<sub><em>criteria</em></sub></sub></h3> 

### Example


```python
import time
import openapi_client
from openapi_client.api import component_api
from openapi_client.model.http_validation_error import HTTPValidationError
from openapi_client.model.component_ssd import ComponentSSD
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
    component_ssd = ComponentSSD(
        hash="hash_example",
        type="SSD",
        capacity=1,
        density=3.14,
        manufacturer="manufacturer_example",
        manufacture_date="manufacture_date_example",
        model="model_example",
    ) # ComponentSSD |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Ssd Impact Bottom Up
        api_response = api_instance.ssd_impact_bottom_up_v1_component_ssd_post(verbose=verbose, component_ssd=component_ssd)
        pprint(api_response)
    except openapi_client.ApiException as e:
        print("Exception when calling ComponentApi->ssd_impact_bottom_up_v1_component_ssd_post: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **verbose** | **bool**|  | [optional] if omitted the server will use the default value of True
 **component_ssd** | [**ComponentSSD**](ComponentSSD.md)|  | [optional]

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

