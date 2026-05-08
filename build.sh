#!/bin/bash

# $1 : choosed version

if [ -z ${1} ]
then
  echo "You need to give the version number as an input (format: X.Y.Z)."
  exit 1
fi

sed -i "s#version = .*#version = \"${1}\"#" pyproject.toml

sed -i "s#project_version: str = .*#project_version: str = '${1}'#" boagent/api/config.py

git add pyproject.toml boagent/api/config.py

git commit -m "chore: preparing release v${1}"

git push

git tag "v${1}"

git push --tags

rm dist/*

python -m build

python3 -m twine upload --repository testpypi dist/*
