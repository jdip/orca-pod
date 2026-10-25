---
name: next-waypoint
description: Claim and work the next frontier ticket from this repository's saved Wayfinder map.
---

# Next Waypoint

Read [selection scope and handoff](../set-map/SELECTIONS.md) before resolving
state. Use the map selector's `show` only to establish a new explicitly authorized
binding, then retain its scope, owner, generation and issue URL. Use `check` with
that binding on continuation and before tracker mutations; transfer or selection
changes stop this run. Missing or invalid context returns to `set-map` with existing
authority; never infer a replacement scope or map.

For a valid selection, read the `wayfinder` skill completely and follow its
**Work through the map** workflow with the saved URL and no named ticket.
Wayfinder owns ticket selection, claiming, human interaction, completion, and
resolution recording; reaching Wayfinder's stopping condition completes this
skill.
