#!/usr/bin/env python3
"""Read-only Orca inventory: worktrees, terminals and orchestration workers with proposed dispositions.

This is always a dry run. It never stops, releases or removes anything; it reports what
is retained and why, and which exact resources are candidates for the supervisor's
recheck and removal under explicit cleanup authority.
"""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import time

TIMEOUT_SECONDS = 60
LIVE_TERMINAL_STATES = {'active', 'retained', 'release_pending', 'release_unknown'}
SETTLED_WORKER_STATES = {'succeeded', 'failed'}


def orca(*command):
    completed = subprocess.run(['orca', *command, '--json'], capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    if completed.returncode != 0:
        raise RuntimeError(f"orca {' '.join(command[:2])} failed")
    payload = json.loads(completed.stdout)
    if payload.get('ok') is not True or not isinstance(payload.get('result'), dict):
        raise RuntimeError(f"orca {' '.join(command[:2])} returned malformed data")
    return payload['result']


def workers(coverage):
    """Every Run's supervised workers; worker-list alone covers only the bound Run."""
    rows, cursor = [], None
    runs = []
    while True:
        page = orca('orchestration', 'run-list', '--limit', '100', *(['--cursor', cursor] if cursor else []))
        runs += page.get('runs', [])
        cursor = page.get('nextCursor')
        if not cursor:
            break
    for run in runs:
        cursor = None
        while True:
            page = orca('orchestration', 'worker-list', '--run', run['id'], '--limit', '100',
                        *(['--cursor', cursor] if cursor else []))
            rows += page.get('workers', [])
            cursor = (page.get('page') or {}).get('nextCursor')
            if not cursor:
                break
    if not runs:
        coverage.append('no orchestration Runs listed')
    return rows


def git_state(path):
    def git(*arguments):
        return subprocess.run(['git', '-C', path, *arguments], capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    if not Path(path).is_dir():
        return ['checkout path is missing']
    reasons = []
    status = git('--no-optional-locks', 'status', '--porcelain')
    if status.returncode != 0:
        return ['git status failed']
    if status.stdout.strip():
        reasons.append('uncommitted or untracked changes')
    unpublished = git('rev-list', '--count', 'HEAD', '--not', '--remotes')
    if unpublished.returncode != 0:
        reasons.append('could not compare HEAD with remote branches')
    elif unpublished.stdout.strip() != '0':
        reasons.append(f'{unpublished.stdout.strip()} commit(s) on no remote branch')
    return reasons


def inventory():
    coverage = []
    current = orca('worktree', 'current').get('worktree') or {}
    listing = orca('worktree', 'ps', '--limit', '1000')
    if listing.get('truncated'):
        coverage.append('worktree ps truncated; unlisted worktrees are retained')
    omitted = (listing.get('hostScope') or {}).get('omittedHostIds') or []
    if omitted:
        coverage.append(f"hosts not covered: {', '.join(omitted)}")
    terminals = orca('terminal', 'list', '--limit', '1000').get('terminals', [])
    worker_rows = workers(coverage)

    by_worktree = {}
    for terminal in terminals:
        by_worktree.setdefault(terminal.get('worktreeId'), []).append(terminal)
    live_workers = {}
    for worker in worker_rows:
        resource = worker.get('resource') or {}
        if worker.get('terminalState') in LIVE_TERMINAL_STATES or worker.get('workerState') not in SETTLED_WORKER_STATES:
            live_workers.setdefault(resource.get('worktreeId'), []).append(worker['dispatchId'])

    report = []
    for row in listing.get('worktrees', []):
        worktree_id = row['worktreeId']
        reasons = []
        if row.get('isMainWorktree'):
            reasons.append('main checkout')
        if worktree_id == current.get('id'):
            reasons.append("this sweep's own worktree")
        if row.get('isPinned'):
            reasons.append('pinned')
        if row.get('liveTerminalCount') or row.get('hasAttachedPty') or by_worktree.get(worktree_id):
            reasons.append('live Orca terminal')
        if row.get('unverifiableTerminalCount'):
            reasons.append('unverifiable terminal')
        agents = row.get('agents') or []
        if any(agent.get('state') != 'done' for agent in agents):
            reasons.append('live Orca agent')
        elif agents:
            reasons.append('finished agent session still attached; confirm with its owner')
        if live_workers.get(worktree_id):
            reasons.append(f"unsettled or unreleased worker {', '.join(live_workers[worktree_id])}")
        if row.get('hostId') != 'local':
            reasons.append('remote host; inspect there')
        else:
            reasons += git_state(row['path'])
        activity = row.get('lastActivityAt')
        idle_days = round((time.time() * 1000 - activity) / 86400000, 1) if isinstance(activity, (int, float)) else None
        entry = {'worktree': worktree_id, 'branch': row.get('branch'), 'archived': row.get('isArchived', False),
                 'idle_days': idle_days, 'disposition': 'retain' if reasons else 'candidate', 'reasons': reasons}
        if not reasons:
            entry['after_recheck'] = f'orca worktree rm --worktree {shlex.quote("id:" + worktree_id)}'
        report.append(entry)

    listed = {row['worktreeId'] for row in listing.get('worktrees', [])}
    orphans = [terminal['handle'] for terminal in terminals if terminal.get('worktreeId') not in listed]
    releasable = [worker['dispatchId'] for worker in worker_rows
                  if worker.get('workerState') in SETTLED_WORKER_STATES and worker.get('terminalState') == 'reclaimable']
    return {'dry_run': True, 'coverage_limits': coverage, 'worktrees': report,
            'terminals_outside_listed_worktrees': orphans,
            'settled_workers_with_reclaimable_terminals': [
                {'dispatch': dispatch, 'after_recheck': f'orca orchestration worker-release --dispatch {shlex.quote(dispatch)}'}
                for dispatch in releasable]}


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        print(json.dumps(inventory(), indent=2))
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        raise SystemExit(f'inventory: {error}; preserve every resource')
