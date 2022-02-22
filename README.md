# 👩🏻‍💻 Hackaton 4

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

Proof of concept using [BOAVIZTAPI](https://github.com/Boavizta/Tools-API).

## :fast_forward: Request BOAVIZTAPI

* See the OpenAPI specification: <http://api.boavizta.org:5000/docs>

* [Documentation](http://api.boavizta.org/)

* Access the demo API: <http://api.boavizta.org:5000>

## :fast_forward: Run BOAVIZTAPI

### :whale: Run API using docker

```bash
$ docker run ghcr.io/boavizta/boaviztapi:latest
```

### 📦 Install using pip package

```bash
$ pip3 install boaviztapi
```


## :fast_forward: Dev BOAVIZTAPI

### Prerequisite

Python 3, pipenv recommended

### Setup pipenv

Install pipenv globally

```bash
$ sudo pip3 install pipenv
```

Install dependencies and create a python virtual environment.

```bash
$ pipenv install -d 
$ pipenv shell
```

### Launch a development server

**Once in the pipenv environment**

Development server uses [uvicorn](https://www.uvicorn.org/) and [fastapi](https://fastapi.tiangolo.com/), you can launch development server with the `uvicorn` CLI.

```bash
$ uvicorn boaviztapi.main:app --host=localhost --port 5000
```

You can run the tests with `pytest`.

## :scroll: License

MIT
