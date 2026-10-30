#!/usr/bin/env python3
"""Install Orca Pod into the default agent homes on macOS; see docs/install.md.

--dry-run (the default) prints every planned action, managed-block diff, conflict and refusal and writes nothing.
--apply installs, recording owned paths, owned keys and their previous values in a private manifest.
--uninstall removes what the manifest owns and restores the previous files and values.
"""
import argparse
import copy
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shlex
import shutil
import stat
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
AUTOMATIONS = ROOT / 'machine' / 'automations.toml'
PYTHON = os.environ.get('ORCA_POD_PYTHON') or sys.executable  # Interpreter for the child Python helpers.
STATE = Path('.local/state/orca-pod')
MANIFEST_VERSION = 1
FILE_ROOTS = ('.agents/skills/', '.claude/', '.codex/')  # Whole files and links the manifest may own.
KEY_FILES = ('.codex/config.toml', '.claude/settings.json', '.claude.json')  # Files owned key by key.
DIR_ROOTS = ('.agents/skills', '.claude', '.codex', STATE.as_posix())  # Created directories lie on or below these.
# The top-level JSON keys the manifest may own, by file, with the type of the value set. Only manifests from earlier
# revisions own the top-level effortLevel, so a reapply can restore it.
JSON_KEYS = {'.claude/settings.json': {'model': str, 'skipDangerousModePermissionPrompt': bool, 'theme': str,
                                       'effortLevel': str},
             '.claude.json': {'hasCompletedOnboarding': bool, 'lastOnboardingVersion': str}}
CLAUDE_MODEL = re.compile(r'claude-[a-z0-9]+(?:-[a-z0-9]+)*')  # A roster Claude model id, owned as a modelSettings key.

ORCA_SKILLS = ('orca-cli', 'orchestration')
ORCA_PATCH = {'branchPrefix': 'custom', 'branchPrefixCustom': 'orca', 'agentPermissionDefault': 'full-access'}
BASE_REF = 'origin/test'  # The Standard's Orca default base ref, so new worktrees start from test.
# roles.toml has no Codex ORC entry; the Codex coordinator alternative is pinned here (jdip/orca-pod#13).
# Codex runs with Full Access, as Orca launches agents (jdip/orca-pod#43); a --profile file layers on top of these.
CODEX_ROOT = {'model': 'gpt-6.1-sol', 'model_reasoning_effort': 'high', 'default_permissions': ':danger-full-access',
              'approval_policy': 'never', 'approvals_reviewer': 'auto_review'}
CODEX_TABLE_KEYS = {'agents': ('enabled', True), 'features': ('hooks', True)}
BLOCKS = ('root', 'agents', 'features', 'hooks.state')
# Each provider's --extra-agent-args for a roster model and effort; Orca 1.4.240 and 1.4.241 accept only these options.
AGENT_ARGS = {'claude': '--model {model} --effort {effort}',
              'codex': '--model {model} -c model_reasoning_effort={effort}'}
AUTOMATION_KEYS = {'name', 'role', 'trigger', 'prompt'}
# Orca stores no ownership marker on an automation, so the installer only ever creates, edits or removes
# automations named with this prefix, whatever the manifest records.
AUTOMATION_PREFIX = 'Orca Pod: '
AUTOMATION_ID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')  # Orca's UUIDs.
CRON = re.compile(r'[0-9*,/-]+(?: [0-9*,/-]+){4}')
PLAIN_TOKEN = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*')
PROMPT_SAFE_PATH = re.compile(r'/[A-Za-z0-9._+/-]+')  # An interpreter path that is safe in a prompt.
ORCA_MISSED_RUN_GRACE = 720  # Orca's default missed-run grace window in minutes (1.4.240 and 1.4.241).

# The known sets of command hooks Orca writes to ~/.codex/hooks.json, by event. Trust follows content, not the
# Orca version: a handler is trusted only when it exactly equals its event's handler in one of these sets.
ORCA_HOOK_COMMAND_1 = (
    ': orca-agent-hook-form=1; '
    'if [ -n "${ORCA_PANE_KEY-}" ] && [ -n "${ORCA_AGENT_HOOK_ROOT-}" ] && '
    '[ -f "${ORCA_AGENT_HOOK_ROOT-}/agent-hooks/codex-hook.sh" ]; '
    'then /bin/sh "${ORCA_AGENT_HOOK_ROOT-}/agent-hooks/codex-hook.sh" || :; '
    'elif [ -z "${ORCA_AGENT_HOOK_ROOT-}" ] && [ -n "${ORCA_PANE_KEY-}" ] && [ -n "${ORCA_AGENT_HOOK_PORT-}" ] && '
    '[ -f "${HOME-}/.orca/agent-hooks/codex-hook.sh" ]; '
    'then /bin/sh "${HOME-}/.orca/agent-hooks/codex-hook.sh" || :; '
    'else { command -p cat 2>/dev/null || cat; } >/dev/null 2>&1 || :; fi')
ORCA_CODEX_HOOK_SETS = (
    # Taken from Orca 1.4.240's agent-hook generator (its Codex command builder and event table); 1.4.241 writes
    # the same handlers.
    {event: {'type': 'command', 'command': ORCA_HOOK_COMMAND_1, 'timeout': 3 if event == 'Interrupt' else 10}
     for event in ('SessionStart', 'UserPromptSubmit', 'PreToolUse', 'PermissionRequest', 'PostToolUse',
                   'SubagentStart', 'SubagentStop', 'Stop', 'Interrupt')},
)
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


# ---------- Path containment ----------

def check_path(home, path, leaf_dir=False):
    """Refuse unless path lies below home and each existing component above the leaf is a real directory.

    The leaf may be absent or, unless leaf_dir, a file or symlink; nothing is ever resolved through a link.
    """
    try:
        parts = path.relative_to(home).parts
    except ValueError:
        raise Refusal(f'{path} is outside {home}')
    if '..' in parts or not (parts or leaf_dir):
        raise Refusal(f'{path} is not a plain path below {home}')
    current = home
    for i, part in enumerate(parts):
        current = current / part
        try:
            mode = os.lstat(current).st_mode
        except FileNotFoundError:
            return
        if (i < len(parts) - 1 or leaf_dir) and not stat.S_ISDIR(mode):
            kind = 'a symlink' if stat.S_ISLNK(mode) else 'not a directory'
            raise Refusal(f'~/{Path(*parts[:i + 1]).as_posix()} is {kind}; refusing to work through it')


def plain_rel(value):
    """A non-empty relative POSIX path with no empty, '.' or '..' component."""
    return (isinstance(value, str) and bool(value) and not value.startswith('/') and '\\' not in value
            and all(part not in ('', '.', '..') for part in value.split('/')))


def validate_manifest(old):
    """Refuse a manifest whose entries could point outside the managed roots."""
    def need(ok, what):
        if not ok:
            raise Refusal(f'the manifest has an invalid {what}')

    def backup_ok(pointer, what):
        need(pointer is None or (isinstance(pointer, dict) and plain_rel(pointer.get('path'))
                                 and pointer['path'].startswith('backups/')
                                 and (pointer.get('mode') is None or isinstance(pointer['mode'], int))), what)

    files, keys, dirs = old.get('files', {}), old.get('keys', {}), old.get('dirs', [])
    need(isinstance(files, dict) and isinstance(keys, dict) and isinstance(dirs, list), 'layout')
    for rel, entry in files.items():
        need(plain_rel(rel) and rel.startswith(FILE_ROOTS) and isinstance(entry, dict)
             and isinstance(entry.get('sha256'), str), f'file entry {rel!r}')
        backup_ok(entry.get('backup'), f'backup for {rel!r}')
    for rel, entry in keys.items():
        need(rel in KEY_FILES and isinstance(entry, dict)
             and entry.get('format') == ('toml' if rel.endswith('.toml') else 'json'), f'key entry {rel!r}')
        hook_keys = entry.get('hook_keys', [])
        need(isinstance(hook_keys, list) and all(isinstance(k, str) for k in hook_keys), f'hook keys for {rel!r}')
        if entry['format'] == 'toml':
            adopted, previous = entry.get('adopted', {}), entry.get('previous', {})
            need(set(entry) <= {'format', 'created', 'adopted', 'previous', 'hook_keys'}
                 and isinstance(entry.get('created'), bool) and isinstance(adopted, dict)
                 and all(name in BLOCKS and isinstance(text, str) for name, text in adopted.items())
                 and isinstance(previous, dict), f'key entry {rel!r}')
            # Recorded hooks.state values outlive the current trust list, so any hooks.state table is accepted.
            managed = [p for paths in codex_managed([]).values() for p in paths]
            for key in previous:
                try:
                    path = json.loads(key)
                except ValueError:
                    path = None
                need(isinstance(path, list) and path and all(isinstance(part, str) for part in path)
                     and (any(tuple(path[:len(m)]) == m for m in managed)
                          or (len(path) >= 3 and path[:2] == ['hooks', 'state'])), f'previous value {key!r} for {rel!r}')
        if entry['format'] == 'json':
            need(set(entry) == {'format', 'created', 'keys'} and isinstance(entry['created'], bool)
                 and isinstance(entry['keys'], dict), f'key entry {rel!r}')
            for name, record in entry['keys'].items():
                need(owned_json_key(rel, name, record), f'owned key {name!r} for {rel!r}')
    for rel in dirs:
        need(plain_rel(rel) and any(rel == r or rel.startswith(r + '/') or r.startswith(rel + '/')
                                    for r in DIR_ROOTS), f'directory {rel!r}')
    settings = old.get('orca_settings')
    need(settings is None or (isinstance(settings, dict) and isinstance(settings.get('previous'), dict)
                              and isinstance(settings.get('set'), dict)), 'Orca settings record')
    if settings and settings.get('backup') is not None:
        backup_ok({'path': settings['backup']}, 'Orca settings backup')
    automations = old.get('automations', {})
    need(isinstance(automations, dict), 'automations record')
    for name, record in automations.items():
        need(automation_name(name) and isinstance(record, dict) and set(record) == {'id', 'adopted'}
             and type(record['id']) is str and bool(AUTOMATION_ID.fullmatch(record['id']))
             and type(record['adopted']) is bool, f'automation record {name!r}')
    ids = [record['id'] for record in automations.values()]
    need(len(ids) == len(set(ids)), 'automations record (an id is recorded twice)')


