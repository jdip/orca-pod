#!/usr/bin/env python3
"""Native Python/TOML/shell syntax checks: every relevant file, or only those HEAD changes versus --base."""
import argparse
import ast
from pathlib import Path
import re
import subprocess
import sys
import tomllib

ROOTS = ('skills', 'machine', 'scripts', 'roster')
SUFFIXES = ('.toml', '.py', '.sh')
REGULAR = (b'100644', b'100755')  # Symlinks and submodules carry no checked source.


def check(path, content):
    """Return False after reporting one syntax failure."""
    try:
        if path.endswith('.toml'):
            tomllib.loads(content.decode('utf-8'))
        elif path.endswith('.py'):
            ast.parse(content, filename=path)
        else:
            subprocess.run(['bash', '-n'], input=content, check=True)
        return True
    except (ValueError, SyntaxError, subprocess.CalledProcessError) as error:
        print(f'Syntax check failed: {path!r}: {error}', file=sys.stderr)
        return False


def git(*args):
    return subprocess.run(['git', *args], check=True, stdout=subprocess.PIPE).stdout


def commit_sha(value):
    if not re.fullmatch(r'[0-9a-f]{40}', value):
        raise argparse.ArgumentTypeError('expected a full 40-character commit SHA')
    return value


def full():
    passed = True
    for root in ROOTS:
        for suffix in SUFFIXES:
            for path in Path(root).rglob(f'*{suffix}'):
                passed &= check(path.as_posix(), path.read_bytes())
    if passed:
        print('Source syntax checks passed. Operational evidence remains required.')
    return passed


def targeted(base, feature):
    """Check committed blobs HEAD adds or modifies versus base; with feature, HEAD must merge exactly base and feature."""
    head = git('rev-parse', '--verify', 'HEAD^{commit}').decode().strip()
    header = git('cat-file', 'commit', head).split(b'\n\n', 1)[0].splitlines()
    parents = [line.split()[1].decode() for line in header if line.startswith(b'parent ')]
    tree = header[0].split()[1].decode()
    if feature and parents != [base, feature]:
        raise ValueError(f'HEAD {head} parents {" ".join(parents) or "none"} are not base {base} and feature {feature}')
    print(f'Targeted checks on {head} tree {tree}; parents {" ".join(parents)}; changes versus {base}', flush=True)
    subprocess.run(['git', 'diff', '--check', base, head], check=True)
    # Raw -z output keeps every path byte intact; without rename detection a rename is a delete plus an add.
    fields = git('diff', '--raw', '-z', '--no-renames', '--no-abbrev', base, head).split(b'\0')
    passed, checked = True, 0
    for metadata, raw_path in zip(fields[0::2], fields[1::2]):
        _, mode, _, oid, status = metadata[1:].split()
        path = raw_path.decode('utf-8', errors='backslashreplace')
        if (status == b'D' or mode not in REGULAR or not path.endswith(SUFFIXES)
                or not any(path.startswith(f'{root}/') for root in ROOTS)):
            continue
        passed &= check(path, git('cat-file', 'blob', oid.decode('ascii')))
        checked += 1
    if passed:
        print(f'Targeted syntax and whitespace checks passed for {checked} changed source file(s) versus {base}. '
              'Full Validate runs on the delivery PR.')
    return passed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=commit_sha, help='check only committed changes from this commit to HEAD')
    parser.add_argument('--feature', type=commit_sha, help='require HEAD to be the merge of --base and this commit')
    args = parser.parse_args()
    if args.feature and not args.base:
        parser.error('--feature requires --base')
    return 0 if (targeted(args.base, args.feature) if args.base else full()) else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, subprocess.CalledProcessError) as error:
        print(f'Source checks stopped: {error}', file=sys.stderr)
        sys.exit(1)
