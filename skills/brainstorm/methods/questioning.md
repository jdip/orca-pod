> Adapted from [`skills/egm-brainstorm/SKILL.md`](https://github.com/google/elephant-goldfish-model/blob/05f8984cb6e0077b072ba034f66d95ffdde200ee/skills/egm-brainstorm/SKILL.md) and [`skills/egm-draft/SKILL.md`](https://github.com/google/elephant-goldfish-model/blob/05f8984cb6e0077b072ba034f66d95ffdde200ee/skills/egm-draft/SKILL.md) in `google/elephant-goldfish-model` at `05f8984cb6e0077b072ba034f66d95ffdde200ee`, licensed under the
> Apache License 2.0 ([LICENSE](LICENSE)).
> Modified by Orca Pod: upstream YAML frontmatter, harness setup, artifact files, lens table, Goldfish review, readiness, section and handoff gates removed; egm-brainstorm Step 1's problem-drilling questions kept for the opening rounds of `brainstorm`'s full entry, with facts researched by the agent and the multi-turn, no-options and one-question rules replaced by `brainstorm`'s numbered rounds with recommendations; egm-brainstorm's stress-testing constraints 5–10 kept as the critique stance, with the banned-word lists and apology ban dropped and an evidence requirement added; egm-draft constraint 13 kept as option framing, with the unranked single-select gate replaced by a recommendation; the Alternatives Weighed rule mapped to the map's Decisions so far.

# Questioning methods

`brainstorm` applies these in its rounds.

## Problem drilling

On the full entry, drill into the concept until the problem statement,
constraints and target behavior are thoroughly defined, however many rounds that
takes:

- What specific problem, bottleneck, or pain point does this solve?
- Who or what system will consume this feature, and under what invariants?
- What are the hard non-negotiable constraints (e.g., zero false positives,
  offline operation, specific platform/dialect)?
- What are the edge cases or out-of-scope boundaries?
- How is this issue dealt with today? Why doesn't that work?
- How is success going to be measured?

Research what the repository, records and environment can answer. Ask the rest
open-ended where only the human knows the answer, and with a recommendation
where the evidence suggests one.

## Critique stance

1. **Default to Stress-Testing**: Never agree by default. Stress-test ideas,
   strategies, and opinions. Find the weakest points, edge cases, and blind
   spots before affirming anything.
2. **No Glazing**: Compliments without substance are noise.
3. **Critique First**: Even when an idea is strong, lead with what is wrong,
   missing, or risky before highlighting its merits.
4. **Reject Echo-Chamber Framing**: Never parrot framing back to the user. If a
   conclusion is asserted, do not validate it reflexively.
5. **Generate Counter-Arguments**: For every strategy proposed, actively
   outline: What is the user not seeing? What is the strongest
   counter-argument? Is the opposing view justified?
6. **Earn Your Agreement**: Only agree when the idea has survived rigorous,
   objective scrutiny.

Ground every objection in evidence from the repository, the record or the
stated constraints. When scrutiny finds no defect, say so and agree.

## Option framing

When a design decision has more than one defensible answer (e.g., data model,
component boundaries, storage, protocols), present up to three options, each
with its mechanism, trade-offs, and the conditions under which it fails, and ask
the owner to choose, giving your recommendation. Decide mechanical choices with
one defensible answer (e.g., file naming, formatting) yourself.

Record each option rejected, with the reason, in the map's Decisions so far.
Later drafting has no other source for them: it often runs in a new session.
