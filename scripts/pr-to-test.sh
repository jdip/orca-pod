#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
exec "${ORCA_POD_PYTHON:-python3}" scripts/delivery.py pr-to-test "$@"
