#!/bin/bash

docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate -i /local/openapi.json -g python -o /local/python-client
