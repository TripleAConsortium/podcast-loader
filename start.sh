#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Using: $0 <name> <path>"
    exit 1
fi

source .venv/bin/activate
python3 script.py $1 $2