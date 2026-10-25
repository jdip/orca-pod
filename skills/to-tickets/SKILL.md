---
name: to-tickets
description: Publish an approved implementation specification parent, native tickets, and their real dependency edges to GitHub.
---

# To Tickets

Adapted from [`mattpocock/skills` to-tickets](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/to-tickets), revision `3cca18b368ae95cdbdebbff572ccafa662551015`.
Copyright (c) 2026 Matt Pocock. This adaptation is licensed under the included [MIT License](LICENSE).

Publish one approved implementation specification parent and its outcome-based
native child issues. Parent membership and blocking are separate GitHub
relationships. This skill prepares work only; it neither selects an active
backlog nor authorizes implementation.

When resolving or changing a saved selection, read
[selection scope and handoff](../set-map/SELECTIONS.md). Carry the explicit
scope, task owner and generation through handoffs to selection/execution owners.
Keep map and backlog bindings independent. Publication and closed design do not
change another effort's selections or grant takeover authority.

## Confirm the approved handoff

Resolve the current repository with `gh repo view`, then read its tracker
instructions, the approved specification, its comments, and linked design and
decision sources. Require a covering resolved Wayfinder map unless the operator
explicitly waived that requirement; missing coverage returns to Wayfinder and
`to-spec`. Confirm the whole map is closed and resolved before publishing
executable children. Use issue bodies for the current approved scope and
acceptance criteria; comments supply decision history and evidence. Update a
body to incorporate an approved amendment before it becomes the published
contract.

Confirm the parent's `Delivery` field is part of that approved contract. One-child
parents default to `direct`. Multiple-child parents use `rollup` and name
the exact `orca/` rollup branch based on fresh `origin/test`; an earlier test
delivery needs an explicit user decision. Read [rollup delivery](../pr-to-test/ROLLUP.md)
for the shared branch and CI rules.

Before creating anything, search open `implementation:backlog` parents and their
native children for the same linked sources and scope. Reuse that same-effort
parent and approved children when found. Inspect each proposed existing child's
parent, dependencies, state, and assignees; preserve claims and work attached to
another effort. Never create a duplicate parent or ticket merely because a prior
publication was partial.

If the specification and ticket breakdown were not reviewed together, draft both
and present one ordinary-text batch: parent scope and acceptance criteria; every
ticket's independently verifiable outcome and acceptance criteria; and each real
blocking edge. Wait for the user's approval. Reuse an earlier explicit approval
only when it covers the same parent scope and breakdown. Do not create issues as
an administrative substitute for missing approval.

## Publish the approved batch

Create or update the one specification parent with its current approved body and
the `implementation:backlog` label. Include links to the resolved map and
material decisions, but do not duplicate their history. Do not replace a parent
from another effort, alter claims or dependencies, or change the saved
active-backlog pointer. Preserve an existing parent's actual scheduling state.
For `rollup`, preserve the named branch and final PR-to-test acceptance boundary
in the parent rather than distributing aggregate delivery across children.

Create the approved child issues in dependency order. Each body contains:

- the parent reference;
- the independently verifiable outcome;
- current acceptance criteria; and
- specification and relevant decision links.

For a `rollup` parent, every child states that its delivery boundary is reviewed
merge-commit integration with targeted checks into the named branch. Full CI, the
final canonical PR-to-test, verified test delivery, and one semver contribution
remain parent acceptance criteria.

Set acceptance evidence by purpose: Application Code requires linting, type
checking, validation, meaningful behavioral tests, and strong coverage; Tooling
requires focused source checks and proportionate behavioral evidence available now.
Keep the approved acceptance within the global Validation and delivery closure
rule: unexercised scenarios are stated limits, not added future-use gates or
separate proof tickets. Prefer clean replacements
that remove superseded callers and configuration. Use expand--contract only when a
concrete blast radius requires temporary coexistence.

Create children without assignees. Publication alone supplies no execution
authorization. Carry an existing implementation request through selection and
`next-issue` or `next-issue-loop` when it covers this approved scope; those
owners select and claim work.

For GitHub, use native sub-issues for membership. Before attaching an existing
issue, inspect `GET repos/<owner>/<repo>/issues/<child>/parent`. Attach a detached
approved child with `POST repos/<owner>/<repo>/issues/<parent>/sub_issues` and
`-F sub_issue_id=<child-database-id>`. A child already attached to the intended
parent needs no change. A child attached to another parent, or carrying an
existing claim, stays in place unless the user explicitly authorizes that move.

After membership is established, add each genuine blocker independently with
`POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by` and
`-F issue_id=<blocker-database-id>`. Do not encode dependency state as a task-list
order or substitute parent membership for a blocker edge.

Use the tracker fallback only when the native membership or dependency feature is
proven unavailable: follow the repository convention for an ordered `## Backlog`
list and `Part of #<parent>` children, and record blockers in the designated child
body. Authentication, authorization, network, or service failures are not feature
unavailability; preserve the partial state and report the access failure.

## Read back and recover

Read `GET repos/<owner>/<repo>/issues/<parent>/sub_issues --paginate` and each
child's `GET repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by --paginate`.
Confirm that all approved children have the intended parent and the actual blockers
match the approved breakdown.

Confirm each parent and child links to the relevant design sources, then read the
design body and comments for a reciprocal link to the parent. If it is missing,
add one concise source comment and read it back. Retain the design's existing
decision history rather than replacing it.

If a write partially fails, inspect the parent, each affected child's parent,
dependencies, state, and claims before retrying. Retry only the missing attachment
or edge after readback. Preserve completed writes and never create a replacement
parent, duplicate ticket, steal a claim, or reparent another effort to recover.

Report the parent and child URLs, verified membership and dependencies, and the
source links. Publication alone leaves a newly created parent prepared; an
existing parent's active or executing state is preserved. An explicitly authorized
backlog selection and `next-issue` or `next-issue-loop` request controls future
execution.
