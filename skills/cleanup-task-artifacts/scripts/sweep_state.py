#!/usr/bin/env python3
"""Report what changed since the previous daily sweep, then keep this sweep's findings for the next one.

The input is a JSON object mapping each finding's stable key (for example `worktree:<id>` or
`discovery:<root>`) to its concise disposition. The previous sweep's findings live in one small file
under the Git common directory; an unreadable file is reported, never silently replaced. One run at a
time holds the directory's lock from reading the previous findings until the new ones replace them.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import secrets
import stat
import subprocess
import sys

STATE_DIRECTORY = 'orca-pod-cleanup-sweep'
STATE_FILE = 'last-sweep.json'
LOCK_FILE = '.lock'
DIRECTORY = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def enter_state_directory():
    """Make the real state directory the working directory, so a later path swap cannot redirect a write."""
    result = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                            check=True, capture_output=True, text=True, timeout=60)
    common = os.open(result.stdout.strip(), DIRECTORY)
    try:
        try:
            os.mkdir(STATE_DIRECTORY, 0o700, dir_fd=common)
        except FileExistsError:
            pass
        directory = os.open(STATE_DIRECTORY, DIRECTORY, dir_fd=common)
    finally:
        os.close(common)
    try:
        details = os.fstat(directory)
        if not stat.S_ISDIR(details.st_mode) or details.st_uid != os.getuid():
            raise ValueError('sweep state path is not a directory this user owns')
        os.fchdir(directory)
    finally:
        os.close(directory)


def regular(descriptor, label):
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise ValueError(f'{label} is not a regular file')
    return descriptor


def findings(text, label):
    def unique(pairs):
        if len({key for key, _ in pairs}) != len(pairs):
            raise ValueError(f'{label} repeats a key')
        return dict(pairs)
    value = json.loads(text, object_pairs_hook=unique)
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
        raise ValueError(f'{label} must be a JSON object of string keys and string dispositions')
    return value


def update(current):
    enter_state_directory()
    lock = regular(os.open(LOCK_FILE, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600), 'sweep state lock')
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        try:
            descriptor = os.open(STATE_FILE, os.O_RDONLY | os.O_NOFOLLOW)
        except FileNotFoundError:
            previous = None
        else:
            with os.fdopen(regular(descriptor, 'sweep state file'), encoding='utf-8') as handle:
                previous = findings(handle.read(), 'previous sweep state')
        before = previous or {}
        changes = {
            'first_sweep': previous is None,
            'new': {key: value for key, value in current.items() if key not in before},
            'changed': {key: {'before': before[key], 'now': value}
                        for key, value in current.items() if key in before and before[key] != value},
            'gone': {key: value for key, value in before.items() if key not in current},
        }
        temporary = f'.pending-{secrets.token_hex(8)}'
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
                json.dump(current, handle, indent=2, sort_keys=True)
                handle.write('\n')
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, STATE_FILE)
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
        return changes
    finally:
        os.close(lock)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('findings', type=Path, help="this sweep's findings JSON file, or - for stdin")
    args = parser.parse_args()
    try:
        text = sys.stdin.read() if str(args.findings) == '-' else args.findings.read_text(encoding='utf-8')
        print(json.dumps(update(findings(text, 'findings')), indent=2))
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f'sweep state: {error}; report every finding as changed\n')
