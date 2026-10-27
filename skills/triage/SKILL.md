---
name: triage
description: Assess incoming implementation work, maintain ready parents, and activate an approved ready parent when no backlog is active.
---

# Triage

Adapted from [`mattpocock/skills` triage](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/triage), revision `3cca18b368ae95cdbdebbff572ccafa662551015`.
Copyright (c) 2026 Matt Pocock. This adaptation is licensed under the included [MIT License](LICENSE).

Refine implementation intake into approved, discoverable work without changing an
active effort. Issue bodies hold current scope and acceptance criteria; comments
hold discussion, decisions, and evidence. Fold an approved amendment into its
body instead of treating a triage brief or comment as the contract.

## Establish backlog state

Resolve the current repository with `gh repo view` and read its tracker guidance.
Read [selection scope and handoff](../set-map/SELECTIONS.md) and inspect the
explicit scope through the backlog selector. Retain and check the task's binding.

- Only an explicit absent result for the established scope means there is no
  active parent. Missing scope/owner context is an error, not an empty queue.
- A selection of a closed parent means no active parent in this scope; retain it
  until an authorized selection replaces it.
- A selection that is unreadable, malformed, transferred, stale, identifies
  another repository, or cannot be read from the tracker is an error, not an
  empty active state. Stop and report it.
- An open pointed parent must be labelled `implementation:backlog`; it is the one
  active parent in this effort. Other efforts may have their own active parents.
  Routine triage preserves their selections and claims; refinement
  follows the approved-scope rules below.

A **Ready Backlog** is an open, non-active parent carrying both
`implementation:backlog` and `implementation:ready`. Read all such parents and
supported task ownership evidence before recommending work; another effort's
active or uncertain claim is not available intake. Readiness is separate from
active selection and execution authorization.

## Assess intake

Read each named issue's full body, comments, labels, parent, dependencies, and
assignees. For broad intake, paginate every open issue from the current repository,
including blocked and claimed candidates; exclude pull requests where the tracker
does not use them as a request surface. Inspect candidate parent and dependency
relationships directly when summary data is unclear.

Use the repository's domain terms and inspect relevant code before recommending an
outcome. Search existing issues and current behavior for duplicates. Refine,
deduplicate, and order work autonomously within already approved scope, while
preserving claims. Surface external blockers rather than absorbing them into an
unrelated parent.

Apply the global Planning before implementation rule. Reuse a resolved map and
approved specification only when they cover the candidate, including small
fixes. Otherwise begin or resume Wayfinder, then use `to-spec` and `to-tickets`
for a proportionate parent and executable-child batch. Only an explicit scoped
operator waiver changes that gate. Substantive unresolved design pauses
associated execution; ordinary refinement within approved coverage does not
reopen the map.

Scope expansion and moving an issue between efforts require the user's explicit
decision. Do not reparent another effort's issue or modify an existing claim.
When approved work enters a parent, use the tracker’s native membership and
dependency operations separately, preserve its actual blockers, and read both
relationships back.

## Admit and activate deliberately

Batch ready human decisions in ordinary text and wait for answers. Reuse explicit
prior admission or activation authorization when it covers the same parent and
scope. When no parent is active, admission and activation may be approved together;
specification approval alone supplies neither.

For a prepared non-active parent, first show its objective, child scope,
external blockers, and source links. Reuse a request that already authorizes
admitting and implementing this same effort; otherwise ask whether it should
join the Ready Backlog. Specification or ticket approval alone does not supply
that authority. After consent, create `implementation:ready` if necessary, apply
it alongside `implementation:backlog`, and read the parent back. Do not alter
the active scoped selection.

Offer activation only when there is no active parent in this scope. Name the selected Ready
Backlog parent and obtain authorization to activate it. Recheck this scope's
selection, owner/generation and parent state immediately before selection; if
another parent has become active in this scope, preserve it and stop activation.
Then invoke
the `set-backlog` owner with this scope, owner and expected generation (or
confirmed absence), and report its readback. This shared operation is the only
selection mechanism; do not duplicate its validation or offer to replace an active
parent during routine triage.

Creating or admitting a Ready Backlog parent does not authorize implementation.
Execution begins through `next-issue` or `next-issue-loop` after activation
under the implementation request's authority; no extra slash command is
required.

## Report

Report the active parent or the exact selection error, Ready Backlog parents,
triaged candidates and visible blockers, duplicate decisions, and every approved
write with its readback. If approval or required context is missing, leave the
affected issue and backlog state unchanged.
