#!/usr/bin/env python3
"""Apply Orca app settings while Orca is quit (macOS); see docs/install.md.

The installer launches this helper detached and waits on its --result file. It quits Orca.app
gracefully, saves the previous `settings` document (payload, content_hash, revision, updated_at) to a
new private --backup file, patches that document, relaunches Orca, waits for the runtime, verifies the
patch survived and writes a JSON result. On any failure after the write it restores the saved document
before Orca starts, quitting Orca again first when the failure is found after the relaunch, and reports
whether the restore was verified. Orca is never force-killed. The gate is the settings schema, not the
app version: an unsupported settings domain_version, or a target key that is missing or has an unexpected
type or value, is refused with nothing changed; the app version is only recorded. Agent sessions run under
Orca's terminal host, so they survive the restart.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time

APP = '/Applications/Orca.app'
APP_BIN = APP + '/Contents/MacOS/Orca'
ORCA_CLI = APP + '/Contents/Resources/bin/orca'
DB = Path('~/Library/Application Support/orca/profiles/local-default/profile-state.db').expanduser()
SUPPORTED_DOMAIN_VERSIONS = {1}  # Settings document versions verified in jdip/orca-pod#6 and #38.
# The settings keys the helper may set, with the type and, where Orca defines a closed set, the values Orca accepts
# (verified against Orca 1.4.240 and 1.4.241). The current and new values must both fit.
SETTINGS_SHAPE = {'branchPrefix': (str, {'git-username', 'custom', 'none'}),
                  'branchPrefixCustom': (str, None),
                  'agentPermissionDefault': (str, {'own', 'ask', 'accept-edits', 'auto', 'full-access'})}
MANUAL = 'set them by hand in Orca Settings instead'
FIELDS = ('domain_version', 'revision', 'payload', 'content_hash', 'updated_at')


def app_version():
    out = subprocess.run(['defaults', 'read', APP + '/Contents/Info.plist', 'CFBundleShortVersionString'],
                         capture_output=True, text=True)
    return out.stdout.strip()


def orca_running():
    return subprocess.run(['pgrep', '-f', APP_BIN], capture_output=True).returncode == 0


def read_settings(conn):
    """The settings document row as {field: value}."""
    row = conn.execute(f"select {', '.join(FIELDS)} from profile_state_documents where domain='settings'").fetchone()
    if row is None:
        raise RuntimeError('the profile store has no settings document')
    return dict(zip(FIELDS, row))


def schema_error(domain_version, current, patch):
    """Why the settings document does not have the verified shape for patch, or None when it does."""
    if domain_version not in SUPPORTED_DOMAIN_VERSIONS:
        return f'unsupported settings domain_version {domain_version}'
    unknown = [k for k in patch if k not in SETTINGS_SHAPE or k not in current]
    if unknown:
        return f'refusing unknown settings keys {unknown}'
    for key, value in patch.items():
        kind, allowed = SETTINGS_SHAPE[key]
        for label, v in (('current', current[key]), ('new', value)):
            if type(v) is not kind or (allowed is not None and v not in allowed):
                return f'unexpected {label} value {json.dumps(v)} for settings key {key!r}'
    return None


def preflight(patch):
    """Read-only gate: return {ok, error?, app_version, domain_version, revision, before, changes}."""
    info = {'ok': False, 'app_version': app_version() if Path(APP).exists() else None}
    if info['app_version'] is None:
        return {**info, 'error': f'{APP} is not installed'}
    if not DB.exists():
        return {**info, 'error': f'no Orca profile store at {DB}; launch Orca once first'}
    conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    try:
        doc = read_settings(conn)
    finally:
        conn.close()
    cur = json.loads(doc['payload'])
    dv = doc['domain_version']
    info.update(domain_version=dv, revision=doc['revision'], before={k: cur.get(k) for k in patch})
    error = schema_error(dv, cur, patch)
    if error:
        return {**info, 'error': f'{error} (Orca {info["app_version"]}); {MANUAL}'}
    info['changes'] = {k: v for k, v in patch.items() if cur.get(k) != v}
    return {**info, 'ok': True}


def wait(pred, timeout, step=1.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if pred():
            return True
        time.sleep(step)
    return pred()


def runtime_ready():
    out = subprocess.run([ORCA_CLI, 'status', '--json'], capture_output=True, text=True)
    try:
        return json.loads(out.stdout)['result']['runtime']['state'] == 'ready'
    except (ValueError, KeyError, TypeError):
        return False


def quit_orca():
    """Quit gracefully and wait; never force-kill."""
    subprocess.run(['osascript', '-e', 'tell application "Orca" to quit'], capture_output=True)
    if not wait(lambda: not orca_running(), 90):
        return False
    time.sleep(2)  # Let the store settle after Orca's final flush.
    return True


def restore(saved):
    """Write the saved settings document back while Orca is quit; return whether it reads back intact."""
    try:
        conn = sqlite3.connect(DB)
        try:
            with conn:
                conn.execute('update profile_state_documents set payload=?, content_hash=?, revision=?, updated_at=? '
                             "where domain='settings'",
                             (saved['payload'], saved['content_hash'], saved['revision'], saved['updated_at']))
            return read_settings(conn) == saved
        finally:
            conn.close()
    except (sqlite3.Error, RuntimeError):
        return False


def write_private(path, text):
    """Create path exclusively as an owner-only file; never follow or replace an existing name."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with open(fd, 'w', encoding='utf-8') as handle:
        handle.write(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--patch', required=True, help='JSON object of top-level settings keys to set')
    ap.add_argument('--result', required=True, type=Path, help='JSON result file the caller waits on')
    ap.add_argument('--backup', required=True, type=Path,
                    help='new file, created owner-only, that receives the previous settings document')
    ap.add_argument('--dry-run', action='store_true', help='run the read-only preflight only')
    a = ap.parse_args()
    patch = json.loads(a.patch)
    res = {'started': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'patch': patch, 'written': False, 'steps': []}

    def save():
        fd, temp = tempfile.mkstemp(dir=a.result.parent, prefix=f'.{a.result.name}.', suffix='.tmp')
        with open(fd, 'w', encoding='utf-8') as handle:
            handle.write(json.dumps(res, indent=2) + '\n')
        os.replace(temp, a.result)

    def step(name, **kw):
        res['steps'].append({'t': round(time.monotonic(), 1), 'step': name, **kw})
        save()

    def finish(ok, **kw):
        res.update(ok=ok, finished=time.strftime('%Y-%m-%dT%H:%M:%S%z'), **kw)
        save()
        sys.exit(0 if ok else 1)

    pre = preflight(patch)
    res['before'] = pre.get('before')
    if not pre['ok']:
        finish(False, error=pre['error'])
    step('preflight', app_version=pre['app_version'], domain_version=pre['domain_version'],
         revision=pre['revision'])
    if not pre['changes']:
        finish(True, unchanged=True)
    if a.dry_run:
        finish(True, dry_run=True)

    # 1. Quit gracefully; never force-kill.
    if not quit_orca():
        finish(False, error='Orca did not quit within 90s; nothing was changed')
    step('quit')

    saved = None
    try:
        # 2. Save only the settings document, privately, then patch it in one transaction.
        conn = sqlite3.connect(DB)
        try:
            saved = read_settings(conn)
            cur = json.loads(saved['payload'])
            error = schema_error(saved['domain_version'], cur, patch)
            if error:
                raise RuntimeError(f'the settings document no longer fits the verified shape: {error}')
            write_private(a.backup, json.dumps(saved) + '\n')
            step('backup', path=str(a.backup))
            cur.update(patch)
            payload = json.dumps(cur, separators=(',', ':'), ensure_ascii=False)
            with conn:
                changed = conn.execute(
                    'update profile_state_documents set payload=?, content_hash=?, revision=?, updated_at=? '
                    "where domain='settings' and revision=?",
                    (payload, hashlib.sha256(payload.encode()).hexdigest(), saved['revision'] + 1,
                     int(time.time() * 1000), saved['revision'])).rowcount
            if changed != 1:
                raise RuntimeError('the settings document changed while Orca was quit')
            res['written'] = True
            ok_ic = conn.execute('pragma integrity_check').fetchone()[0]
        finally:
            conn.close()
        step('write', new_revision=saved['revision'] + 1, integrity=ok_ic)
        if ok_ic != 'ok':
            raise RuntimeError('integrity_check failed: ' + ok_ic)
    except Exception as e:  # Restore before Orca starts.
        verified = restore(saved) if res['written'] else None
        if res['written']:
            step('restored', verified=verified)
        subprocess.run(['open', APP])
        finish(False, error=f'write failed: {e}', restore_verified=verified)

    # 3. Relaunch and wait for the runtime.
    subprocess.run(['open', APP])
    ready = wait(runtime_ready, 180, 2)
    step('relaunch', runtime_ready=ready)
    time.sleep(5)

    # 4. Verify the patch survived Orca's startup.
    conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    try:
        doc = read_settings(conn)
    finally:
        conn.close()
    after = json.loads(doc['payload'])
    res['after'] = {k: after.get(k) for k in patch}
    survived = all(after.get(k) == v for k, v in patch.items())
    if ready and survived:
        finish(True, runtime_ready=ready, survived=survived, revision_after=doc['revision'])

    # 5. Roll back: quit Orca again, restore the saved document before it starts, then relaunch.
    if orca_running() and not quit_orca():
        finish(False, error='the patch was not verified and Orca did not quit for the restore',
               runtime_ready=ready, survived=survived, restore_verified=False)
    verified = restore(saved)
    step('restored', verified=verified)
    subprocess.run(['open', APP])
    finish(False, error='the patch was not verified after the relaunch; the previous settings were restored'
           if verified else 'the patch was not verified and the restore did not read back intact',
           runtime_ready=ready, survived=survived, restore_verified=verified)


if __name__ == '__main__':
    main()
