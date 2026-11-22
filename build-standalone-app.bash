#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pushd "$SCRIPT_DIR" > /dev/null

cleanup() {
    popd > /dev/null
}
trap cleanup EXIT

if command -v pyinstaller >/dev/null 2>&1; then
    PYINSTALLER_PATH="$(command -v pyinstaller)"
elif [ -f "$SCRIPT_DIR/.venv/bin/pyinstaller" ]; then
    PYINSTALLER_PATH="$SCRIPT_DIR/.venv/bin/pyinstaller"
else
    echo "PyInstaller was not found. Activate the project's virtual environment or install PyInstaller first."
    exit 1
fi

"$PYINSTALLER_PATH" \
    --onefile \
    --name PrivvyCeeDev \
    --collect-all textual \
    --add-data "src/css:src/css" \
    main.py

echo "Build completed successfully."