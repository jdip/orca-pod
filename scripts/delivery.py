#!/usr/bin/env python3
"""Orca Pod's linear GitHub delivery path; local effects live in the runbooks."""
import argparse
import json
import os
import shutil
from pathlib import Path
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True


def plain_path(path):
    """Return an absolute POSIX path, refusing symlinked components that would redirect delivery."""
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f'symlink requires investigation: {part}')
    return path


def command_path(name):
    """Locate a native command without resolving launcher symlinks."""
    executable = shutil.which(name)
    if executable is None:
        raise ValueError(f'{name} executable is unavailable')
    return Path(os.path.abspath(executable))


class DeliveryContext:
    """Local, per-run evidence; never a recovery plan or persisted retry state."""

    def __init__(self):
        self.flow = 'delivery'
        self.repository = 'not yet resolved'
        self.revision = 'not yet resolved'
        self.stage = 'preflight'
        self.operation = 'validate checkout and tools'
        self.completed = []
        self.uncertain = []
        self.retained = []

    def enter(self, stage, operation):
        self.stage, self.operation = stage, operation

    def attempt(self, effect):
        self.uncertain.append(effect)

    def confirm(self, effect):
        if effect in self.uncertain:
            self.uncertain.remove(effect)
        self.completed.append(effect)

    def report(self, error, terminal=True):
        if isinstance(error, subprocess.CalledProcessError):
            cause = f'{Path(error.cmd[0]).name} exited {error.returncode}; native stderr remains above'
        elif isinstance(error, subprocess.TimeoutExpired):
            cause = f'{Path(error.cmd[0]).name} exceeded its {error.timeout:g}s bound; native output remains above'
        else:
            cause = str(error)
        status = 'Delivery stopped' if terminal else 'Advisory failure'
        print(f'{status} at {self.stage}: {self.operation}\n'
              f'Identity: {self.flow}; repository {self.repository}; revision {self.revision}\n'
              f'Cause: {cause}\n'
              f'Confirmed effects: {"; ".join(self.completed) or "none recorded"}\n'
              f'Attempted effects requiring inspection: {"; ".join(self.uncertain) or "none recorded"}\n'
              f'Retained diagnostics: {"; ".join(self.retained) or "native output above"}\n'
              'Next: inspect actual refs, PR/check state and retained local evidence before recovery.\n'
              'Review local diagnostics before public sharing.', file=sys.stderr, flush=True)
        if terminal:
            print('Primary handoff pending: reconcile actual effects and local required completion, '
                  'then apply one Reflection screen before resolution.', file=sys.stderr, flush=True)


run = DeliveryContext()


def call(*args, capture=True, timeout=None):
    result = subprocess.run([str(command_path(args[0])), *args[1:]], check=True, text=True, encoding='utf-8',
                            stdout=subprocess.PIPE if capture else None, timeout=timeout)
    return result.stdout.strip() if capture else None


def github(*args, timeout=None):
    return json.loads(call('gh', *args, timeout=timeout))


def sha(ref):
    return call('git', 'rev-parse', ref)


# validate.yml's run-name records github.sha: the synthetic integration actually
# checked out and tested. The API's head_sha names only the PR feature head.
# Lookup reads only validate.yml, so rollup.yml's targeted runs never count as full evidence.
RUN_NAME = re.compile(r'Validate integration ([0-9a-f]{40})')
CONTEXT_STEP = re.compile(r'Validate integration \((.+)\)')
API_TIMEOUT = 60
CATCH_UPS = 3  # Per PR-to-test run; each catch-up during the wait restarts its fifteen-minute limit.


class BaseMoved(ValueError):
    """The PR base moved or GitHub reports the head behind it. PR-to-test catches up; other flows stop."""


def commit(repository, revision):
    """Return (tree, parents) from local objects, else GitHub's Git commit API."""
    present = subprocess.run([str(command_path('git')), 'cat-file', '-e', f'{revision}^{{commit}}'],
                             stderr=subprocess.DEVNULL).returncode == 0
    if present:
        header = call('git', 'cat-file', 'commit', revision).split('\n\n', 1)[0].splitlines()
        return header[0].split()[1], [line.split()[1] for line in header if line.startswith('parent ')]
    data = github('api', f'repos/{repository}/git/commits/{revision}', timeout=API_TIMEOUT)
    return data['tree']['sha'], [parent['sha'] for parent in data['parents']]


