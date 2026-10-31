# Selection scope and handoff

Read this contract when a workflow selects, reads, resumes, forks, moves or hands
off a saved map or implementation backlog. The select package owns the shared
resolver and its `map|backlog` entry script. Use that script, never direct
state-file edits. Run `--help` for exact arguments. The script runs on the
`ORCA_POD_PYTHON` interpreter, Python 3.14+.

## Establish the binding

An **effort scope** is a stable identifier for independently selected work in one
repository. It is not a branch, checkout path, issue number or permission to act.
A **task owner** is derived by the selector's `owner` command from the current
worktree's identity key in `orca worktree current`, in one of three forms:

- `<worktree key>:<dispatch-id>` for a worker inside an Orca Run. Pass `--dispatch
  <dispatch-id>` from the task's own dispatch context; the command verifies the
  dispatch's worktree through `orca orchestration worker-show`.
- `<worktree key>:session:<session-id>` for an Orca agent session outside a Run.
  The command reads `ORCA_AGENT_SESSION_ID` and accepts it only when `orca
  worktree ps` lists that structured agent session under the current worktree, so
  two coordinator threads in one checkout get distinct owners.
- `<worktree key>` when the session is unset or Orca lists no such agent, such as
  in a plain terminal.

Its JSON reports `session` and `dispatch` beside `worktree_identity`. A session
that Orca lists under a different worktree, an unsafe session ID or an incomplete
Orca listing is conflicting context, and `owner` fails. For the
**cross-repository owner**, a coordinator working another repository runs `owner`
in its own checkout, where Orca lists its session, and passes that owner with
`--owner` to the target repository's commands. Selection state is per repository,
so one owner string is valid in each. Outside Orca, record an explicit unique
path-safe identity with this task instead. Establish both scope and owner from
the current task's explicit context; missing or conflicting context is an error.
Derive ownership only through `owner` or that explicit context, never
by enumerating scope files or trusting a shell environment inherited from another
task; Orca's `ORCA_WORKTREE_ID` can name the launching coordinator's worktree
rather than the worker's.
A scope selected under the earlier worktree-only owner keeps that owner and stays
valid. A task with a new session owner receives a still-live scope only through
the approved handoff's `transfer`; nothing migrates silently.
For a new effort, the agent may choose a unique scope and report it under existing
selection authority. Reuse the established scope on continuation.

Each scope has independent map and backlog records, each with its own owner and
generation. Two tasks in one checkout use different scopes, just as tasks in
separate worktrees do. Following a partial handoff, a task may bind its map and
backlog to different scopes; record each explicitly. One scope does not silently
replace a task's other selection. State lives untracked under
`orca-pod-selection-scopes` in Git's absolute common directory. A scope record is
atomically replaced under a scope lock; the two entries change together only for
an explicitly requested full handoff. Legacy root pointers remain separate.

Use the relevant selector's `show --scope <scope> --owner <task>` only when first
binding to an explicitly selected effort or receiving an approved handoff. Retain
the returned scope, owner, generation and issue URL in the current task/handoff
context. For an existing binding use `check --scope <scope> --owner <task>
--generation <generation>`; never replace a stale generation with `show` to make
a continuation succeed. A confirmed absent entry is different from unreadable,
invalid, inaccessible, foreign or transferred state. Only explicit absence in a
known scope permits initial `select --expect-absent`.

## Assess selections

To learn which efforts hold selections, run `list` under either kind instead of
reading state files. It reads local state only, without locks or tracker lookups,
and reports every scope's map and backlog issue, owner and generation, Agent Team
scoped records and legacy root pointers; an unreadable record appears as that
scope's `error`. The inventory is assessment evidence, never a binding: a task
still establishes its own scope and owner from explicit context and binds through
`show`. Agent Team records or pointers mean legacy state awaiting import, not an
empty repository.

Before repository/tracker mutations, on resume after interruption or human input,
and between loop tickets, check the retained binding and current tracker/design
state. Failure stops dependent work with existing state preserved. Changes made
through an authorized selection operation return a new binding; record it as that
operation's result. A selection error never authorizes a new scope, another issue,
a takeover or removal of an uncertain lock.

## Select and continue

`select` validates an open issue in the current repository with the required
`wayfinder:map` or `implementation:backlog` role. An initial selection requires
`--expect-absent`; changing one requires the current owner and `--generation`.
Read the returned issue name/URL, scope, owner and generation back. Preserve the
other selection. All consumers use this contract, including triage and planning
or specification handoffs. A closed selected issue remains historical state;
completion never selects a replacement automatically.

Selection grants no implementation or claim authority. Preserve the existing
map/spec gates, tracker membership, native dependencies and claim rules.
Implementation always checks its specification's associated map, even if its
independently selected planning map points elsewhere. Before adopting a parent
also selected by another task, establish that task's ownership and obtain the
required handoff; creating another scope does not bypass claims.

