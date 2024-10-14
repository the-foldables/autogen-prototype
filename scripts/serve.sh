#!/bin/bash -e
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
REPO_DIR=$(realpath ${SCRIPT_DIR}/..)
pushd ${REPO_DIR}
source .env.development.local

panel serve main.py
