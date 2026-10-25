---
name: cleanup-task-artifacts
description: Establish ownership before launching temporary compute; release task-owned resources at major work boundaries or during an authorized daily sweep.
disable-model-invocation: true
---

# Cleanup Task Artifacts

Use before launching temporary compute and at the end of validation, a proof, a substantial work phase, delivery or
promotion, and before pausing for failure, human input or final handoff. The
authorized work includes cleanup of its own temporary resources; another cleanup
request is unnecessary. Also use for the explicitly installed daily sweep.
Cleanup does not authorize Machine Reconciliation, updates, unrelated repair,
publication, or broader deletion. Read the relevant repository's AGENTS.md and
local delivery/artifact guidance. Protect the current task's own environment.

## Establish resource lifetime

When starting temporary compute, establish its exact identity, owning operation,
and teardown command through the existing local lifecycle owner. Prefer its
automatic cleanup on success, failure and handled interruption. Keep evidence in
the existing task/run output and native resource metadata, not a new registry.
If a launcher lacks teardown, the supervising agent still owns safe cleanup and
files the launcher defect through the repository's tracker guidance.

At a major boundary, inspect resources started or retained by the work, including
delegated work. An ended validation operation can release its compute while the
overall task remains open. An attached checkout, retained data or failed proof is
not by itself a reason to leave temporary services running. Capture needed
diagnostics, then stop proven-owned compute that is no longer needed. Preserve
failed diagnostic state unless its deletion is independently safe. Remove stopped
containers and dedicated networks only when no needed state or other user depends
on them; volumes and checkpoint images retain their local ownership rules.

Keep services required by active work or a pending verification gate. An explicitly
retained live preview needs exact resources, an owner, a reason and a stop/restart
procedure in the task's existing evidence. Durable product agents and shared
services have their own lifecycle; task completion never makes them disposable.
An interruption that bypasses teardown, such as host loss, needs later inspection
by the supervisor or daily sweep, not a claim that exit handlers always ran.

## Discover participating repositories

For a daily sweep, obtain exact known project roots from the host's supported project
inventory, or use roots explicitly supplied by the supervising agent. On Codex, use
the supported Codex project inventory. Pass those roots to this package's
`scripts/discover.py` with Python 3.9+ (resolve the script relative to this skill).
It parses only the root AGENTS.md Repository Standard section and verifies the exact
Orca Pod source and adopted commit through gh. It checks each distinct revision
once and reports eligible roots or skip reasons. Never replace this discovery procedure
with a grep for arbitrary hashes, a filesystem sweep, internal app-storage scraping,
or a new registry. Unavailable inventory/source evidence means skip, not inferred
participation. Direct delivery cleanup may use the already verified current
task/repository scope before the repository's first adoption.

Read every discovery result. Distinguish roots without adoption from a declared
adoption whose source cannot be verified or whose guidance cannot be read. A newly
observed broken participation path or unavailable discovery is actionable; report
it with its skip reason and continue independent eligible roots. Missing evidence
preserves the affected resources; it is not a successful empty sweep.

For participating roots, explicitly inventory running AND stopped containers,
dedicated networks and local background processes where those resources are used.
Resolve the actual Docker context/endpoint used by the work; inspect `docker ps -a`
and only relevant `docker inspect` fields (state, labels, mounts and restart
policy), without dumping environment variables or credentials. Use Compose project
and working-directory labels or the local owner's equivalent to find candidates,
including projects in retained worktrees. A default development `down` command may
target a different namespace from validation. Missing Docker/process access is a
coverage limit, not proof of no leftovers. Do not start an unavailable engine or
contact an unrelated remote context just to expand the sweep.

## Establish what can be removed

Eligibility only establishes participation. For every candidate establish BOTH
association with the owning task/operation and safety of the proposed stop/removal,
using actual task, Git, container, process, or artifact evidence. Establish that
the operation has ended and the resource is no longer needed; the entire task
need not be completed. Names, age and a stopped state suggest candidates but never
prove ownership or safety. Inspect exact resource identifiers and local
runbook-defined artifacts; handle all qualifying task resources, not just branches.

Preserve active work, shared resources, uncommitted/unpublished changes, needed
evidence, uncertain artifacts, and the sweep's stable source checkout. Verify a
branch's commits are delivered before deleting it. Inspect dirty state and current
users before considering a worktree. Never blanket-prune branches, worktrees,
containers, or logs. Reinspect the exact resource immediately before mutation.

Never remove a checkout still backing a task. Use supported host lifecycle
operations for app-owned worktrees. On Codex, use Handoff only when supported,
appropriate, and safe for both checkouts; the calling task cannot hand itself off,
and shell cd does not change task attachment. Do not create helper tasks or edit
internal app storage to evade this limitation. On a host without supported lifecycle
evidence or handling, retain the checkout. Report actual cleanup separately from
delivery completion.

## Conservative automatic archival

Automatic archival additionally requires positively verified completion, unpinned
status, no active execution, no pending input/approval or unresolved work, and MORE
THAN SEVEN DAYS since the task's exact observed last-turn timestamp. No timestamp
or unclear completion means skip. Do not use file modification time, task title,
creation date, or an invented timestamp as a substitute. Do not relax the threshold.

Use supported task listing/reading to establish evidence, recheck current state,
then use supported archival. Do not assume that archival physically removed its
checkout; observe and report actual lifecycle results. Preserve any local state
that archival/removal could endanger. Headless hosts without supported task evidence
skip affected archival and checkout removal.

## Verify the disposition before reporting

Recheck identity and current users immediately before a stop/removal. Invoke the
existing exact-resource teardown and inspect the resulting container/process state;
a launched cleanup command or successful validation exit is not teardown evidence.
Account for stopped/removed resources, explicitly retained live resources and
unresolved resources in the existing task/run evidence. Missing task timestamps or
checkout lifecycle tools restrict archival/checkout removal, not independently
provable cleanup of an ended operation's temporary compute.

Investigate unexpected failures before further action; do not blindly retry destructive steps
or build a cleanup journal/state machine. Batch genuine human decisions after
finishing independent cleanup. Before the final response or pause, report meaningful
cleanup and any retained live resources, failed teardown or missing evidence that
needs action. Do not describe unresolved teardown as completed cleanup or close an
issue whose acceptance requires it.

Scheduled runs retain a concise disposition in their existing run output/memory,
including coverage limits and discovery failures. Notify on meaningful cleanup,
new or materially changed failures, or required action; remain quiet on unchanged
non-actionable skips and genuine no-ops. An unchanged known failure remains
unresolved in the run evidence even when it needs no repeat notification.
