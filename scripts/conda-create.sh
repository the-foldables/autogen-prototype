#!/bin/bash -e
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
REPO_DIR=$(realpath ${SCRIPT_DIR}/..)
pushd ${REPO_DIR}
source .env.development.local

# Create and activate a new conda environment:
conda create --name autogen_env python=3.12
conda activate autogen_env

# Install packages (on Mac):
python -m pip install -r requirements.txt
brew install libomp
