# Boagent

Local API / sidecar / companion of a running application that computes and gives insights to the application regarding its environmental impacts. If no parameters are passed to the API to isolate the application, then the impact of the whole machine is calculated.

## How to use

This is an API, you could use either your browser, curl, or call it directly from an application (which is the main usecase).

Once the API is running, a Swagger interface is available on localhost:8000/docs.

To run it :

```
cd api/
pip3 install -r requirements.txt
uvicorn api:app --reload
```

## How to setup

### BoaviztAPI

You need to build the BoaviztAPI container image, then run the container locally on port 5000.

Look at the BoaviztAPI for the setup.


### BoaviztaAPI SDK

Once the BoaviztAPI is running, the generate.sh script will download the new openapi.json definition and generate the client lib :

```
cd impact
bach generate.sh
```

Generate and install the lib as a pip package :

```
cd impact/python-client
bash build.sh
```

### Scaphandre TO BE IMPROVED

Pour obtenir les données de puissance et d'énergie, il faut lancer scaphandre en arrière plan avec l'exporter json en écrivant les données dans un fichier, dans le même dossier que celui depuis lequel vous avez lancé l'API:

```
scaphandre json -s 5 -t 9999999999 -f power_data.json
```

Une feature doit être publiée prochainement dans scaphandre pour ne pas avoir à ajouter un timeout avec l'option `-t`. En attendant, vous pouvez compiler le binaire depuis la branche `feature/#169-allow-json-exporter-to-run-as-a-daemon` de scaphandre.

## Deeper explanations

### Environmental metrics

This project uses the Life Cycle Assessment (ISO 14040 / 14044) methodology as a reference.

This way, it is intended to evaluate the impacts on all life cycle phases (extraction, manufacturing, shipping, use, end of life). **Today we only evaluate manufacturing and use phases.**

Here are the impacts considered so far :

- Green House Gaz emissions / Global Warming Potential (see GHG protocol as a reference)
    - resources extraction (LCA) / scope 3 (GHG protocol) ❌
    - use (LCA) / scope 2 (GHG protocol) ✔️
    - manufacturing (LCA) / scope 3 (GHG protocol) ✔️
    - shipping (LCA) / scope 3 (GHG protocol) ❌
    - end of life (LCA) / scope 3 (GHG protocol) ❌
- Abiotic ressources depletion (minerals), criteria called ADP or Abiotic Depletion Potential
    - resources extraction (LCA) ❌
    - use (LCA) ❌
    - manufacturing (LCA) 🚧
    - shipping (LCA) ❌
    - end of life (LCA) ❌
- Primary energy usage : PE
    - resources extraction (LCA) ❌
    - use (LCA) ❌
    - manufacturing (LCA) 🚧
    - shipping (LCA) ❌
    - end of life (LCA) ❌

# Historic README from the #4th hackathon of @Boavizta

# 👩🏻‍💻 Hackaton 4 - Proof of concept using BOAVIZTAPI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## :dart: Objective

As part of Boavizta's desire to improve the quality of the measurement of the environmental impacts of ICTs in organizations, boaviztapi project aims at giving access to the group's work to as many people as possible in an automated and industrialized way.

The various data and methodologies integrated by Boavizta are aggregated and made available via an API.

The objectif of the hackaton is to implement proof of concept of [use cases](https://github.com/Boavizta/Hackaton_4/issues) calling the boaviztapi.


## :fast_forward: Request BOAVIZTAPI

* See the OpenAPI specification: <http://hackaton.boavizta.org:5000/docs>

* [Documentation](http://hackaton.boavizta.org/)

* Access the demo API: <http://hackaton.boavizta.org:5000>


## :scroll: License

MIT
