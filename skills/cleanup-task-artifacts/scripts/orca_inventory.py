#!/usr/bin/env python3
"""Read-only Orca inventory: worktrees, terminals and orchestration workers with proposed dispositions.

This is always a dry run. It never stops, releases or removes anything; it reports what
is retained and why, and which exact resources are candidates for the supervisor's
recheck and removal under explicit cleanup authority. A worktree is a candidate only when
its repository passed this run's discovery, Orca's remote identity for it is exactly the
repository discovery recorded, every Orca field its disposition reads is present with its
exact type, and a hosted compare against that repository shows its HEAD on the delivery branch.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

TIMEOUT_SECONDS = 60
LIVE_TERMINAL_STATES = {'active', 'retained', 'release_pending', 'release_unknown'}
IDLE_TERMINAL_STATES = {'reclaimable', 'released'}  # Orca 1.4.241's other terminal states; any other is a gap.
SETTLED_WORKER_STATES = {'succeeded', 'failed'}
SETTLED_DISPATCH_STATUSES = {'completed', 'failed'}
# Every discovered repository adopts, or is the source of, the Repository Standard, which delivers through PR-to-test.
DELIVERY_BRANCH = 'test'
SOURCE_KEY = 'github.com/jdip/orca-pod'  # discover.py's only repository for its source-repository basis
REPOSITORY_KEY = re.compile(r'github\.com/[\w.-]+/[\w.-]+')
# Orca activity timestamps are epoch milliseconds; one before 2020 or more than a day ahead is not real.
EARLIEST_ACTIVITY_MS = 1577836800000
CLOCK_SKEW_MS = 86400000
# The Orca fields a worktree disposition reads, with their exact types.
ROW_FIELDS = {'worktreeId': str, 'repoId': str, 'hostId': str, 'path': str, 'isMainWorktree': bool,
              'isPinned': bool, 'isArchived': bool, 'liveTerminalCount': int, 'hasAttachedPty': bool,
              'unverifiableTerminalCount': int, 'lastActivityAt': int, 'agents': list}


class Gap(ValueError):
    """Inventory data that is missing, malformed or incomplete."""


def strict_json(text):
    def unique(pairs):
        if len({key for key, _ in pairs}) != len(pairs):
            raise Gap('duplicate JSON key')
        return dict(pairs)
    return json.loads(text, object_pairs_hook=unique)


def field(record, name, kind, label):
    value = record.get(name) if isinstance(record, dict) else None
    # Exact type: JSON true is not a count or timestamp, and a missing value is never a default.
    if type(value) is not kind:
        raise Gap(f'{label} {name} is missing or not {kind.__name__}')
    return value


def cursor(page, label):
    value = page.get('nextCursor') if isinstance(page, dict) else None
    if value is not None and (type(value) is not str or not value):
        raise Gap(f'{label} nextCursor is malformed')
    return value


def orca(*command):
    label = f"orca {' '.join(command[:2])}"
    completed = subprocess.run(['orca', *command, '--json'], capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    if completed.returncode != 0:
        raise Gap(f'{label} failed')
    payload = strict_json(completed.stdout)
    if not isinstance(payload, dict) or payload.get('ok') is not True:
        raise Gap(f'{label} did not succeed')
    return field(payload, 'result', dict, label)


def complete(result, key, label):
    """A host-scoped listing that is untruncated, covers every host and counts every row."""
    rows = field(result, key, list, label)
    if field(result, 'truncated', bool, label):
        raise Gap(f'{label} is truncated')
    if field(result, 'totalCount', int, label) != len(rows):
        raise Gap(f'{label} totalCount does not match its rows')
    if field(field(result, 'hostScope', dict, label), 'omittedHostIds', list, label):
        raise Gap(f'{label} omits hosts')
    return rows


def workers():
    """Every Run's supervised workers; worker-list alone covers only the bound Run."""
    runs, after = [], None
    while True:
        page = orca('orchestration', 'run-list', '--limit', '100', *(['--cursor', after] if after else []))
        runs += [field(run, 'id', str, 'run') for run in field(page, 'runs', list, 'run-list')]
        after = cursor(page, 'run-list')
        if not after:
            break
    if len(set(runs)) != len(runs):
        raise Gap('run-list repeats a Run')
    rows = []
    for run in runs:
        listed, after = [], None
        while True:
            page = orca('orchestration', 'worker-list', '--run', run, '--limit', '100',
                        *(['--cursor', after] if after else []))
            listed += field(page, 'workers', list, 'worker-list')
            paging = field(page, 'page', dict, 'worker-list')
            more, after = field(paging, 'hasMore', bool, 'worker-list page'), cursor(paging, 'worker-list')
            total = field(paging, 'total', int, 'worker-list page')
            if more != bool(after):
                raise Gap('worker-list hasMore disagrees with nextCursor')
            if not more:
                break
        if total != len(listed):
            raise Gap(f'worker-list for {run} is incomplete')
        rows += listed
    for worker in rows:
        for name in ('dispatchId', 'workerState', 'terminalState'):
            field(worker, name, str, 'worker')
        if worker['terminalState'] not in LIVE_TERMINAL_STATES | IDLE_TERMINAL_STATES:
            raise Gap(f'worker terminalState {worker["terminalState"]!r} is unknown')
        if 'resource' in worker and worker['resource'] is None:
            # A settled dispatch Orca itself reports resource-absent holds no worktree or terminal resource.
            projection = field(field(worker, 'projection', dict, 'worker'), 'resource', dict, 'worker projection')
            if (field(projection, 'state', str, 'worker projection resource') != 'absent'
                    or field(worker, 'dispatchStatus', str, 'worker') not in SETTLED_DISPATCH_STATUSES):
                raise Gap(f'worker {worker["dispatchId"]} has no resource but is not a settled resource-absent dispatch')
        else:
            field(field(worker, 'resource', dict, 'worker'), 'worktreeId', str, 'worker resource')
    return runs, [worker for worker in rows if worker['resource'] is not None]