def automation_name(value):
    """An Orca Pod automation name, stored by Orca as given: the managed prefix, no surrounding space and no
    control characters."""
    return (type(value) is str and value.startswith(AUTOMATION_PREFIX) and len(value) > len(AUTOMATION_PREFIX)
            and value == value.strip() and len(value) <= 200
            and not any(ord(ch) < 0x20 or 0x7f <= ord(ch) <= 0x9f for ch in value))


def owned_json_key(rel, name, record):
    """Whether a manifest record names a JSON key the installer owns in rel, with the shape the installer writes:
    a listed top-level key, or the effortLevel of one Claude model under modelSettings in the Claude settings."""
    if not (isinstance(record, dict) and isinstance(record.get('had'), bool) and 'set' in record
            and 'previous' in record and (record['had'] or record['previous'] is None)):
        return False
    extra = set(record) - {'had', 'previous', 'set'}
    if name in JSON_KEYS[rel]:
        return not extra and type(record['set']) is JSON_KEYS[rel][name]
    model = name.removeprefix('modelSettings.').removesuffix('.effortLevel')
    return (rel == '.claude/settings.json' and name == f'modelSettings.{model}.effortLevel'
            and bool(CLAUDE_MODEL.fullmatch(model)) and extra == {'path', 'created_parents'}
            and record['path'] == ['modelSettings', model, 'effortLevel']
            and type(record['created_parents']) is int and 0 <= record['created_parents'] <= 2
            and type(record['set']) is str)


def single_link(path, st):
    """Refuse a regular file with other hard links: its bytes also live outside the managed path."""
    if stat.S_ISREG(st.st_mode) and st.st_nlink > 1:
        raise Refusal(f'{path} is a hard link ({st.st_nlink} links); refusing to read, back up or replace it')


def read_regular(path, links_ok=False):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with open(fd, 'rb') as handle:
        if not links_ok:
            single_link(path, os.fstat(fd))
        return handle.read()


def current_bytes(path, links_ok=False):
    """File bytes, or b'symlink:<target>' for a link, or None when absent; a hard-linked file is refused."""
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(st.st_mode):
        return b'symlink:' + os.readlink(path).encode()
    if stat.S_ISREG(st.st_mode):
        if not links_ok:
            single_link(path, st)
        return read_regular(path, links_ok)
    raise Refusal(f'{path} exists and is not a regular file or symlink')


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
    """Return {state key: trusted_hash} for each hook in <home>/.codex/hooks.json that exactly matches its
    event's handler in a pinned Orca hook set, whatever the Orca version; any other hook is reported and
    left untrusted."""
    path = home / '.codex' / 'hooks.json'
    check_path(home, path)
    data = current_bytes(path, links_ok=True)  # Only hashed, never copied or replaced.
    if data is None:
        notes.append('~/.codex/hooks.json is absent, so no Codex hook trust is seeded; '
                     'rerun --apply after Orca installs its hooks')
        return {}
    raw = read_regular(path.resolve(), links_ok=True) if data.startswith(b'symlink:') else data
    events = json.loads(raw).get('hooks', {})
    source = path.resolve()  # Codex keys hook state by the canonical hooks.json path.
    trust, skipped = {}, []
    for name, groups in events.items() if isinstance(events, dict) else ():
        for gi, group in enumerate(groups if isinstance(groups, list) else []):
            handlers = group.get('hooks', []) if isinstance(group, dict) else []
            for hi, handler in enumerate(handlers if isinstance(handlers, list) else []):
                if set(group) == {'hooks'} and any(pinned.get(name) == handler for pinned in ORCA_CODEX_HOOK_SETS):
                    trust[f'{source}:{snake(name)}:{gi}:{hi}'] = hook_hash(snake(name), None, handler)
                else:
                    skipped.append(f'{name}[{gi}][{hi}]')
    if skipped:
        notes.append(f'~/.codex/hooks.json: {len(skipped)} hook(s) match no pinned Orca hook set, '
                     'so they get no new trust: ' + ', '.join(skipped))
    return trust


# ---------- TOML managed blocks ----------

def toml_lines(text):
    """Split on newlines only, terminating every line; the caller restores a missing final newline."""
    return [line if line.endswith('\n') else line + '\n' for line in re.findall(r'[^\n]*\n|[^\n]+$', text)]


def finish(text, eof_newline):
    return text[:-1] if not eof_newline and text.endswith('\n') else text


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
    raise Refusal('no key')


def statements(lines, table=()):
    """Split TOML lines into (start, end, kind, path) statements; kind is table, array, key or None (trivia).

    A multi-line value is one statement, so comment-like lines inside a string are never trivia.
    """
    out, i = [], 0
    while i < len(lines):
        text = lines[i].strip()
        try:
            if not text or text.startswith('#'):
                out.append((i, i + 1, None, None))
                i += 1
                continue
            if text.startswith('['):
                table, leaf = single_path(tomllib.loads(lines[i]))
                out.append((i, i + 1, 'array' if isinstance(leaf, list) else 'table', table))
                i += 1
                continue
            path = table + key_path(lines[i])
        except (Refusal, tomllib.TOMLDecodeError):
            raise Refusal(f'cannot parse the TOML statement at line {i + 1}')
        j = i + 1
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
    """Remove managed blocks; return (base lines, {name: (base index, inner lines)}).

    Markers count only as top-level comment lines, never inside a multi-line string or array.
    """
    trivia = {start for start, _, kind, _ in statements(lines) if kind is None}
    begin = {i: m[1] for i in trivia if (m := BEGIN_RE.match(lines[i]))}
    end = {i: m[1] for i in trivia if (m := END_RE.match(lines[i]))}
    base, blocks, i = [], {}, 0
    while i < len(lines):
        if i in end:
            raise Refusal(f'line {i + 1} closes an orca-pod block that was never opened')
        if i not in begin:
            base.append(lines[i])
            i += 1
            continue
        name, j = begin[i], i + 1
        if name not in BLOCKS:
            raise Refusal(f'line {i + 1} opens an unknown orca-pod block {name!r}')
        while j < len(lines) and j not in begin and j not in end:
            j += 1
        if j == len(lines) or end.get(j) != name:
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


def unowned(inner, table, paths, keep=()):
    """The lines of a managed block body that the block does not own, in order, and whether any is a statement.

    Comments and blank lines are unowned too, except the blank line the installer writes between two owned
    tables. An owned table header listed in keep stays in place.
    """
    stmts = statements(inner, table)
    lines, foreign = [], False
    for i, (start, end, kind, path) in enumerate(stmts):
        if kind is None:
            separator = (not inner[start].strip() and 0 < i < len(stmts) - 1 and owns(*stmts[i - 1][2:], paths)
                         and stmts[i + 1][2] == 'table' and owns(*stmts[i + 1][2:], paths))
            if not separator:
                lines += inner[start:end]
        elif not owns(kind, path, paths):
            lines += inner[start:end]
            foreign = True
        elif kind == 'table' and path in keep:
            lines += inner[start:end]
    return lines, foreign


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
        state = trust_state(value)
        body += ['\n'] if body else []
        body += [f'[hooks.state.{toml_str(key)}]\n', f'enabled = {str(state["enabled"]).lower()}\n',
                 f'trusted_hash = {toml_str(state["trusted_hash"])}\n']
    return body


def trust_state(value):
    """A trust value is a pinned hook's hash, seeded enabled, or a kept entry's recorded hash and enabled state."""
    return value if isinstance(value, dict) else {'enabled': True, 'trusted_hash': value}


def set_path(doc, path, value):
    for key in path[:-1]:
        doc = doc.setdefault(key, {})
    doc[path[-1]] = value


def get_path(doc, path):
    for key in path:
        if not isinstance(doc, dict) or key not in doc:
            return None, False
        doc = doc[key]
    return doc, True


def without(doc, paths):
    """A copy of a parsed document with the given key paths removed."""
    doc = copy.deepcopy(doc)
    for path in paths:
        node, found = get_path(doc, path[:-1])
        if found and isinstance(node, dict):
            node.pop(path[-1], None)
    return doc


