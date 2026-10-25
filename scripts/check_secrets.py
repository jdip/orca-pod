#!/usr/bin/env python3
"""Reject recognizable credentials and personal home paths in the Git index."""
from pathlib import PurePosixPath
import re
import subprocess
import sys


FORBIDDEN_NAMES = {'auth.json', 'cookies.json', 'credentials.json', '.env'}
PATTERNS = {
    'OpenAI-style API key': rb'\bsk-[A-Za-z0-9_-]{20,}\b',
    'GitHub token': rb'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b',
    'Slack token': rb'\bxox[baprs]-[A-Za-z0-9-]{20,}\b',
    'AWS access key': rb'\bAKIA[A-Z0-9]{16}\b',
    'absolute home path': rb'/(?:Users|home)/[A-Za-z0-9][A-Za-z0-9._-]*(?:/|\b)',
    'Windows home path': rb'(?i:[a-z]:[\\/]+(?:Users|Documents and Settings)[\\/]+[A-Za-z0-9][A-Za-z0-9._-]*(?:[\\/]|\b))',
    'private key': rb'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----',
}


def main():
    entries = subprocess.check_output(['git', 'ls-files', '--stage', '-z'])
    failed = False
    for entry in entries.split(b'\0'):
        if not entry:
            continue
        metadata, raw_path = entry.split(b'\t', 1)
        mode, oid, stage = metadata.split()
        path = raw_path.decode('utf-8', errors='backslashreplace')
        if stage != b'0':
            print(f'Unmerged index entry: {path!r}', file=sys.stderr)
            failed = True
            continue
        if PurePosixPath(path).name.lower() in FORBIDDEN_NAMES:
            print(f'Credential filename in index: {path!r}', file=sys.stderr)
            failed = True
        if mode == b'160000':
            continue  # A submodule has its own repository and checks.
        content = subprocess.check_output(['git', 'cat-file', 'blob', oid.decode('ascii')])
        for category, pattern in PATTERNS.items():
            if re.search(pattern, content):
                print(f'Possible {category} in index: {path!r}', file=sys.stderr)
                failed = True
    if failed:
        return 1
    print('Git index credential and personal-path checks passed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
