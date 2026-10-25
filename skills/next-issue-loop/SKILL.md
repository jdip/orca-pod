---
name: next-issue-loop
description: Work successive issues from the saved implementation backlog until completed, stopped, or genuinely blocked on human input or external work.
---

# Next Issue Loop

Read the `next-issue` skill completely and use it as the canonical execution
workflow. If it is unavailable, report the missing dependency. This invocation
authorizes continuing across issue boundaries in the current conversation; it
overrides next-issue's one-issue stopping rule. An authorized `whats-next`
handoff supplies the invocation and can select an eligible child under
next-issue's coordinator-selection rule. Its backlog scope, claims, delivery
requirements, Design gate, and approval boundaries remain in force. Missing
map/spec coverage returns to the planning owner under the global rule; loop
continuation and task size do not waive planning. Bind the run to the initially
selected parent URL and explicit scope/owner/generation binding from
[selection scope and handoff](../set-map/SELECTIONS.md). A changed selection or
transferred ownership stops this run; never reload a newer generation to defeat
the stop. Resume only through the authorized selection or handoff owner.

After resolving an issue, finish all tracker bookkeeping, refresh the bound
parent's children/dependencies/claims, and recheck next-issue’s Design gate
before selecting the next eligible issue. Under `whats-next`, return at this
verified child-completion boundary (rollup integration or direct test delivery)
for reassessment; continue this bound run when that
parent remains the selected action. A different effort needs its own established
selection and execution authority. An open or reopened associated map
pauses the whole backlog, even if another child has no blockers. Do not ask
whether to continue, stop merely because an issue finished, or
require main promotion before progressing from the approved child-completion boundary.

Before pausing on the current issue, survey its whole remaining decision set.
Complete independent work and batch every ready human decision with concrete
recommendations in ordinary text, and wait for answers without timed question
widgets. Wait only on genuine prerequisites; do not assume answers to
inflate a batch or reduce a round to one question by habit. Apply all supplied
answers and continue; unresolved answers remain pending. Do not claim another
issue while this one is waiting for the human.

Continue until the backlog outcome is complete, the user stops or changes scope,
or no authorized progress remains. For blocked/claimed work, name the dependency
or ownership condition that must change. For a tool/access failure, report the
exact blocker and preserve unresolved work. Do not poll indefinitely or create
an automation to keep the loop alive.

When called by `whats-next`, return the outcome or specific pending decision or
blocker at a pause or completion. The coordinator can progress unrelated authorized
work while preserving this issue's claim and unresolved decisions.

When all children are complete, recheck the full outcome and Design gate. For a
rollup, use [rollup completion](../pr-to-test/ROLLUP.md) to deliver and verify the
combined change through one canonical PR-to-test cycle before closing the parent.
An all-closed child list does not establish test delivery. Resume a parent awaiting
that delivery without inventing or claiming another child. Retain this scope's binding as the completed selection; do
not activate, claim, or start a Ready Backlog parent. Another effort requires a
new explicit selection and execution authorization. At a pause, keep unfinished child work claimed and open; after
child integration, keep pending aggregate delivery on the open parent. Give a concise linked account of issues delivered
and the pending decision or stopping reason. Never mark partial work complete
because the turn is ending.
