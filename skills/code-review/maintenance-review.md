# Maintenance review

Apply to the assigned diff and relevant callers. These checks extend Standards and
Spec; they do not add another reviewer or authorize a repository-wide cleanup.

## Standards: maintenance benefit

Check that a structural change reduces a concrete burden: knowledge required of
callers, repeated decisions, coordinated edits, or integration upkeep. Trace the
before/after path for a representative future change. Moving complexity into more
files or helpers is not evidence that it disappeared. File length and abstraction
counts prompt investigation, not automatic violations.

Keep responsibilities with their owner. Look for a new special case where an
existing rule could handle the behavior, duplicate helpers that diverge, or a
pass-through layer that adds no useful contract. Conversely, preserve an adapter
that isolates policy or platform behavior. Consolidation must share a real rule;
splitting must improve locality rather than create cross-file coordination.

For added or replaced dependencies, inspect the requirement, actual capabilities
used, existing overlap, and total maintenance tradeoff. When supplied evidence and
permitted source reads cannot establish the decision, report the specific gap to
the primary. The primary can use `dependency-review` scoped to the changed
packages and supply the evidence for review; a restricted reviewer stays within
its assigned capabilities. A used package may be unjustified, while a large
package may cost less than its proposed in-house replacement. Judge reductions
against replacement code and migration cost, not package count. Keep conclusions
within available evidence; missing rationale calls for investigation, not an
automatic demand to remove a dependency.

## Spec: preserved contracts

Trace behavior through the changed interface: outputs, errors, side effects and
ordering, configuration, and relevant performance or compatibility commitments.
Examine whether allegedly dead code is reachable through registration, generated
entry points, dynamic imports, CLI/configuration, or external consumers. Removed
validation and error handling need a demonstrated equivalent or an explicit
requirement change. Type checking and passing tests alone do not prove equivalence.

For migrations, account for callers and retire obsolete paths and configuration
within the approved compatibility contract. Identify leftover parallel behavior or
shims introduced only to avoid finishing the migration. Preserve public contracts
that still require compatibility; escalate a conflict between the proposed cleanup
and those contracts instead of assuming all consumers are local.

Assess verification against the changed behavior and the repository's Application
Code/Tooling classification. Application checks should preserve observable
assertions at stable interfaces; tests coupled to retired structure may need to
change. Tooling needs relevant real-use evidence under local rules. Check that a
cleanup has not weakened assertions or smuggled in a feature or bug fix.

Report evidence-backed regressions and requirement failures at the changed
locations through the existing Standards/Spec report. State tradeoffs and optional
improvements as such; do not invent a blocker merely because a different design
is possible.
