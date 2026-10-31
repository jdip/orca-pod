#!/usr/bin/env bash
# Render the private engineering-brief archive with its package-owned dependency.
set -euo pipefail
# Refuse a Python older than .python-version's minimum; scripts/check_source.py keeps the copies in step.
python_minimum=3.14
python=${ORCA_POD_PYTHON:-python3}
if ! "$python" -c 'import sys; sys.exit(sys.version_info < tuple(map(int, sys.argv[1].split("."))))' "$python_minimum" 2>/dev/null; then
  printf '%s: %s is not Python %s or newer; set ORCA_POD_PYTHON to one, for example: export ORCA_POD_PYTHON="$(uv python find %s)"\n' \
    "${0##*/}" "$python" "$python_minimum" "$python_minimum" >&2
  exit 1
fi

skill_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
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
# Rebuild the environment when its Python version differs from the selected interpreter's.
version='import sys; print(*sys.version_info[:3], sep=".")'
if [[ ! -x "$venv_dir/bin/python" || "$("$venv_dir/bin/python" -c "$version" 2>/dev/null)" != "$("$python" -c "$version")" ]]; then
  "$python" -m venv --clear "$venv_dir"
fi
PIP_DISABLE_PIP_VERSION_CHECK=1 "$venv_dir/bin/pip" install --quiet --require-hashes --requirement "$skill_dir/requirements.txt"

exec "$venv_dir/bin/python" "$skill_dir/scripts/render.py" "$@"
