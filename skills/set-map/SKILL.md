---
name: set-map
description: Select a Wayfinder map in an explicit effort scope, or carry out an approved map handoff or legacy import.
---

# Set Map

Read [selection scope and handoff](SELECTIONS.md) before selecting, reading,
resuming, importing, refreshing or transferring a map. Establish the explicit
scope and task-owner binding from the current task, preserving other efforts.

Use the map URL supplied by the user or established by an authorized workflow.
The human need not repeat the URL or invoke another command. Preserve competing
selections unless existing authority covers switching. Resolve scripts relative
to this skill directory; `scripts/set-map.sh --help` owns the exact interface.

For a new selection run `scripts/set-map.sh select --scope <scope> --owner <task>
--expect-absent <map-url>`. For an authorized change use the retained
`--generation <generation>` instead of `--expect-absent`. The helper validates an
open `wayfinder:map` issue in the current repository, atomically updates only that
scope's map entry and preserves existing state on failure.

Establish an initial binding through `show`; continue with `check` against the
retained generation. Report scope, owner, generation, issue name and URL from the
result. Completion requires successful readback, not just a launched script.

For human-approved handoff/takeover, explicit legacy migration or repository
rename, follow the corresponding branch in the shared contract and use
`transfer`, `import-legacy` or `refresh`. Selection and ownership transfer never
substitute for planning, execution or tracker claim authority.