def git(path, *arguments):
    return subprocess.run(['git', '-C', path, *arguments], capture_output=True, text=True, timeout=TIMEOUT_SECONDS)


def common_dir(path):
    result = git(path, 'rev-parse', '--path-format=absolute', '--git-common-dir')
    return os.path.realpath(result.stdout.strip()) if result.returncode == 0 and result.stdout.strip() else None


def git_state(path):
    if not Path(path).is_dir():
        return ['checkout path is missing']
    reasons = []
    status = git(path, '--no-optional-locks', 'status', '--porcelain')
    if status.returncode != 0:
        return ['git status failed']
    if status.stdout.strip():
        reasons.append('uncommitted or untracked changes')
    unpublished = git(path, 'rev-list', '--count', 'HEAD', '--not', '--remotes')
    if unpublished.returncode != 0:
        reasons.append('could not compare HEAD with remote branches')
    elif unpublished.stdout.strip() != '0':
        reasons.append(f'{unpublished.stdout.strip()} commit(s) on no remote branch')
    return reasons


def delivery(slug, path):
    """Hosted evidence that the checkout's HEAD is already on the delivery branch; local refs never count."""
    head = git(path, 'rev-parse', '--verify', 'HEAD^{commit}').stdout.strip()
    if not re.fullmatch(r'[0-9a-f]{40}', head):
        return None
    response = subprocess.run(['gh', 'api', f'repos/{slug}/compare/{DELIVERY_BRANCH}...{head}', '--jq',
                               '{status, ahead_by, merge_base: .merge_base_commit.sha}'],
                              capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    if response.returncode != 0:
        return None
    try:
        compare = strict_json(response.stdout)
    except ValueError:
        return None
    if (isinstance(compare, dict) and compare.get('status') in ('behind', 'identical')
            and type(compare.get('ahead_by')) is int and compare['ahead_by'] == 0 and compare.get('merge_base') == head):
        return f'hosted compare: {head[:12]} is on {slug} {DELIVERY_BRANCH}'
    return None


def eligible_roots(source):
    """Roots this run's discover.py output reports eligible, each with the repository key it recorded, or None."""
    if source is None:
        return {}
    text = sys.stdin.read() if source == '-' else Path(source).read_text(encoding='utf-8')
    roots = {}
    for line in filter(str.strip, text.splitlines()):
        result = strict_json(line)
        root, eligible = field(result, 'root', str, 'discovery'), field(result, 'eligible', bool, 'discovery')
        if eligible:
            if not re.fullmatch(r'[0-9a-f]{40}', field(result, 'revision', str, 'discovery')):
                raise Gap('discovery revision is malformed')
            basis, key = field(result, 'basis', str, 'discovery'), result.get('repository')
            if basis == 'source repository' and key != SOURCE_KEY:
                raise Gap(f'discovery source repository is not {SOURCE_KEY}')
            if basis not in ('source repository', 'adoption') or 'repository' not in result or not (
                    key is None or type(key) is str and REPOSITORY_KEY.fullmatch(key)):
                raise Gap('discovery basis or repository is malformed')
            real = os.path.realpath(root)
            if roots.get(real, key) != key:
                raise Gap('discovery records one root with two repositories')
            roots[real] = key
    return roots


def repositories(roots):
    """Orca's repositories by id, each bound to this run's discovery only when its root passed it.

    Orca's remote identity is recorded as reported; only an exact match with discovery's key earns a hosted compare."""
    repos = {}
    for repo in field(orca('repo', 'list'), 'repos', list, 'repo list'):
        repo_id, path = field(repo, 'id', str, 'repo'), field(repo, 'path', str, 'repo')
        if repo_id in repos:
            raise Gap('repo list repeats a repository id')
        identity = repo.get('gitRemoteIdentity')
        key = identity.get('canonicalKey') if isinstance(identity, dict) else None
        bound = os.path.realpath(path) in roots
        repos[repo_id] = {'root': path, 'bound': bound, 'expected': roots.get(os.path.realpath(path)),
                          'identity': key, 'common_dir': common_dir(path) if bound else None}
    return repos


def gathered(gaps, label, collect, fallback):
    try:
        return collect()
    except (Gap, OSError, subprocess.TimeoutExpired) as error:
        gaps.append(f'{label}: {error}')
        return fallback


def disposition(row, repos, current, terminals, live_workers, gaps):
    reasons = [f'inventory gap ({gap}); retained' for gap in gaps]
    try:
        values = {name: field(row, name, kind, 'worktree') for name, kind in ROW_FIELDS.items()}
        states = [field(agent, 'state', str, 'worktree agent') for agent in values['agents']]
        if values['liveTerminalCount'] < 0 or values['unverifiableTerminalCount'] < 0:
            raise Gap('worktree terminal count is negative')
        if not EARLIEST_ACTIVITY_MS <= values['lastActivityAt'] <= time.time() * 1000 + CLOCK_SKEW_MS:
            raise Gap('worktree lastActivityAt is not a plausible timestamp')
    except Gap as error:
        worktree_id = row.get('worktreeId') if isinstance(row, dict) and type(row.get('worktreeId')) is str else None
        return {'worktree': worktree_id, 'disposition': 'retain', 'reasons': reasons + [f'{error}; retained']}

    worktree_id, repo = values['worktreeId'], repos.get(values['repoId'])
    if repo is None:
        reasons.append('unknown repository identity')
    elif not repo['bound']:
        reasons.append("repository did not pass this run's discovery")
    elif repo['expected'] is None:
        reasons.append("this run's discovery recorded no hosted GitHub repository for it")
    elif repo['identity'] != repo['expected']:
        reasons.append(f"Orca remote identity {repo['identity']!r} is not discovery's {repo['expected']}")
    if values['isMainWorktree']:
        reasons.append('main checkout')
    if worktree_id == current:
        reasons.append("this sweep's own worktree")
    if values['isPinned']:
        reasons.append('pinned')
    if values['liveTerminalCount'] or values['hasAttachedPty'] or terminals.get(worktree_id):
        reasons.append('live Orca terminal')
    if values['unverifiableTerminalCount']:
        reasons.append('unverifiable terminal')
    if any(state != 'done' for state in states):
        reasons.append('live Orca agent')
    elif states:
        reasons.append('finished agent session still attached; confirm with its owner')
    if live_workers.get(worktree_id):
        reasons.append(f"unsettled or unreleased worker {', '.join(live_workers[worktree_id])}")
    if values['hostId'] != 'local':
        reasons.append('remote host; inspect there')
    else:
        if repo and repo['bound'] and (not repo['common_dir'] or common_dir(values['path']) != repo['common_dir']):
            reasons.append('checkout is not a worktree of its Orca repository')
        reasons += git_state(values['path'])
    evidence = None
    if not reasons:
        slug = repo['expected'].removeprefix('github.com/')
        evidence = delivery(slug, values['path'])
        if not evidence:
            reasons.append(f"delivery to {slug} {DELIVERY_BRANCH} not shown by a hosted compare")
    branch = row.get('branch')
    entry = {'worktree': worktree_id, 'repo_id': values['repoId'], 'repo_root': repo and repo['root'],
             'branch': branch if type(branch) is str else None, 'archived': values['isArchived'],
             'idle_days': round((time.time() * 1000 - values['lastActivityAt']) / 86400000, 1),
             'delivery': evidence, 'disposition': 'retain' if reasons else 'candidate', 'reasons': reasons}
    if not reasons:
        entry['after_recheck'] = f'orca worktree rm --worktree {shlex.quote("id:" + worktree_id)}'
    return entry


def inventory(discovery):
    roots = eligible_roots(discovery)
    gaps, coverage = [], []
    if not roots:
        coverage.append('no repository passed discovery in this run; no worktree is a candidate')
    current = gathered(gaps, 'worktree current',
                       lambda: field(field(orca('worktree', 'current'), 'worktree', dict, 'worktree current'),
                                     'id', str, 'worktree current'), None)
    repos = gathered(gaps, 'repo list', lambda: repositories(roots), {})
    listing = orca('worktree', 'ps', '--limit', '1000')
    rows = field(listing, 'worktrees', list, 'worktree ps')
    gathered(gaps, 'worktree ps', lambda: complete(listing, 'worktrees', 'worktree ps'), None)
    terminals = gathered(gaps, 'terminal list', lambda: complete(orca('terminal', 'list', '--limit', '1000'),
                                                                  'terminals', 'terminal list'), [])
    by_worktree = {}
    for terminal in terminals:
        terminal_id = gathered(gaps, 'terminal list', lambda: field(terminal, 'worktreeId', str, 'terminal'), None)
        by_worktree.setdefault(terminal_id, []).append(terminal)
    runs, worker_rows = gathered(gaps, 'orchestration workers', workers, (None, []))
    if runs == []:
        coverage.append('no orchestration Runs listed')
    live_workers = {}
    for worker in worker_rows:
        if worker['terminalState'] not in IDLE_TERMINAL_STATES or worker['workerState'] not in SETTLED_WORKER_STATES:
            live_workers.setdefault(worker['resource']['worktreeId'], []).append(worker['dispatchId'])

    ids = [row.get('worktreeId') if isinstance(row, dict) else None for row in rows]
    if any(type(i) is not str or not i for i in ids) or len(set(ids)) != len(ids):
        gaps.append('worktree ps: a worktreeId is missing, empty or repeated')
    report = [disposition(row, repos, current, by_worktree, live_workers, gaps) for row in rows]
    listed = {entry['worktree'] for entry in report}
    orphans = [terminal.get('handle') for terminal in terminals
               if isinstance(terminal, dict) and terminal.get('worktreeId') not in listed]
    releasable = [worker['dispatchId'] for worker in worker_rows
                  if worker['workerState'] in SETTLED_WORKER_STATES and worker['terminalState'] == 'reclaimable']
    return {'dry_run': True, 'inventory_gaps': gaps, 'coverage_limits': coverage, 'worktrees': report,
            'terminals_outside_listed_worktrees': orphans,
            'settled_workers_with_reclaimable_terminals': [
                {'dispatch': dispatch, 'after_recheck': f'orca orchestration worker-release --dispatch {shlex.quote(dispatch)}'}
                for dispatch in releasable]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--discovery', metavar='FILE',
                        help="this run's discover.py output, or - for stdin; without it no worktree is a candidate")
    try:
        print(json.dumps(inventory(parser.parse_args().discovery), indent=2))
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        raise SystemExit(f'inventory: {error}; preserve every resource')
