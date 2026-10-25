#!/usr/bin/env python3
"""Check imported skills and the Standard for Agent Team leftovers, manual-only frontmatter and upstream licenses."""
from pathlib import Path
import re
import sys

ROOTS = ('skills', 'standard')
SCRIPTS = ('.py', '.sh')  # A `$name` there is a shell variable, not a skill sigil.
# A `codex/` path segment inside a URL or path is Codex the product, not a branch prefix.
BRANCH = re.compile(r'(?<![\w/.-])codex/')
ROUTE = re.compile(r'(?i:herdr)|\bPI_CODING_AGENT_DIR\b|\bpi-fast\b|\b(?:On|When) Pi\b')
MANUAL = re.compile(r'^\s*allow_implicit_invocation:\s*false\s*$', re.M)
FRONTMATTER = re.compile(r'\A---\n(.*?)\n---\n', re.S)
UPSTREAM = re.compile(r'^\| `([\w-]+)` \|', re.M)


def main():
    packages = sorted(path for path in Path('skills').iterdir() if path.is_dir())
    names = {path.name for path in packages} | {'roster'}
    sigil = re.compile(r'\$(' + '|'.join(sorted(map(re.escape, names), key=len, reverse=True)) + r')(?![\w-])')
    failures = []
    for root in ROOTS:
        for path in sorted(Path(root).rglob('*')):
            if not path.is_file() or path.name == 'LICENSE':
                continue
            try:
                text = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                problems = [label for label, pattern in (('codex/ branch reference', BRANCH),
                                                         ('Pi/Herdr delegation route', ROUTE))
                            if pattern.search(line)]
                if path.suffix not in SCRIPTS and sigil.search(line):
                    problems.append('$skill sigil')
                failures += [f'{path}:{number}: {problem}' for problem in problems]
    upstream = set(UPSTREAM.findall(Path('skills/UPSTREAM.md').read_text(encoding='utf-8')))
    for package in packages:
        derived = package.name in upstream or any(
            'github.com/mattpocock/skills' in path.read_text(encoding='utf-8', errors='replace')
            for path in package.glob('SKILL.md'))
        if derived and not (package / 'LICENSE').is_file():
            failures.append(f'{package}: upstream-derived package lacks LICENSE')
        manifest = package / 'agents' / 'openai.yaml'
        if manifest.is_file() and MANUAL.search(manifest.read_text(encoding='utf-8')):
            match = FRONTMATTER.match((package / 'SKILL.md').read_text(encoding='utf-8'))
            if not match or not re.search(r'^disable-model-invocation:\s*true\s*$', match[1], re.M):
                failures.append(f'{package}: manual-only package lacks disable-model-invocation: true')
    for name in sorted(upstream - names):
        failures.append(f'skills/UPSTREAM.md: {name} has no package')
    for failure in failures:
        print(f'Skill check failed: {failure}', file=sys.stderr)
    if not failures:
        print(f'Skill checks passed for {len(packages)} package(s).')
    return not failures


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