def pruned(doc):
    """Drop empty tables, which carry no value, so documents compare by their keys and values."""
    if isinstance(doc, dict):
        return {k: v for k, v in ((k, pruned(v)) for k, v in doc.items()) if v != {}}
    if isinstance(doc, list):
        return [pruned(v) for v in doc]
    return doc


def merge_codex_config(text, trust, old_hook_keys):
    """Return (new text, moved, adopted {block: text}, previous {path: value}) for config.toml.

    moved lists (line, dotted key) for managed keys defined outside the blocks; the caller refuses them
    unless adopting. The result must equal the parsed original with only the managed paths replaced.
    """
    original = tomllib.loads(text)  # Refuse invalid TOML before touching anything.
    base, old_blocks = strip_blocks(toml_lines(text))
    stmts = statements(base)
    # Report the original file's line numbers: each stripped block sat, with its two markers, before its base index.
    shifts = [(index, len(inner) + 2) for index, inner in old_blocks.values()]
    managed = codex_managed(trust)
    domain = {**managed, 'hooks.state': managed['hooks.state'] + [('hooks', 'state', k) for k in old_hook_keys]}
    moved, removed, owner, first_removed, owned_tables, moved_paths = [], set(), {}, {}, set(), {}
    for start, end, kind, path in stmts:
        if kind is None:
            continue
        for name, paths in managed.items():
            hit = any(path[:len(m)] == m for m in paths) if kind != 'key' else any(overlaps(path, m) for m in paths)
            if hit:
                if kind != 'key':
                    owned_tables.add(path)
                if kind != 'key' or path[:-1] not in owned_tables:  # Report a whole owned table once.
                    moved.append((start + 1 + sum(n for index, n in shifts if index <= start), '.'.join(path)))
                removed.update(range(start, end))
                owner[start] = name
                moved_paths.setdefault(name, []).append(path)
                first_removed.setdefault(name, start)
                break
    # Move blank lines between two adopted statements, such as the gaps between adopted tables, along with
    # them, so uninstall puts them back too.
    for start, end, kind, _ in stmts:
        if kind is None and not base[start].strip():
            above = [s for s in stmts if s[1] <= start and s[2] is not None]
            below = [s for s in stmts if s[0] >= end and s[2] is not None]
            if above and below and above[-1][0] in removed and below[0][0] in removed:
                removed.add(start)
                owner[start] = owner[below[0][0]]
    adopted = {}
    for start, end, _, _ in stmts:
        if start in owner:
            adopted[owner[start]] = adopted.get(owner[start], '') + ''.join(base[start:end])
    # An adopted key's original value is restored on uninstall; it cannot also sit in a block, or the
    # original would not have parsed. A managed key already in the block was not adopted and has no original.
    previous = {m: get_path(original, m)[0] for name in adopted for m in managed[name]
                if get_path(original, m)[1] and any(overlaps(path, m) for path in moved_paths[name])}
    headers = {path: start for start, _, kind, path in stmts if kind == 'table'}
    inserts = {}  # base index -> [(block lines, foreign lines)]
    for name in BLOCKS:
        old_index, inner = old_blocks.get(name, (None, []))
        foreign, _ = unowned(inner, table_at(stmts, old_index or 0), domain[name])
        header = name in CODEX_TABLE_KEYS and (name,) not in headers
        if name in CODEX_TABLE_KEYS and not header:
            index = headers[(name,)] + 1
        elif old_index is not None:
            index = old_index
        elif header:  # A block carrying its own table header goes last, where it cannot capture other keys.
            index = len(base)
        elif name in first_removed:
            index = first_removed[name]
        elif name == 'root':  # After any leading comments, before the first statement.
            index = next((start for start, _, kind, _ in stmts if kind is not None), len(base))
        else:
            index = len(base)
        body = render_body(name, trust, header)
        block = [BEGIN.format(name), *body, END.format(name)] if body else []
        inserts.setdefault(index, []).append((block, foreign))
    out = []
    for i in range(len(base) + 1):
        for block, foreign in inserts.get(i, []):
            out += block + foreign
        if i < len(base) and i not in removed:
            out.append(base[i])
    new = finish(''.join(out), not text or text.endswith('\n'))
    expected = without(original, [p for paths in domain.values() for p in paths])
    for path in managed['root']:
        set_path(expected, path, CODEX_ROOT[path[0]])
    for name, (key, value) in CODEX_TABLE_KEYS.items():
        set_path(expected, (name, key), value)
    for path in managed['hooks.state']:
        set_path(expected, path, trust_state(trust[path[2]]))
    try:
        ok = pruned(tomllib.loads(new)) == pruned(expected)
    except tomllib.TOMLDecodeError:
        ok = False
    if not ok:
        raise Refusal('the managed blocks cannot be merged without changing other keys; edit config.toml by hand')
    return new, moved, adopted, previous


def unmerge_codex_config(text, adopted, hook_keys, previous):
    """Remove managed blocks, keep foreign statements found inside them and restore adopted originals.

    The result must equal the parsed current file with only the owned paths removed or set back to their
    previous values.
    """
    current = tomllib.loads(text)
    base, blocks = strip_blocks(toml_lines(text))
    stmts = statements(base)
    domain = {**codex_managed({}), 'hooks.state': [('hooks', 'state', k) for k in hook_keys]}
    inserts = {}
    for name, (index, inner) in blocks.items():
        table = table_at(stmts, index)
        keep, foreign = unowned(inner, table, domain[name])
        # The block's own table header still opens that table for foreign keys inside or just after it.
        after = next((kind for start, _, kind, _ in stmts if start >= index and kind is not None), None)
        if foreign or after == 'key':
            keep, _ = unowned(inner, table, domain[name], keep=[(name,)])
        inserts.setdefault(index, []).append(adopted.get(name, '') + ''.join(keep))
    out = []
    for i in range(len(base) + 1):
        out += inserts.get(i, [])
        if i < len(base):
            out.append(base[i])
    new = finish(''.join(out), not text or text.endswith('\n'))
    expected = without(current, [p for paths in domain.values() for p in paths] + list(previous))
    for path, value in previous.items():
        set_path(expected, path, value)
    try:
        ok = pruned(tomllib.loads(new)) == pruned(expected)
    except tomllib.TOMLDecodeError:
        ok = False
    if not ok:
        raise Refusal('removing the managed blocks would change other keys')
    return new


def block_view(text, domain):
    """The owned statement lines of each managed block in text, and the number of every other line."""
    base, blocks = strip_blocks(toml_lines(text))
    stmts = statements(base)
    shown, other = {}, len(base)
    for name, (index, inner) in blocks.items():
        shown[name] = []
        for start, end, kind, path in statements(inner, table_at(stmts, index)):
            if kind is not None and owns(kind, path, domain[name]):
                shown[name] += [line.rstrip('\n') for line in inner[start:end]]
            else:
                other += sum(1 for line in inner[start:end] if line.strip())
    return shown, other


def managed_diff(old, new, domain):
    """A diff of the owned lines in the managed blocks; unowned lines are only counted, never shown."""
    before, _ = block_view(old, domain)
    after, unowned = block_view(new, domain)
    out = []
    for name in BLOCKS:
        if before.get(name, []) != after.get(name, []):
            out.append(f'@@ block {name} @@')
            out += list(difflib.unified_diff(before.get(name, []), after.get(name, []), lineterm='', n=0))[2:]
    if unowned:
        out.append(f'… {unowned} unowned line(s) not shown …')
    return out


# ---------- Planning ----------

class Plan:
    def __init__(self, home, old):
        self.home = home
        self.old = old
        self.ops = []
        self.notes = []
        self.refusals = []
        self.automations = []
        self.base_ref = None

    def show(self, path):
        try:
            return '~/' + Path(path).relative_to(self.home).as_posix()
        except ValueError:
            return str(path)

    def rel(self, path):
        return path.relative_to(self.home).as_posix()

    def check(self, path, leaf_dir=False):
        """Containment and hard-link preflight: record a refusal and return False for an unsafe path."""
        try:
            check_path(self.home, path, leaf_dir)
            if os.path.lexists(path):
                single_link(path, os.lstat(path))
            return True
        except Refusal as error:
            if str(error) not in self.refusals:
                self.refusals.append(str(error))
            return False


def text_diff(plan, path, old, new):
    if old is None or old.startswith(b'symlink:') or new.startswith(b'symlink:'):
        return []
    name = plan.show(path)
    return list(difflib.unified_diff(old.decode('utf-8', 'replace').splitlines(),
                                     new.decode('utf-8', 'replace').splitlines(),
                                     f'{name} (current)', f'{name} (planned)', lineterm='', n=2))


