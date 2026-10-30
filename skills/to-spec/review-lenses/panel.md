> Adapted from [`skills/egm-review-loop/SKILL.md`](https://github.com/google/elephant-goldfish-model/blob/05f8984cb6e0077b072ba034f66d95ffdde200ee/skills/egm-review-loop/SKILL.md), [`skills/egm-resolve/SKILL.md`](https://github.com/google/elephant-goldfish-model/blob/05f8984cb6e0077b072ba034f66d95ffdde200ee/skills/egm-resolve/SKILL.md) and [`agents/synthesizer.md`](https://github.com/google/elephant-goldfish-model/blob/05f8984cb6e0077b072ba034f66d95ffdde200ee/agents/synthesizer.md) in `google/elephant-goldfish-model` at `05f8984cb6e0077b072ba034f66d95ffdde200ee`, licensed under the
> Apache License 2.0 ([LICENSE](LICENSE)).
> Modified by Orca Pod: upstream YAML frontmatter, harness setup and interactive intake removed; the three sources merged into one rule set for Orca Pod's map panel and spec panel; role names (Goldfish to a fresh cross-provider REV per persona, Elephant to coordinator ORC); the nested synthesizer, report files and per-round human gates replaced by direct ORC synthesis and one tracker comment per round; the target file and line range mapped to a frozen subject; dispositions extended with a decision impact, settlement by a recorded decision and return to the map; A/B sampling limited to an explicit high-risk designation.

# Review panel rules

A **panel** reviews one frozen draft through isolated personas: one fresh REV
session per persona, in parallel, each applying only its persona file, mode and
`Lens:` line. The **map panel** runs four lenses in `MAP PASS` mode on a drafted
map. The **spec panel** runs five personas in `SPEC REVIEW` mode on a
specification parent and its child breakdown. The owning skill decides when a
panel runs and what its result unlocks; `roster`'s **Review panel** section owns
dispatch. These rules govern every round of both panels.

## Reviewer contract

You are one persona on the panel. Your brief names your persona file, mode,
`Lens:` line, the frozen subject and the governing map decisions.

1. Read this file, your persona file, its standard where it names one, the frozen
   subject and the governing decisions. Inspect repository evidence as your lens
   requires.
2. Open your report with the required reads you made. A required read you could
   not make makes your review incomplete; report it rather than reviewing around
   it.
3. Comprehension then gives its paraphrase. Every persona reports each finding
   with its lens severity (Blocker, Major or Nit), the affected scope, exact
   evidence and a recommended correction or question, or states that it has no
   findings.

Your brief deliberately carries the draft alone: the dialogue, the drafter's
reasoning, other reviewers' output and earlier findings stay with the
coordinator. Judge the draft as written.

## Rounds

Every round runs the full fresh panel against a frozen subject:

- **Map panel:** the repository SHA plus the inline draft text.
- **Spec panel:** the parent issue body with its GraphQL `lastEditedAt`, or its
  `createdAt` when never edited, and the full child breakdown.

Each reviewer gets the frozen subject, the governing map decisions, and its
persona file and standard. It is withheld the dialogue, the drafter's reasoning,
other reviewers' output and earlier findings. Before recording a round, re-read
the subject's identity; an edit made while the round ran invalidates it, so run
the round again on the new text.

## Completeness

A persona is **not run** when its report is missing, its required reads are
incomplete, or its receipt-verified model or effort differs from the assignment.
Never count it as a reviewer with zero findings. A not-run persona gets one
retry on the same assignment, launched only after the earlier attempt is settled
or stopped. A persona still not run after its retry stays not run for the round.

**A/B sampling** runs only on the operator's explicit high-risk designation: two
fresh sessions of a persona, and the persona completes only when both do.

## Findings

Give each finding a stable ID, `<persona>-<round>-<n>`. The coordinator keeps the
**settled list** across rounds and loops of one subject:

- A finding is **settled** when it is contested, declined or settled by an exact
  recorded decision. If a later reviewer raises it again (same scope, same
  issue), it stays settled.
- A **fixed** finding is not settled. If a later reviewer raises the same issue
  at the same scope, the fix failed or a later edit reintroduced it: reopen it.

## Classification

Each finding carries two fields:

- **Severity:** the lens severity as reported: Blocker, Major or Nit. Change it
  only by contesting it with its reason.
- **Decision impact:** `map` or `in-scope`, assigned by the coordinator. A
  finding that exposes a missing or changed map decision is `map`, whatever its
  severity: a scope expansion or reduction, a contradicted decision, a new
  decision the map does not record, or a substantive design choice left open for
  the implementer. Every other finding is `in-scope`. A disagreement over
  impact, from the reviewer's evidence, another persona or the drafter, makes it
  `map`.

A `map` finding returns to the map and the human. Accepted risk never settles a
scope change, so a `map` finding is never settled to reach convergence.

## Dispositions

The coordinator gives each finding exactly one disposition:

- **fixed:** the critique is valid; apply a precise correction.
- **contested:** cite evidence the reviewer could read: a file and symbol, or a
  decision recorded in the subject or the governing decisions. "This was
  intentional" is not evidence.
- **escalated:** the refutation is real but lies outside every source the
  reviewer could read, such as an unrecorded convention. Leave the text, and
  give the finding to the human.
- **declined:** a Nit not worth fixing, recorded with its rationale.
- **settled:** an exact earlier decision already answers it; cite that decision.
- **returned to map:** its impact is `map`.

Add context when a human reader of the record needs it. When only a zero-context
reviewer needs it, escalate. A comprehension gap is fixed, never contested: if a
fresh reader could not follow the draft, the draft is missing context. You or
your drafter wrote the draft; a wish to contest is not evidence that the reviewer
is wrong.

**Post-fix bloat check.** Before applying a fix, check that it adds no
machinery, condition or step the map decisions don't require; take the smallest
correction. In rounds 2 and later, zoom-out's lens includes post-fix complexity:
its brief states the round number and carries no earlier findings.

## Convergence

Fresh reviewers sample differently each round, so a round with zero findings is
rare even when the draft improves:

- **Clean round:** every persona ran, and no Blocker or Major finding is
  unsettled. Nits do not block. Decide this from the round's results, before
  applying its fixes.
- **Converged:** two consecutive clean rounds. One clean round is not enough,
  because the next fresh reviewer can find a different gap in the same text. In
  the converging round, decline remaining Nits or fix them and run another
  round; an edit after a `converged` record makes it stale.
- **Cap:** 5 rounds per loop.
- **Churn:** a new finding is at the scope of an applied fix, and reverting that
  fix would resolve it.

A `map` finding ends the loop as `returned to map`. Churn or reaching the cap
without converging goes to the human with the open findings by severity.

## Synthesis

The coordinator synthesizes directly, at its listed xhigh synthesis setting,
with no nested synthesizer:

- Merge only findings about the same issue at the same scope. Keep every source
  ID and any dissent; record agreements and contradictions rather than a
  majority vote.
- A merged finding takes the highest severity among its sources.
- Pass comprehension's paraphrase through verbatim, including when it has no
  findings. A wrong paraphrase is a finding.

## Record

Post one sanitized record per round, under the target's publication policy:

1. The panel, round and frozen subject identity.
2. A per-persona status table: persona; role with its receipt-verified model and
   effort; `completed`, `not run` or `retried`.
3. Comprehension's paraphrase, verbatim.
4. The findings: ID, merged IDs, severity, impact, affected section or child,
   evidence and disposition.
5. The settled list.
6. The result: `clean`, `converged`, `revise`, `returned to map` or `escalated`.
