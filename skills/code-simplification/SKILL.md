---
name: code-simplification
description: Simplify a selected code area while preserving its behavior, compatibility contract, and useful maintenance boundaries. Use for focused refactors or cleanup candidates, not dependency selection or substantial redesign.
---

# Code Simplification

Simplify an authorized area when doing so makes future work more local, removes a
concept, or clarifies the owning implementation. Keep the area as-is when the
concrete maintenance benefit does not justify a change.

## Establish the behavior

Before implementation, including characterization tests intended to ship, apply
the global Planning before implementation rule. Reuse the invoking workflow's
covering map/spec; direct invocation carries planning authority without waiving
it.

Read applicable repository guidance, domain documentation, and design decisions.
Inspect dirty state, the selected implementation, its callers, its requirements,
and relevant history. Establish the current compatibility contract from actual
inputs, outputs, errors, ordering, and side effects; do not infer it from names
or tests alone. Include performance and platform guarantees where callers depend
on them. Run the relevant baseline before editing and distinguish existing
failures from regressions. For Application Code with an uncovered affected
contract, add meaningful characterization or equivalence checks at the existing
interface before moving structure; use available `tdd` guidance as needed.

Choose a small cohesive slice with a stated benefit. Work within existing
authorization without a per-edit approval round. A dependency decision belongs to
`dependency-review`, including whether a used dependency is still justified.
Reuse a supplied assessment when its evidence still covers the change.

## Simplify the owning path

Use the mechanism that owns the behavior. Keep required security, validation, and
error handling unless the authorized contract changes. Move or combine code only
when the new locality makes the behavior easier to understand or change.

Migrate affected callers and remove the replaced implementation and configuration
cleanly within the compatibility contract. Tests may follow the new structure, but
preserve externally observable assertions. Do not hide a separately discovered
behavioral bug in a simplification; follow repository remediation guidance for it.
Keep each slice verifiable before proceeding to another. Investigate a failed
check at its cause; revise or revert the attempted simplification rather than
weakening the contract to make it pass.

For a substantial interface decision, use the available `codebase-design` skill.
Substantial redesign needs approved scope or a design handoff before implementation.

## Verify and deliver

Verify at existing interfaces and run the repository's applicable gates.
Application Code needs meaningful behavioral validation and its established lint,
type, and test checks. Tooling uses proportionate source checks and available
authorized behavioral checks under the repository's closure policy. Report
unexercised scenarios as limits; do not create a characterization suite merely
for this refactor.

Use `code-review` for review. When delivery is authorized, follow `pr-to-test` and
the repository's local delivery rules. Report the behavior preserved, maintenance
benefit, verification evidence, and any unresolved design decision.