def plan_file(plan, group, path, data, mode=0o644, diff=True):
    """Plan one owned whole file (or symlink when data starts with b'symlink:')."""
    if not plan.check(path):
        return
    rel = plan.rel(path)
    entry = plan.old.get('files', {}).get(rel)
    try:
        cur = current_bytes(path)
    except Refusal as error:
        plan.refusals.append(str(error))
        return
    cur_mode = None if cur is None or cur.startswith(b'symlink:') else stat.S_IMODE(os.lstat(path).st_mode)
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
    # Only content Orca Pod wrote is diffed; a file it does not own yet, or one changed since, is not shown.
    plan.ops.append({'kind': 'file', 'group': group, 'path': path, 'rel': rel, 'data': data, 'mode': mode,
                     'action': action, 'current': cur, 'entry': entry,
                     'diff': text_diff(plan, path, cur, data) if diff and action == 'update' else []})


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
        if not plan.check(dest, leaf_dir=True):
            continue
        before = len(plan.ops)
        for src in sorted(files[name]):
            mode = 0o755 if src.stat().st_mode & 0o111 else 0o644
            plan_file(plan, 'skills', dest / src.relative_to(skill), src.read_bytes(), mode, diff=False)
        if dest.is_dir():
            ours = {op['path'] for op in plan.ops[before:]}
            extra = [Path(d) / f for d, _, names in os.walk(dest) for f in names]
            extra = [p for p in extra if p not in ours and plan.rel(p) not in plan.old.get('files', {})]
            if extra:
                plan.notes.append(f'{plan.show(dest)} holds files Orca Pod does not own, left in place: '
                                  + ', '.join(p.relative_to(dest).as_posix() for p in extra[:5]))
        link = plan.home / '.claude' / 'skills' / name
        target = os.path.relpath(dest, link.parent)
        plan_file(plan, 'skills', link, b'symlink:' + target.encode())


def render_roles():
    check = run(PYTHON, str(GENERATE), '--check')
    if check.returncode:
        raise Refusal('roster tables are stale; run roster/generate.py and commit: ' + check.stderr.strip())
    with tempfile.TemporaryDirectory(prefix='orca-pod-roster-') as tmp:
        result = run(PYTHON, str(GENERATE), '--out', tmp)
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
            backup = entry.get('backup')
            if plan.check(path) and (not backup or plan.check(plan.home / STATE / backup['path'])):
                plan.ops.append({'kind': 'remove', 'group': 'stale', 'path': path, 'rel': rel, 'entry': entry,
                                 'action': 'restore backup' if entry.get('backup') else 'remove'})


def read_key_file(plan, path):
    """Current bytes of a key-managed file (None when absent), or False after recording a refusal."""
    if not plan.check(path):
        return False
    if os.path.islink(path):
        plan.refusals.append(f'{plan.show(path)} is a symlink; refusing to replace it')
        return False
    try:
        return current_bytes(path)
    except Refusal as error:
        plan.refusals.append(str(error))
        return False


def json_style(text):
    """The indent and final newline of a JSON document, so a rewrite keeps its look."""
    indent = re.search(r'\n([ \t]+)\S', text)
    return {'indent': indent[1] if indent else (None if text.strip() else 2),
            'newline': text.endswith('\n') or not text.strip()}


def dump_json(data, style):
    return (json.dumps(data, indent=style['indent'], ensure_ascii=False, allow_nan=False)
            + ('\n' if style['newline'] else '')).encode('utf-8')


def restore_key(doc, path, record):
    """Put back one owned JSON key that still holds the value set, dropping any parents the installer created
    and left empty; return False when the key changed since install, so it stays as is."""
    value, found = get_path(doc, path)
    if not found or value != record['set']:
        return False
    if record['had']:
        set_path(doc, path, record['previous'])
        return True
    del get_path(doc, path[:-1])[0][path[-1]]
    for depth in range(len(path) - 1, len(path) - 1 - record.get('created_parents', 0), -1):
        if get_path(doc, path[:depth])[0] != {}:
            break
        del get_path(doc, path[:depth - 1])[0][path[depth - 1]]
    return True


def plan_json(plan, group, path, sets, defaults, keep=()):
    """Plan the owned keys of a JSON file. A key is a top-level name or a tuple key path; an owned key the plan no
    longer sets or keeps gets its previous value back and leaves the manifest."""
    rel = plan.rel(path)
    entry = plan.old.get('keys', {}).get(rel)
    cur = read_key_file(plan, path)
    if cur is False:
        return
    try:
        data = json.loads(cur) if cur else {}
    except ValueError as error:
        plan.refusals.append(f'{plan.show(path)} is not valid JSON ({error})')
        return
    if not isinstance(data, dict):
        plan.refusals.append(f'{plan.show(path)} is not a JSON object')
        return
    owned = copy.deepcopy(entry['keys']) if entry else {}  # The previous value of each owned key.
    new, changes = copy.deepcopy(data), []
    parts = {key: key if isinstance(key, tuple) else (key,) for key in [*sets, *defaults]}
    names = {'.'.join(p) for p in parts.values()} | set(keep)
    for name in [name for name in owned if name not in names]:
        record = owned.pop(name)
        if not restore_key(new, record.get('path', [name]), record):
            plan.notes.append(f'{plan.show(path)}: {name} is no longer managed and changed since install; left as is')
        elif record['had']:
            changes.append(f'restore {name} = {json.dumps(record["previous"])} (no longer managed)')
        else:
            changes.append(f'remove {name} (no longer managed; unset before install)')
    wanted = dict(sets)
    for key, value in defaults.items():
        current, found = get_path(data, parts[key])
        if not found or current is None or current is False:
            wanted[key] = value
    for key, value in wanted.items():
        name, missing = '.'.join(parts[key]), 0
        for depth in range(1, len(parts[key])):  # Parents count against the document after restoring stale keys.
            node, found = get_path(new, parts[key][:depth])
            if not found:
                missing = len(parts[key]) - depth
                break
            if not isinstance(node, dict):
                plan.refusals.append(f'{plan.show(path)}: {".".join(parts[key][:depth])} is not a JSON object')
                return
        current, found = get_path(data, parts[key])
        record = owned.setdefault(name, {'had': found, 'previous': current})
        if len(parts[key]) > 1:
            record['path'] = list(parts[key])
            record['created_parents'] = max(record.get('created_parents', 0), missing)
        record['set'] = value
        if not found or current != value:
            changes.append(f'set {name} = {json.dumps(value)} (was {json.dumps(current) if found else "unset"})')
        set_path(new, parts[key], value)
    for key in defaults:
        if key not in wanted and '.'.join(parts[key]) not in owned:
            plan.notes.append(f'{plan.show(path)}: {".".join(parts[key])} is already set; left as is')
    out = cur if new == data else dump_json(new, json_style(cur.decode('utf-8') if cur else ''))
    if not owned and not entry and out == cur:
        return
    plan.ops.append({'kind': 'keys', 'group': group, 'path': path, 'rel': rel, 'data': out, 'current': cur,
                     'action': 'unchanged' if out == cur else ('create' if cur is None else 'update keys'),
                     'changes': changes, 'diff': [],
                     'entry': {'format': 'json', 'created': entry['created'] if entry else cur is None,
                               'keys': owned}})


def plan_codex_config(plan, adopt):
    path = plan.home / '.codex' / 'config.toml'
    rel = plan.rel(path)
    entry = plan.old.get('keys', {}).get(rel)
    cur = read_key_file(plan, path)
    if cur is False:
        return
    matched = orca_hook_trust(plan.home, plan.notes)
    old_keys = entry.get('hook_keys', []) if entry else []
    text = cur.decode('utf-8') if cur else ''
    try:
        # An owned trust entry whose hook no longer matches a pinned set keeps its recorded hash, so an Orca
        # hook change is reported instead of silently untrusting the hook; the changed hook gains no trust.
        kept, doc = {}, tomllib.loads(text)
        for key in old_keys:
            value, found = get_path(doc, ('hooks', 'state', key))
            if key not in matched and found and isinstance(value, dict) and isinstance(value.get('trusted_hash'), str):
                kept[key] = {'enabled': value.get('enabled') is not False, 'trusted_hash': value['trusted_hash']}
        if kept:
            plan.notes.append(f'{plan.show(path)}: kept {len(kept)} existing Orca hook trust entr'
                              f'{"y" if len(kept) == 1 else "ies"} whose hook no longer matches a pinned Orca hook '
                              'set; check the Orca hooks and update the pinned set: '
                              + ', '.join(':'.join(key.rsplit(':', 3)[1:]) for key in kept))
        trust = {key: matched.get(key, kept.get(key)) for key in [*old_keys, *matched] if key in matched or key in kept}
        new, moved, adopted, previous = merge_codex_config(text, trust, old_keys)
        domain = codex_managed(list(trust) + old_keys)
        diff = managed_diff(text, new, domain)
    except (Refusal, tomllib.TOMLDecodeError) as error:
        plan.refusals.append(f'{plan.show(path)}: {error}')
        return
    diff_note = ''
    if moved:
        lines = '\n'.join(f'      line {n}: {key}' for n, key in moved)
        if adopt:
            diff = [f'adopt line {n}: {key} (moved into the managed block)' for n, key in moved] + diff
        else:
            plan.refusals.append(f'{plan.show(path)} defines managed keys outside the orca-pod blocks; rerun with '
                                 f'--adopt-config to move them into the blocks:\n{lines}')
            diff_note = ' (as it would be with --adopt-config)'
    previous_adopted = copy.deepcopy(entry.get('adopted', {})) if entry else {}
    for name, original in adopted.items():
        previous_adopted[name] = previous_adopted.get(name, '') + original
    recorded = {json.dumps(list(p)): v for p, v in previous.items()}
    recorded.update(entry.get('previous', {}) if entry else {})  # The first recorded value is the original.
    data = new.encode('utf-8')
    changes = [f'{len(trust)} Orca hook trust entr{"y" if len(trust) == 1 else "ies"} in [hooks.state]'
               + diff_note] if trust else []
    plan.ops.append({'kind': 'keys', 'group': 'codex config', 'path': path, 'rel': rel, 'data': data,
                     'current': cur, 'action': 'unchanged' if data == cur else ('create' if cur is None
                                                                                   else 'update managed blocks'),
                     'changes': changes, 'diff': diff if data != cur else [],
                     'entry': {'format': 'toml', 'created': entry['created'] if entry else cur is None,
                               'adopted': previous_adopted, 'previous': recorded, 'hook_keys': list(trust)}})


