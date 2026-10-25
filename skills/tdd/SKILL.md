---
name: tdd
description: Use when fixing application bugs, adding or changing application behavior, or explicitly requesting test-first work or red-green-refactor.
---

# Test-Driven Development

Use **red → green → refactor** for application bug fixes and new or changed
behavior. For a bug, diagnose uncertain causes first, then normally reproduce the
failure in a behavioral regression test before changing the implementation. Use
`diagnosing-bugs` when difficult diagnosis needs its loop. Explicit user constraints
and the repository's Application Code/Tooling classification govern execution;
record a concrete limitation when a meaningful automated regression cannot be
established, and verify through the strongest available behavioral evidence.

A request for integration tests alone specifies a test type, not an implementation
method. Use this loop when those tests cover a bug fix or new/changed behavior,
or when the user requests test-first work.

When exploring the codebase, read `CONTEXT.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

## Independent bug proof

Choose separate proof and fix owners for consequential permission, data-integrity
or security failures, subtle regressions or failed prior fixes when the expected
benefit justifies coordination. Straightforward low-impact changes keep the normal
loop. Choosing separate owners is selective; once chosen, they run on opposite
providers.

Dispatch both owners per the `roster` skill (skills/roster/SKILL.md) as separate
workers:

- **Proof owner:** TST-proof, on the other provider from the fix owner. When WRK
  runs on Codex, use TST-proof's Claude alternate.
- **Fix owner:** WRK.
- **Security fix:** SEC-PROOF owns the proof, launched through the roster's SEC
  launch, and WRK on Claude writes the fix against it.

Verify each owner's model from its receipt and provider records as the roster
requires. A launch failure is reported, never rerouted.

Before a proposed patch steers reproduction, the primary gives the proof owner
the reported symptom, expected contract and authorized environment.
That proof owner establishes the behavioral failure at a public seam and records
the unfixed revision, exact command/assertions, result and limits. An unavailable
meaningful reproduction remains an explicit proof gap.

Give the fix owner the established contract and proof to fix it.
The proof owner reruns the same assertions and relevant native regressions at the
fixed revision. Necessary assertion changes return to that owner, who first checks
that they still expose the original symptom on the unfixed revision, then rechecks
the fix. Retain attributable fail-before/pass-after evidence and any missed symptom,
rework or intervention in the existing task. Independent `code-review` still applies,
with SEC-REV for a security fix.

## What a good test is

Tests verify observable behavior through the subject's public contract and survive
changes to its internal implementation. A good test reads like a specification:
"user can checkout with valid cart" describes the capability being proved.

Read [tests.md](tests.md) when examples would help choose a behavioral test shape.
When substituting an external system boundary, read [mocking.md](mocking.md).

## Seams: where tests go

Apply the global Planning before implementation rule before tests or code
intended to ship. Reuse the implementing workflow's covering map/spec; a direct
test-first request enters planning when coverage is missing.

A **seam** is a component's stable caller-facing interface: an in-process function,
module API, handler or network protocol. Choose the smallest seam that proves the
required behavior. A public contract does not require deployed ingress; exercise
the real transport or service when its semantics are part of the assertion.

Select seams from the approved behavior, supplied acceptance criteria, and established public interfaces. State the boundary under test and proceed within that scope; prior approval does not need a second seam-confirmation round. Ask only when choosing a boundary would settle an unresolved interface or scope decision. Complete independent inspection before presenting that decision.

For tests needing real services, separate service lifetime from test-state
isolation. Let the suite or worker reuse service processes while each case gets
isolated records, identities and fresh consumable credentials. Use fresh instances
for lifecycle assertions or global state that cannot be reliably isolated. Trace
inherited fixtures and helpers before reuse: requesting test data should not also
bootstrap a stack unless the case needs that lifecycle. Inspect destructive callers
and credential consumption before broadening fixture scope; a scope change alone
does not establish isolation.

When the interface itself is in question, read the available `codebase-design` skill for the module, interface, depth, seam, adapter, leverage and locality vocabulary. Use it as a reference, not a new planning session.

Apply the repository's classification before adding tests. For Application Code, use meaningful behavioral tests and actual local gates. For Tooling maintained through real-use verification, exercise the actual operation and source checks; this skill does not require a new coverage suite or simulated infrastructure.

## Anti-patterns

- **Implementation-coupled**: mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological**: the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth: a known-good literal, a worked example, the spec.
- **Horizontal slicing**: writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead: one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactor after green.** The implementation agent may simplify within the approved scope while preserving passing behavior, then rerun affected checks. Substantial redesign returns to the planning owner. Use `code-review` for the subsequent read-only review; its findings return to the implementation agent for fixes.

## Attribution

Adapted by Agent Team from [Matt Pocock’s tdd](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/tdd), revision `3cca18b368ae95cdbdebbff572ccafa662551015`. The [MIT notice](LICENSE) covers reused upstream material. Agent Team owns this adaptation.