def validation(repository, head, parents):
    """Latest Validate pull_request run for head whose recorded integration has exactly these parents."""
    runs = github('run', 'list', '-R', repository, '--workflow', 'validate.yml', '--event', 'pull_request',
                  '--commit', head, '--limit', '20', '--json', 'databaseId,displayTitle,event,headSha',
                  timeout=API_TIMEOUT)
    for item in sorted(runs, key=lambda item: item['databaseId'], reverse=True):
        match = RUN_NAME.fullmatch(item['displayTitle'])
        if item['event'] != 'pull_request' or item['headSha'] != head or not match:
            continue  # Includes historical runs without the recorded integration.
        tree, tested_parents = commit(repository, match[1])
        if tested_parents != parents:
            continue
        # gh reports the latest attempt; an older pass never outranks a newer pertinent failure.
        detail = github('run', 'view', str(item['databaseId']), '-R', repository,
                        '--json', 'status,conclusion,jobs,attempt,url', timeout=API_TIMEOUT)
        jobs = [job for job in detail['jobs'] if job['name'] == 'validate']
        steps = [(context_match[1], step['conclusion']) for job in jobs for step in job['steps']
                 if (context_match := CONTEXT_STEP.fullmatch(step['name']))]
        contexts = [context for context, conclusion in steps if conclusion == 'success']
        succeeded = (detail['status'] == 'completed' and detail['conclusion'] == 'success'
                     and len(jobs) == 1 and jobs[0]['conclusion'] == 'success')
        # GitHub can list a successful job's steps late or without conclusions; that is not yet evidence.
        return {'integration': match[1], 'tree': tree,
                'context': contexts[0] if len(contexts) == 1 else None,
                'passed': succeeded and len(contexts) == 1,
                'context_unexposed': succeeded and not any(conclusion for _, conclusion in steps),
                'evidence': f'{detail["url"]} attempt {detail["attempt"]}'}
    return None


def validate():
    """Validate job entry point: reuse one attributable pass on an identical tree, else run the actual check."""
    run.flow = 'validate'
    run.enter('validate', 'resolve the checked-out integration')
    repository, tested = os.environ.get('GITHUB_REPOSITORY'), sha('HEAD')
    if os.environ.get('GITHUB_EVENT_NAME') != 'pull_request' or os.environ.get('GITHUB_SHA') != tested:
        raise ValueError('validate runs only in the Validate pull_request job on its checked-out GITHUB_SHA')
    if os.environ.get('GITHUB_BASE_REF') not in ('test', 'main'):
        raise ValueError('full Validate runs only for delivery PRs into test or main; other bases use targeted checks')
    run.repository, run.revision = repository, tested
    tree, parents = commit(repository, tested)
    print(f'Integration {tested} tree {tree}; parents {" ".join(parents)}', flush=True)
    run.enter('validate', 'find prior validation of the PR head integration')
    prior, reason = None, 'PR head is not a merge with a prior integration'
    try:
        if len(parents) == 2:
            head_parents = commit(repository, parents[1])[1]
            if len(head_parents) == 2:
                prior = validation(repository, head_parents[1], head_parents)
                reason = 'no attributable Validate pull_request run recorded that integration'
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        reason = f'lookup unavailable ({error})'
    context = os.environ.get('VALIDATION_CONTEXT')
    if prior and prior['passed'] and prior['tree'] == tree and context and prior['context'] == context:
        print(f'Reused Validate {prior["evidence"]}: it passed on integration {prior["integration"]} '
              f'with identical tree {tree}. Context: same repository, Validate workflow, pull_request '
              f'validate job; runtime {context}; the tree contains the checks and workflow definition.', flush=True)
        return
    if prior:
        reason = (f'prior integration {prior["integration"]} has different source or runtime context' if prior['passed']
                  else f'latest prior validation did not pass ({prior["evidence"]})')
    print(f'Running actual source checks: {reason}.', flush=True)
    run.enter('validate', f'run scripts/check.sh on integration {tested}')
    call('bash', 'scripts/check.sh', capture=False)
    print(f'Actual source checks passed on integration {tested} tree {tree}.', flush=True)


