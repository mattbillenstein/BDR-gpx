#!/bin/bash

set -eo pipefail

cd "$(dirname "$0")/.."

rm -fR .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