def role_model(role_id):
    """The default provider, model and effort of one roster role."""
    roles = tomllib.loads(ROLES.read_text(encoding='utf-8'))['role']
    matches = [role for role in roles if role['id'] == role_id]
    if len(matches) != 1:
        raise Refusal(f'roles.toml has no single role {role_id!r}')
    return matches[0]['models'][0]


def orc_claude_model():
    model = role_model('orc')
    if model['provider'] != 'claude':
        raise Refusal('roles.toml: the ORC default model is not a Claude model')
    if not CLAUDE_MODEL.fullmatch(model['model']):
        raise Refusal(f'roles.toml: the ORC default model {model["model"]!r} is not a plain Claude model id')
    return model['model'], model['effort']


def claude_version():
    result = run('claude', '--version') if shutil.which('claude') else None
    match = re.match(r'\s*(\d+\.\d+\.\d+)', result.stdout) if result and result.returncode == 0 else None
    return match[1] if match else None


def plan_claude(plan):
    model, effort = orc_claude_model()
    # Claude Code reads the session's default effort from modelSettings.<model>.effortLevel; a top-level
    # effortLevel is a legacy value it does not apply at startup.
    plan_json(plan, 'claude settings', plan.home / '.claude' / 'settings.json',
              {'model': model, ('modelSettings', model, 'effortLevel'): effort,
               'skipDangerousModePermissionPrompt': True},
              {'theme': 'dark'})
    # First-run keys only; Orca's "Trust the folder" covers project trust for every agent it launches (#14).
    first_run = {'hasCompletedOnboarding': True}
    version = claude_version()
    if version:
        first_run['lastOnboardingVersion'] = version
    else:
        plan.notes.append('claude is not on PATH, so lastOnboardingVersion is not seeded')
    plan_json(plan, 'claude first run', plan.home / '.claude.json', {}, first_run, keep=('lastOnboardingVersion',))


# ---------- Orca automations ----------

def automation_python():
    """The absolute path of the install-time interpreter, which each automation run uses for its Python helpers."""
    found = shutil.which(PYTHON)
    real = os.path.realpath(found) if found else None  # The link target, so a later repointed link is not used.
    if not real or not os.path.isfile(real) or not os.access(real, os.X_OK):
        raise Refusal(f'the Python interpreter {PYTHON!r} (ORCA_POD_PYTHON, else the installer\'s own) is not an '
                      'executable; an automation run could not use it')
    if not PROMPT_SAFE_PATH.fullmatch(real):  # It is written into unattended prompts, so no newlines or markup.
        raise Refusal(f'the Python interpreter path {real!r} has characters outside letters, digits and ._+-/; '
                      'install it at a plain path or set ORCA_POD_PYTHON to one')
    return real


def automation_definitions():
    """The automations in machine/automations.toml, each run by its roster role's default model and effort. Each
    prompt ends with the install-time interpreter, so a run does not depend on the host's default python3."""
    path = automation_python()
    python = shlex.quote(path)
    python_line = (f'Run this run\'s Python helpers with ORCA_POD_PYTHON={python}, the interpreter the installer '
                   f'resolved: invoke each `.py` script as `{python} <script>` and give each shell script the same '
                   f'setting, as `ORCA_POD_PYTHON={python} <script>`.')
    table = tomllib.loads(AUTOMATIONS.read_text(encoding='utf-8'))
    if set(table) - {'automation'} or not isinstance(table.get('automation', []), list):
        raise Refusal('machine/automations.toml must hold only [[automation]] tables')
    definitions = []
    for entry in table.get('automation', []):
        if not (isinstance(entry, dict) and set(entry) == AUTOMATION_KEYS
                and all(isinstance(value, str) and value.strip() for value in entry.values())):
            raise Refusal('machine/automations.toml: each automation needs exactly '
                          f'{", ".join(sorted(AUTOMATION_KEYS))}, as non-empty text')
        name = entry['name']
        if not automation_name(name) or any(d['name'] == name for d in definitions):
            raise Refusal(f'machine/automations.toml: the automation name {name!r} is invalid or repeated')
        if not CRON.fullmatch(entry['trigger']):
            raise Refusal(f'machine/automations.toml: {name}: {entry["trigger"]!r} is not a 5-field cron expression')
        model = role_model(entry['role'])
        if model['provider'] not in AGENT_ARGS or not all(PLAIN_TOKEN.fullmatch(model[k]) for k in ('model', 'effort')):
            raise Refusal(f'roles.toml: the {entry["role"]} default model cannot run an Orca automation')
        definitions.append({'name': name, 'role': entry['role'], 'trigger': entry['trigger'],
                            'prompt': f'{entry["prompt"].strip()} {python_line}', 'provider': model['provider'],
                            'extra_args': AGENT_ARGS[model['provider']].format(**model), 'python': path})
    return definitions


def orca_cli():
    return shutil.which('orca') or orca_settings_module().ORCA_CLI


def orca_json(*args):
    """Run one `orca ... --json` command and return its result, or raise Refusal with Orca's error."""
    command = ' '.join(args[:2])
    try:
        result = run(orca_cli(), *args, '--json', timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Refusal(f'`orca {command}` failed: {error}')
    try:
        data = json.loads(result.stdout)
    except ValueError:
        data = None
    if not (isinstance(data, dict) and data.get('ok') is True and isinstance(data.get('result'), dict)):
        error = data.get('error') if isinstance(data, dict) else None
        detail = error.get('message') if isinstance(error, dict) else (result.stderr or result.stdout).strip()
        raise Refusal(f'`orca {command}` failed: {detail or f"exit {result.returncode}"}')
    return data['result']


def orca_list(*args, key):
    """The object rows of one list in an `orca ... --json` result."""
    rows = orca_json(*args).get(key)
    if not isinstance(rows, list):
        raise Refusal(f'`orca {" ".join(args[:2])}` returned no {key} list')
    return [row for row in rows if isinstance(row, dict)]


def primary_repo():
    """The Orca repository row of this repository's primary checkout, and that checkout's path."""
    common = Path(subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                                 capture_output=True, text=True, check=True).stdout.strip())
    if common.name != '.git':
        raise Refusal(f'{ROOT} has no primary checkout (its Git directory is {common})')
    primary = common.parent.resolve()
    repos = [repo for repo in orca_list('repo', 'list', key='repos')
             if isinstance(repo.get('path'), str) and Path(repo['path']).resolve() == primary]
    if len(repos) != 1 or not isinstance(repos[0].get('id'), str):
        raise Refusal(f'the primary checkout {primary} is not an Orca repository; add it with '
                      f'`orca repo add --path {primary}` and rerun')
    return repos[0], primary


def primary_workspace():
    """The Orca worktree (id, path) of this repository's primary checkout."""
    repo, primary = primary_repo()
    mains = [tree for tree in orca_list('worktree', 'list', '--repo', f'id:{repo["id"]}', key='worktrees')
             if tree.get('isMainWorktree') is True and tree.get('repoId') == repo['id']]
    if len(mains) != 1 or not all(isinstance(mains[0].get(k), str) for k in ('id', 'path')):
        raise Refusal(f'Orca lists no single main worktree for {primary}')
    return mains[0]['id'], mains[0]['path']


def automation_changes(current, definition):
    """The managed fields in which a live Orca automation differs from its definition."""
    wanted = {'name': definition['name'], 'prompt': definition['prompt'], 'agentId': definition['provider'],
              'extraAgentArgs': definition['extra_args'], 'rrule': definition['trigger'],
              'workspaceMode': 'existing', 'workspaceId': definition['workspace_id'], 'reuseSession': False}
    return [field for field, value in wanted.items() if current.get(field) != value]


def host_timezone():
    """The host's IANA timezone, which Orca gives a new automation, or None when /etc/localtime names none."""
    path = os.path.realpath('/etc/localtime')
    return path.split('/zoneinfo/', 1)[1] if '/zoneinfo/' in path else None


def unmanaged_options(current):
    """The execution-affecting options of a live Orca automation that automations.toml does not declare and that
    are set to other than what `orca automations create` gives a new one."""
    defaults = {'precheck': None, 'timezone': host_timezone(), 'missedRunGraceMinutes': ORCA_MISSED_RUN_GRACE,
                'executionTargetType': 'local', 'baseBranch': None, 'setupDecision': None}
    return [field for field, value in defaults.items()
            if current.get(field) is not None and (value is None or current[field] != value)]


