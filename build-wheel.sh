#!/bin/bash

# cd to the script's directory
cd "$(dirname "$0")"

# Activate virtual env
. ./venv/bin/activate

# Clean build directory
rm -r ./dist

# Actually build the wheel
python -m build