def pr(base, head, title, body_file, semver):
    run.enter('push/PR', f'resolve PR to {base}')
    matches = github('pr', 'list', '--base', base, '--head', head, '--state', 'open',
                     '--json', 'number')
    if len(matches) > 1:
        raise ValueError('multiple matching PRs; inspect before proceeding')
    if matches:
        number = str(matches[0]['number'])
    else:
        args = ['gh', 'pr', 'create', '--base', base, '--head', head, '--title', title]
        args += ['--body-file', body_file] if body_file else ['--body', f'Canonical {head} to {base} delivery. Semver: {semver}.']
        effect = f'create PR to {base}'
        run.attempt(effect)
        url = call(*args)
        print(f'Created {url}', flush=True)
        number = url.rsplit('/', 1)[1]
        run.confirm(effect)
    run.confirm(f'PR {number} available to {base}')
    effect = f'update PR {number} version labels'
    try:
        labels = github('pr', 'view', number, '--json', 'labels')['labels']
        run.attempt(effect)
        for label in labels:
            if label['name'].startswith('semver:') and label['name'] != f'semver:{semver}':
                call('gh', 'pr', 'edit', number, '--remove-label', label['name'])
        call('gh', 'pr', 'edit', number, '--add-label', f'semver:{semver}')
        run.confirm(effect)
    except subprocess.CalledProcessError as error:
        run.report(error, terminal=False)
        print(f'Version label update incomplete for PR {number}; inspect metadata. Delivery gates remain required.', flush=True)
    return number


def merge(repository, number, expected_head, expected_base, pushed_over=None):
    run.enter('check/readiness', f'check PR {number} at expected head/base')
    account = github('api', 'user')
    author_email = f'{account["id"]}+{account["login"]}@users.noreply.github.com'
    info = github('pr', 'view', number, '--json', 'headRefOid,state,url')
    if info['state'] != 'OPEN' or info['headRefOid'] not in (expected_head, pushed_over):
        raise ValueError(f'PR revision/state changed: {info["url"]}')
    print(f'Waiting for checks: {info["url"]}', flush=True)
    deadline = time.monotonic() + 900
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError(f'PR {number} did not become ready within 15 minutes; inspect required checks and branch policy')
        registered = github('pr', 'view', number, '--json', 'state,headRefOid,baseRefOid,statusCheckRollup',
                            timeout=min(API_TIMEOUT, remaining))
        head = registered['headRefOid']
        if registered['state'] != 'OPEN' or head not in (expected_head, pushed_over):
            raise ValueError(f'PR {number} state/head changed while waiting for checks to register')
        if head == expected_head and registered['baseRefOid'] != expected_base:
            raise BaseMoved(f'PR {number} base moved from {expected_base} to {registered["baseRefOid"]} '
                            'while waiting for checks to register')
        # A just-pushed head can reach the PR after the push returns; only the head it replaced is tolerated.
        if head != expected_head or not registered['statusCheckRollup']:
            time.sleep(min(10, max(0, deadline - time.monotonic())))
            continue
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            continue
        subprocess.run([str(command_path('gh')), 'pr', 'checks', number, '--watch', '--fail-fast', '--interval', '10'],
                       check=True, timeout=remaining)
        fresh = github('pr', 'view', number, '--json',
                       'state,headRefOid,baseRefOid,mergeStateStatus,reviewDecision,isDraft')
        if fresh['state'] != 'OPEN' or fresh['headRefOid'] != expected_head:
            raise ValueError(f'PR {number} state/head changed while waiting; reassess scope before merging')
        if fresh['baseRefOid'] != expected_base:
            raise BaseMoved(f'PR {number} base moved from {expected_base} to {fresh["baseRefOid"]} while waiting')
        readiness = fresh['mergeStateStatus']
        if readiness == 'BEHIND':
            raise BaseMoved(f'PR {number} head {expected_head} is behind its base')
        if fresh['isDraft'] or fresh['reviewDecision'] in ('REVIEW_REQUIRED', 'CHANGES_REQUESTED'):
            raise ValueError(f'PR {number} needs draft/review policy resolution before merging')
        if readiness == 'CLEAN':
            break
        if readiness not in ('BLOCKED', 'UNKNOWN'):
            raise ValueError(f'PR {number} merge readiness is {readiness}; inspect branch policy and conflicts')
        # Older passing runs can precede registration of the new PR checks.
        print(f'PR {number} checks passed but merge readiness is {readiness}; waiting for GitHub.', flush=True)
        time.sleep(min(10, max(0, deadline - time.monotonic())))
    run.enter('check/readiness', f'read Validate record for PR {number} integration onto {expected_base}')
    validated = validation(repository, expected_head, [expected_base, expected_head])
    if validated is None:
        raise ValueError(f'PR {number} has no Validate pull_request run recording an integration of '
                         f'{expected_head} onto {expected_base}; inspect its runs and base before merging')
    if validated['context_unexposed']:
        raise ValueError(f'latest Validate run for PR {number} integration passed, but GitHub has not yet exposed '
                         f'its runtime-context step: {validated["evidence"]}; re-run delivery once it does')
    if not validated['passed']:
        raise ValueError(f'latest Validate run for PR {number} integration did not pass: {validated["evidence"]}')
    run.confirm(f'Validate {validated["evidence"]} passed on integration {validated["integration"]}')
    run.enter('merge', f'merge PR {number} at {expected_head}')
    effect = f'merge PR {number}'
    run.attempt(effect)
    call('gh', 'pr', 'merge', number, '--merge', '--match-head-commit', expected_head,
         '--author-email', author_email, capture=False)
    result = github('pr', 'view', number, '--json', 'state,mergeCommit')
    if result['state'] != 'MERGED':
        raise ValueError(f'PR {number} is not merged; inspect external gates')
    revision = result['mergeCommit']['oid']
    run.confirm(effect)
    run.revision = revision
    print(f'Merged PR {number} as {revision}', flush=True)
    call('git', 'fetch', 'origin', capture=False)
    author = call('git', 'show', '-s', '--format=%an%n%ae', revision).splitlines()
    if (len(author) != 2 or author[1] != author_email
            or author[0] not in (account['login'], account.get('name'))):
        raise ValueError(f'PR {number} merge author differs from the approved account/no-reply identity; preserve repository state and investigate')
    parents = call('git', 'show', '-s', '--format=%P', revision).split()
    if parents != [expected_base, expected_head]:
        raise ValueError(f'PR {number} merged with unexpected parents; merge exists but verification/tagging stopped')
    run.confirm(f'merge parents and author verified on {revision}')
    run.enter('merged-source proof', f'compare merged revision {revision} with the validated integration')
    if commit(repository, revision)[0] != validated['tree']:
        raise ValueError(f'PR {number} merged tree differs from Validate-tested integration '
                         f'{validated["integration"]}; merge exists but verification/tagging stopped')
    run.confirm(f'merged tree on {revision} matches validated integration {validated["integration"]}')
    print(f'Verified {revision} tree matches Validate-tested integration {validated["integration"]}; '
          'no deployed application exists in this repository.', flush=True)
    return revision


