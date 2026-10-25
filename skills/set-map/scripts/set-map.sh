#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
python_command=${ORCA_POD_PYTHON:-python3}
resolver="$script_dir/selection-state.py"
if [[ ! -f "$resolver" ]]; then
  echo "error: shared selection resolver is missing: $resolver" >&2
  exit 1
fi
exec "$python_command" "$resolver" --kind map "$@"