A resume or move among worktrees sharing the same Git common directory retains
the explicit binding; checkout names and paths play no part. A moved task keeps
its retained owner rather than deriving a new one; another agent, worktree or
dispatch derives a different owner, so continuing there is a handoff. An independent fork
gets a new scope and task owner, and establishes its own authorized selections.
It cannot reuse a copied parent binding. For a separate clone, no state follows
automatically: preserve the old binding and require explicit validated selection
or import in the destination with handoff evidence. Missing host lifecycle or
source evidence stops the dependent transfer; never claim automatic cross-clone
or cross-machine synchronization.

## Human-approved handoff

Use this branch when the operator asks tasks to hand off or take over a map,
backlog or both. Reuse an existing explicit approval only for the named source,
recipient, selections, included claims and execution scope. A finished turn,
shared assignee, tool access or approval of this feature is not approval for an
unrelated real transfer.

1. Read the source and recipient task state with `orca worktree ps --json` and,
   for Run workers, `orca orchestration worker-show --dispatch <id> --json`, their
   retained selection bindings, related issues, claims, dependencies and unfinished
   repository work. Present the concrete transfer when approval is missing.
   Preserve a recipient's conflicting selection until the operator resolves it.
2. Stop source work in the transferred selections through an acknowledged
   handoff or, for a Run worker, its coordinator's `orca orchestration worker-stop`.
   Verify quiescence, including delegated work and in-flight repository/tracker
   writes. In a fresh `orca worktree ps --json`, the source worktree's row shows
   no agent outside the `done` state; inside a Run, `worker-show` reports the
   source dispatch settled (for example `completed`, with its worker terminal
   released). Merely sending a message or seeing an old status is insufficient.
   Missing or unverifiable evidence preserves ownership.
3. Record approval, source-stop evidence, included claim transfers, unfinished
   changes/branch references, and the next permitted action in the existing task
   or tracker context. Keep private host/session details out of public tracker
   records. Use existing tracker owners to transfer included claims explicitly;
   do not reparent issues or change dependencies. Verify their readback. Leave
   source and recipient stopped if a partial failure needs investigation.
4. Invoke `transfer` under either kind with `--scope`, `--from-owner`,
   `--to-owner`, `--kinds map|backlog|both`, each selected kind's expected
   `--map-generation` / `--backlog-generation`, `--approval-ref`, and
   `--source-stopped-ref`. The references point to the actual evidence above.
   The helper requires them but does not establish human approval or Orca
   quiescence: the supervising agent owns that verification.
5. The helper atomically changes only the named entries' owners and generations
   in the same scope. Verify the recipient's `show` result, establish its new
   binding, and recheck tracker claims and associated design before resuming.
   A partial transfer leaves the other entry and owner intact. Retire the source's
   transferred binding in its task context; its old owner/generation must now fail.
   Future work in the source task uses only its remaining authorized selections.

There is no distributed transaction with GitHub or task controls. On an uncertain
result, inspect actual selection and claim state, preserve partial effects, and
resume only the missing operation under the same approval. Do not restart source
work, silently reverse claims or repeat a completed transfer. Checking a binding
cannot cancel an already-running command; verified source quiescence is essential.

## Legacy import and rename

Legacy state in Git's common directory is a historical input, never a fallback
selection. Root pointer files are `orca-pod-wayfinder-map` and
`orca-pod-implementation-backlog`, or their Agent Team-era names
`codex-wayfinder-map` and `codex-implementation-backlog`; import reads whichever
exist and refuses pointers that disagree. Agent Team scoped records live in
`codex-selection-scopes/<scope>.json` with the current record format.

With explicit migration authority, run the relevant selector's `import-legacy
--scope <scope> --owner <task> --expect-absent`, adding `--agent-team-scope
<scope>` to import that Agent Team scope's entry. Normally keep the scope name.
Without that option, import refuses root pointers when the same-named Agent Team
scope holds that kind. Import validates that the legacy URL belongs to the current
repository and has the required issue role, and that an Agent Team entry still
resolves to its recorded issue identity; closed historical issues are allowed. It
creates only the absent scoped entry, owned by the importing task at generation 1,
and leaves every legacy file and the other scoped entry unchanged. The Agent Team
owner is not carried over. Import each kind separately and verify each result.
Existing destination state, malformed input or a failed lookup preserves all
state; investigate rather than choosing a different scope silently.

For an authorized repository rename, capture the map's immutable issue node ID
before the rename. After updating the remote, use map `refresh` with its scope,
owner, current generation and `--expected-issue-node-id`. It must resolve the same
issue in the current repository, including a completed map, then return the new
binding and canonical URL. A failed identity check preserves the selection.
