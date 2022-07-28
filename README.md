# Boagent

Local API / sidecar / companion of a running application that computes and gives insights to the application regarding its environmental impacts. If no parameters are passed to the API to isolate the application, then the impact of the whole machine is calculated.

## How to use

This is an API, you could use either your browser, curl, or call it directly from an application (which is the main usecase).

Once the API is running, a Swagger interface is available on localhost:8000/docs.

### Run natively

To run it :

```
cd boagent/
pip3 install -r requirements.txt
cd api/
uvicorn api:app --reload
```

The app can run without root privileges, but you won't get full data about the RAM and get some warnings.
Run as root to have the best evaluation possible.

### Run in docker-compose (with all the requirements)

To get the full setup easily, you could run the stack in docker-compose. `docker-compose.yml`, at the root of the project will build a docker image from the source for boagent, and setup a container for [Scaphandre](#Scaphandre) and another for the [BoaviztAPI](#BoaviztAPI), allowing you to get the full evaluation easily on a physical machine.

Please see [Configuration](#Configuration) for the environment variables you can tweak in the Boagent container.

## Setup required

### BoaviztAPI

You need either to use an existing BoaviztAPI endpoint, or to build the BoaviztAPI container image, then run the container locally on port 5000.

Depending or your setup, specify the endpoint to be used with the environment variable `BOAVIZTAPI_ENDPOINT`, see [Configuration](#Configuration).

Ensure that the version of BoaviztAPI SDK installed (see `requirements.txt`) is the same as the version of the API running the endpoint you use.

### Scaphandre

To get power consumption metrics, you need [Scaphandre](https://github.com/hubblo-org/scaphandre) runnig in the background, with the json exporter. This will write power metrics to a file, that Boagent will read :

```
scaphandre json -s 5 -f power_data.json
```

## Configuration

Boagent can be configured with the following variables :

- `DEFAULT_LIFETIME`: machines lifetime used to compute the scope 3 / manufacturing, transport, end of life impacts
- `HARDWARE_FILE_PATH`: path to the file containing the hardware list (output from hardware.py)
- `POWER_FILE_PATH`: path to the file containing power mearsurements (output from [Scaphandre](https://github.com/hubblo-org/scaphandre) with JSON exporter)
- `HARDWARE_CLI`: path to the executable file to collect hardware information (hardware.py from this project)
- `BOAVIZTAPI_ENDPOINT`: http endpoint to the BoaviztAPI, in the form `http://myendpoint.com:PORTNUMBER`

You can set those variables in the following order (as interpreted by the tool):

1. export the variable in the environment
2. write it in the .env file in the same folder as `api.py`
3. rely on default values from `config.py`

You can check the configuration applied by querying the `/info` route.

## Deeper explanations

### Environmental metrics

This project uses the Life Cycle Assessment (ISO 14040 / 14044) methodology as a reference.

This way, it is intended to evaluate the impacts on all life cycle phases (extraction, manufacturing, shipping, use, end of life). **Today we only evaluate manufacturing and use phases.**

Here are the impacts considered so far :

- Green House Gaz emissions / Global Warming Potential (see GHG protocol as a reference)
    - resources extraction (LCA) / scope 3 (GHG protocol) ✔️
    - use (LCA) / scope 2 (GHG protocol) ✔️
    - manufacturing (LCA) / scope 3 (GHG protocol) ✔️
    - shipping (LCA) / scope 3 (GHG protocol) ❌
    - end of life (LCA) / scope 3 (GHG protocol) ❌
- Abiotic ressources depletion (minerals), criteria called ADP or Abiotic Depletion Potential
    - resources extraction (LCA) ✔️
    - use (LCA) ✔️
    - manufacturing (LCA) ✔️
    - shipping (LCA) ❌
    - end of life (LCA) ❌
- Primary energy usage : PE
    - resources extraction (LCA) ✔️
    - use (LCA) ✔️
    - manufacturing (LCA) ✔️
    - shipping (LCA) ❌
    - end of life (LCA) ❌
