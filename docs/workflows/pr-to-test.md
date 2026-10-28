# PR to test

Before GitHub writes, follow the [public-work policy](../../SECURITY.md#public-repository-work)
for outgoing source, metadata and evidence, including approved commit identity.
The script verifies the merge author; inspect that result and the remaining
platform-created metadata against the policy after delivery.

The authenticated GitHub account must enable email privacy for its GitHub-provided
no-reply address to be used for web merges. Repository-local Git author settings
do not configure that account setting. If GitHub rejects the explicit merge email,
preserve the open PR and resolve the account's email privacy setting before
resuming; never fall back to a personal address.

An implementation request includes preparation, intended commits, push, PR, checks,
merge, and verified test delivery. Preserve unrelated work and use a clean committed
task checkout. Read AGENTS.md and docs/development.md. Required tools are Git,
authenticated gh, Bash, and Python 3.11+ (`ORCA_POD_PYTHON` can select it).

Review all submitted changes. Reuse completed review only with evidence covering
every change and resolved/accepted findings; doubt requires the relevant review.
Run git diff --check and exercise changed helpers where practical under the
repository's closure policy.
The script runs the mandatory staged privacy check before pushing; hosted Validate
is the authoritative source check for delivery to test/main, so a full local run
before that delivery is optional, following
[development guidance](../development.md). No review record framework or Tooling
coverage suite is needed.

For an implementation rollup, use the child integration path below until every
child is complete. Run this canonical test-delivery path once from the completed
rollup, with final acceptance recorded on the implementation parent. Single-ticket
work defaults to direct delivery. The shared
[rollup contract](../../skills/pr-to-test/ROLLUP.md) owns the lifecycle; the
`pr-to-test` skill that holds it and the guidance linked below arrives in #10.

Choose the contribution using the shared
[Version classification](../../skills/pr-to-test/SKILL.md#version-classification)
guidance, then set `contribution` to `major`, `minor`, `patch` or `none`.
From the repository root run:

```bash
scripts/pr-to-test.sh --title 'Concrete change' --body-file /path/to/pr-body.md --semver "${contribution:?Set contribution from the actual change}"
```

The script catches the current named task branch up with test, pushes it, creates
or reuses its open PR to test, applies the chosen advisory semver label, waits up
to fifteen minutes for checks and GitHub merge readiness within one shared
fifteen-minute limit, and merges the exact intended head with a merge commit.
Passing older checks alone do not establish readiness while new PR checks register.
Draft/review requirements, unexpected readiness, head drift and failed checks
return for investigation. GitHub's protected branch gate remains authoritative;
the required validate job runs the actual source checks or proves equivalent prior
integration evidence. Missing/failed gates stop the script.

Protection on test requires the branch to be up to date and allows no bypass.
A **catch-up** merges fetched `origin/test` into the task branch with a merge
commit under the repository-local no-reply identity, then reruns the privacy gate
on the result. The script catches up before the first push when the branch lacks
`origin/test`, and whenever test moves during the wait: a changed PR base or
BEHIND readiness triggers a catch-up, a re-push and a fresh fifteen-minute wait.
A run allows at most 3 catch-ups in total, counting a merging pre-push catch-up
and every drift signal during the wait; the cap or a timeout stops the script, with
each catch-up listed among its confirmed effects. After any push the wait tolerates
the replaced head until GitHub shows the new one. Re-run once test
settles. A catch-up is neither a merge retry nor a protection bypass. A clean
catch-up needs no new review, because Validate reruns on the new integration.
A conflict at any catch-up aborts the merge, verifies the branch is unchanged with
a clean tree and stops: resolve it with `resolving-merge-conflicts`, have the
resolution reviewed, then re-run the script. Promotion and main-to-test
synchronization still stop when behind or when their base moves.

The passing Validate run identifies the integration revision it tested. After
merge the script fetches origin and verifies that the merge commit has that
integration's parents and tree, making the run the merged revision's attributable
evidence instead of repeating the checks locally. A mismatch or missing run stops
for investigation; that merge needs its own validation. This repository has no
deployed application: completion is that attributed Validate evidence plus the
issue's proportionate checks and available behavioral evidence.

Validate's run name records the tested synthetic integration SHA, which differs
from the API's feature-head SHA. Its validation step records the runner image and
Python version. Reuse requires a successful prior integration run with the same
tree and runtime context; the tree includes the workflow and check definitions.
An absent, failed or inequivalent prior record falls back to `scripts/check.sh`.
Only Validate runs qualify, and Validate refuses PR bases other than test and main;
rollup children's Targeted checks runs never do, so a completed rollup's PR runs
the full check.
This source-only equivalence does not establish application or deployment acceptance.

The supervising agent then records the PR, review, behavioral evidence and
verification limits, closes the issue when its acceptance outcome is met under the
global closure rule, and cleans
all associated resources proven safe. Task-created branches/worktrees, staging, and logs can qualify; shared
or uncertain resources cannot. Never remove a worktree backing a live Orca agent. Use
supported lifecycle handling or retain it. An attached worktree is not a delivery
failure. Do not use broad pruning or edit app storage.

At coherent recovery or closeout, complete the shared
[primary handoff](../../skills/pr-to-test/SKILL.md#primary-handoff).
The helper leaves screening, bookkeeping and locally required completion pending;
its terminal text is evidence for the primary, not an executed conversation callback.
Preserve any locally mandatory retrospective on the existing delivery record when
post-merge proof fails or only partially completes. Orca Pod does not require a
durable retrospective for every PR.

On failure inspect the earliest causal error and actual push/PR/check/merge effects.
The helper's local diagnostic names the failed stage, operation, repository/revision,
native result, confirmed effects and attempts requiring inspection. Native stderr
remains the causal evidence; command arguments and PR body inputs are not repeated.
Retained checkout paths and other local diagnostics need publication review and
sanitization before sharing. This in-memory report does not establish current remote
state or authorize another attempt.
Use gh pr view/checks and git state before deciding recovery; do not blindly replay.
If already merged, verify that exact merge directly and finish bookkeeping instead
of opening another PR. Resolve routine problems within the authorized issue. External
approval or a new intent-dependent decision stays pending. Report partial results.

Semver labels are advisory, with none valid. No tag is made on task delivery. This
workflow does not promote main; verified direct delivery permits continuation,
and verified rollup delivery completes the implementation parent's delivery gate.

## Feature PR into an implementation rollup

This is the native integration path for a parent whose specification records the
rollup. Use Git and `gh`; `scripts/pr-to-test.sh` always targets test and must not be
used for child integration. Before the first push, inspect `.github/workflows/`
and relevant hosted deployment configuration. Orca Pod currently runs full
Validate only on PRs into test and main, Targeted checks (`rollup.yml`) on PRs into
every other base, and has no deployed app. Changes to those triggers require fresh
inspection.

For a new rollup, verify that its remote ref is absent, create it from fresh
`origin/test`, then publish it before creating the first child PR:

```bash
git ls-remote --heads origin "refs/heads/${rollup:?Set the parent rollup}"
git branch "$rollup" origin/test
git push origin "refs/heads/$rollup:refs/heads/$rollup"
git fetch origin
```

Run the creation steps only after resolving local refs too. Verify the remote SHA
matches the intended baseline and record it on the parent. An existing owned
rollup is fetched and verified, never reset or force-pushed.

Start a child's `orca/` branch in its worktree from the fetched rollup. Review,
commit, run `git diff --check`, and run the staged privacy check from
[SECURITY.md](../../SECURITY.md) before pushing. Optional local feedback uses the
targeted form, `scripts/check.sh --base "$(git merge-base HEAD "origin/$rollup")"`;
children use only targeted validation. Set `rollup` to the exact branch recorded on the parent
and `feature` to the current child branch. Inspect existing PRs before creating one:

```bash
git push origin "HEAD:refs/heads/${feature:?Set the child branch}"
gh pr list --base "${rollup:?Set the parent rollup}" --head "$feature" --state open
gh pr create --base "$rollup" --head "$feature" --title 'Concrete child outcome' --body-file /path/to/child-pr.md
```

Reuse one matching PR; multiple matches or an unexpected base require investigation.
Record the intended feature head and current rollup base SHAs. Wait at most fifteen
minutes for the current PR's Targeted checks run to register and pass, using
`gh pr view`, `gh pr checks` and `gh run view` to inspect the linked run. Require the
`targeted` job of the current pull_request run for the current integration revision;
an older run tested a different integration. All other applicable checks must pass
too. No registered checks, a skipped required job, or unavailable evidence means
stop. The rollup may lack branch protection, so `--required` alone and merge
readiness alone are insufficient.

```bash
gh run list --workflow rollup.yml --event pull_request --branch "$feature" --commit "$child_head" --json databaseId,status,conclusion,headSha,url
gh run view "$check_run" --json displayTitle,event,headSha,status,conclusion,jobs,url
gh run view "$check_run" --log
gh pr checks "$child_pr" --watch --fail-fast --interval 10
gh pr view "$child_pr" --json state,baseRefName,baseRefOid,headRefName,headRefOid,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup
```

Select `check_run` from the actual check linked to this PR. Its run name,
`Targeted checks integration <sha>`, records the synthetic merge it tested; its log's
`Targeted checks on <sha> tree <tree>; parents <base> <head>` line shows that the
checked-out merge has exactly the recorded rollup base and child head as parents.
Require that name, line and the current head and base to agree; the list command
narrows candidates but does not establish that match alone. Inspect the linked run
when multiple events/reruns exist. Require successful completion of its `targeted`
job and the whole run. Keep this wait within the same fifteen-minute bound.

Before merging, require OPEN, the intended branch names and SHAs, non-draft status,
satisfied hosted review policy and CLEAN merge readiness. Recheck parent ownership
and serialize integrations. On base/head drift, merge current rollup into the child
and repeat affected review/checks. Use the authenticated account's GitHub no-reply
address for `merge_email`, following the public-work policy above:

```bash
gh pr merge "$child_pr" --merge --match-head-commit "$child_head" --author-email "$merge_email"
gh pr view "$child_pr" --json state,mergeCommit,url
git fetch origin
```

Verify MERGED, exactly two merge parents matching the intended rollup base and child
head, and merge reachability in `origin/$rollup`. Inspect author/committer metadata
against the public-work policy. Compare the merge's parents and tree with the
integration revision recorded by `check_run`; a match makes that run the merge's
targeted evidence. On a mismatch, stop and investigate; the child stays open while
its merged revision lacks attributable checks. Record review, checks and merge
evidence on the child before explicitly closing it. Do not rely on issue auto-close
keywords for a PR into a non-default branch. Keep the parent open for final delivery.
The PR body links the parent without an auto-close instruction.

For final delivery, review the complete rollup-to-test diff and use the canonical
path above with one semver classification for the whole result. It catches the
rollup up with test like any task branch, and its PR to test runs full Validate. Promotion already counts only
first-parent test PR merges, so child integration PRs are excluded without a new
version ledger. On a failure inspect actual refs, PR state and merge effects before
resuming; never blindly replay a merge or bypass branch protection.
