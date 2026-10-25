#!/usr/bin/env python3
"""Install Orca Pod into the default agent homes on macOS; see docs/install.md.

--dry-run (the default) prints every planned action, diff, conflict and refusal and writes nothing.
--apply installs, recording owned paths and keys in a manifest and backing up anything it replaces.
--uninstall removes what the manifest owns and restores the backups.
"""
import argparse
import copy
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / 'machine' / 'global-rules.md'
ORCA_SETTINGS = ROOT / 'machine' / 'orca_settings.py'
GENERATE = ROOT / 'roster' / 'generate.py'
ROLES = ROOT / 'roster' / 'roles.toml'
STATE = Path('.local/state/orca-pod')
MANIFEST_VERSION = 1

ORCA_SKILLS = ('orca-cli', 'orchestration')
ORCA_PATCH = {'branchPrefix': 'custom', 'branchPrefixCustom': 'orca'}
# roles.toml has no Codex ORC entry; the Codex coordinator alternative is pinned here (jdip/orca-pod#13).
CODEX_ROOT = {'model': 'gpt-6.1-sol', 'model_reasoning_effort': 'high'}
CODEX_TABLE_KEYS = {'agents': ('enabled', True), 'features': ('hooks', True)}
ORCA_HOOK_MARK = ': orca-agent-hook-form='  # Prefix of every hook command Orca writes to hooks.json.
HOOK_EVENTS = {'pre_tool_use', 'permission_request', 'post_tool_use', 'pre_compact', 'post_compact',
               'pre_model_request', 'post_model_request', 'session_start', 'session_end',
               'user_prompt_submit', 'subagent_start', 'subagent_stop', 'stop', 'interrupt'}
MATCHER_EVENTS = {'pre_tool_use', 'permission_request', 'post_tool_use', 'session_start', 'session_end',
                  'subagent_start', 'subagent_stop', 'pre_compact', 'post_compact'}
CONTEXT_LIMIT_EVENTS = {'pre_tool_use', 'post_tool_use', 'session_start', 'user_prompt_submit', 'subagent_start'}
DEFAULT_CONTEXT_LIMIT = 2500

BEGIN = '# >>> orca-pod managed: {} >>> machine/install.py rewrites this block; edit roster or rerun instead\n'
END = '# <<< orca-pod managed: {} <<<\n'
BEGIN_RE = re.compile(r'# >>> orca-pod managed: (\S+) >>>')
END_RE = re.compile(r'# <<< orca-pod managed: (\S+) <<<')


