#!/usr/bin/env python3
"""Report what changed since the previous daily sweep, then keep this sweep's findings for the next one.

The input is a JSON object mapping each finding's stable key (for example `worktree:<id>` or
`discovery:<root>`) to its concise disposition. The previous sweep's findings live in one small file
under the Git common directory; an unreadable file is reported, never silently replaced.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

STATE_DIRECTORY = 'orca-pod-cleanup-sweep'
STATE_FILE = 'last-sweep.json'


def state_path():
    result = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                            check=True, capture_output=True, text=True, timeout=60)
    common = Path(result.stdout.strip())
    if common.is_symlink() or not common.is_dir():
        raise ValueError('Git common directory is not a real directory')
    directory = common / STATE_DIRECTORY
    if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
        raise ValueError('sweep state path is not a real directory')
    return directory / STATE_FILE


def findings(text, label):
    value = json.loads(text)
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
        raise ValueError(f'{label} must be a JSON object of string keys and string dispositions')
    return value


def update(current):
    path = state_path()
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError('sweep state file is not a regular file')
    previous = findings(path.read_text(encoding='utf-8'), 'previous sweep state') if path.exists() else None
    before = previous or {}
    changes = {
        'first_sweep': previous is None,
        'new': {key: value for key, value in current.items() if key not in before},
        'changed': {key: {'before': before[key], 'now': value}
                    for key, value in current.items() if key in before and before[key] != value},
        'gone': {key: value for key, value in before.items() if key not in current},
    }
    path.parent.mkdir(exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            json.dump(current, handle, indent=2, sort_keys=True)
            handle.write('\n')
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return changes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('findings', type=Path, help="this sweep's findings JSON file, or - for stdin")
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if str(args.findings) == '-' else args.findings.read_text(encoding='utf-8')
        print(json.dumps(update(findings(text, 'findings')), indent=2))
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f'sweep state: {error}; report every finding as changed\n')
