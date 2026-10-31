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

usage() {
  cat <<'EOF'
usage: select.sh {map|backlog} <command> [options]

Manage an explicitly scoped, task-owned selection: map selects a Wayfinder map
(wayfinder:map), backlog an implementation backlog (implementation:backlog).
Each scope keeps independent map and backlog entries with their own owner and
generation.

Run "select.sh <kind> --help" for the commands, and
"select.sh <kind> <command> --help" for a command's options.
EOF
}

case "${1:-}" in
  map | backlog)
    kind=$1
    shift
    ;;
  -h | --help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
resolver="$script_dir/selection-state.py"
if [[ ! -f "$resolver" ]]; then
  echo "error: shared selection resolver is missing: $resolver" >&2
  exit 1
fi
exec "$python" "$resolver" --kind "$kind" "$@"
