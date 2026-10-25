#!/usr/bin/env python3
"""Apply Orca app settings while Orca is quit (macOS); see docs/install.md.

The installer launches this helper detached and waits on its --result file. It quits Orca.app
gracefully, backs up the profile store, patches the `settings` document (payload, sha256 content_hash,
revision, updated_at), relaunches Orca, waits for the runtime, verifies the patch survived and writes a
JSON result. Any failure after the write restores the backup before Orca starts. Orca is never
force-killed, and an unverified Orca or settings-document version is refused with nothing changed.
Agent sessions run under Orca's terminal host, so they survive the restart.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

APP = '/Applications/Orca.app'
APP_BIN = APP + '/Contents/MacOS/Orca'
ORCA_CLI = APP + '/Contents/Resources/bin/orca'
DB = Path('~/Library/Application Support/orca/profiles/local-default/profile-state.db').expanduser()
SUPPORTED = {('1.4.240', 1)}  # (app version, settings domain_version) verified in jdip/orca-pod#6
MANUAL = 'set them by hand in Orca Settings instead'


def app_version():
    out = subprocess.run(['defaults', 'read', APP + '/Contents/Info.plist', 'CFBundleShortVersionString'],
                         capture_output=True, text=True)
    return out.stdout.strip()


def orca_running():
    return subprocess.run(['pgrep', '-f', APP_BIN], capture_output=True).returncode == 0


def read_settings(conn):
    row = conn.execute("select domain_version, revision, payload from profile_state_documents "
                       "where domain='settings'").fetchone()
    if row is None:
        raise RuntimeError('the profile store has no settings document')
    return row[0], row[1], json.loads(row[2])


def preflight(patch):
    """Read-only gate: return {ok, error?, app_version, domain_version, revision, before, changes}."""
    info = {'ok': False, 'app_version': app_version() if Path(APP).exists() else None}
    if info['app_version'] is None:
        return {**info, 'error': f'{APP} is not installed'}
    if not DB.exists():
        return {**info, 'error': f'no Orca profile store at {DB}; launch Orca once first'}
    conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    try:
        dv, rev, cur = read_settings(conn)
    finally:
        conn.close()
    info.update(domain_version=dv, revision=rev, before={k: cur.get(k) for k in patch})
    if (info['app_version'], dv) not in SUPPORTED:
        return {**info, 'error': f'unverified Orca {info["app_version"]} / settings domain_version {dv}; {MANUAL}'}
    unknown = [k for k in patch if k not in cur]
    if unknown:
        return {**info, 'error': f'refusing unknown settings keys {unknown}; {MANUAL}'}
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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--patch', required=True, help='JSON object of top-level settings keys to set')
    ap.add_argument('--result', required=True, type=Path, help='JSON result file the caller waits on')
    ap.add_argument('--backup-dir', required=True, type=Path)
    ap.add_argument('--dry-run', action='store_true', help='run the read-only preflight only')
    a = ap.parse_args()
    patch = json.loads(a.patch)
    res = {'started': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'patch': patch, 'steps': []}

    def save():
        temp = a.result.with_name(a.result.name + '.tmp')
        temp.write_text(json.dumps(res, indent=2) + '\n', encoding='utf-8')
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
    subprocess.run(['osascript', '-e', 'tell application "Orca" to quit'], capture_output=True)
    if not wait(lambda: not orca_running(), 90):
        finish(False, error='Orca did not quit within 90s; nothing was changed')
    time.sleep(2)  # Let the store settle after Orca's final flush.
    step('quit')

    wrote = False
    bpath = a.backup_dir / 'profile-state.db'
    try:
        # 2. Back up through SQLite, which is safe for the WAL-mode store.
        a.backup_dir.mkdir(parents=True, exist_ok=True)
        src = sqlite3.connect(DB)
        dst = sqlite3.connect(bpath)
        src.backup(dst)
        dst.close()
        step('backup', path=str(bpath))

        # 3. Patch the settings document in one transaction, re-read after Orca's flush.
        dv, rev, cur = read_settings(src)
        if (pre['app_version'], dv) not in SUPPORTED:
            raise RuntimeError(f'settings domain_version changed to {dv}')
        cur.update(patch)
        payload = json.dumps(cur, separators=(',', ':'), ensure_ascii=False)
        with src:
            src.execute('update profile_state_documents set payload=?, content_hash=?, revision=?, updated_at=? '
                        "where domain='settings'",
                        (payload, hashlib.sha256(payload.encode()).hexdigest(), rev + 1, int(time.time() * 1000)))
        wrote = True
        ok_ic = src.execute('pragma integrity_check').fetchone()[0]
        src.close()
        step('write', new_revision=rev + 1, integrity=ok_ic)
        if ok_ic != 'ok':
            raise RuntimeError('integrity_check failed: ' + ok_ic)
    except Exception as e:  # Restore before Orca starts.
        if wrote:
            r = sqlite3.connect(bpath)
            t = sqlite3.connect(DB)
            r.backup(t)
            t.close()
            r.close()
            step('restored_backup')
        subprocess.run(['open', APP])
        finish(False, error=f'write failed: {e}')

    # 4. Relaunch and wait for the runtime.
    subprocess.run(['open', APP])
    ready = wait(runtime_ready, 180, 2)
    step('relaunch', runtime_ready=ready)
    time.sleep(5)

    # 5. Verify the patch survived Orca's startup.
    conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    _, rev_after, after = read_settings(conn)
    conn.close()
    res['after'] = {k: after.get(k) for k in patch}
    survived = all(after.get(k) == v for k, v in patch.items())
    finish(ready and survived, runtime_ready=ready, survived=survived, revision_after=rev_after)


if __name__ == '__main__':
    main()
