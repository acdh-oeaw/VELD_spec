#!/bin/bash

cp README.md veld_spec/
python -m build
twine upload dist/*
rm -rf dist
rm -rf ./*.egg-info
