#!/bin/bash
ROOT="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; cd .. ; pwd -P )"
export PYTHONPATH=${PYTHONPATH}:$ROOT
python3 -m unittest -v $ROOT/tests/model.py
