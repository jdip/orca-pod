---
name: cleanup-task-artifacts
description: Establish ownership before launching temporary compute; release task-owned resources at major work boundaries or during an authorized daily sweep.
---

# Cleanup Task Artifacts

Use before launching temporary compute and at the end of validation, a proof, a substantial work phase, delivery or
promotion, and before pausing for failure, human input or final handoff. The
authorized work includes cleanup of its own temporary resources; another cleanup
request is unnecessary. Also use for the explicitly installed daily sweep.
Cleanup does not authorize host installation (`machine/install.py --apply`, see
`docs/install.md`), updates, unrelated repair,
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

For a daily sweep, obtain exact known project roots from Orca's project inventory
(each `path` in `orca repo list --json`), or use roots explicitly supplied by the
supervising agent. Pass those roots to this package's
`scripts/discover.py` with Python 3.9+ (resolve the script relative to this skill)
and keep its output for the inventory's `--discovery`. It parses only the root AGENTS.md Repository Standard section and verifies the exact
Orca Pod source and adopted commit through gh. One explicit exception: the
Standard's own source repository adopts no Standard, so a checkout top level whose
`origin` remote is jdip/orca-pod is admitted with basis `source repository`, its
HEAD verified through gh the same way. Its worktrees still face every inventory and
delivery-evidence check below. It checks each distinct revision once and reports
eligible roots, each with its basis and expected `repository` key
(`github.com/jdip/orca-pod` for the source repository, else the root's GitHub
`origin`, or none), or skip reasons. Never replace this discovery procedure
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

## Inventory Orca resources

Run this package's `scripts/orca_inventory.py --discovery <file>` (Python 3.9+,
resolved relative to this skill), passing this run's saved `discover.py` output. It
is always a dry run: it reads `orca worktree current`, `orca repo list`, `orca
worktree ps`, `orca terminal list`, and `orca orchestration worker-list --run <id>`
for every Run in `orca orchestration run-list`, plus each local checkout's Git state
and a hosted `gh` compare, and changes nothing. It marks each Orca worktree
`retain`, with its reasons, or `candidate`, with its `repo_id` and `repo_root`, and
lists settled workers whose terminals are reclaimable.

A candidate's repository passed this run's discovery, Orca's `gitRemoteIdentity`
`canonicalKey` for it is exactly that discovery's `repository` key, and its checkout
shares that repository's Git common directory. A worktree in any other repository,
with unknown, mismatched or stale remote identity, or whose discovery recorded no
repository, is retained before any hosted compare; without `--discovery` nothing is a
candidate. The inventory validates every Orca response strictly: required fields
present with exact types, complete pagination and untruncated listings covering
every host, booleans as booleans and timestamps as plausible epoch milliseconds,
never a missing value read as an empty default. A gap in a worktree's row retains
that worktree; a gap in a listing that covers all worktrees (`inventory_gaps`)
retains every worktree. Both report the gap. A live Orca terminal or agent, an
unsettled or unreleased worker, the main checkout, the sweep's own worktree, local
changes or unpublished commits also retain the worktree. A settled worker's adopted
terminal (`external`, `retained`), which `worker-release` keeps, counts as released
once closed and absent from a complete `orca terminal list`. A candidate also needs
hosted delivery evidence (`delivery`): a `gh` compare against discovery's repository
showing its HEAD already on its `test` delivery branch. Local remote-tracking refs never count. A
failed inventory preserves every resource. A candidate is only a proposal for the
checks below.

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

Never remove a worktree backing a live Orca agent, terminal or unsettled worker,
and never remove the calling task's own worktree. Remove an Orca-managed worktree
only with `orca worktree rm --worktree id:<worktreeId>`, never with `git worktree
remove` or by editing Orca's app storage; it keeps branches Orca cannot prove are
merged, and repo archive hooks run only with `--run-hooks`. Use exactly the
selector the inventory prints in `after_recheck`. Release a settled
worker's terminal with `orca orchestration worker-release --dispatch <id>`; leave
`worker-retain`ed terminals alone. Without Orca inventory evidence, retain the
checkout. Report actual cleanup separately from delivery completion.

## Conservative sweep removal

A daily sweep is a dry run by default: it reports the inventory and dispositions.
Removing a worktree the sweep did not create needs explicit removal authority from
the installed sweep or the operator, an inventory `candidate` disposition whose
`repo_id` and `repo_root` match a repository that passed this run's discovery,
authoritative hosted delivery evidence (the inventory's hosted compare, or a hosted
merged PR whose merge commit contains its HEAD on the delivery branch; local
remote-tracking refs alone never count), no pending input/approval or unresolved
work, and MORE THAN SEVEN DAYS since its Orca `lastActivityAt` (the inventory's
`idle_days`). Without that delivery evidence, skip. No timestamp or unclear completion means skip. Do not use
file modification time, worktree name, creation date, or an invented timestamp as a
substitute. Do not relax the threshold.

The installed sweep's authority covers exactly that removal: a worktree meeting every
condition above, with no live Orca agent or terminal attached, removed only with
`orca worktree rm --worktree id:<worktreeId>` and no other flag. Everything else it finds
stays report-only, including settled worker terminals, branches, containers,
networks, processes and any worktree failing one condition.

Rerun discovery and the inventory immediately before each removal and recheck the
exact worktree, its repository identity and delivery evidence. Observe and report the actual result of `orca worktree rm`, including a
retained branch. Preserve any local state that removal could endanger. A host
without Orca inventory skips worktree removal.

## Verify the disposition before reporting

Recheck identity and current users immediately before a stop/removal. Invoke the
existing exact-resource teardown and inspect the resulting container/process state;
a launched cleanup command or successful validation exit is not teardown evidence.
Account for stopped/removed resources, explicitly retained live resources and
unresolved resources in the existing task/run evidence. Missing Orca timestamps or
inventory restrict worktree removal, not independently provable cleanup of an
ended operation's temporary compute.

Investigate unexpected failures before further action; do not blindly retry destructive steps
or build a cleanup journal/state machine. Batch genuine human decisions after
finishing independent cleanup. Before the final response or pause, report meaningful
cleanup and any retained live resources, failed teardown or missing evidence that
needs action. Do not describe unresolved teardown as completed cleanup or close an
issue whose acceptance requires it.

Scheduled runs retain a concise disposition, including coverage limits and
discovery failures, in this package's `scripts/sweep_state.py` (Python 3.9+). Once
the run's actions are done, pass it a JSON object mapping each finding's stable key
(such as `worktree:<id>` or `discovery:<root>`) to its concise disposition from the
final inventory, leaving out values that change every run, such as `idle_days`
itself rather than whether it exceeds seven days. It reports what is new, changed or gone since the previous sweep
and keeps these findings for the next one in one file under the Git common
directory, holding an exclusive lock from read to replace and refusing a
symlinked, foreign or duplicate-keyed state. Report the run's own cleanup actions and those changes only; when
nothing changed, say so in one line. An unchanged known failure stays recorded as
unresolved even though it is not repeated. If the state cannot be read or kept,
report that and every finding.
