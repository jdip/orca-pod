---
name: dependency-review
description: Review whether a used or proposed dependency still earns its place. Use to assess one dependency or a scoped dependency inventory before retaining, adding, replacing, consolidating, or removing packages.
---

# Dependency Review

Review the dependency against the repository's current requirements. A dependency
that is used may still be unnecessary; a dependency with little visible use may
protect important behavior. `Keep` is a decisive and useful outcome.

This skill is read-only. It establishes an evidence-backed decision for the owning
workflow. It does not edit manifests, lockfiles, or callers, and it does not create
or update tracker items.

For requested version currency, dependency alerts or protection configuration,
return the assessment to [dependabot-upkeep](../dependabot-upkeep/SKILL.md). This
read-only assessment does not itself authorize those changes.

## Establish the dependency's job

For each dependency, trace the current requirement to actual callers and every
relevant integration surface: runtime and build code, configuration, command-line
entry points, plugins, generated outputs, and dynamic loading. Record the concrete
capabilities in use, rather than treating an import or a package-manager listing
as a justification.

Recover historical rationale when it can clarify a present tradeoff: commit and
issue context, prior incidents, or compatibility constraints. History explains a
choice; it does not establish that the choice remains required.

Scanner output, including optional tools such as deptry or Knip, is a lead for
inspection. Use an already available tool if it fits the repository; do not install
one or introduce a runtime to perform the review. Dynamic or generated usage can
be invisible to scanners. When external consumers or a plugin contract cannot be
established, report that uncertainty and make no deletion claim.

## Test the current choice

Compare the dependency's needed capabilities with:

- native runtime or framework facilities available in the deployed versions;
- repository-owned code or another existing dependency that already provides the
  capability; and
- a narrower use of the same dependency when only part of it is justified.

When proposing a native or framework alternative, verify the version-specific
behavior in primary documentation or the deployed source. Verify current API,
pricing, or security claims when they materially support the decision; this review
is not a blanket security audit.

Assess both sides of the decision. Keeping a dependency includes its direct and
transitive footprint, upgrade burden, integration complexity, and operational
cost. Replacing it includes migration work, compatibility and edge cases,
verification, and the ongoing ownership of code moved in-house. Prefer a proven
dependency when reimplementation would create a library the repository must now
maintain without a material benefit.

## Decide and hand off

Choose the outcome supported by the evidence: **keep**, **narrow**,
**consolidate**, **replace with a native capability**, **remove**, or
**investigate further**. State the condition that would change the decision when
evidence is incomplete.

Return the assessment to the caller, including affected callers and configuration,
compatibility risks, and the behavior that must be verified. An implementation
owner can use [code-simplification](../code-simplification/SKILL.md) for an
authorized behavior-preserving replacement or removal. Additions that implement
new behavior belong to the feature's implementation workflow. An assessment
requested by a reviewer remains read-only; leave edits and unrelated candidates
to their owning workflow.

## Report

Produce a concise dependency decision or inventory with:

- the dependency and review scope;
- required behavior and evidence of its actual use or non-use;
- historical context and unresolved consumers, when relevant;
- alternatives considered and the deployed-version evidence for each viable one;
- the keep-versus-migration cost, material risk, and decision; and
- the verification needed before an authorized implementation is complete.
