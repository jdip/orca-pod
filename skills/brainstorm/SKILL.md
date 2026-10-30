---
name: brainstorm
description: Plan new work or stress-test a plan, decision or idea through recommended question rounds, with an isolated map panel and one confirmation before a new map. Use for a new-work discussion, a reopened map dialogue, a human decision inside confirmed scope, or any 'grill' or 'brainstorm' request.
---

# Brainstorm

Interview the user relentlessly until you reach a shared understanding. This
skill owns the planning dialogue, the map panel and the single confirmation;
`wayfinder` owns the map and its tracker records.

## Choose the entry

- **Full entry:** a new-work discussion, including a stress-test of planned new
  work, or an existing map's dialogue reopened by a material change to scope,
  assumptions or outcome. Run every section below, then hand the confirmed
  draft to Wayfinder's **Chart the map**, or back to the Wayfinder step that
  reopened the map.
- **Dialogue-only entry:** a human decision inside an already-confirmed scope:
  a waypoint decision such as a `wayfinder:grilling` ticket,
  `define-project-goal`, or an `improve-codebase-architecture` candidate. Run
  **Ground** and **Rounds** only. The rounds end when no human decision within
  that scope remains; the caller owns completion and its record. There is no
  panel and no extra confirmation.
- **Stress-test:** any other plan, decision or idea the user wants challenged.
  Run **Ground** and **Rounds**. It ends at the user's confirmation that you
  have reached a shared understanding; do not act on it before then.

## Ground

Resolve the target and read the actual repository, the supplied direction and
prior answers. Before reusing a covering map, apply Wayfinder's **Map-entry
evidence** rule. Reuse settled answers. Use `domain-modeling` when terminology or
domain relationships need resolution.

## Rounds

Map the discussion as a **design tree**: every decision branches into the
decisions that hang off it. Frame every question under the
[questioning methods](methods/questioning.md): open the full entry with its
problem drilling, and apply its critique stance and option framing throughout.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a subagent per `roster` to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the subagent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait for their actual answer, never supplying it yourself.

On the full entry, the rounds end when no human decision about the destination
remains. A deeper design question you can already state precisely becomes a
proposed decision ticket; one you cannot yet state sharply stays as fog, under
Wayfinder's fog rules.

## Draft the map

Draft the map body in Wayfinder's map shape: the Destination with its success
criteria, Notes, Decisions so far with each rejected alternative and its reason,
proposed decision tickets, Not yet specified and Out of scope. When the route is
clear, draft a compact map with the agreed direction and no invented tickets; it
still precedes the spec unless the operator explicitly waived planning. Delegate
a substantive draft to PLN under `roster` rule 9; draft a compact, fully settled
one yourself.

## Map panel

**When it runs.** On a full map, one that will carry decision tickets or **Not
yet specified** fog, and on any map that introduces a new mechanism: a new skill,
script, role, workflow step, gate, tracker convention, or language, runtime or
environment, as opposed to a change to the mechanism that already owns the
behavior. A compact map for small, settled work that introduces no new mechanism
skips it. A map waiver means no panel.

**Rounds.** Run each round under the
[panel rules](../to-spec/review-lenses/panel.md) and `roster`'s **Review panel**,
on the provider opposite the drafter: four personas in `MAP PASS` mode, each in
its own fresh session:
[zoom out](../to-spec/review-lenses/zoom_out.md),
[design critic](../to-spec/review-lenses/design_critic.md),
[implementation readiness](../to-spec/review-lenses/implementation_readiness.md)
and [comprehension](../to-spec/review-lenses/comprehension.md). The subject is the
repository SHA plus the inline draft. Its Decisions so far are the governing
decisions, with the existing map's URL for a reopened map. Do not manufacture
frontier detail to start a round.

**Disposition.** Under the panel rules, fix or contest factual findings
yourself, building on the facts the reviewer established. A `map`-impact finding is the
user's: ask it as a numbered question with your recommendation in the next round,
and revise the draft from the answer. Settle a finding the user already answered
in this dialogue with that answer. Once the answers are in, start a fresh loop
on the revised draft: panel, refine, panel until the loop converges. Bring churn
or the round cap to the user with the open findings. The panel adds no gate.

**Reruns.** One converged panel per confirmation. A material change to scope,
assumptions or outcome that reopens an existing map, through Wayfinder's
**Map-entry evidence**, **Work through the map** or **Implementation handoff**,
gets a fresh panel if the map qualifies. Recovering Map-entry evidence without
such a change, or a compact map that later grows through frontier mapping, gets
none.

**Record.** Post each round's record as one `Map panel <n>` comment on the map,
in the panel record format, giving a `returned to map` finding its Q<n> and the
gist of the answer; post rounds run before the map existed once Wayfinder
creates it. A skipped panel records nothing. A missing panel record alone does
not block Map-entry evidence; its dialogue and confirmation requirements still
apply.

## Confirm

Once the panel converges, or when none runs, present the shared understanding,
the rejected alternatives, the remaining fog, the scope and, when a panel ran,
the latest comprehension paraphrase verbatim. Obtain the user's explicit
confirmation: the **`brainstorm` confirmation**. A detailed request, an agent
proposal or reading this skill does not establish it.

This confirmation is the single human planning gate. Under `whats-next` or an
implementation request it carries through the spec panel, publication, backlog
selection, execution and verified test delivery; a planning-only request ends at
the approved, published spec. Preserve the global Planning before implementation
rule and its explicit-waiver boundary.

## Attribution

Adapted by Orca Pod from [Matt Pocock’s grilling](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/grilling/SKILL.md) and the chart-the-map passages of Orca Pod's Wayfinder, itself adapted from [Matt Pocock’s Wayfinder](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/wayfinder/SKILL.md), both at revision `3cca18b368ae95cdbdebbff572ccafa662551015`. The [MIT notice](LICENSE) covers that material. [Questioning methods](methods/questioning.md) adapts `skills/egm-brainstorm` and `skills/egm-draft` from [google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model/tree/05f8984cb6e0077b072ba034f66d95ffdde200ee) at `05f8984cb6e0077b072ba034f66d95ffdde200ee` under the Apache License 2.0, with upstream's [LICENSE](methods/LICENSE) beside it.
