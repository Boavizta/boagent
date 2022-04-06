#!/bin/bash

rm -f openapi.json
wget http://localhost:5000/openapi.json
docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate -i /local/openapi.json -g python -o /local/python-client
