#!/usr/bin/env bash
# Full source checks, or targeted ones with check_source.py's --base/--feature; the skill and privacy checks always run.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
"${ORCA_POD_PYTHON:-python3}" scripts/check_source.py "$@"
"${ORCA_POD_PYTHON:-python3}" scripts/check_skills.py
"${ORCA_POD_PYTHON:-python3}" scripts/check_secrets.py
