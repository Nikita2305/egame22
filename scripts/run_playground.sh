#!/bin/bash
ROOT="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; cd .. ; pwd -P )"
export PYTHONPATH=${PYTHONPATH}:$ROOT
python3 $ROOT/playground/playground.py
