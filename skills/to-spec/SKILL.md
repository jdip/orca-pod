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
`to-tickets` publishes the parent as the review subject, and the children after
the draft passes independent review against the map.

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
associated effort; routine implementation choices stay with the implementer.

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
independent review of the parent and full breakdown against the map replaces
human spec and ticket approval.

Under a recorded, scoped map waiver there is no map to review against: present
the parent and its full breakdown to the operator in one ordinary-text batch and
wait for their approval, which `to-tickets` records on the parent. That waiver
covers the map alone; every other gate still applies. Otherwise run this loop:

1. **Publish the review subject.** Through `to-tickets`, publish or update the
   parent body, without children, as the map's implementation follow-up. The map
   stays open.
2. **Dispatch a fresh reviewer.** Per `roster`, dispatch REV on the other provider
   from the drafter (PLN, or the primary for a compact record), as a new dispatch
   each iteration. The brief carries:
   - the map URL with its Destination, Decisions so far and Out of scope text;
   - the parent URL with its current body;
   - the child breakdown: each ticket's outcome, acceptance criteria, source
     links and blockers; and
   - every earlier iteration's findings with their dispositions.

   Leave out the drafter's reasoning; the reviewer works from the brief and the
   repository.
3. **Review against the checklist.** The reviewer reports each finding with
   evidence, checking:
   - scope fidelity: every map decision is reflected and none is contradicted;
   - acceptance criteria and the completion boundary against the map;
   - ticket granularity: each child is an independently verifiable outcome;
   - dependency edges: only real blockers;
   - the `Delivery` mode and, for `rollup`, its named branch; and
   - source links to the map and material decisions.
4. **Classify and dispose.** The reviewer flags each finding major or minor and the
   primary confirms. A finding is **major** when it shows a missing or
   contradicted map decision, a scope expansion or reduction, or a new decision the
   map does not record. A disagreement over major versus minor makes the finding
   major. Return a major finding to the map under Wayfinder's Implementation
   handoff; the spec never absorbs it. Once the map settles that decision,
   redraft and start a fresh loop of up to 3 iterations. Fix each minor finding
   or reject it with a recorded rationale, then run the next iteration; its
   reviewer receives that disposition.
5. **Record the iteration.** Post one comment on the parent per iteration,
   sanitized under the target's publication policy: `Spec review <n>/3`, the
   reviewer role and its receipt-verified model and effort, each finding with its
   classification and disposition, and the result: `pass`, `revise`,
   `returned to map` or `escalated`.

An iteration passes when the reviewer reports no actionable findings for the
current parent body and breakdown. Run at most 3 iterations per loop. Escalate
findings that remain after the 3rd to the human in ordinary text, with the parent
link and iteration comments, and record the human's decision on the parent.

An **approved specification** is a parent with one of:

- a latest spec review comment that passed and is fresh: the body's GraphQL
  `lastEditedAt`, or its `createdAt` when `lastEditedAt` is null (never edited),
  is strictly earlier than that comment's `createdAt`; an equal or unclear order
  is not fresh, so review again;
- the human's approval after escalation;
- a human approval recorded before this loop existed; or
- the operator's approval under a recorded, scoped map waiver.

An in-scope amendment to the body goes back through this loop, or to the operator
under a map waiver.

## Publish and continue

Once the parent is an approved specification, normally through a fresh pass, and
every map decision is settled, complete Wayfinder's resolution/handoff
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
