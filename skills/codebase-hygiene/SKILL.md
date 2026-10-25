---
name: codebase-hygiene
description: Survey codebase maintenance opportunities and carry out authorized cleanup batches. Use for repository hygiene, periodic maintenance assessments, or broad cleanup across dependencies and module structure.
---

# Codebase Hygiene

Find changes that make future work easier, then carry the authorized scope through
verification and delivery. A healthy area and a justified dependency are successful
outcomes. Optimize for fewer concepts, coordinated edits, and maintenance burdens;
file size, line count, and dependency count are investigation signals, not quotas.

## Establish the assignment

Resolve the repository, revision, requested areas, local instructions, domain docs,
and existing work. Read relevant decisions and prior findings before proposing the
same change again; reopen a rejected recommendation only with material new evidence.

An assessment or bare invocation surveys and recommends. A request to clean up
authorizes carrying cohesive behavior-preserving improvements through the global
Planning before implementation rule and routine verification. Use `pr-to-test`
for delivery when the request or local workflow authorizes it. Carry forward any
approved batch and constraints without asking again for each edit. Substantial
architectural refactoring needs explicit scope approval; prepare its concrete
design decision while completing independent authorized work. Scheduling and
host installation (`machine/install.py --apply`, see `docs/install.md`) remain
separate requests.

## Survey and investigate

Establish current verification results for the affected areas before changing code.
Distinguish existing failures from regressions and investigate failures according to
the repository's development guidance. Use existing tools and the approved runtime;
a hygiene request does not authorize a new language, runtime, or toolchain.

Start with actual maintenance evidence: repeated edits across callers, recurring
defects, duplicate decisions, abandoned migration paths, or expensive integration.
Use recent Git hotspots to prioritize exploration without excluding stable code
from a requested repository-wide assessment. Exclude generated/vendor content from
authored-code cleanup while inspecting its integration when relevant.

- **Dependencies:** use `dependency-review` for the scoped inventory, including
  packages actively used by the code. Establish whether their capabilities justify
  their ongoing cost; an unused-dependency report alone cannot answer this.
  For requested version currency, current dependency alerts or protection settings,
  hand the concrete candidate to `dependabot-upkeep` under the existing
  assessment/edit authority.
- **Module structure:** use available `codebase-design` guidance for depth and
  locality. Trace callers and responsibilities. Look for changes that consolidate
  one business rule, remove an unnecessary layer, or separate unrelated reasons to
  change. Respect existing architecture decisions. Preserve manual-only upstream
  skill invocation settings; this survey does not automatically invoke
  `improve-codebase-architecture`.
- **Simplification:** inspect redundant branches, overlapping implementations,
  indirection, obsolete configuration, and partially retired paths. Verify why each
  exists before calling it waste. Similar-looking code may represent different rules.

Use configured static analysis to locate candidates and inspect its entry points,
generated inputs, dynamic use, and exclusions before trusting an absence report.
Report unavailable checks and unexamined areas instead of claiming full coverage.
Bound independent delegated surveys by paths or concerns; retain one implementation
owner for overlapping changes and the existing reviewer routing.

## Select actionable work

For each supported candidate, give the location and evidence, present maintenance
cost, proposed end state, expected benefit, confidence, affected contracts, and
verification approach. Rank by benefit and confidence against migration risk and
effort. Explain why a recommendation earns its place; skip aesthetic churn and
speculative abstractions. Record important keep/defer decisions with their rationale
in the existing task or decision location, without creating a separate ledger.

Use the repository's tracker guidance for deduplication and actionable
remediation findings. Recommendations and issue filing do not change the Active
Backlog or authorize implementation. Before cleanup edits, reuse covering
resolved map/spec work or use Wayfinder, `to-spec` and `to-tickets` under the
global planning rule. Keep small plans brief; batch only unresolved decisions
with concrete recommendations.

## Execute and finish

Use `code-simplification` for each authorized cohesive change, supplying the
candidate evidence, intended end state, behavior to preserve, and scope. It owns
implementation, verification, and the handoff to `code-review` and local delivery.
For approved dependency changes, include `dependency-review`'s comparison and
required compatibility checks. Recheck remaining candidates after each slice;
earlier changes may remove their rationale.

Continue until the authorized batch is complete, no remaining candidate has a
supported benefit, or a real blocker prevents progress. Finish independent work
before reporting a blocker. For recurring maintenance, use existing findings and
current evidence to avoid repeating unchanged recommendations; recurring execution
requires separately established scheduling and scope.

Report assessed scope and gaps, delivered changes and their maintenance benefit,
actual verification, retained dependencies with material rationale, and unresolved
findings or decisions. When useful and authorized, enforce an agreed architectural
rule with an existing native check to prevent recurrence; do not add a general
hygiene scoring system.
