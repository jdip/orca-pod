#!/usr/bin/env bash
set -euo pipefail

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
python_command=${ORCA_POD_PYTHON:-python3}
resolver="$script_dir/selection-state.py"
if [[ ! -f "$resolver" ]]; then
  echo "error: shared selection resolver is missing: $resolver" >&2
  exit 1
fi
exec "$python_command" "$resolver" --kind "$kind" "$@"
