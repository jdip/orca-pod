---
name: whats-next
description: Choose and advance repository work when the operator asks what to do next or to keep progress moving.
---

# What's Next

Choose the next useful action in this repository and carry it through its existing
workflow. A request to choose and advance work authorizes continuing an already
approved Active Backlog and selected Wayfinder map after their gates are checked.
Keep a conversational loop: take an obvious authorized step, offer meaningful
choices, and resume after the human answers.

## Discover and choose

Start with a lightweight overview: root README purpose, Git/worktree and dirty
state, saved map/backlog selections, issue/PR status and labels, native dependencies,
Orca ownership evidence, current dependency alerts and existing
remediation, and recent hygiene, adopted-verification and alignment assessment
evidence.
For ownership, read `orca worktree ps --json` (worktrees, their agents and live
terminals) and, for a promising issue or PR, `orca reference find <url> --json`
(workspaces and agents linked to it). Inspect detailed requirements,
checks, reviews, and code only for promising candidates and their necessary
eligibility checks.

On each ordinary discovery pass, read current open Dependabot alerts with
pagination through [dependency upkeep](maintenance.md#dependency-upkeep), even
while code work is active. Reuse a successful read within that pass; refresh at the
next pass and after relevant remediation. Report disabled or inaccessible alert
coverage separately from zero alerts. This read does not start maintenance edits.

Read [selection scope and handoff](../set-map/SELECTIONS.md) whenever reading,
selecting, resuming, forking, moving or handing off a map/backlog. Use the existing
selector owners with the explicit scope/task binding; preserve each effort. A closed
historical selection permits discovering alternatives without replacing this scoped selection.
Investigate invalid, conflicting, or unreadable state; a failed read is not an empty
queue. Preserve partial work and pause only actions depending on unresolved evidence.

Dependencies precede the work they unblock; otherwise favor work closest to
completion. Use status/labels and loose estimates of effort remaining. For ties or
meaningful competing paths, present a short list with rough effort and a
recommendation, then let the human choose. A prerequisite for blocked work need
not outrank an unrelated almost-delivered PR. Respect explicit user order,
dependencies, claims, design gates, and scope even when selecting a later eligible
backlog child. Do not do a sizing investigation just to rank work.

Work owned by another Orca worktree or agent is excluded from our candidates: an
issue or PR linked to another workspace through `orca reference find`, a branch
checked out in another worktree, or a selection owned by another worktree or
dispatch. Recorded links and live agents establish ownership; workspace
membership alone, or an archived workspace, does not. Account for its expected
outcome and its effect on dependencies and code stability.
When its turn finishes with work remaining, offer a concrete human-approved
takeover through the selection handoff owner; verify source quiescence, included
claims and recipient binding before assuming ownership. An assignee, inactivity, or a finished turn
alone is not permission. If Orca inventory is unavailable or `orca worktree ps`
reports a host as not covered, preserve uncertain claims and continue work whose
ownership is established. A worktree listed by `git worktree list` but absent from
`orca worktree ps`, such as one created by an agent outside Orca, is an uncertain
claim; record its branch, any open PR for that branch and its dirty state as evidence.

When starting selected work in a new Orca worktree, attach its issue at creation
with `orca worktree create --reference <issue-url>`, or afterwards with
`orca reference add <issue-url> --worktree <selector>`, so other sessions see the
ownership.

## Plan the selected change

Apply the global Planning before implementation rule to every implementation
candidate, including an existing PR and direct maintenance or alignment work.
Before reusing any map or approved spec, apply Wayfinder's **Map-entry evidence**
rule. Reuse a resolved map and approved spec covering the actual change. If coverage
is missing, begin or resume Wayfinder from the inspected target and desired
outcome. Hand control to Wayfinder's **Chart the map** entry and stay in its
grilling dialogue until its completion gate is satisfied. A concrete destination
is the result of that dialogue, not an alternative gate. Smallness or a delivery
request does not supply a planning waiver.
Read-only assessment may continue while planning remains open.

After Wayfinder's entry dialogue and user confirmation, carry the request's
planning authority through
`wayfinder`, `set-map` and `next-waypoint` continue mode; resolve their repository
context against the target. A compact settled map may have no decision children.
Select a new map while it is open, before resolution/closure; reusing resolved
coverage needs no new map selection. Then use `to-spec` and `to-tickets` for the
specification parent and executable children: `to-spec`'s independent review
against the map stands in for a spec approval prompt, and the spec-link report
needs no reply. Continue through the existing selection/execution owners under
the confirmation. Preserve another effort's selection and ownership. Ask about a
competing selection only when existing authority does not settle it. Missing capabilities leave a
concrete planning blocker; continue independent discovery without silently
implementing.

## Carry authority through the owner

Read the skill that owns the selected operation and supply the concrete repository,
target, scope, prior approval, and relevant evidence. Approved contextual handoffs
are sufficient; the human need not repeat a URL or slash command. Preserve deliberate
manual-only upstream packages. Missing skill/tool capability leaves the affected
step unresolved, with a concrete limitation reported to the human.

Reuse explicit consent only when it covers the same repository, target, scope, and
action and has not been superseded. Labels, assignment, publication, or an open PR
alone do not establish permission. Before asking, finish independent investigation
and present the actual missing decision or approval with a recommendation. Batch
ready questions; the human supplies the answers. Execute only the approved portion
of a combined proposal and carry it forward across ordinary skill boundaries.

| Selected work | Owning handoff |
| --- | --- |
| Almost-delivered code/PR | Establish map/spec coverage, requirements, ownership, and delivery authority; use `code-review` when needed and `next-issue` for a rollup child under its parent's integration boundary; use `pr-to-test` for a completed rollup or direct test delivery. Ask about finishing that specific PR if delivery consent is missing. |
| Approved Active Backlog | Use `next-issue-loop`, supplying the eligible selection when completion-first ranking changes ordinary order. Preserve the associated map's Design gate and existing claim/delivery rules. |
| Prepared inactive backlog | Use `triage` for necessary intake/admission and `set-backlog` for approved selection. Present only missing admission, activation, and execution approvals together, then start `next-issue-loop` to the extent approved. |
| Selected Wayfinder map | Use `next-waypoint` continue mode; research facts and present human decisions. A different map needs an approved select-and-start proposal through `set-map`. |
| New planning destination | Hand off to Wayfinder's **Chart the map** dialogue and completion gate before map creation; then use `set-map` and `next-waypoint` continue mode under existing authority. Preserve its required human questions and confirmation. |
| Entire map resolved | Use `to-spec` to draft the parent and complete ticket breakdown automatically and run its review against the map. Once the parent is an approved specification under `to-spec`, normally through a pass, use `to-tickets`, send the spec-link report and continue through admission, activation and execution under `to-spec`'s handoff. Reuse the effort's implementation follow-up. |
| Alert-protection gaps, actionable dependency alerts or existing remediation | Follow [dependency upkeep](maintenance.md#dependency-upkeep), then hand the selected repository-owned remediation or protection scope and existing approval to `dependabot-upkeep`. Return after the coherent step. |
| Hygiene, adopted repository verification or Orca Pod alignment | Follow [maintenance and alignment](maintenance.md) once the relevant baseline is stable. |
| Missing or unclear project purpose | Use `define-project-goal` with the human operator when direction is needed; reuse an existing clear root README purpose. Agree missing invocation authority with a concrete offer, then carry approved wording through its owning documentation workflow. |

## Refresh and continue

Finish the coherent step and its verification/bookkeeping, then reassess after a
verified child integration/direct delivery, completed rollup delivery, resolved planning ticket, completed assessment, or human
answer. Nested loops return here at those boundaries before their next selection;
this does not require a new invocation from the human. Do not reprioritize between
ordinary tool calls. New direction, a blocker, or changed ownership can interrupt
a step when necessary.

Refresh selections, ownership, actual partial effects, and the associated design
before resuming. A changed selection binding does not redirect a bound implementation loop:
follow established explicit direction or ask whether to continue the old effort or
select the new one. Preserve unresolved work and avoid replaying completed mutations.
A reopened associated map pauses its entire implementation backlog; bring its
required decision to the human while advancing unrelated authorized work if possible.

When tracked work is completed or no longer actionable, follow
[maintenance and alignment](maintenance.md) before concluding that no useful work
remains. Establish whether relevant assessment evidence exists and still applies;
missing history makes a bounded assessment a candidate even with no open issues.
Present the useful candidate and rough effort, or explain the evidence for deferral
or no further assessment. Reuse unchanged assessment and operator decisions.

Then compare observed repository capabilities and expected active-work outcomes
with the documented purpose using the bounded
[outcome assessment](maintenance.md#outcome-assessment). A clear README purpose can be reused without a prior
`define-project-goal` invocation; its presence establishes direction, not fulfillment.
If the operator questions that direction or its agreement, offer the purpose workflow
instead of treating the wording as settled. Support any fulfillment conclusion with
observed outcomes and state what remains unassessed. An empty queue establishes only
that tracked work is complete.

For an evidenced gap within the requested scope, begin Wayfinder dialogue and
reuse covering maps; propose a changed destination when it would expand that
scope. When maintenance has been considered and no useful candidate is
established, ask which desired outcome should guide the next session; there is
no need to claim the purpose is fully served. Preserve the agreed purpose rather
than inventing a deficiency or rewriting it to justify more work.

Continue until the human stops, a real decision is pending, or external work or
missing capability leaves no authorized progress. State delivered outcomes and the
specific remaining decision or blocker, retaining the context to resume after an
answer. Use existing conversation, Git, and tracker evidence rather than a new
workflow ledger. Repeated unchanged assessment, indefinite polling, main promotion,
host installation (`machine/install.py --apply`, see `docs/install.md`), and
background scheduling are not implied by this loop.
