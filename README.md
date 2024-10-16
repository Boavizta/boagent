<p align="center">
    <img src="https://github.com/Boavizta/boagent/blob/main/boagent_color.svg" height="100">
</p>
<h3 align="center">
  Local API / sidecar / companion of a running application that computes and gives insights to the application regarding its environmental impacts.
</h3>

---

_If no parameters are passed to the API to isolate the application, then the impact of the whole machine is calculated._

## How to use

This is an API, you could use either your browser, cURL, or call it directly from an application (which is the main usecase).

Once the API is running, a Swagger interface is available on [localhost:8000/docs](http://localhost:8000/docs).


### Run natively

Boagent will not be able to return proper responses from its endpoints without root privileges in order to fetch hardware data.
It also needs information from BoaviztAPI and Scaphandre, see the [setup informations](#Setup).

To run it :

Without `poetry`

```
apt update && apt install lshw nvme-cli -y
pip3 install -r requirements.txt
cd boagent/api/
uvicorn api:app --reload
```

With `poetry`

```
apt update && apt install lshw nvme-cli -y
poetry install --only main
poetry run uvicorn --reload boagent.api.api:app
```

### Run in a docker container

You could pull the [image](https://github.com/Boavizta/boagent/pkgs/container/boagent) with `docker pull ghcr.io/boavizta/boagent:0.1.0`.

### Run in docker-compose (with all the requirements)

To get started you need docker and docker-compose installed on your machine. On a Debian or Ubuntu environment, run :

    # apt update && apt install -y docker.io docker-compose

To get the full setup easily, you could run the stack in docker-compose with `docker-compose up -d`. `docker-compose.yml`, at the root of the project will build a Docker image from the source for Boagent, and setup a container for [Scaphandre](#Scaphandre) and another for the [BoaviztAPI](#BoaviztAPI), allowing you to get the full evaluation easily on a physical machine.

Please see [Configuration](#Configuration) for the environment variables you can tweak in the Boagent container.

### Use `hardware_cli`

To have an example of the retrieved hardware information by Boagent, you can run `sudo ./hardware_cli.py`.
At the moment, it will output the formatted data for CPU, RAM and storage devices used by Boagent when sending a request to BoaviztAPI.
`sudo ./hardware_cli.py --output-file <file>` can send the formatted output to a file.

## Setup

## Linux

Boagent parses output from `lshw` (a tool listing hardware components and characteristics) and `nvme-cli` (a tool listing information on SSD storage
devices available through NVME interfaces). To get all actually parsed information (and for future developments), Boagent needs those two programs and to execute them with root privileges.

### BoaviztAPI

You need either to use an existing BoaviztAPI endpoint, or to build the BoaviztAPI container image, then run the container locally on port 5000.

Depending or your setup, specify the endpoint to be used with the environment variable `BOAVIZTAPI_ENDPOINT`, see [Configuration](#Configuration).

Ensure that the version of BoaviztAPI SDK installed (see `requirements.txt` or `pyproject.toml`) is the same as the version of the API running the endpoint you use.

### Scaphandre

To get power consumption metrics, you need [Scaphandre](https://github.com/hubblo-org/scaphandre) running in the background, with the JSON exporter. This will write power metrics to a file, that Boagent will read :

```
scaphandre json -s 5 -f power_data.json
```

## Configuration

Boagent can be configured with the following variables :

- `DEFAULT_LIFETIME`: machines lifetime used to compute the scope 3 / manufacturing, transport, end-of-life impacts
- `HARDWARE_FILE_PATH`: path to the file containing the hardware list (output from `lshw.py`)
- `POWER_FILE_PATH`: path to the file containing power measurements (output from [Scaphandre](https://github.com/hubblo-org/scaphandre) with JSON exporter)
- `HARDWARE_CLI`: path to the executable file to collect hardware information (`lshw.py` from this project)
- `BOAVIZTAPI_ENDPOINT`: HTTP endpoint to the BoaviztAPI, in the form `http://myendpoint.com:PORTNUMBER`

You can set those variables in the following order (as interpreted by the tool):

1. export the variable in the environment
2. write it in the .env file in the same folder as `api.py`
3. rely on default values from `config.py`

You can check the configuration applied by querying the `/info` route.

## How it works

Currently, Boagent only works for Linux systems.

Boagent exposes multiple API endpoints, most notably `/query` and `/metrics`. Both will query an instance of [BoaviztAPI](https://doc.api.boavizta.org/) in order to give the environmental impacts
of the received hardware data. `/query` will return a response in JSON format, and `/metrics` will return a response parsable by a Prometheus instance. If needed, both those
endpoints can return data from [Scaphandre](https://github.com/hubblo-org/scaphandre/) and give the energy consumption of components from the queried hardware.

Presently, Boagent gets hardware data through a parsing of the output of `lshw`, a common utility available for Linux distributions that lists a lot of information of all
hardware components on a running computer. The code for this `Lshw` class is an adaptation of [netbox-agent](https://github.com/Solvik/netbox-agent)'s implementation.
`lshw`, to get all proper data needed by BoaviztAPI, needs to be executed as a privileged user with `sudo`. Boagent, executed with the available `docker-compose` file,
will run as privileged and will be able to receive the needed hardware data. At the moment, only data for the CPU, RAM and storage (either HDD or SSD) are parsed and sent to BoaviztAPI
in order to calculate impacts.

Another endpoint, `process_embedded_impacts`, allows to calculate the embedded impacts of a process running on the host, in relation to the host components (CPU, RAM and storage). It will give, for all the components, the average, maximum and minimum values between two timestamps for three environmental impact factors : Global Warming Potential (in KgCO2e), Abiotic Depletion Potential (in KgSbeq) and Primary Energy (in microjoules). To get these informations, a Linux Process ID has to be provided.

## Deeper explanations

### Environmental metrics

This project uses the Life Cycle Assessment (ISO 14040 / 14044) methodology as a reference.

This way, it is intended to evaluate the impacts on all life cycle phases (extraction, manufacturing, shipping, use, end of life). **Today we only evaluate manufacturing and use phases.**

Here are the impacts considered so far :

- Green House Gas emissions / Global Warming Potential (see GHG protocol as a reference)
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