def catch_up(branch):
    """Merge fetched origin/test into the task branch with a merge commit; abort, never resolve, a conflict."""
    git = str(command_path('git'))
    before, base = sha('HEAD'), sha('origin/test')
    status = subprocess.run([git, 'merge-base', '--is-ancestor', base, before]).returncode
    if status == 0:
        return False
    if status != 1:
        raise ValueError(f'cannot establish whether {branch} contains origin/test {base}')
    run.enter('catch-up', f'merge origin/test {base} into {branch} at {before}')
    # The configured repository-local identity authors the commit; refuse anything but a no-reply email.
    for role in ('AUTHOR', 'COMMITTER'):
        if not re.search(r'@users\.noreply\.github\.com>', call('git', 'var', f'GIT_{role}_IDENT')):
            raise ValueError('catch-up commit identity is not a GitHub no-reply address; '
                             'configure the repository-local identity under the public-work policy')
    effect = f'merge origin/test {base} into {before}'
    run.attempt(effect)
    if subprocess.run([git, 'merge', '--no-ff', '--no-edit', '-m', f'Merge origin/test into {branch}', base]).returncode:
        conflicted = call('git', 'diff', '--name-only', '--diff-filter=U')
        subprocess.run([git, 'merge', '--abort'])
        residual = subprocess.run([git, 'rev-parse', '-q', '--verify', 'MERGE_HEAD'],
                                  stdout=subprocess.DEVNULL).returncode == 0
        if sha('HEAD') != before or residual or call('git', 'status', '--porcelain'):
            raise ValueError(f'aborted catch-up did not restore {branch} at {before} with a clean tree; '
                             'preserve the checkout and investigate')
        run.uncertain.remove(effect)
        run.confirm(f'aborted catch-up; {branch} unchanged at {before}')
        if conflicted:
            raise ValueError(f'catch-up merge of origin/test {base} conflicts; resolve it with '
                             'resolving-merge-conflicts, have the resolution reviewed, then re-run')
        raise ValueError(f'catch-up merge of origin/test {base} failed before conflicts; native stderr remains above')
    run.confirm(effect)
    run.revision = sha('HEAD')
    print(f'Caught up {branch} with origin/test {base} as {run.revision}', flush=True)
    run.enter('source gate', f'run Git index privacy checks on catch-up {run.revision}')
    call(sys.executable, 'scripts/check_secrets.py', capture=False)
    run.confirm(f'privacy gate passed on {run.revision}')
    return True