def name_mismatch(name, record_id, current):
    return (f'the manifest records "{name}" as the Orca automation {record_id}, but Orca names that automation '
            f'{json.dumps(current.get("name"))}; Orca Pod does not change or remove an automation whose name does '
            'not match its record. Rename it back in Orca, or remove its record from the manifest, then rerun')


def confirm_live(record_id, name):
    """Re-read an owned automation immediately before changing it, refusing unless its name still matches."""
    current = orca_json('automations', 'show', '--id', record_id).get('automation')
    if not isinstance(current, dict) or current.get('id') != record_id:
        raise Refusal(f'`orca automations show` returned no automation {record_id}')
    if current.get('name') != name:
        raise Refusal(name_mismatch(name, record_id, current))


def automation_args(definition):
    """The `orca automations create/edit` flags that set every managed field."""
    return ['--name', definition['name'], '--prompt', definition['prompt'], '--provider', definition['provider'],
            f'--extra-agent-args={definition["extra_args"]}', '--trigger', definition['trigger'],
            '--workspace', f'id:{definition["workspace_id"]}', '--workspace-mode', 'existing', '--fresh-session']


def plan_automations(plan, args):
    """Plan the managed automations against Orca's live list. A scratch run, or --skip-orca-settings, only lists
    them and never reads or changes the live Orca."""
    definitions = automation_definitions()
    if args.scratch or args.skip_orca_settings:
        action, reason = ('planned', 'not created: scratch --home run') if args.scratch else ('skip', '--skip-orca-settings')
        plan.automations = [{'action': action, 'name': d['name'], 'definition': d, 'reason': reason} for d in definitions]
        return
    owned = plan.old.get('automations', {})
    owned_ids = {record['id'] for record in owned.values()}
    workspace_id, workspace_path = primary_workspace()
    live = orca_list('automations', 'list', key='automations')
    by_id = {entry.get('id'): entry for entry in live}
    ops = []
    for definition in definitions:
        definition = {**definition, 'workspace_id': workspace_id, 'workspace_path': workspace_path}
        name, record = definition['name'], owned.get(definition['name'])
        current = by_id.get(record['id']) if record else None
        if current is not None and current.get('name') != name:
            plan.refusals.append(name_mismatch(name, record['id'], current))
            continue
        if current is not None:
            changes = automation_changes(current, definition)
            ops.append({'action': 'update' if changes else 'unchanged', 'name': name, 'id': record['id'],
                        'definition': definition, 'changes': changes})
            if current.get('enabled') is False:
                plan.notes.append(f'the Orca automation "{name}" is disabled in Orca; left disabled')
            continue
        if record:
            plan.notes.append(f'the recorded Orca automation "{name}" ({record["id"]}) is gone from Orca; '
                              'it is created again')
        same = [entry for entry in live if entry.get('name') == name and entry.get('id') not in owned_ids]
        if not same:
            ops.append({'action': 'create', 'name': name, 'definition': definition, 'changes': []})
        elif len(same) == 1 and AUTOMATION_ID.fullmatch(str(same[0].get('id'))) \
                and not automation_changes(same[0], definition) and not unmanaged_options(same[0]):
            ops.append({'action': 'adopt (identical)', 'name': name, 'id': same[0]['id'], 'definition': definition,
                        'changes': []})
        else:
            differs = automation_changes(same[0], definition) if len(same) == 1 else []
            unmanaged = unmanaged_options(same[0]) if len(same) == 1 else []
            plan.refusals.append(
                f'Orca already has {len(same)} automation(s) named "{name}" that Orca Pod does not own ('
                + ', '.join(str(entry.get('id')) for entry in same) + ')'
                + (f', differing in {", ".join(differs)}' if differs else '')
                + (f'{" and" if differs else ","} setting {", ".join(unmanaged)}, which automations.toml does not '
                   'declare and Orca Pod neither adopts nor clears' if unmanaged else '')
                + '; rename or remove them in Orca, then rerun')
    names = {d['name'] for d in definitions}
    for name, record in owned.items():
        if name in names:
            continue
        if record['adopted'] or record['id'] not in by_id:
            reason = 'adopted; left in Orca' if record['adopted'] else 'already gone from Orca'
            ops.append({'action': 'forget', 'name': name, 'id': record['id'], 'reason': f'no longer managed; {reason}'})
        elif by_id[record['id']].get('name') != name:
            plan.refusals.append(name_mismatch(name, record['id'], by_id[record['id']]))
        else:
            ops.append({'action': 'remove', 'name': name, 'id': record['id'], 'reason': 'no longer managed'})
    plan.automations = ops


def plan_base_ref(plan, args):
    """Plan the primary checkout's Orca default base ref. It is the Standard's repository setting, not an installed
    artifact, so the manifest does not record it and --uninstall leaves it set."""
    if args.scratch or args.skip_orca_settings:
        plan.base_ref = {'action': 'planned' if args.scratch else 'skip',
                         'reason': 'not set: scratch --home run' if args.scratch else '--skip-orca-settings'}
        return
    repo, primary = primary_repo()
    current = repo.get('worktreeBaseRef')
    plan.base_ref = {'action': 'unchanged' if current == BASE_REF else 'set', 'repo_id': repo['id'],
                     'primary': str(primary), 'current': current}


def apply_base_ref(plan):
    """Set the primary checkout's Orca default base ref, then confirm it with `orca repo show`."""
    op = plan.base_ref
    if not op or op['action'] != 'set':
        return True
    try:
        orca_json('repo', 'set-base-ref', '--repo', f'id:{op["repo_id"]}', '--ref', BASE_REF)
        repo = orca_json('repo', 'show', '--repo', f'id:{op["repo_id"]}').get('repo')
        current = repo.get('worktreeBaseRef') if isinstance(repo, dict) else None
        if current != BASE_REF:
            raise Refusal(f'`orca repo show` reads back {json.dumps(current)}, not {BASE_REF}')
    except Refusal as error:
        print(f'Orca default base ref: FAILED: {error}')
        return False
    print(f'Orca default base ref: set to {BASE_REF} for {op["primary"]}')
    return True


def apply_automations(plan, writer, manifest):
    """Carry out the planned automation changes, recording each owned id in the manifest as soon as it changes."""
    ok, records = True, manifest.setdefault('automations', {})
    for op in plan.automations:
        action, name = op['action'], op['name']
        if action in ('unchanged', 'planned', 'skip'):
            continue
        try:
            if action == 'create':
                created = orca_json('automations', 'create', *automation_args(op['definition']), '--enabled')
                automation = created.get('automation')
                new_id = automation.get('id') if isinstance(automation, dict) else None
                if not (isinstance(new_id, str) and AUTOMATION_ID.fullmatch(new_id)):
                    raise Refusal(f'Orca returned no automation id ({new_id!r})')
                records[name] = {'id': new_id, 'adopted': False}
                done = f'created {new_id}'
            elif action == 'update':
                confirm_live(op['id'], name)
                orca_json('automations', 'edit', '--id', op['id'], *automation_args(op['definition']))
                done = f'updated {op["id"]} ({", ".join(op["changes"])})'
            elif action.startswith('adopt'):
                records[name] = {'id': op['id'], 'adopted': True}
                done = f'adopted {op["id"]}'
            else:
                if action == 'remove':
                    confirm_live(op['id'], name)
                    orca_json('automations', 'remove', '--id', op['id'])
                del records[name]
                done = f'{"removed" if action == "remove" else "forgot"} {op["id"]} ({op["reason"]})'
        except Refusal as error:
            print(f'Orca automation "{name}": FAILED: {error}')
            ok = False
            continue
        print(f'Orca automation "{name}": {done}')
        write_manifest(writer, manifest)
    return ok


def uninstall_automations(old, args):
    """Remove the automations Orca Pod created, before any other uninstall step; adopted ones stay in Orca. Returns
    the refusals found before any removal and the failures of attempted removals."""
    records = old.get('automations', {})
    created = {name: record for name, record in sorted(records.items()) if not record['adopted']}
    if created and (args.scratch or args.skip_orca_settings):
        names = ', '.join(f'"{name}"' for name in created)
        rerun = 'for the real home' if args.scratch else 'without --skip-orca-settings'
        return [f'the Orca automations Orca Pod created ({names}) cannot be checked or removed '
                f'{"from a scratch --home run" if args.scratch else "with --skip-orca-settings"}; '
                f'rerun --uninstall {rerun}'], []
    live = {}
    if created:
        try:
            live = {entry.get('id'): entry for entry in orca_list('automations', 'list', key='automations')}
        except Refusal as error:
            return [f'the Orca automations Orca Pod created cannot be checked: {error}'], []
    mismatched = [name_mismatch(name, record['id'], live[record['id']]) for name, record in created.items()
                  if record['id'] in live and live[record['id']].get('name') != name]
    if mismatched:
        return mismatched, []
    failures = []
    for name, record in created.items():
        if record['id'] not in live:
            print(f'  gone         Orca automation "{name}" (already removed from Orca)')
            continue
        try:
            confirm_live(record['id'], name)
            orca_json('automations', 'remove', '--id', record['id'])
            print(f'  removed      Orca automation "{name}" ({record["id"]})')
        except Refusal as error:
            failures.append(f'Orca automation "{name}" not removed: {error}')
    if not failures:
        for name in sorted(set(records) - set(created)):
            print(f'  kept         Orca automation "{name}" (adopted, not created by Orca Pod)')
    return [], failures


