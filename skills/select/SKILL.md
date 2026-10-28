---
name: select
description: Select a Wayfinder map or an implementation backlog in an explicit effort scope, inventory existing selections, or carry out an approved selection handoff or legacy import.
---

# Select

## Binding and owner

Read [selection scope and handoff](SELECTIONS.md) before selecting, reading,
resuming, importing, refreshing or transferring a map or backlog, or assessing
which efforts hold selections. Establish the explicit scope and task-owner binding
from the current task, preserving other efforts. Each scope keeps independent map
and backlog entries, each with its own owner and generation, so concurrent
orchestrator threads, including two in one checkout, each bind their own scope.

Resolve scripts relative to this skill directory. `scripts/select.sh <kind>` passes
`map` or `backlog` to the shared resolver; its `--help` owns the exact interface.
Derive the owner, this task's Orca worktree identity (plus its dispatch ID inside a
Run), with `scripts/select.sh <kind> owner [--dispatch <dispatch-id>]`. A missing
script or resolver is a concrete failure, never a reason to write state manually.

For a new selection run `scripts/select.sh <kind> select --scope <scope> --owner
<task> --expect-absent <issue-url>`. For an authorized change use the retained
`--generation <generation>` instead of `--expect-absent`. The helper validates an
open issue in the current repository with the kind's label, atomically updates
only that scope's entry of that kind and preserves existing state on failure.

Establish an initial binding through `show`; continue with `check` against the
retained generation. Report scope, owner, generation, issue name and URL from the
result. Completion requires successful readback, not just a launched script.

For human-approved handoff/takeover or explicit legacy migration, follow the
corresponding branch in the shared contract and use `transfer` or `import-legacy`,
preserving the other selection, tracker claims, dependencies and design gates.
For read-only assessment use `list`, which establishes no binding. Selection and
ownership transfer never substitute for planning, execution or tracker claim
authority.

## Map

Use the `wayfinder:map` URL supplied by the user or established by an authorized
workflow; the human need not repeat the URL or invoke another command. Preserve
competing selections unless existing authority covers switching. After an
authorized repository rename, use `refresh` through the shared contract's rename
branch.

## Backlog

Use GitHub through `gh` and read the repository's tracker instructions. Resolve
this repository with `gh repo view`. This kind selects an existing parent; `triage`
owns intake and grouping, while `to-spec` and `to-tickets` own preparing and
publishing an approved specification and breakdown. Triage selects through this
same owner and mechanism.

### Select the existing parent

A supplied parent may come from the owning workflow under an implementation
request covering its approved scope and selection; the human need not repeat its
URL or issue a separate command. Preserve a competing effort unless switching is
authorized.

Read the supplied issue, comments, all native children (`sub_issues
--paginate`), and its linked design. Verify it is an open implementation
specification in this repository with an objective, approved scope and sources,
completion boundary, and standing preferences. Verify covering resolved map/spec
evidence under the global Planning before implementation rule, or the explicit
scoped planning waiver; a closed planning map is not an implementation parent.
Show the parent's name, objective, and child scope. Preserve membership,
blockers, and claims.

An explicit request to select that parent is sufficient authorization, including
replacing an existing selection. Add `implementation:backlog` if absent and the
issue is clearly the requested implementation parent; create the label if needed.
Clarify an ambiguous issue's role before converting it. Ready admission alone is
not activation authorization.

Without a supplied parent, inspect this task's explicit scoped binding through
`scripts/select.sh backlog` (missing context is an error), and paginate all open
`implementation:backlog` parents. Show the current selection and recommend an
existing prepared parent by name and scope. Wait for the user's selection in
ordinary text, unless this conversation already supplies it. If no suitable parent
exists, use `triage` to prepare approved work; do not create or group issues here.

Recheck the intended parent's state and role immediately before `select`, then
save and read back the binding under Binding and owner. Selection does not claim
work or authorize development.
