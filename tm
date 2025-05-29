#!/usr/bin/env bash
set -euo pipefail

# Ensure we return to the original directory even if a command fails
cleanup() {
    popd >/dev/null || true
}

pushd "$(dirname "$0")" >/dev/null
trap cleanup EXIT

./init_venv >/dev/null
source .venv/bin/activate
python task-manager/task_manager.py "$@"

