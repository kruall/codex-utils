#!/usr/bin/env bash
set -e

pushd "$(dirname "$0")" >/dev/null

./init_venv >/dev/null
source .venv/bin/activate
python task-manager/task_manager.py "$@"

popd >/dev/null