---
name: to-spec
description: Turn a resolved map into a proportionate implementation specification and executable ticket batch, reusing approved coverage for existing work.
---

# To Spec

Adapted from [`mattpocock/skills` to-spec](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/to-spec), revision `3cca18b368ae95cdbdebbff572ccafa662551015`.
Copyright (c) 2026 Matt Pocock. This adaptation is licensed under the included [MIT License](LICENSE).

Turn resolved Wayfinder design into the draft for one implementation
specification parent and its executable ticket breakdown. The parent is also the
implementation backlog; do not create a parallel planning or queue issue.
`to-tickets` publishes the parent as the review subject, and the children once
the draft is an approved specification, normally through a converged spec panel.

When resolving or changing a saved selection, read
[selection scope and handoff](../select/SELECTIONS.md). Carry the explicit
scope, task owner and generation through handoffs to selection/execution owners.
Keep map and backlog bindings independent. Publication and closed design do not
change another effort's selections or grant takeover authority.

## Choose the planning path

Read the repository instructions, issue-tracker conventions, domain vocabulary,
relevant code, and supplied design sources. Treat issue bodies as the current
approved scope and acceptance criteria; use comments for discussion, decisions,
and evidence. Fold an approved amendment into the draft body instead of making a
comment the authoritative contract.

Search the open `implementation:backlog` parents for one already linked to the
same effort. Reuse that parent and its approved children when they match the
sources and scope; preserve their claims, dependencies, and current scheduling
state. Do not create a duplicate parent or move work from another effort.

Require a covering Wayfinder map unless the operator explicitly waived it under
the global Planning before implementation rule. Before reusing a map or its spec,
apply Wayfinder's **Map-entry evidence** rule, including for closed maps.
If the covering map is missing, begin Wayfinder from the supplied outcome and
evidence. Read the complete map, its comments, every
child and material linked decisions. Draft once all decisions are settled; a map
awaiting only its resolution/handoff bookkeeping can receive this draft before
closure. A substantive unresolved decision returns to Wayfinder and pauses the
associated effort.

Keep planning proportionate. Reuse an existing resolved map and approved spec
only when they cover this change. Otherwise draft a brief spec even for small
work, using one parent and at least one executable child. Add children only for
genuinely independent outcomes; settled design needs no invented decision
tickets or research.

Before a resolved design closes, ensure its implementation follow-up is open and
linked both ways, or record the user's explicit decision to defer or abandon that
work. Reuse one follow-up across related decisions rather than creating duplicates.

## Draft the handoff

Set the parent's delivery mode before drafting its acceptance criteria. A parent
with one executable child defaults to `direct`. A parent with multiple executable
children uses `rollup`: name one `orca/` rollup branch based on fresh
`origin/test` in the parent body. Delivery to `test` before the final rollup
requires the user's explicit decision. Read [rollup delivery](../pr-to-test/ROLLUP.md)
for the shared branch and CI rules.

Synthesize a parent issue draft with:

- an objective and current approved scope;
- acceptance criteria and completion boundary;
- links to the resolved map, material decisions, and other accepted sources;
- the `implementation:backlog` role; a newly created parent is not active or
  implementation authorization, while an existing parent's actual scheduling
  state remains unchanged;
- a `Delivery` field: `direct`, or `rollup` with the exact rollup branch; the
  parent acceptance boundary is the final canonical PR-to-test and verified test
  delivery; and
- applicable standing execution preferences, without copying the design's full
  discussion history.

Then propose independently verifiable ticket outcomes. Prefer vertical slices
where they make a complete behavior demonstrable; create prerequisite
infrastructure work only when it is a real prerequisite. For every proposed
ticket, state its outcome, acceptance criteria, relevant source links, and only
the tickets that genuinely block it.

For `rollup`, a child's delivery acceptance ends when its reviewed feature PR
passes targeted checks and merges with a merge commit into the named rollup
branch; this verified integration can close the child and unblock the next one
without a test deploy. Reserve full CI, aggregate test delivery and the one semver
contribution for the parent.

