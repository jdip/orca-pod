#!/usr/bin/env bash
# Render the private engineering-brief archive with its package-owned dependency.
set -euo pipefail

skill_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
python_bin=${ORCA_POD_PYTHON:-python3}
common_dir=$(git rev-parse --path-format=absolute --git-common-dir)
archive_dir="$common_dir/orca-pod-engineering-brief"

if [[ -L "$archive_dir" ]]; then
  printf 'render: preserve symlinked archive; resolve its ownership first\n' >&2
  exit 1
fi
if [[ -e "$archive_dir" && ! -d "$archive_dir" ]]; then
  printf 'render: archive path is not a directory\n' >&2
  exit 1
fi

"$python_bin" -c 'import sys; sys.exit("render: Python 3.11 or newer is required") if sys.version_info < (3, 11) else None'
if [[ ! -d "$archive_dir" ]]; then
  printf 'render: no existing archive; save a completed report first\n' >&2
  exit 1
fi
venv_dir="$archive_dir/.render-venv"
tmp_dir="$archive_dir/.render-tmp"
if [[ -L "$venv_dir" || -L "$tmp_dir" ]]; then
  printf 'render: preserve symlinked render environment\n' >&2
  exit 1
fi
# Keep everything the render writes inside the archive: no bytecode beside the skill, no pip cache, archive temp.
mkdir -p -m 700 "$tmp_dir"
export PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 TMPDIR="$tmp_dir"
if [[ ! -x "$venv_dir/bin/python" ]]; then
  "$python_bin" -m venv "$venv_dir"
fi
"$venv_dir/bin/python" -c 'import sys; sys.exit("render: existing environment requires Python 3.11 or newer") if sys.version_info < (3, 11) else None'
PIP_DISABLE_PIP_VERSION_CHECK=1 "$venv_dir/bin/pip" install --quiet --require-hashes --requirement "$skill_dir/requirements.txt"

exec "$venv_dir/bin/python" "$skill_dir/scripts/render.py" "$@"