def build_plan(home, old, args):
    plan = Plan(home, old)
    for path, leaf_dir in ((home / STATE, True), (home / STATE / 'backups', True), (home / STATE / 'manifest.json', False)):
        plan.check(path, leaf_dir)
    for step in (plan_skills, plan_roles, plan_rules, lambda p: plan_codex_config(p, args.adopt_config),
                 plan_claude, plan_stale, lambda p: plan_automations(p, args), lambda p: plan_base_ref(p, args)):
        try:
            step(plan)
        except (Refusal, ValueError, OSError, subprocess.CalledProcessError) as error:
            if str(error) not in plan.refusals:  # The automations and base ref share the primary checkout lookup.
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
    print_automations(plan)
    print_base_ref(plan)
    if not args.scratch:
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


def print_automations(plan):
    for op in plan.automations:
        definition = op.get('definition')
        detail = f' ({op["reason"]})' if op.get('reason') else f' {op["id"]}' if op.get('id') else ''
        print(f'  {op["action"]:<12} automation "{op["name"]}"{detail}')
        if definition and op['action'] != 'unchanged':
            workspace = definition.get('workspace_path', 'the primary checkout (not resolved on this run)')
            print(f'      {definition["provider"]} {definition["extra_args"]} (roster {definition["role"]}); '
                  f'cron "{definition["trigger"]}"; workspace {workspace} (existing); fresh session per run; '
                  f'Python helpers {definition["python"]}')
        if op.get('changes'):
            print(f'      changes: {", ".join(op["changes"])}')


def print_base_ref(plan):
    op = plan.base_ref
    if not op:
        return
    if op.get('reason'):
        detail = f' ({op["reason"]})'
    elif op['action'] == 'set':
        detail = f' for {op["primary"]} (was {json.dumps(op["current"]) if op["current"] else "unset"})'
    else:
        detail = f' for {op["primary"]}'
    print(f'  {op["action"]:<12} Orca default base ref {BASE_REF}{detail}')


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
    """Contained filesystem changes under home, with private backups and created-directory bookkeeping.

    Every operation rechecks containment first, and every file is written to an exclusively created
    temporary name in the same directory, then atomically renamed into place.
    """

    def __init__(self, home, stamp, dirs):
        self.home = home
        self.state = home / STATE
        self.backup_root = self.state / 'backups' / stamp
        self.dirs = list(dirs)
        self.saved = {}
        self.changed = 0

    def check(self, path, leaf_dir=False):
        check_path(self.home, path, leaf_dir)

    def ensure_dir(self, path, private=False, record=True):
        self.check(path, leaf_dir=True)
        missing = []
        while not os.path.lexists(path):
            missing.append(path)
            path = path.parent
        for path in reversed(missing):
            path.mkdir(mode=0o700 if private else 0o777)
            if private:
                os.chmod(path, 0o700)
            rel = path.relative_to(self.home).as_posix()
            if record and rel not in self.dirs:
                self.dirs.append(rel)

    def state_dir(self):
        """The private (0700) state directory, created when missing."""
        self.ensure_dir(self.state)
        os.chmod(self.state, 0o700)
        return self.state

    def write(self, path, data, mode):
        temp = path.with_name(f'.{path.name}.orca-pod-{secrets.token_hex(8)}.tmp')
        if data.startswith(b'symlink:'):
            os.symlink(data[8:].decode(), temp)
        else:
            fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            try:
                with open(fd, 'wb') as handle:
                    handle.write(data)
                os.chmod(temp, mode)
            except BaseException:
                os.unlink(temp)
                raise
        os.replace(temp, path)

    def backup(self, path):
        """Copy a whole owned file or link privately into this run's backups; return its manifest pointer."""
        self.check(path)
        dest = self.backup_root / path.relative_to(self.home)
        if dest in self.saved:
            return self.saved[dest]
        data = current_bytes(path)
        if data is None:
            return None
        self.state_dir()  # Backup directories themselves are never owned or pruned.
        self.ensure_dir(dest.parent, private=True, record=False)
        mode = None if data.startswith(b'symlink:') else stat.S_IMODE(os.lstat(path).st_mode)
        self.write(dest, data, 0o600)
        self.saved[dest] = {'path': dest.relative_to(self.state).as_posix(), 'mode': mode}
        return self.saved[dest]

    def put(self, path, data, mode=None):
        """Atomically replace path with bytes, or with a symlink when data starts with b'symlink:'."""
        self.check(path)
        if os.path.isdir(path) and not os.path.islink(path):
            raise Refusal(f'{path} is a directory')
        if os.path.lexists(path):
            single_link(path, os.lstat(path))
        self.ensure_dir(path.parent)
        self.write(path, data, mode if mode is not None else 0o644)
        self.changed += 1

    def restore(self, path, pointer):
        src = self.state / pointer['path']
        self.check(src)
        data = current_bytes(src)
        if data is None:
            raise Refusal(f'the backup {src} is missing')
        self.put(path, data, pointer.get('mode'))

    def remove(self, path):
        self.check(path)
        data = current_bytes(path)
        if data is not None:
            path.unlink()
            self.changed += 1

    def prune_dirs(self, rels, empty_only=False):
        """Remove the listed created directories, deepest first, when empty.

        Return those still present, or with empty_only, those removed (or already gone).
        """
        kept, gone = [], []
        for rel in sorted(rels, key=lambda r: r.count('/'), reverse=True):
            try:
                self.check(self.home / rel, leaf_dir=True)
                (self.home / rel).rmdir()
                gone.append(rel)
            except FileNotFoundError:
                gone.append(rel)
            except (OSError, Refusal):
                kept.append(rel)
        return gone if empty_only else kept


def write_manifest(writer, manifest):
    """Write the manifest privately through an exclusively created temporary file and an atomic rename."""
    state = writer.state_dir()
    path = state / 'manifest.json'
    writer.check(path)
    fd, temp = tempfile.mkstemp(dir=state, prefix='.manifest-', suffix='.tmp')
    try:
        with open(fd, 'w', encoding='utf-8') as handle:
            handle.write(json.dumps(manifest, indent=2, sort_keys=True, default=str) + '\n')
        os.replace(temp, path)
    except BaseException:
        if os.path.lexists(temp):
            os.unlink(temp)
        raise


def apply(plan, args, source, stamp):
    old = plan.old
    writer = Writer(plan.home, stamp, old.get('dirs', []))
    # Start from the previous records so a failure part way keeps ownership of paths not yet processed.
    manifest = {'version': MANIFEST_VERSION, 'files': copy.deepcopy(old.get('files', {})),
                'keys': copy.deepcopy(old.get('keys', {}))}
    if old.get('orca_settings'):
        manifest['orca_settings'] = old['orca_settings']
    if 'automations' in old:
        manifest['automations'] = copy.deepcopy(old['automations'])
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
                # Key-managed files hold credentials and private state, so they are never copied: the
                # manifest records only the previous values of the owned keys and blocks. No whole-file hash
                # is kept, since other programs add content that uninstall must not take for its own.
                if op['data'] != op['current']:
                    mode = stat.S_IMODE(os.lstat(path).st_mode) if os.path.lexists(path) else \
                        0o644 if path.name == 'settings.json' else 0o600
                    writer.put(path, op['data'], mode)
                manifest['keys'][op['rel']] = entry
        writer.dirs = [rel for rel in writer.dirs if rel not in writer.prune_dirs(writer.dirs, empty_only=True)]
    finally:
        writer.state_dir()
        manifest['dirs'] = writer.dirs
        manifest['source'] = {'revision': source['revision'], 'dirty': source['dirty']}
        if {k: v for k, v in old.items() if k != 'applied_at'} != manifest:
            manifest['applied_at'] = time.strftime('%Y-%m-%dT%H:%M:%S%z')
            write_manifest(writer, manifest)
    return writer, manifest


def orca_settings_module():
    sys.path.insert(0, str(ORCA_SETTINGS.parent))
    import orca_settings
    return orca_settings