class Refusal(Exception):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(*cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# ---------- Codex hook trust ----------

def snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def hook_hash(event, matcher, handler):
    """Codex 0.164 `hook_hash`: sha256 of the sorted, compact JSON of the normalized hook identity.

    Codex serializes {event_name, matcher, hooks: [normalized handler]} through TOML (dropping unset
    options) and hashes `serde_json` output with sorted keys; see codex-rs/hooks/src/engine/discovery.rs.
    """
    timeout = handler.get('timeout')
    if event in ('session_end', 'interrupt'):
        timeout = min(max(timeout if timeout is not None else 1, 1), 3)
    else:
        timeout = max(timeout if timeout is not None else 600, 1)
    normalized = {'type': 'command', 'command': handler['command'], 'timeout': timeout,
                  'async': bool(handler.get('async', False))}
    if handler.get('statusMessage') is not None:
        normalized['statusMessage'] = handler['statusMessage']
    limit = handler.get('additionalContextLimit')
    if event in CONTEXT_LIMIT_EVENTS and limit is not None and limit != DEFAULT_CONTEXT_LIMIT:
        normalized['additionalContextLimit'] = limit
    identity = {'event_name': event, 'hooks': [normalized]}
    if matcher is not None and event in MATCHER_EVENTS:
        identity['matcher'] = matcher
    text = json.dumps(identity, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return 'sha256:' + sha(text.encode('utf-8'))


def orca_hook_trust(home, notes):
    """Return {state key: trusted_hash} for every Orca-written command hook in <home>/.codex/hooks.json."""
    path = home / '.codex' / 'hooks.json'
    if not path.exists():
        notes.append('~/.codex/hooks.json is absent, so no Codex hook trust is seeded; '
                     'rerun --apply after Orca installs its hooks')
        return {}
    events = json.loads(path.read_text(encoding='utf-8')).get('hooks', {})
    source = path.resolve()  # Codex keys hook state by the canonical hooks.json path.
    trust = {}
    for name, groups in events.items():
        event = snake(name)
        if event not in HOOK_EVENTS:
            notes.append(f'~/.codex/hooks.json: unknown hook event {name!r} skipped')
            continue
        for gi, group in enumerate(groups):
            for hi, handler in enumerate(group.get('hooks', [])):
                if handler.get('type') == 'command' and handler.get('command', '').startswith(ORCA_HOOK_MARK):
                    trust[f'{source}:{event}:{gi}:{hi}'] = hook_hash(event, group.get('matcher'), handler)
    return trust


# ---------- TOML managed blocks ----------

def single_path(doc):
    """Walk a one-key-per-level dict from tomllib down to its leaf; return (path, leaf)."""
    path = []
    while isinstance(doc, dict) and len(doc) == 1:
        (key, doc), = doc.items()
        path.append(key)
    return tuple(path), doc


def key_path(line):
    """Return the dotted key path a `key = value` line defines."""
    quote, i = None, 0
    while i < len(line):
        ch = line[i]
        if quote == '"' and ch == '\\':
            i += 1  # Skip the escaped character.
        elif quote:
            quote = None if ch == quote else quote
        elif ch in '"\'':
            quote = ch
        elif ch == '=':
            path, _ = single_path(tomllib.loads(line[:i] + '= 0'))
            return path
        i += 1
    raise Refusal(f'cannot parse TOML line {line.strip()!r}')


def statements(lines, table=()):
    """Split TOML lines into (start, end, kind, path) statements; kind is table, array, key or None (trivia)."""
    out, i = [], 0
    while i < len(lines):
        text = lines[i].strip()
        if not text or text.startswith('#'):
            out.append((i, i + 1, None, None))
            i += 1
        elif text.startswith('['):
            table, leaf = single_path(tomllib.loads(lines[i]))
            out.append((i, i + 1, 'array' if isinstance(leaf, list) else 'table', table))
            i += 1
        else:
            path, j = table + key_path(lines[i]), i + 1
            while True:
                try:
                    tomllib.loads(''.join(lines[i:j]))
                    break
                except tomllib.TOMLDecodeError:
                    if j >= len(lines):
                        raise Refusal(f'cannot parse the TOML statement at line {i + 1}')
                    j += 1
            out.append((i, j, 'key', path))
            i = j
    return out


def table_at(stmts, index):
    """The table in effect before base line index."""
    table = ()
    for start, _, kind, path in stmts:
        if start >= index:
            break
        if kind in ('table', 'array'):
            table = path
    return table


def strip_blocks(lines):
    """Remove managed blocks; return (base lines, {name: (base index, inner lines)})."""
    base, blocks, i = [], {}, 0
    while i < len(lines):
        if END_RE.match(lines[i]):
            raise Refusal(f'line {i + 1} closes an orca-pod block that was never opened')
        begin = BEGIN_RE.match(lines[i])
        if not begin:
            base.append(lines[i])
            i += 1
            continue
        name, j = begin[1], i + 1
        while j < len(lines) and not BEGIN_RE.match(lines[j]) and not END_RE.match(lines[j]):
            j += 1
        if j == len(lines) or not END_RE.match(lines[j]) or END_RE.match(lines[j])[1] != name:
            raise Refusal(f'the orca-pod block {name!r} opened at line {i + 1} is not closed')
        if name in blocks:
            raise Refusal(f'the orca-pod block {name!r} appears twice')
        blocks[name] = (len(base), lines[i + 1:j])
        i = j + 1
    return base, blocks


def overlaps(path, managed):
    return path[:len(managed)] == managed or managed[:len(path)] == path


def codex_managed(trust):
    """Managed key paths per block; a hooks.state path owns its whole table."""
    return {'root': [(key,) for key in CODEX_ROOT],
             'agents': [('agents', 'enabled')], 'features': [('features', 'hooks')],
             'hooks.state': [('hooks', 'state', key) for key in trust]}


def owns(kind, path, paths):
    """Whether a statement inside a managed block belongs to it (rather than being foreign)."""
    return kind is not None and any(path[:len(m)] == m or (kind != 'key' and m[:len(path)] == path) for m in paths)


def toml_str(value):
    return json.dumps(value, ensure_ascii=False)  # A JSON string is a valid TOML basic string.


def render_body(name, trust, header):
    if name == 'root':
        return [f'{key} = {toml_str(value)}\n' for key, value in CODEX_ROOT.items()]
    if name in CODEX_TABLE_KEYS:
        key, value = CODEX_TABLE_KEYS[name]
        return ([f'[{name}]\n'] if header else []) + [f'{key} = {str(value).lower()}\n']
    body = []
    for key, value in trust.items():
        body += ['\n'] if body else []
        body += [f'[hooks.state.{toml_str(key)}]\n', 'enabled = true\n', f'trusted_hash = {toml_str(value)}\n']
    return body


def set_path(doc, path, value):
    for key in path[:-1]:
        doc = doc.setdefault(key, {})
    doc[path[-1]] = value


def merge_codex_config(text, trust, old_hook_keys, adopt):
    """Return (new text, conflicts, adopted {block: text}) for config.toml with managed blocks rewritten."""
    tomllib.loads(text)  # Refuse invalid TOML before touching anything.
    lines = text.splitlines(keepends=True)
    base, old_blocks = strip_blocks(lines)
    if base and not base[-1].endswith('\n'):
        base[-1] += '\n'
    stmts = statements(base)
    managed = codex_managed(trust)
    domain = {**managed, 'hooks.state': managed['hooks.state'] + [('hooks', 'state', k) for k in old_hook_keys]}
    conflicts, removed, adopted, first_removed, owned_tables = [], set(), {}, {}, set()
    for start, end, kind, path in stmts:
        if kind is None:
            continue
        for name, paths in managed.items():
            hit = any(path[:len(m)] == m for m in paths) if kind != 'key' else any(overlaps(path, m) for m in paths)
            if hit:
                if kind != 'key':
                    owned_tables.add(path)
                if kind != 'key' or path[:-1] not in owned_tables:  # Report a whole owned table once.
                    conflicts.append((start + 1, ''.join(base[start:end]).rstrip('\n')))
                removed.update(range(start, end))
                adopted[name] = adopted.get(name, '') + ''.join(base[start:end])
                first_removed.setdefault(name, start)
                break
    # Drop blank lines left between two adopted statements, such as the gaps between adopted tables.
    for start, end, kind, _ in stmts:
        if kind is None and not base[start].strip():
            above = [s for s in stmts if s[1] <= start and s[2] is not None]
            below = [s for s in stmts if s[0] >= end and s[2] is not None]
            if above and below and above[-1][0] in removed and below[0][0] in removed:
                removed.add(start)
    if conflicts and not adopt:
        return None, conflicts, {}
    headers = {path: start for start, _, kind, path in stmts if kind == 'table'}
    inserts = {}  # base index -> [(block lines, foreign lines)]
    for name in ('root', 'agents', 'features', 'hooks.state'):
        old_index, inner = old_blocks.get(name, (None, []))
        foreign = []
        for start, end, kind, path in statements(inner, table_at(stmts, old_index or 0)):
            if kind is not None and not owns(kind, path, domain[name]):
                foreign += inner[start:end]
        header = name in CODEX_TABLE_KEYS and (name,) not in headers
        if name in CODEX_TABLE_KEYS and not header:
            index = headers[(name,)] + 1
        elif old_index is not None:
            index = old_index
        elif name in first_removed:
            index = first_removed[name]
        elif name == 'root':  # After any leading comments, before the first statement.
            index = next((start for start, _, kind, _ in stmts if kind is not None), len(base))
        else:
            index = len(base)
        body = render_body(name, trust, header)
        block = [BEGIN.format(name), *body, END.format(name)] if body else []
        inserts.setdefault(index, []).append((block, foreign))

    def assemble(with_blocks):
        out = []
        for i in range(len(base) + 1):
            for block, foreign in inserts.get(i, []):
                out += (block if with_blocks else []) + foreign
            if i < len(base) and i not in removed:
                out.append(base[i])
        return ''.join(out)

    new = assemble(True)
    try:
        expected = tomllib.loads(assemble(False))
        for paths in managed.values():
            for path in paths:
                if path[0] == 'hooks':
                    set_path(expected, path, {'enabled': True, 'trusted_hash': trust[path[2]]})
                elif path[0] in CODEX_TABLE_KEYS:
                    set_path(expected, path, CODEX_TABLE_KEYS[path[0]][1])
                else:
                    set_path(expected, path, CODEX_ROOT[path[0]])
        ok = tomllib.loads(new) == expected
    except tomllib.TOMLDecodeError:
        ok = False
    if not ok:
        raise Refusal('the managed blocks cannot be merged without changing other keys; edit config.toml by hand')
    return new, [], adopted


def unmerge_codex_config(text, adopted, hook_keys):
    """Remove managed blocks, keep foreign statements found inside them and restore adopted originals."""
    base, blocks = strip_blocks(text.splitlines(keepends=True))
    stmts = statements(base)
    domain = {**codex_managed({}), 'hooks.state': [('hooks', 'state', k) for k in hook_keys]}
    inserts = {}
    for name, (index, inner) in blocks.items():
        keep = []
        for start, end, kind, path in statements(inner, table_at(stmts, index)):
            if kind is not None and not owns(kind, path, domain.get(name, [])):
                keep += inner[start:end]
        inserts.setdefault(index, []).append(adopted.get(name, '') + ''.join(keep))
    out = []
    for i in range(len(base) + 1):
        out += inserts.get(i, [])
        if i < len(base):
            out.append(base[i])
    new = ''.join(out)
    tomllib.loads(new)
    return new


# ---------- Planning ----------

class Plan:
    def __init__(self, home, old):
        self.home = home
        self.old = old
        self.ops = []
        self.notes = []
        self.refusals = []

    def show(self, path):
        try:
            return '~/' + Path(path).relative_to(self.home).as_posix()
        except ValueError:
            return str(path)

    def rel(self, path):
        return path.relative_to(self.home).as_posix()


def current_bytes(path):
    """File bytes, or b'symlink:<target>' for a link, or None when absent."""
    if path.is_symlink():
        return b'symlink:' + os.readlink(path).encode()
    if path.is_file():
        return path.read_bytes()
    if path.exists():
        raise Refusal(f'{path} exists and is not a regular file or symlink')
    return None


def text_diff(plan, path, old, new):
    if old is None or old.startswith(b'symlink:') or new.startswith(b'symlink:'):
        return []
    name = plan.show(path)
    return list(difflib.unified_diff(old.decode('utf-8', 'replace').splitlines(),
                                     new.decode('utf-8', 'replace').splitlines(),
                                     f'{name} (current)', f'{name} (planned)', lineterm='', n=2))


def plan_file(plan, group, path, data, mode=0o644, diff=True):
    """Plan one owned whole file (or symlink when data starts with b'symlink:')."""
    rel = plan.rel(path)
    entry = plan.old.get('files', {}).get(rel)
    try:
        cur = current_bytes(path)
    except Refusal as error:
        plan.refusals.append(str(error))
        return
    cur_mode = None if cur is None or path.is_symlink() else path.stat().st_mode & 0o777
    is_link = data.startswith(b'symlink:')
    if cur is None:
        action = 'create'
    elif entry and sha(cur) == entry['sha256']:
        action = 'unchanged' if cur == data and (is_link or cur_mode == mode) else 'update'
    elif entry:
        action = 'update (changed since install; current copy backed up)'
    else:
        action = 'adopt (identical; backed up)' if cur == data and (is_link or cur_mode == mode) \
            else 'replace (backed up)'
    plan.ops.append({'kind': 'file', 'group': group, 'path': path, 'rel': rel, 'data': data, 'mode': mode,
                     'action': action, 'current': cur, 'entry': entry,
                     'diff': text_diff(plan, path, cur, data) if diff and action.startswith(('update', 'replace'))
                     else []})


def plan_skills(plan):
    """Install each tracked skills/<name>/ package holding a SKILL.md, whatever skills/ holds at run time."""
    listed = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z', '--', 'skills'],
                            capture_output=True, check=True).stdout.decode().split('\0')
    files = {}
    for rel in filter(None, listed):
        parts = Path(rel).parts
        if len(parts) > 2 and (ROOT / rel).is_file() and not (ROOT / rel).is_symlink():
            files.setdefault(parts[1], []).append(ROOT / rel)
    skills = sorted(name for name, paths in files.items() if ROOT / 'skills' / name / 'SKILL.md' in paths)
    if not skills:
        plan.notes.append('skills/ holds no skill packages')
    for name in skills:
        skill, dest = ROOT / 'skills' / name, plan.home / '.agents' / 'skills' / name
        if dest.is_symlink():
            plan.refusals.append(f'{plan.show(dest)} is a symlink; refusing to write through it')
            continue
        before = len(plan.ops)
        for src in sorted(files[name]):
            mode = 0o755 if src.stat().st_mode & 0o111 else 0o644
            plan_file(plan, 'skills', dest / src.relative_to(skill), src.read_bytes(), mode, diff=False)
        if dest.is_dir() and not dest.is_symlink():
            ours = {op['path'] for op in plan.ops[before:]}
            extra = [p for p in dest.rglob('*') if p.is_file() and p not in ours
                     and plan.rel(p) not in plan.old.get('files', {})]
            if extra:
                plan.notes.append(f'{plan.show(dest)} holds files Orca Pod does not own, left in place: '
                                  + ', '.join(p.relative_to(dest).as_posix() for p in extra[:5]))
        link = plan.home / '.claude' / 'skills' / name
        target = os.path.relpath(dest, link.parent)
        plan_file(plan, 'skills', link, b'symlink:' + target.encode())


def render_roles():
    check = run(sys.executable, str(GENERATE), '--check')
    if check.returncode:
        raise Refusal('roster tables are stale; run roster/generate.py and commit: ' + check.stderr.strip())
    with tempfile.TemporaryDirectory(prefix='orca-pod-roster-') as tmp:
        result = run(sys.executable, str(GENERATE), '--out', tmp)
        if result.returncode:
            raise Refusal('roster/generate.py failed: ' + (result.stderr or result.stdout).strip())
        return {p.relative_to(tmp).as_posix(): p.read_bytes() for p in Path(tmp).rglob('*') if p.is_file()}


def plan_roles(plan):
    rendered = render_roles()
    for rel, data in sorted(rendered.items()):
        provider, rest = rel.split('/', 1)
        dest = plan.home / ('.claude' if provider == 'claude' else '.codex') / rest
        plan_file(plan, 'roles', dest, data)


def plan_rules(plan):
    data = RULES.read_bytes()
    plan_file(plan, 'global rules', plan.home / '.codex' / 'AGENTS.md', data)
    plan_file(plan, 'global rules', plan.home / '.claude' / 'rules' / 'orca-pod.md', data)


def plan_stale(plan):
    planned = {op['rel'] for op in plan.ops}
    for rel, entry in plan.old.get('files', {}).items():
        if rel not in planned:
            path = plan.home / rel
            plan.ops.append({'kind': 'remove', 'group': 'stale', 'path': path, 'rel': rel, 'entry': entry,
                             'action': 'restore backup' if entry.get('backup') else 'remove'})


def key_entry_base(plan, rel, cur, entry):
    """Shared bookkeeping for a key-managed file: backup pointer, creation and pristine state."""
    if entry:
        pristine = entry['pristine'] and cur is not None and sha(cur) == entry['sha256']
        return {'backup': entry.get('backup'), 'created': entry['created'], 'pristine': pristine}
    return {'backup': None, 'created': cur is None, 'pristine': True}


def plan_json(plan, group, path, sets, defaults):
    rel = plan.rel(path)
    entry = plan.old.get('keys', {}).get(rel)
    if path.is_symlink():
        plan.refusals.append(f'{plan.show(path)} is a symlink; refusing to replace it')
        return
    cur = path.read_bytes() if path.exists() else None
    try:
        data = json.loads(cur) if cur else {}
    except ValueError as error:
        plan.refusals.append(f'{plan.show(path)} is not valid JSON ({error})')
        return
    if not isinstance(data, dict):
        plan.refusals.append(f'{plan.show(path)} is not a JSON object')
        return
    owned = copy.deepcopy(entry['keys']) if entry else {}
    new, changes = dict(data), []
    wanted = dict(sets)
    for key, value in defaults.items():
        if key not in data or data[key] is None or data[key] is False:
            wanted[key] = value
    for key, value in wanted.items():
        owned.setdefault(key, {'had': key in data, 'previous': data.get(key)})['set'] = value
        if key not in data or data[key] != value:
            changes.append(f'set {key} = {json.dumps(value)} (was {json.dumps(data[key]) if key in data else "unset"})')
        new[key] = value
    for key in defaults:
        if key not in wanted and key not in owned:
            plan.notes.append(f'{plan.show(path)}: {key} is already set; left as is')
    if new == data:
        out = cur
    else:
        out = (json.dumps(new, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    if not owned and out == cur:
        return
    plan.ops.append({'kind': 'keys', 'group': group, 'path': path, 'rel': rel, 'data': out, 'current': cur,
                     'action': 'unchanged' if out == cur else ('create' if cur is None else 'update keys'),
                     'changes': changes, 'diff': [],
                     'entry': {'format': 'json', **key_entry_base(plan, rel, cur, entry), 'keys': owned}})


def plan_codex_config(plan, adopt):
    path = plan.home / '.codex' / 'config.toml'
    rel = plan.rel(path)
    entry = plan.old.get('keys', {}).get(rel)
    if path.is_symlink():
        plan.refusals.append(f'{plan.show(path)} is a symlink; refusing to replace it')
        return
    cur = path.read_bytes() if path.exists() else None
    trust = orca_hook_trust(plan.home, plan.notes)
    old_keys = entry.get('hook_keys', []) if entry else []
    text = cur.decode('utf-8') if cur else ''
    try:
        new, conflicts, adopted = merge_codex_config(text, trust, old_keys, adopt)
        if conflicts:
            plan.refusals.append(f'{plan.show(path)} defines managed keys outside the orca-pod blocks; rerun with '
                                 '--adopt-config to move them into the blocks:\n'
                                 + '\n'.join(f'      line {n}: {line}' for n, line in conflicts))
            shown, _, _ = merge_codex_config(text, trust, old_keys, True)
            diff_note = ' (as it would be with --adopt-config)'
        else:
            shown, diff_note = new, ''
    except (Refusal, tomllib.TOMLDecodeError) as error:
        plan.refusals.append(f'{plan.show(path)}: {error}')
        return
    previous_adopted = copy.deepcopy(entry.get('adopted', {})) if entry else {}
    for name, original in adopted.items():
        previous_adopted[name] = previous_adopted.get(name, '') + original
    data = shown.encode('utf-8')
    changes = [f'{len(trust)} Orca hook trust entr{"y" if len(trust) == 1 else "ies"} in [hooks.state]'
               + diff_note] if trust else []
    plan.ops.append({'kind': 'keys', 'group': 'codex config', 'path': path, 'rel': rel, 'data': data,
                     'current': cur, 'action': 'unchanged' if data == cur else ('create' if cur is None
                                                                                   else 'update managed blocks'),
                     'changes': changes, 'diff': text_diff(plan, path, cur, data) if cur else [],
                     'entry': {'format': 'toml', **key_entry_base(plan, rel, cur, entry),
                               'adopted': previous_adopted, 'hook_keys': list(trust)}})


def orc_claude_model():
    roles = tomllib.loads(ROLES.read_text(encoding='utf-8'))['role']
    (orc,) = [role for role in roles if role['id'] == 'orc']
    model = orc['models'][0]
    if model['provider'] != 'claude':
        raise Refusal('roles.toml: the ORC default model is not a Claude model')
    return model['model'], model['effort']


def claude_version():
    result = run('claude', '--version') if shutil.which('claude') else None
    match = re.match(r'\s*(\d+\.\d+\.\d+)', result.stdout) if result and result.returncode == 0 else None
    return match[1] if match else None


def plan_claude(plan):
    model, effort = orc_claude_model()
    plan_json(plan, 'claude settings', plan.home / '.claude' / 'settings.json',
              {'model': model, 'effortLevel': effort, 'skipDangerousModePermissionPrompt': True},
              {'theme': 'dark'})
    # First-run keys only; Orca's "Trust the folder" covers per-project trust for the agents it launches.
    first_run = {'hasCompletedOnboarding': True}
    version = claude_version()
    if version:
        first_run['lastOnboardingVersion'] = version
    else:
        plan.notes.append('claude is not on PATH, so lastOnboardingVersion is not seeded')
    plan_json(plan, 'claude first run', plan.home / '.claude.json', {}, first_run)


def build_plan(home, old, args):
    plan = Plan(home, old)
    for step in (plan_skills, plan_roles, plan_rules, lambda p: plan_codex_config(p, args.adopt_config),
                 plan_claude, plan_stale):
        try:
            step(plan)
        except (Refusal, ValueError, OSError, subprocess.CalledProcessError) as error:
            plan.refusals.append(str(error))
    return plan


# ---------- Printing ----------

def print_plan(plan, args, source):
    mode = 'dry run: nothing is written' if not args.apply else 'apply'
    print(f'Orca Pod installer ({mode})')
    if source:
        state = 'published' if source['published'] else 'UNPUBLISHED (allowed for testing)'
        print(f'Source: {source["revision"][:12]} {state}{", uncommitted changes" if source["dirty"] else ""}')
    print(f'Home: {plan.home}{" (scratch)" if args.scratch else ""}')
    groups = {}
    for op in plan.ops:
        groups.setdefault(op['group'], []).append(op)
    counts = {}
    for group, ops in groups.items():
        print(f'\n[{group}]')
        for op in ops:
            counts[op['action'].split()[0]] = counts.get(op['action'].split()[0], 0) + 1
            if op['action'] == 'unchanged' and not args.verbose:
                continue
            target = ''
            if op.get('data', b'').startswith(b'symlink:'):
                target = ' -> ' + op['data'][8:].decode()
            print(f'  {op["action"]:<12} {plan.show(op["path"])}{target}')
            for change in op.get('changes', []):
                print(f'      {change}')
            for line in op.get('diff', []):
                print(f'      {line}')
        unchanged = sum(op['action'] == 'unchanged' for op in ops)
        if unchanged and not args.verbose:
            print(f'  unchanged    {unchanged} path(s)')
    print('\n[orca]')
    if args.scratch:
        print('  skip         Orca skills and app settings (scratch --home run)')
    else:
        print(f'  run          orca skills install {" ".join("--skill " + s for s in ORCA_SKILLS)} --agent claude,codex')
        print(f'  run          orca skills update {" ".join("--skill " + s for s in ORCA_SKILLS)}')
        if args.skip_orca_settings:
            print('  skip         Orca app settings (--skip-orca-settings)')
        else:
            pre = orca_settings_module().preflight(ORCA_PATCH)
            if not pre['ok']:
                plan.refusals.append(f'Orca app settings: {pre["error"]}; or pass --skip-orca-settings')
                print(f'  REFUSED      Orca app settings: {pre["error"]}')
            elif pre['changes']:
                print(f'  patch        Orca {pre["app_version"]} settings {json.dumps(pre["changes"])} '
                      f'(was {json.dumps(pre["before"])}); quits and relaunches Orca')
            else:
                print(f'  unchanged    Orca {pre["app_version"]} settings {json.dumps(ORCA_PATCH)}')
    print('\n[sign-in]')
    for line in sign_in_status(args):
        print(f'  {line}')
    for note in plan.notes:
        print(f'\nNote: {note}')
    if plan.refusals:
        print(f'\nREFUSED ({len(plan.refusals)}); --apply writes nothing until these are resolved:')
        for refusal in plan.refusals:
            print(f'  - {refusal}')
    summary = ', '.join(f'{n} {action}' for action, n in sorted(counts.items()))
    print(f'\nSummary: {summary or "no managed paths"}.')


SIGN_IN = {'claude': (('claude', 'auth', 'status', '--json'), ('claude', 'auth', 'login', '--claudeai')),
           'codex': (('codex', 'login', 'status'), ('codex', 'login', '--device-auth'))}


def signed_in(cli):
    status_cmd, _ = SIGN_IN[cli]
    if not shutil.which(cli):
        return None
    result = run(*status_cmd)
    if cli == 'claude':
        try:
            return bool(json.loads(result.stdout).get('loggedIn'))
        except ValueError:
            return False
    return result.returncode == 0


def sign_in_status(args):
    if args.scratch:
        return [f'not checked (scratch --home run); sign in with: {" ".join(SIGN_IN[c][1])}' for c in SIGN_IN]
    lines = []
    for cli, (_, login) in SIGN_IN.items():
        state = signed_in(cli)
        lines.append(f'{cli}: ' + ('not installed' if state is None else 'signed in' if state
                                   else f'NOT signed in; run: {" ".join(login)}'))
    return lines


def sign_in(args):
    if args.scratch:
        return
    for cli, (_, login) in SIGN_IN.items():
        if signed_in(cli) is False:
            if sys.stdin.isatty():
                print(f'{cli} is not signed in; running: {" ".join(login)}')
                subprocess.run(login)
            else:
                print(f'{cli} is not signed in; run this in a terminal: {" ".join(login)}')


# ---------- Applying ----------

class Writer:
    """Filesystem changes under home, with backups and created-directory bookkeeping."""

    def __init__(self, home, stamp, dirs):
        self.home = home
        self.state = home / STATE
        self.backup_root = self.state / 'backups' / stamp
        self.dirs = list(dirs)
        self.changed = 0

    def ensure_dir(self, path):
        missing = []
        while not path.exists() and not path.is_symlink():
            missing.append(path)
            path = path.parent
        for path in reversed(missing):
            path.mkdir()
            rel = path.relative_to(self.home).as_posix()
            if rel not in self.dirs:
                self.dirs.append(rel)

    def backup(self, path):
        """Copy path (file, link or directory) into this run's backup directory; return its state-relative path."""
        dest = self.backup_root / path.relative_to(self.home)
        if dest.exists() or dest.is_symlink():
            return dest.relative_to(self.state).as_posix()
        self.ensure_dir(self.state)  # Backup directories themselves are never owned or pruned.
        dest.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir() and not path.is_symlink():
            shutil.copytree(path, dest, symlinks=True)
        else:
            shutil.copy2(path, dest, follow_symlinks=False)
        return dest.relative_to(self.state).as_posix()

    def put(self, path, data, mode=None):
        """Atomically replace path with bytes, or with a symlink when data starts with b'symlink:'."""
        if path.is_dir() and not path.is_symlink():
            raise Refusal(f'{path} is a directory')
        self.ensure_dir(path.parent)
        temp = path.with_name(f'.{path.name}.orca-pod-{os.getpid()}.tmp')
        if data.startswith(b'symlink:'):
            os.symlink(data[8:].decode(), temp)
        else:
            fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode if mode is not None else 0o644)
            with open(fd, 'wb') as handle:
                handle.write(data)
            os.chmod(temp, mode if mode is not None else 0o644)
        os.replace(temp, path)
        self.changed += 1

    def restore(self, path, backup_rel):
        src = self.state / backup_rel
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.exists():
            shutil.rmtree(path)
        self.ensure_dir(path.parent)
        if src.is_dir() and not src.is_symlink():
            shutil.copytree(src, path, symlinks=True)
        else:
            shutil.copy2(src, path, follow_symlinks=False)
        self.changed += 1

    def remove(self, path):
        if path.is_symlink() or path.is_file():
            path.unlink()
            self.changed += 1
        elif path.exists():
            shutil.rmtree(path)
            self.changed += 1

    def prune_dirs(self, rels, empty_only=False):
        """Remove the listed created directories, deepest first, when empty.

        Return those still present, or with empty_only, those removed (or already gone).
        """
        kept, gone = [], []
        for rel in sorted(rels, key=lambda r: r.count('/'), reverse=True):
            try:
                (self.home / rel).rmdir()
                gone.append(rel)
            except FileNotFoundError:
                gone.append(rel)
            except OSError:
                kept.append(rel)
        return gone if empty_only else kept


def apply(plan, args, source, stamp):
    old = plan.old
    writer = Writer(plan.home, stamp, old.get('dirs', []))
    # Start from the previous records so a failure part way keeps ownership of paths not yet processed.
    manifest = {'version': MANIFEST_VERSION, 'files': copy.deepcopy(old.get('files', {})),
                'keys': copy.deepcopy(old.get('keys', {}))}
    if old.get('orca_settings'):
        manifest['orca_settings'] = old['orca_settings']
    try:
        for op in plan.ops:
            path, entry = op['path'], op['entry']
            if op['kind'] == 'file':
                # The restore pointer is the pre-install original; a changed owned copy gets a safety backup.
                backup = entry.get('backup') if entry else None
                if op['current'] is not None and not entry:
                    backup = writer.backup(path)
                elif op['action'].startswith('update (changed'):
                    writer.backup(path)
                if op['action'] != 'unchanged' and not op['action'].startswith('adopt'):
                    writer.put(path, op['data'], op['mode'])
                manifest['files'][op['rel']] = {'sha256': sha(op['data']), 'backup': backup}
            elif op['kind'] == 'remove':
                cur = current_bytes(path)
                if cur is not None and sha(cur) != entry['sha256']:
                    writer.backup(path)
                if entry.get('backup'):
                    writer.restore(path, entry['backup'])
                else:
                    writer.remove(path)
                del manifest['files'][op['rel']]
            else:
                record = dict(entry)
                if op['data'] != op['current']:
                    if op['current'] is not None:
                        saved = writer.backup(path)
                        if record['backup'] is None and not record['created']:
                            record['backup'] = saved
                    mode = path.stat().st_mode & 0o777 if path.exists() else \
                        0o644 if path.name == 'settings.json' else 0o600
                    writer.put(path, op['data'], mode)
                record['sha256'] = sha(op['data'])
                manifest['keys'][op['rel']] = record
        writer.dirs = [rel for rel in writer.dirs if rel not in writer.prune_dirs(writer.dirs, empty_only=True)]
    finally:
        writer.ensure_dir(plan.home / STATE)
        manifest['dirs'] = writer.dirs
        manifest['source'] = {'revision': source['revision'], 'dirty': source['dirty']}
        if {k: v for k, v in old.items() if k != 'applied_at'} != manifest:
            manifest['applied_at'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
            write_manifest(plan.home, manifest)
    return writer.changed


def write_manifest(home, manifest):
    path = home / STATE / 'manifest.json'
    temp = path.with_name('.manifest.json.tmp')
    temp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(temp, path)


def orca_settings_module():
    sys.path.insert(0, str(ORCA_SETTINGS.parent))
    import orca_settings
    return orca_settings


def patch_orca(patch, state_dir, stamp):
    """Run machine/orca_settings.py detached (it quits and relaunches Orca) and wait on its result file."""
    result_path = state_dir / f'orca-settings-{stamp}.json'
    with open(state_dir / f'orca-settings-{stamp}.log', 'wb') as log:
        subprocess.Popen([sys.executable, str(ORCA_SETTINGS), '--patch', json.dumps(patch),
                          '--result', str(result_path), '--backup-dir', str(state_dir / 'backups' / stamp / 'orca')],
                         stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    print(f'Orca app settings: the detached helper quits, patches and relaunches Orca; waiting on {result_path}')
    deadline = time.monotonic() + 420
    while time.monotonic() < deadline:
        try:
            result = json.loads(result_path.read_text(encoding='utf-8'))
            if 'ok' in result:
                print(f'Orca app settings: {"ok" if result["ok"] else "FAILED"} '
                      f'{json.dumps(result.get("after") or result.get("error"))}')
                return result['ok']
        except (FileNotFoundError, ValueError):
            pass
        time.sleep(2)
    print('Orca app settings: the helper did not finish within 7 minutes; check its result file and log')
    return False


def orca_steps(args, state_dir, stamp):
    """Install Orca's own skills, then patch Orca's app settings, recording previous values in the manifest."""
    if args.scratch:
        return True
    ok = True
    skills = [arg for s in ORCA_SKILLS for arg in ('--skill', s)]
    orca = shutil.which('orca') or orca_settings_module().ORCA_CLI
    for cmd in ([orca, 'skills', 'install', *skills, '--agent', 'claude,codex'],
                [orca, 'skills', 'update', *skills]):
        print('$ ' + ' '.join(cmd))
        ok &= subprocess.run(cmd).returncode == 0
    if args.skip_orca_settings:
        return ok
    pre = orca_settings_module().preflight(ORCA_PATCH)
    if not pre['ok']:
        print(f'Orca app settings refused: {pre["error"]}')
        return False
    if not pre['changes']:
        print('Orca app settings already match.')
        return ok
    if not patch_orca(ORCA_PATCH, state_dir, stamp):
        return False
    manifest_path = state_dir / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if not manifest.get('orca_settings'):
        manifest['orca_settings'] = {'previous': pre['before'], 'set': ORCA_PATCH}
        write_manifest(args.home_dir, manifest)
    return ok


# ---------- Uninstall ----------

def uninstall(home, old, args, stamp):
    writer = Writer(home, stamp, [])
    problems = []
    print(f'Orca Pod uninstall from {home}')
    for rel, entry in sorted(old.get('files', {}).items()):
        path = home / rel
        cur = current_bytes(path)
        if cur is not None and sha(cur) != entry['sha256']:
            print(f'  backed up    ~/{rel} (changed since install)')
            writer.backup(path)
        if entry.get('backup'):
            writer.restore(path, entry['backup'])
            print(f'  restored     ~/{rel}')
        elif cur is not None:
            writer.remove(path)
            print(f'  removed      ~/{rel}')
    for rel, entry in sorted(old.get('keys', {}).items()):
        path = home / rel
        cur = path.read_bytes() if path.exists() else None
        if cur is None:
            continue
        if entry['pristine'] and sha(cur) == entry['sha256'] and (entry['backup'] or entry['created']):
            if entry['backup']:
                writer.restore(path, entry['backup'])
                print(f'  restored     ~/{rel}')
            else:
                writer.remove(path)
                print(f'  removed      ~/{rel}')
            continue
        writer.backup(path)
        try:
            if entry['format'] == 'json':
                data = json.loads(cur)
                for key, record in entry['keys'].items():
                    if key in data and data[key] == record['set']:
                        if record['had']:
                            data[key] = record['previous']
                        else:
                            del data[key]
                new = (json.dumps(data, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
            else:
                new = unmerge_codex_config(cur.decode('utf-8'), entry.get('adopted', {}),
                                           entry.get('hook_keys', [])).encode('utf-8')
        except (ValueError, Refusal) as error:
            problems.append(f'~/{rel}: could not remove managed keys ({error}); the pre-install copy is at '
                            f'{home / STATE / entry["backup"]}' if entry['backup'] else f'~/{rel}: {error}')
            continue
        if new != cur:
            writer.put(path, new, path.stat().st_mode & 0o777)
            print(f'  removed keys ~/{rel} (changed since install, so managed keys were removed in place)')
    settings = old.get('orca_settings')
    if settings and not args.scratch and not args.skip_orca_settings:
        pre = orca_settings_module().preflight(settings['previous'])
        if not pre['ok']:
            problems.append(f'Orca app settings not restored: {pre["error"]}')
        elif pre['before'] != settings['set']:
            print('Orca app settings changed since install; left as they are')
        elif not patch_orca(settings['previous'], home / STATE, stamp):
            problems.append(f'Orca app settings not restored to {json.dumps(settings["previous"])}')
    kept = writer.prune_dirs(old.get('dirs', []))
    manifest = home / STATE / 'manifest.json'
    if problems:  # Keep the ownership record next to the backups for manual recovery.
        manifest.rename(manifest.with_name(f'manifest-{stamp}.incomplete.json'))
    else:
        manifest.unlink()
    writer.prune_dirs(kept)
    for problem in problems:
        print(f'PROBLEM: {problem}')
    print(f'Uninstalled; {writer.changed} change(s). Backups are kept under {home / STATE / "backups"}.')
    return 1 if problems else 0


# ---------- Entry point ----------

def source_state(allow):
    def git(*a):
        return subprocess.run(['git', '-C', str(ROOT), *a], capture_output=True, text=True)

    head = git('rev-parse', 'HEAD').stdout.strip()
    dirty = bool(git('status', '--porcelain').stdout.strip())
    published = any(git('merge-base', '--is-ancestor', 'HEAD', f'origin/{b}').returncode == 0
                    for b in ('test', 'main'))
    if not head:
        raise Refusal(f'{ROOT} is not a Git checkout')
    if (dirty or not published) and not allow:
        reason = 'has uncommitted changes' if dirty else 'HEAD is not on origin/test or origin/main (git fetch?)'
        raise Refusal(f'the source checkout {reason}; install from a clean, published revision')
    return {'revision': head, 'dirty': dirty, 'published': published}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true', help='print the plan and write nothing (default)')
    mode.add_argument('--apply', action='store_true', help='install or update the managed targets')
    mode.add_argument('--uninstall', action='store_true', help='remove owned paths and keys, restoring backups')
    parser.add_argument('--home', type=Path, default=Path.home(),
                        help='home directory holding every target (default: ~); another directory is a scratch run')
    parser.add_argument('--adopt-config', action='store_true',
                        help='move unmarked managed keys in ~/.codex/config.toml into the managed blocks')
    parser.add_argument('--skip-orca-settings', action='store_true', help='leave Orca app settings alone')
    parser.add_argument('--allow-unpublished', action='store_true',
                        help='testing only: install from a dirty or unpublished checkout')
    parser.add_argument('--verbose', action='store_true', help='also list unchanged paths')
    args = parser.parse_args()
    if sys.platform != 'darwin':
        raise SystemExit('install.py: Orca Pod installs on macOS only')
    home = Path(os.path.abspath(args.home.expanduser()))
    if not home.is_dir():
        raise SystemExit(f'install.py: {home} is not a directory')
    args.scratch = home.resolve() != Path.home().resolve()
    args.home_dir = home
    manifest_path = home / STATE / 'manifest.json'
    old = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    if old and old.get('version') != MANIFEST_VERSION:
        raise SystemExit(f'install.py: {manifest_path} has unknown version {old.get("version")}')
    stamp = time.strftime('%Y%m%dT%H%M%S') + f'-{os.getpid()}'
    if args.uninstall:
        if not old:
            print(f'Nothing to uninstall: no manifest at {manifest_path}')
            return 0
        return uninstall(home, old, args, stamp)
    try:
        source = source_state(args.allow_unpublished)
    except Refusal as error:
        raise SystemExit(f'install.py: {error}')
    plan = build_plan(home, old, args)
    print_plan(plan, args, source)
    if plan.refusals:
        return 2
    if not args.apply:
        print('Dry run complete; rerun with --apply to install.')
        return 0
    changed = apply(plan, args, source, stamp)
    print(f'\nApplied: {changed} change(s).' if changed else '\nNo changes: the managed targets are current.')
    ok = orca_steps(args, home / STATE, stamp)
    sign_in(args)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