def push(branch):
    """Push HEAD; return it with the remote branch head it replaces, if any."""
    previous = subprocess.run([str(command_path('git')), 'rev-parse', '-q', '--verify', f'refs/remotes/origin/{branch}'],
                              stdout=subprocess.PIPE, text=True).stdout.strip() or None
    intended = run.revision = sha('HEAD')
    run.enter('push/PR', f'push intended revision {intended}')
    effect = f'push intended revision {intended}'
    run.attempt(effect)
    call('git', 'push', 'origin', f'HEAD:refs/heads/{branch}', capture=False)
    run.confirm(effect)
    return intended, previous


def version_for_promotion(repository, old_main, intended_test):
    """Apply canonical test PR labels after the highest published tag in the previous main, without a ledger."""
    if call('git', 'rev-parse', '--is-shallow-repository') == 'true':
        raise ValueError('shallow history cannot prove version contributions; use a complete checkout')
    # Remote refs exclude local-only tags; an annotated tag's ^{} entry names its peeled commit.
    refs = {name: value for value, name in
            (line.split('\t') for line in call('git', 'ls-remote', '--tags', 'origin', timeout=API_TIMEOUT).splitlines())}
    published = sorted((name[10:] for name in refs if re.fullmatch(r'refs/tags/v\d+\.\d+\.\d+', name)),
                       key=lambda tag: tuple(map(int, tag[1:].split('.'))), reverse=True)
    baseline = target = None
    for tag in published:
        target = refs.get(f'refs/tags/{tag}^{{}}', refs[f'refs/tags/{tag}'])
        status = subprocess.run([str(command_path('git')), 'merge-base', '--is-ancestor', target, old_main]).returncode
        if status == 0:
            baseline = tag
            break
        if status != 1:
            raise ValueError(f'published tag {tag} commit {target} is unavailable for ancestry review')
    # Ancestry of the tagged main merge excludes contributions it already versioned; later
    # test PRs count once even when an untagged promotion already carried them to main.
    contributions = []
    # With no baseline, classify incoming PRs only to decide whether an initial version is needed.
    span = f'{target if baseline else old_main}..{intended_test}'
    for commit in call('git', 'rev-list', '--first-parent', '--reverse', span).splitlines():
        pages = json.loads(call('gh', 'api', '--paginate', '--slurp',
                                f'repos/{repository}/commits/{commit}/pulls?per_page=100', timeout=API_TIMEOUT))
        merged = [item for page in pages for item in page
                  if item.get('merged_at') and item['base']['repo']['full_name'] == repository
                  and item['base']['ref'] == 'test' and item['merge_commit_sha'] == commit]
        if len(merged) != 1:
            raise ValueError(f'test commit {commit} lacks exactly one merged test PR; review version evidence')
        item = merged[0]
        if item['head']['ref'] == 'main':
            continue  # Main-to-test synchronization wrapper.
        labels = [label['name'][7:] for label in item['labels'] if label['name'].startswith('semver:')]
        if len(labels) != 1 or labels[0] not in ('major', 'minor', 'patch', 'none'):
            raise ValueError(f'PR {item["number"]} needs semver metadata review')
        contributions.append((item['number'], labels[0]))
    print(f'Version baseline {baseline or "none published"}; canonical test PRs: '
          f'{", ".join(f"#{number} {bump}" for number, bump in contributions) or "none"}', flush=True)
    if not any(bump != 'none' for _, bump in contributions):
        print(f'All-none promotion: retain {baseline or "no existing version"}; no new tag.', flush=True)
        return None
    if baseline is None:
        raise ValueError('no established initial version; report bookkeeping for a human decision')
    major, minor, patch = map(int, baseline[1:].split('.'))
    for _, bump in contributions:
        if bump == 'major':
            major, minor, patch = major + 1, 0, 0
        elif bump == 'minor':
            minor, patch = minor + 1, 0
        elif bump == 'patch':
            patch += 1
    return f'v{major}.{minor}.{patch}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('flow', choices=['pr-to-test', 'promote-to-main', 'validate'])
    parser.add_argument('--title')
    parser.add_argument('--body-file')
    parser.add_argument('--semver', choices=['major', 'minor', 'patch', 'none'], default='none')
    args = parser.parse_args()
    run.flow = args.flow
    plain_path(Path.cwd())
    plain_path(call('git', 'rev-parse', '--path-format=absolute', '--git-common-dir'))
    run.revision = sha('HEAD')
    if call('git', 'status', '--porcelain'):
        raise ValueError('use a clean committed checkout; preserve unrelated work elsewhere')
    if args.flow == 'validate':
        validate()  # Hosted CI check only; never reaches publication or merge.
        return
    call('git', 'fetch', '--no-tags', 'origin', capture=False)
    run.enter('preflight', 'resolve repository identity')
    repository = github('repo', 'view', '--json', 'nameWithOwner')['nameWithOwner']
    run.repository = repository
    # Hosted Validate is the authoritative source check; keep the cheap privacy scan before any push.
    run.enter('source gate', 'run Git index privacy checks')
    call(sys.executable, 'scripts/check_secrets.py', capture=False)
    run.confirm(f'privacy gate passed on {run.revision}')
    run.enter('preflight', 'validate delivery branch and intended revision')
    if args.flow == 'pr-to-test':
        branch = call('git', 'branch', '--show-current')
        if not branch or branch in ('main', 'test'):
            raise ValueError('PR-to-test requires a named task branch')
        catch_ups = int(catch_up(branch))  # An up-to-date branch spends none of the budget.
        intended, pushed_over = push(branch)
        number = pr('test', branch, args.title or f'Deliver {branch}', args.body_file, args.semver)
        while True:
            try:
                merge(repository, number, intended, sha('origin/test'), pushed_over)
                break
            except BaseMoved as moved:
                if catch_ups == CATCH_UPS:
                    raise ValueError(f'{moved}; stopped after {CATCH_UPS} catch-ups because test is still '
                                     'moving. Re-run when test settles.') from moved
                catch_ups += 1  # Every drift signal counts, so a lagging BEHIND report cannot loop.
                print(f'{moved}; catch-up {catch_ups} of {CATCH_UPS}.', flush=True)
                run.enter('catch-up', 'fetch the moved test branch')
                call('git', 'fetch', '--no-tags', 'origin', capture=False)
                catch_up(branch)
                intended, pushed_over = push(branch)
    else:
        old_main, intended = sha('origin/main'), sha('origin/test')
        if sha('HEAD') != intended:
            raise ValueError('promotion requires a clean checkout of the intended origin/test revision')
        tag = None
        run.enter('promotion bookkeeping', 'classify version from published tags and test PRs')
        try:
            tag = version_for_promotion(repository, old_main, intended)
        except (ValueError, subprocess.SubprocessError) as error:
            run.report(error, terminal=False)
            print('Version bookkeeping unresolved. Continuing actual delivery gates.', flush=True)
        number = pr('main', 'test', args.title or 'Promote verified test to main', args.body_file, 'none')
        merged = merge(repository, number, intended, old_main)
        if tag:
            run.enter('tag', f'publish version {tag}')
            try:
                effect = f'create local tag {tag} on {merged}'
                run.attempt(effect)
                call('git', 'tag', tag, merged)
                run.confirm(effect)
                effect = f'publish tag {tag}'
                run.attempt(effect)
                call('git', 'push', 'origin', f'refs/tags/{tag}', capture=False)
                run.confirm(effect)
                print(f'Published {tag}', flush=True)
            except subprocess.CalledProcessError as error:
                run.report(error, terminal=False)
                print(f'Tag {tag} publication incomplete; inspect local/remote tags. No tag was moved.', flush=True)
        run.enter('synchronization', 'verify promoted branch state before main-to-test synchronization')
        if sha('origin/test') != intended or sha('origin/main') != merged:
            raise ValueError('branch drift after promotion; inspect before main-to-test synchronization')
        number = pr('test', 'main', 'Synchronize main back to test', None, 'none')
        merge(repository, number, merged, intended)
    print('Delivery verified. Primary handoff pending: finish local required completion, issue bookkeeping '
          'and safe associated-artifact cleanup; apply one consolidated Reflection screen before resolution.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        run.report(error)
        sys.exit(1)
