#!/bin/bash

set -eo pipefail

if [ "$1" == "--clean" ]; then
  git clean -xdf
  scripts/venv.sh
fi

cd "$(dirname "$0")/.."

source .venv/bin/activate
pyinstaller --onefile --add-data elevation-api.key:. bdr-gpx.py

# windows
# .venv\Scripts\activate.bat
# pyinstaller --onefile --add-data elevation-api.key;. bdr-gpx.py

OS="$(uname -s | tr '[:upper:]' '[:lower:]' | sed -e 's/darwin/macos/')"
ARCH="$(uname -m | sed -e 's/x86_64/amd64/')"
mv dist/bdr-gpx dist/bdr-gpx-$OS-$ARCH
