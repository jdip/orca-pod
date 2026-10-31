#!/usr/bin/env bash
set -euo pipefail
# Refuse a Python older than .python-version's minimum; scripts/check_source.py keeps the copies in step.
python_minimum=3.14
python=${ORCA_POD_PYTHON:-python3}
if ! "$python" -c 'import sys; sys.exit(sys.version_info < tuple(map(int, sys.argv[1].split("."))))' "$python_minimum" 2>/dev/null; then
  printf '%s: %s is not Python %s or newer; set ORCA_POD_PYTHON to one, for example: export ORCA_POD_PYTHON="$(uv python find %s)"\n' \
    "${0##*/}" "$python" "$python_minimum" "$python_minimum" >&2
  exit 1
fi
cd "$(git rev-parse --show-toplevel)"
exec "$python" scripts/delivery.py pr-to-test "$@"
