---
name: next-waypoint-loop
description: Work successive frontier tickets from this repository's saved Wayfinder map until human input or approval is needed, or no further ticket is available.
---

# Next Waypoint Loop

This is the continuous version of `next-waypoint`. Its invocation authorizes
continuing across ticket boundaries in the current conversation. It overrides
Wayfinder's one-ticket-per-session limit and normal stop after a resolved
ticket; all other Wayfinder rules, including the map's planning/execution
boundary, remain in force. It does not authorize answering human decisions or
bypassing approvals. An authorized `whats-next` handoff supplies this invocation
for the established selected map; an implementation request can likewise carry
planning continuation authority through its owner. No additional slash command
is needed.

## Load the saved map

Read [selection scope and handoff](../set-map/SELECTIONS.md) before resolving
state. Use the map selector's `show` only to establish a new explicitly authorized
binding, then retain its scope, owner, generation and issue URL. Use `check` with
that binding on continuation and before tracker mutations; transfer or selection
changes stop this run. Missing or invalid context returns to `set-map` with existing
authority; never infer a replacement scope or map.

Read the `wayfinder` skill completely and the repository's issue-tracker
instructions. Use the saved URL with **Work through the map**, with no named
ticket. If Wayfinder is unavailable, report the missing dependency.

## Continue through the frontier

1. Apply Wayfinder's **Map-entry evidence** rule before advancing, then select
   its first open, unblocked, unclaimed child in tracker
   order. Claim it before work. Do not skip a human-in-the-loop ticket to reach
   an autonomous one. Do not take a ticket claimed by another session.
2. Follow Wayfinder's workflow and the selected ticket's required skills.
   Continue independently through authorized work and routine recoverable
   failures. For prototypes, follow the `prototype` skill's inquiry rules.
   Grilling and other human-dependent tickets require the human's actual
   participation; never supply their answers yourself.
3. For a human decision, follow Wayfinder's **Human-decision completion** rule,
   invoking `grilling` for the actual dialogue. Keep the ticket claimed and unresolved
   while waiting; do not claim another ticket to bypass that dependency.
4. When the ticket is resolved, finish **all** Wayfinder bookkeeping: record the
   resolution, satisfy Wayfinder’s implementation handoff, close the ticket,
   append the map's context pointer, and create or
   update newly surfaced tickets and dependency edges. A subagent's report or
   a completed local artifact alone is not a resolved tracker ticket.
5. Refresh the map and frontier from the tracker, accounting for concurrent
   sessions. Under `whats-next`, return for reassessment at this boundary before
   the next selection, continuing here when the same map remains the chosen action.
   Otherwise immediately repeat from step 1 without asking whether to continue
   or ending the turn merely because one ticket finished.

After the human answers, resume the same claimed ticket through its required
skill, preserving supplied answers and existing approval. Complete its bookkeeping
and refresh the tracker frontier before continuing. Honor a later request to stop
or change scope.

## End conditions

Pause for required human input or approval. Otherwise continue until the map is
complete, the user stops the run, or no actionable frontier remains.

For a map with direction confirmed through Wayfinder's entry and no decision
children, complete Wayfinder's implementation
handoff and resolution directly; do not create work just to populate the
frontier. Once the map is resolved, carry an existing implementation request
through the specification, publication and backlog owners, asking only for
missing approval of the concrete draft. A planning-only request ends with its
planning outcome.

An empty frontier is not necessarily a complete map: distinguish completion
from tickets blocked or claimed elsewhere, and from remaining fog. If a precise
in-scope question can now be ticketed, follow Wayfinder's fog-graduation rules
and refresh the frontier. If progress requires a human decision, ask it. If only
external work remains, report what must change and stop; do not steal claims,
invent work, poll indefinitely, or create a scheduled automation.

If an unrecoverable tool/access failure prevents progress, report the exact
blocker and preserve unresolved work. Never mark a ticket resolved merely to
keep the loop moving.

When called by `whats-next`, return the completed outcome or specific pending
decision/blocker to it; the coordinator may continue independent authorized work
without claiming this loop's unresolved ticket or supplying a human answer.

At a pause or end, briefly name and link the tickets completed during the run
and the pending question or stopping reason. The human should not need to
reconstruct the run from progress messages.