def patch_orca(writer, patch, stamp):
    """Run machine/orca_settings.py detached (it quits and relaunches Orca) and wait on its result file.

    Return the helper's result, or a failure without `written` when it does not finish in time.
    """
    state = writer.state_dir()
    result_path, log_path = state / f'orca-settings-{stamp}.json', state / f'orca-settings-{stamp}.log'
    backup = writer.backup_root / 'orca-settings.json'
    writer.ensure_dir(backup.parent, private=True, record=False)
    for path in (result_path, log_path, backup):
        writer.check(path)
    fd, temp = tempfile.mkstemp(dir=state, prefix='.orca-settings-log-', suffix='.tmp')
    os.replace(temp, log_path)
    with open(fd, 'wb') as log:
        subprocess.Popen([PYTHON, str(ORCA_SETTINGS), '--patch', json.dumps(patch), '--result', str(result_path),
                          '--backup', str(backup)],
                         stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    print(f'Orca app settings: the detached helper quits, patches and relaunches Orca; waiting on {result_path}')
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        try:
            result = json.loads(read_regular(result_path, links_ok=True))
            if 'ok' in result:
                detail = result.get('after') if result['ok'] else result.get('error')
                print(f'Orca app settings: {"ok" if result["ok"] else "FAILED"} {json.dumps(detail)}'
                      + (f'; restored: {result.get("restore_verified", False)}' if result.get('written') else ''))
                return result
        except (FileNotFoundError, ValueError):
            pass
        time.sleep(2)
    print('Orca app settings: the helper did not finish within 10 minutes; check its result file and log')
    return {'ok': False, 'timeout': True}


def record_orca_patch(writer, manifest, pre, patch):
    """Record the previous Orca values before the helper starts; return the record set in the manifest."""
    earlier = copy.deepcopy(manifest.get('orca_settings'))
    record = copy.deepcopy(earlier) if earlier else {}
    record['previous'] = {**pre['before'], **record.get('previous', {})}  # Keep the first original values.
    record.update(set=dict(patch), status='pending', app_version=pre['app_version'],  # The version is informational.
                  domain_version=pre['domain_version'],
                  backup=(writer.backup_root / 'orca-settings.json').relative_to(writer.state).as_posix())
    manifest['orca_settings'] = record
    write_manifest(writer, manifest)
    return earlier


def settle_orca_record(writer, manifest, result, earlier):
    """Keep the restoration record until the settings are verified as applied or verified as restored."""
    if result.get('ok'):
        manifest['orca_settings']['status'] = 'applied'
    elif result.get('timeout'):
        manifest['orca_settings']['status'] = 'unverified'
    elif not result.get('written') or result.get('restore_verified'):
        if earlier:
            manifest['orca_settings'] = earlier
        else:
            manifest.pop('orca_settings', None)
    else:
        manifest['orca_settings']['status'] = 'failed'
    write_manifest(writer, manifest)


def orca_steps(plan, args, writer, manifest, stamp):
    """Install Orca's own skills, apply the managed automations and default base ref, then patch Orca's app settings,
    recording owned automation ids and previous settings values in the manifest."""
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
    ok &= apply_automations(plan, writer, manifest)  # Before the settings patch, which restarts Orca.
    ok &= apply_base_ref(plan)
    pre = orca_settings_module().preflight(ORCA_PATCH)
    if not pre['ok']:
        print(f'Orca app settings refused: {pre["error"]}')
        return False
    if not pre['changes']:
        print('Orca app settings already match.')
        record = manifest.get('orca_settings')
        seen = {'app_version': pre['app_version'], 'domain_version': pre['domain_version']}
        if record and any(record.get(k) != v for k, v in seen.items()):  # Note the versions it was last seen on.
            record.update(seen)
            write_manifest(writer, manifest)
        return ok
    earlier = record_orca_patch(writer, manifest, pre, ORCA_PATCH)
    result = patch_orca(writer, ORCA_PATCH, stamp)
    settle_orca_record(writer, manifest, result, earlier)
    return ok and result.get('ok', False)


# ---------- Uninstall ----------

def uninstall_preflight(home, old):
    """Containment-check every path the manifest names before anything is written."""
    problems = []

    def check(path, leaf_dir=False, links=False):
        try:
            check_path(home, path, leaf_dir)
            if links and os.path.lexists(path):
                single_link(path, os.lstat(path))
        except Refusal as error:
            problems.append(str(error))

    for rel, entry in old.get('files', {}).items():
        check(home / rel, links=True)
        if entry.get('backup'):
            check(home / STATE / entry['backup']['path'], links=True)
    for rel in old.get('keys', {}):
        check(home / rel, links=True)
        if os.path.islink(home / rel):
            problems.append(f'~/{rel} is a symlink; refusing to replace it')
    for rel in old.get('dirs', []):
        check(home / rel, leaf_dir=True)
    for path in (home / STATE, home / STATE / 'backups'):
        check(path, leaf_dir=True)
    return list(dict.fromkeys(problems))


def uninstall(home, old, args, stamp):
    refused = uninstall_preflight(home, old)
    if refused:
        print(f'REFUSED ({len(refused)}); --uninstall writes nothing until these are resolved:')
        for problem in refused:
            print(f'  - {problem}')
        return 2
    print(f'Orca Pod uninstall from {home}')
    # The automations go first: a schedule left in Orca after its skills and rules are removed would keep running
    # without them, so a refused or failed removal stops the uninstall with every file and the manifest in place.
    refused, failed = uninstall_automations(old, args)
    if refused or failed:
        print(f'{"REFUSED" if refused else "STOPPED"}: --uninstall changed no files, keys or Orca settings and kept '
              'the manifest; resolve these, then rerun:')
        for problem in refused + failed:
            print(f'  - {problem}')
        return 2 if refused else 1
    writer = Writer(home, stamp, [])
    problems = []
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
        cur = current_bytes(path)
        if cur is None:
            continue
        # The owned keys are always removed first; a file the installer created is deleted only when nothing
        # else is left in it, never on the strength of a whole-file hash.
        try:
            if entry['format'] == 'json':
                data = json.loads(cur)
                if not isinstance(data, dict):
                    raise ValueError('not a JSON object')
                before = copy.deepcopy(data)
                for key, record in entry['keys'].items():
                    restore_key(data, record.get('path', [key]), record)
                new = cur if data == before else dump_json(data, json_style(cur.decode('utf-8')))
                empty = data == {}
            else:
                previous = {tuple(json.loads(p)): v for p, v in entry.get('previous', {}).items()}
                new = unmerge_codex_config(cur.decode('utf-8'), entry.get('adopted', {}),
                                           entry.get('hook_keys', []), previous).encode('utf-8')
                empty = not new.strip()
        except (ValueError, Refusal) as error:
            problems.append(f'~/{rel}: could not remove the managed keys ({error}); left as is')
            continue
        if entry['created'] and empty:
            writer.remove(path)
            print(f'  removed      ~/{rel} (only managed keys were left)')
            continue
        if new != cur:
            writer.put(path, new, stat.S_IMODE(os.lstat(path).st_mode))
            print(f'  removed keys ~/{rel} (restored the previous values of the managed keys)')
        if entry['created']:
            print(f'  kept         ~/{rel} (created by the installer, but it now holds content Orca Pod does not own)')
    settings = old.get('orca_settings')
    if settings and not args.scratch and not args.skip_orca_settings:
        pre = orca_settings_module().preflight(settings['previous'])
        if not pre['ok']:
            problems.append(f'Orca app settings not restored: {pre["error"]}')
        elif pre['before'] == settings['previous']:
            print('Orca app settings already have their previous values')
        elif pre['before'] != settings['set']:
            print('Orca app settings changed since install; left as they are')
        elif not patch_orca(writer, settings['previous'], stamp).get('ok'):
            # The kept incomplete manifest still holds the previous values for a later restore.
            problems.append(f'Orca app settings not restored to {json.dumps(settings["previous"])}')
    kept = writer.prune_dirs(old.get('dirs', []))
    manifest = home / STATE / 'manifest.json'
    if problems:  # Keep the ownership record next to the backups for manual recovery.
        os.replace(manifest, manifest.with_name(f'manifest-{stamp}.incomplete.json'))
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


def load_manifest(home):
    path = home / STATE / 'manifest.json'
    check_path(home, path)
    data = current_bytes(path)
    if data is None:
        return {}
    if data.startswith(b'symlink:'):
        raise Refusal(f'{path} is a symlink')
    def finite(constant):
        raise ValueError(f'non-finite number {constant}')

    try:
        old = json.loads(data, parse_constant=finite)
    except (ValueError, RecursionError) as error:
        raise Refusal(f'{path} is not valid JSON ({error})')
    if not isinstance(old, dict):
        raise Refusal(f'{path} is not a JSON object')
    if old.get('version') != MANIFEST_VERSION:
        raise Refusal(f'{path} has unknown version {old.get("version")}')
    validate_manifest(old)
    return old


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
    parser.add_argument('--skip-orca-settings', action='store_true',
                        help="leave Orca's app settings, automations and default base ref alone")
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
    try:
        old = load_manifest(home)
    except (Refusal, ValueError, OSError, RecursionError) as error:
        print(f'install.py: REFUSED: {error}')
        return 2
    stamp = time.strftime('%Y%m%dT%H%M%S') + f'-{os.getpid()}'
    if args.uninstall:
        if not old:
            print(f'Nothing to uninstall: no manifest at {home / STATE / "manifest.json"}')
            return 0
        return uninstall(home, old, args, stamp)
    try:
        source = source_state(args.allow_unpublished)
    except Refusal as error:
        print(f'install.py: REFUSED: {error}')
        return 2
    plan = build_plan(home, old, args)
    print_plan(plan, args, source)
    if plan.refusals:
        return 2
    if not args.apply:
        print('Dry run complete; rerun with --apply to install.')
        return 0
    writer, manifest = apply(plan, args, source, stamp)
    print(f'\nApplied: {writer.changed} change(s).' if writer.changed else
          '\nNo changes: the managed targets are current.')
    ok = orca_steps(plan, args, writer, manifest, stamp)
    sign_in(args)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