Classify each outcome by purpose. Application Code needs linting, type checking,
validation, meaningful behavioral tests, and strong coverage. Tooling needs
focused source checks and proportionate behavioral evidence available now; do not
manufacture coverage or fake-environment suites. Write acceptance that present
checks, review and required delivery can satisfy under the global Validation and
delivery closure rule. Name foreseeable unexercised scenarios as expected limits;
add a future incident, pilot or scheduled-run gate only when the operator
explicitly requests that observation as the outcome. Prefer a clean replacement
that removes superseded callers and configuration; use expand--contract only when
a concrete blast radius requires both forms to coexist temporarily.

## Review the draft against the map

With a map, the Chart-the-map confirmation is the only human planning gate. An
isolated spec panel reviewing the parent and full breakdown against the map
replaces human spec and ticket approval.

Under a recorded, scoped map waiver there is no map to review against: present
the parent and its full breakdown to the operator in one ordinary-text batch and
wait for their approval, which `to-tickets` records on the parent. That waiver
covers the map alone; every other gate still applies. Otherwise run the spec
panel under the [panel rules](review-lenses/panel.md):

1. **Publish the review subject.** Through `to-tickets`, publish or update the
   parent body, without children, as the map's implementation follow-up. The map
   stays open.
2. **Run a round.** Freeze the parent body with its `lastEditedAt` (or
   `createdAt`) and the child breakdown: each ticket's outcome, acceptance
   criteria, source links and blockers. Start the round per `roster`'s **Review
   panel**, on the provider opposite the drafter (PLN, or the primary for a
   compact record): five personas in `SPEC REVIEW` mode, each in its own fresh
   session:
   - [fidelity and grounding](review-lenses/fidelity_and_grounding.md);
   - [zoom out](review-lenses/zoom_out.md) with its adapted
     [standard](review-lenses/zoom-out-standard.md);
   - [design critic](review-lenses/design_critic.md);
   - [implementation readiness](review-lenses/implementation_readiness.md); and
   - [comprehension](review-lenses/comprehension.md).

   Each brief carries the map URL with its Destination, Decisions so far and Out
   of scope text, and the frozen parent and breakdown. The settled list and
   earlier findings stay with the coordinator.
3. **Synthesize and dispose** under the panel rules. A substantive design choice
   left open for the implementer, or a reuse that would change a map decision, has
   `map` impact; a routine choice within the approved scope is not a finding.
   Return a `map` finding to the map under Wayfinder's Implementation handoff;
   the spec never absorbs it. Once the map settles that decision, redraft and
   start a fresh loop of up to 5 rounds.
4. **Record the round.** Post one `Spec panel <n>` comment on the parent per
   round, in the panel record format.

Repeat until the loop converges. Escalate churn, or reaching 5 rounds without
converging, to the human in ordinary text with the parent link and round
comments, and record the human's decision on the parent.

An **approved specification** is a parent with one of:

- a latest `Spec panel` record whose result is `converged` and which is fresh;
- the human's approving decision after escalation;
- a passing `Spec review <n>/3` comment, the format used before the spec panel,
  that is still fresh;
- a human approval recorded before the review loop existed; or
- the operator's approval under a recorded, scoped map waiver.

A record is **fresh** when the body's GraphQL `lastEditedAt`, or its `createdAt`
when `lastEditedAt` is null (never edited), is strictly earlier than the
`createdAt` of that record or of a later administrative-edit comment; an equal or
unclear order is not fresh, so review again.

An **administrative edit** changes no scope, acceptance criterion or decision,
such as recording the rollup's creation revision in the Delivery field or adding
a source link. Make it without a new panel, then post a comment on the parent
naming exactly what changed. Every other body edit is a material amendment and
goes back through the spec panel, or to the operator under a map waiver.

## Publish and continue

Once the parent is an approved specification, normally through a converged spec
panel, and every map decision is settled, complete Wayfinder's resolution/handoff
bookkeeping and close the map, reusing this draft rather than replanning; a map
waiver has no map to close. Then hand the approved draft and sources to
`to-tickets`. It creates the children, records separate native membership and
dependency edges, reads them back and sends the human its spec-link report
without waiting for a reply.

Publication does not select the parent or authorize execution. Under `whats-next`
or an implementation request, the Chart-the-map confirmation, or the operator's
approval under a map waiver, carries on with no further prompt: `triage` admits
the parent to `implementation:ready`, `select backlog` activates it when no parent is
active in that scope, and `next-issue` or its continue mode carries it to
verified test delivery. Keep an active parent from
another effort in that scope; report it and stop, leaving any switch to the human.
A planning-only request ends at the approved, published spec.
