#!/usr/bin/env bash

pytest -vs utils/
python -m unittest discover -s object_detection -p "*_test.py"

