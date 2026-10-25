# Evidence and repository comparison

Keep four independent fields: **source tier** is discovery priority; **claim
type** describes what is asserted; **evidence grade** describes support; **impact**
describes the potential effect on Orca Pod. A watched engineer can make an
unsupported claim. Many outlets repeating one source do not corroborate it.

## Classify each substantive claim

| Claim type | Meaning |
| --- | --- |
| Built/measured | Code, implementation, experiment, measurement, or documented result |
| Observed firsthand | Direct operational experience, possibly without a reproducible record |
| Reasoned argument | An explicit technical argument rather than an observed result |
| Prediction/opinion | A forecast, preference, or interpretation without sufficient verification |
| Hype/repetition | Promotional assertion or repeated claim with no additional evidence |

| Evidence | Required support |
| --- | --- |
| A | Primary code/release/experiment; a benchmark with methodology; or a firsthand engineering write-up with concrete implementation/results |
| B | Credible firsthand observation or technically strong discussion with incomplete empirical support |
| C | Anecdotal, weakly verified, speculative, or primarily commentary |

Grade the precise claim. Release notes can establish that a feature exists,
without establishing that it improves productivity. Cite the direct source and
mark unknowns; do not let the feature's Evidence A spill into an untested benefit.
A grade measures support, not newsworthiness. Select stories using the editorial
criteria in [brief format](brief.md); rigorous grading also permits discussing a
valuable argument as an argument rather than pretending it is measured.

| Impact | Meaning for this repository |
| --- | --- |
| HIGH | Could materially alter agent architecture or engineering workflow |
| MEDIUM | Useful improvement or meaningful engineering trend |
| LOW | Limited current practical significance |

A HIGH-impact hypothesis may have Evidence C. Explain both independently.

## Establish repository relevance

Read relevant source rather than inferring behavior from a skill name or role
description. Trace callers and workflow ownership when the comparison depends on
them. Consult root/local instructions, agent definitions, skills, orchestration,
prompts, routing, context/memory, planning, review, tests/runtime validation,
worktrees/branches, remote execution, and architecture notes as relevant.

Cite repository-relative paths and the inspected revision in saved reports. Render
those paths as code text or use a verified permalink; archive-relative Markdown
links do not point back into the checkout. Conversation links can resolve actual
local paths. Locate each rule in its owning file: session-injected instructions
are not necessarily the contents of root `AGENTS.md`. A baseline documents observed
capability at that revision; absence of an eval is not proof of poor performance.

Classify each comparison, explaining why:

- **We already do this** — the same practice is implemented.
- **We do something equivalent** — a different mechanism serves the same purpose.
- **Worth borrowing** — concrete fit and benefit justify a proposal for adoption.
- **Worth testing** — a bounded experiment can resolve a real uncertainty.
- **Interesting but incompatible** — explain the actual architectural constraint.
- **Probably unnecessary** — insufficient benefit for this system.
- **Actively worse than our current approach** — identify evidence of regression.

Report **unknown** when inspection or measurement cannot support a comparison;
do not disguise unknown capability as a proven gap. External novelty creates no
presumption of adoption. Skills, plugins, and MCP servers are software supply-chain
inputs: examine provenance, permissions, data access, dependencies, isolation, and
what installation/execution would permit before proposing a test.

## Prefer engineering signal

Favor code, firsthand implementation details, measured results, postmortems,
explicit failures, reproducible workflows, and practitioners changing their minds
after experiments. Seek contrary evidence. Preserve credible disagreement and
describe an experiment that could distinguish the competing explanations.

Exclude funding/celebrity news, generic job-displacement discourse, unsupported
launch reactions, follower authority, methodology-free benchmark screenshots,
model fandom, viral prompts, and unsupported productivity multipliers unless a
concrete engineering claim and useful evidence make them relevant.

For evals inspect methodology, model plus harness, available context, tool access,
attempt count, human intervention, cost, task realism, and failure modes. Label
unreported fields. Avoid generalizing a benchmark beyond the conditions measured.
