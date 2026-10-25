#!/usr/bin/env python3
"""Read-only discovery from supported project roots supplied by the supervising agent."""
import argparse
import json
from pathlib import Path
import re
import subprocess

SOURCE = 'https://github.com/jdip/orca-pod'


def declaration(text):
    if text.count('<!--') != text.count('-->'):
        raise ValueError('ambiguous or unclosed Markdown comment')
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    starts = [i for i, line in enumerate(lines) if line.strip() == '## Repository Standard']
    if len(starts) != 1:
        raise ValueError('missing or ambiguous Repository Standard section')
    body = []
    for line in lines[starts[0]+1:]:
        if re.match(r'^#{1,2}\s', line):
            break
        body.append(line)
    sources = [match[1].strip() for line in body if (match := re.fullmatch(r'- Source:\s*(.+)', line))]
    revisions = [match[1].strip() for line in body if (match := re.fullmatch(r'- Revision:\s*(.+)', line))]
    if len(sources) != 1 or sources[0].removesuffix('/').removesuffix('.git') != SOURCE:
        raise ValueError('missing, ambiguous, or wrong Orca Pod source')
    if len(revisions) != 1 or not re.fullmatch(r'[0-9a-f]{40}', revisions[0]):
        raise ValueError('missing or malformed full adopted revision')
    return revisions[0]


def discover(roots):
    verified = {}
    for supplied in dict.fromkeys(roots):
        root = Path(supplied).expanduser().absolute()
        result = {'root': str(root), 'eligible': False}
        try:
            if root.is_symlink() or not root.is_dir():
                raise ValueError('root is missing or indirect')
            instructions = root / 'AGENTS.md'
            if instructions.is_symlink() or not instructions.is_file():
                raise ValueError('root AGENTS.md is missing or indirect')
            revision = declaration(instructions.read_text(encoding='utf-8'))
            if revision not in verified:
                response = subprocess.run(['gh', 'api', f'repos/jdip/orca-pod/commits/{revision}', '--jq', '.sha'],
                                          capture_output=True, text=True)
                verified[revision] = response.returncode == 0 and response.stdout.strip() == revision
            if not verified[revision]:
                raise ValueError('revision could not be verified in the trusted source repository')
            result.update(eligible=True, revision=revision)
        except (OSError, UnicodeError, ValueError) as error:
            result['reason'] = str(error)
        print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('roots', nargs='+', help='exact known project roots; no recursive filesystem discovery')
    discover(parser.parse_args().roots)
