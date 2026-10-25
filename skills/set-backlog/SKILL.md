---
name: set-backlog
description: Select an implementation backlog in an explicit effort scope, or carry out an approved backlog handoff or legacy import.
---

# Set Backlog

Read [selection scope and handoff](../set-map/SELECTIONS.md) to establish the
explicit scope and task-owner binding for selection, continuation, import or
handoff. Use GitHub through `gh` and read the repository's tracker instructions. Resolve
this repository with `gh repo view`. This entry point selects an existing parent;
`triage` owns intake and grouping, while `to-spec` and `to-tickets` own preparing
and publishing an approved specification and breakdown.

## Select the existing parent

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
the selector (missing context is an error), and paginate all open
`implementation:backlog` parents. Show the current selection and recommend an
existing prepared parent by name and scope. Wait for the user's selection in
ordinary text, unless this conversation already supplies it. If no suitable parent
exists, use `triage` to prepare approved work; do not create or group issues here.

## Save and verify

Recheck the intended parent's state and role, then run
`scripts/set-backlog.sh select --scope <scope> --owner <task> --expect-absent
<parent-url>` relative to this skill directory. For an authorized change use the
retained `--generation <generation>` instead of `--expect-absent`. Triage uses
this same owner and mechanism. `--help` owns the exact interface.

The helper validates the open current-repository parent and atomically updates
only this scope's backlog entry; failure preserves existing state. It requires
the installed sibling set-map package's shared resolver. Missing capability is a
concrete failure, never a reason to write a pointer manually.

Establish a new authorized binding with `show`, then use `check` with the retained
generation for continuation. Report scope, owner, generation and the parent's
name/URL. Selection does not claim work or authorize development. Follow the
shared contract for human-approved `transfer` or explicit `import-legacy`,
preserving the map binding, tracker claims, dependencies and design gates.
