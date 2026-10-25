#!/usr/bin/env python3
"""Check imported skills and the Standard for Agent Team leftovers, manual-only frontmatter and upstream licenses."""
from pathlib import Path
import re
import sys

ROOTS = ('skills', 'standard')
# Skills referenced without a package here: external ones and retired Agent Team ones.
UNPACKAGED = ('openai-docs', 'workflow-refresh', 'cleanup-schedule')
# A `codex/` segment starting a token or following a Git ref prefix (origin/, refs/heads/) is a branch.
BRANCH = re.compile(r'(?<![\w-])codex/')
# Only Codex product URLs and the `.codex/` config directory may carry that segment.
PRODUCT = re.compile(r'(?:https?://)?(?:(?:[\w-]+\.)*openai\.com/(?:[\w.~-]+/)*|github\.com/openai/)\Z|(?:.*/)?\.\Z')
TOKEN = re.compile(r'[\s<>(\[`"\']')
RUNTIME = re.compile(r'(?i:herdr)|\bPI_CODING_AGENT_DIR\b|\bpi-fast\b')
PI = re.compile(r'\bPi\b|(?i:\b(?:to|via|through|ask|use)\s+pi\b)')
# Pi remains only as a research source cited in the engineering brief.
SOURCES = 'skills/engineering-brief/references/sources.md'
RESEARCH = re.compile(r'\| .*\]\(https://(?:mariozechner\.at|github\.com/earendil-works/pi)/?\)')
DELEGATE = re.compile(r'(?i)dispatch|delegat|hand(?:s|ed|ing)?[ -]?off|\brout|\bsend|spawn|review')
MANUAL = re.compile(r'^\s*allow_implicit_invocation:\s*false\s*$', re.M)
FRONTMATTER = re.compile(r'\A---\n(.*?)\n---\n', re.S)
UPSTREAM = re.compile(r'^\| `([\w-]+)` \|', re.M)


def branch(line):
    return any(not PRODUCT.match(TOKEN.split(line[:match.start()])[-1]) for match in BRANCH.finditer(line))


def route(path, line):
    retained = path.as_posix() == SOURCES and RESEARCH.match(line) and not DELEGATE.search(line)
    return bool(RUNTIME.search(line) or (PI.search(line) and not retained))


def shell_variables(path, text, names):
    """Return skill names a shell script assigns as variables; elsewhere a `$name` is always a sigil."""
    if path.suffix != '.sh':
        return set()
    return {name for name in names if re.fullmatch(r'[A-Za-z_]\w*', name) and re.search(
        rf'(?m)(?<![\w$-]){name}=|\bfor\s+{name}\s+in\b|^\s*(?:local|declare|readonly|export|read)\b[^\n#]*(?<![\w$-]){name}\b',
        text)}


def main():
    packages = sorted(path for path in Path('skills').iterdir() if path.is_dir())
    names = {path.name for path in packages}
    skills = names | {'roster', *UNPACKAGED}
    sigil = re.compile(r'\$(' + '|'.join(sorted(map(re.escape, skills), key=len, reverse=True)) + r')(?![\w-])')
    failures = []
    for root in ROOTS:
        for path in sorted(Path(root).rglob('*')):
            if not path.is_file() or path.name == 'LICENSE':
                continue
            try:
                text = path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            variables = shell_variables(path, text, skills)
            for number, line in enumerate(text.splitlines(), 1):
                problems = [label for label, found in (('codex/ branch reference', branch(line)),
                                                       ('Pi/Herdr delegation route', route(path, line)))
                            if found]
                if any(match[1] not in variables for match in sigil.finditer(line)):
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
