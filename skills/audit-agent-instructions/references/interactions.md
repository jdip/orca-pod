# Instruction interactions

Use for a corpus with multiple instruction surfaces. Trace representative paths
through the actual owners; document-level findings alone cannot establish that
the system routes work correctly.

## Discovery and loading

Check which descriptions and rules the host actually exposes, including truncation,
shadowing, scoped rules, explicit-only settings, and installed/source drift when
those surfaces are in scope. Static inventory is evidence of available files, not
proof of runtime loading. Test a trigger against its intended request and a nearby
request that should use another owner; broad synonyms can attract unrelated work.

For each instruction pointer, establish its target and the branch that needs it.
Find dead links, unreferenced required guidance, cycles, unconditional reference
loads, and competing routers. Disclose a branch only when the caller can still
reach its required constraints. Keep essential invariants visible at their point
of use; a shorter root that hides them is not an improvement.

## Authority and ownership

Resolve precedence and scope before calling two rules contradictory. Record
explicit user requirements and local exceptions; model advice does not repeal
them. Distinguish permission requirements from discovery settings, and executable
enforcement from prose. Preserve state or report the conflict when they differ.

Trace repeated meanings to their maintenance owner. Similar wording may protect
separate load boundaries; independent role instructions need not share a renderer.
Conversely, a downstream skill that copies another skill's method can drift even
when both copies currently agree. Prefer an actionable invocation pointer.

## Workflow boundaries

Trace entry, handoff, continuation, failure, and completion for the relevant paths.
Check whether the receiving skill actually runs or is merely named. Where a
workflow requires human dialogue, establish that the interaction and required
confirmation occur before its artifacts or mutations. Reuse recorded answers
on approved continuation; materially changed assumptions belong in the owning
dialogue. An artifact or closed issue alone does not establish that interaction.

Check that a handoff carries scope, source decisions, existing approval, unresolved
work, and its completion boundary. Flag loops that restart settled decisions,
invent permission from tool access, repeat unchanged checks, or stop before the
authorized outcome. Preserve required durable records, claims, dependencies and
separate promotion gates. Callers should reach their owners rather than maintain
another copy of the whole process.
