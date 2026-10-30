# Issue tracker: GitHub

Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

Before creating, editing or commenting on issues/PRs, applying labels, or
uploading evidence, follow the [public-work policy](../../SECURITY.md#public-repository-work).
Review the outgoing text, metadata, attachments and linked destinations; publish
sanitized evidence and keep private originals outside this repository.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

Task, child and rollup branches use the `orca/` prefix. Skills named here live
under `skills/<name>/`.

## Remediation findings and deduplication

Use this procedure for actionable friction, discovered weaknesses, and deferred
blockers under the global scope guidance. The primary agent completes filing for
findings returned by delegated agents.

1. Establish the task's target repository from its authorized scope and verify its
   remote. Resolve the finding's owning repository separately; component ownership
   or changing checkouts does not expand the task's target. Use explicit
   `--repo <owner>/<repo>` arguments for destination-specific operations.
2. Search open and closed issues using component names, symptoms, and distinctive
   error text, for example
   `gh issue list --repo <owner>/<repo> --state all --search '<terms>' --limit 100`.
   Vary the terms and expand or paginate results when truncated; an empty narrow
   search alone is insufficient. Read likely matches with
   `gh issue view <number> --repo <owner>/<repo> --comments` and inspect relevant
   code or recorded fixes. Match the underlying problem and affected behavior,
   rather than title similarity alone.
3. Before any issue creation, comment or evidence update outside the task's target
   repository, apply the global target-repository write boundary: present the exact
   destination and sanitized proposed content and obtain explicit operator approval,
   even for another operator-owned repository. Reuse prior explicit approval only
   when it covers that write. Read-only investigation and deduplication need no such
   approval. Retain pending drafts in the authorized task context and continue
   independent work. Filing within the task's target remains autonomous.
4. Reuse a matching open issue, adding a comment only for material new evidence.
   For a closed match, inspect its resolution and current behavior: a resolved
   problem needs no new issue; a demonstrated recurrence can be recorded in a new
   issue linked to the prior fix, explaining why it is new work. Preserve existing
   ownership, claims, and approved scope.
5. If no issue covers the remaining problem, create a scoped issue with the
   observed behavior, concrete reproduction or source evidence, impact, relevant
   workaround, and a verifiable remediation outcome. State whether it blocks the
   current task and link the originating issue or PR when one exists. Use a body
   file for multiline text: `gh issue create --repo <owner>/<repo> --title '<title>'
   --body-file <path>`. Filing does not admit work to an implementation backlog.
6. Read back the created issue or updated comment and report its URL. When the
   current task has an issue, link the finding there and record an actual blocker
   using the native dependency convention below; use an explicit linked blocker
   note when native dependencies cannot represent it. Keep the blocked task open.
   If tracker access fails, retain the evidence and proposed issue text in the task
   response and identify the failed operation; the global blocker rule still applies.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> --comments` and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either: resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used after the `brainstorm` confirmation settles direction for new work. The
**map** is a single issue; real decision tickets are
native children. A compact settled map records the agreed direction directly and
needs no invented children. Keep it open through handoff bookkeeping, then
record resolution and close it before executable ticket publication. Use the
existing `select map` owner for selection; retain completed pointers until an
authorized selection replaces them.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (`gh api` on the sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitHub's **native issue dependencies**, the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). GitHub reports `issue_dependencies_summary.blocked_by` (open blockers only, the live gate). Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: list the map's open children (`gh issue list --state open`, scoped to the map's sub-issues / task list), drop any with an open blocker (`issue_dependencies_summary.blocked_by > 0`, or an open issue in the `Blocked by` line) or an assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write.
- **Resolve**: record the answer, complete Wayfinder’s implementation handoff,
  close the decision, then append a context pointer to its map when present.
  Before closing a design with remaining implementation, verify an open follow-up
  linked both ways, or record the user’s explicit deferral/abandonment. Reuse the
  same effort’s follow-up; unsettled designs remain explicitly awaiting planning.

## Implementation backlogs

Used by `to-spec`, `to-tickets`, `triage`, `select backlog` and `next-issue`,
including its continue mode.

The Implementation Specification body owns current approved scope and acceptance;
comments hold decisions, discussion, and evidence. `to-spec`'s isolated spec
panel reviews the drafted parent and child breakdown against the map, recording
each round as a parent comment, in place of human approval; under a map waiver
the operator approves them. Publish the approved relationships through
`to-tickets` and verify them before reporting completion. Publication alone does
not select or execute a backlog.

- **Parent**: an open issue labelled `implementation:backlog`, containing the
  implementation objective, approved design links, execution boundaries, and
  completion criteria. Native sub-issues hold the ordered work set. Do not use
  the closed planning map as the implementation parent.
- **Selection**: use [selection scope and handoff](../../skills/select/SELECTIONS.md)
  and the owning selectors for all reads and writes. Each effort has an explicit
  scope and task-owner binding; map and backlog selections remain independent.
  State is untracked in Git's common directory but isolated by scope. Retain
  generations through continuation; changed ownership stops stale tasks. Legacy
  root pointers remain unchanged until explicitly imported, with no fallback.
- **Handoff**: require human approval of source, recipient, map/backlog/both and
  included claims. Stop source work and verify supported task evidence before
  transfer. Record sanitized handoff and claim evidence in existing issues,
  preserving native dependencies and specification-associated design gates.
  Read back recipient ownership before continuing; partial transfer preserves
  the source's other selection. Missing evidence preserves the claim and state.
- **Membership**: use the same native sub-issue operations described above. Inspect
  `GET repos/<owner>/<repo>/issues/<child>/parent` before attaching existing work.
  Do not silently reparent issues from another effort. Preserve dependencies.
- **Design gate**: before taking or continuing implementation, require covering
  resolved map and approved specification evidence under `to-spec`'s definition,
  a fresh confirmation of a still-eligible [fast-lane issue](#fast-lane-issues),
  or an explicit scoped operator planning waiver. Follow next-issue’s Design gate against the specification’s
  associated map, not the saved planning pointer. An open/reopened map pauses the whole backlog until resolved. Routine
  implementation choices do not reopen maps. A substantive missing decision is
  recorded in the reopened map and linked from the claimed, open implementation
  issue. A closed map with unsettled required decisions is not clearance.
- **Selection and claim**: first open, unblocked, unclaimed child in parent order,
  or a completion-first eligible child supplied by `whats-next`. Its ranking
  preserves dependencies and explicit user ordering; eligibility and claims are
  still checked by `next-issue`.
  Recheck before assigning `@me`, then leave a session-identifying claim comment.
  An existing assignee can belong to another session of the same user; do not
  steal it. Resume only this conversation's claim or an explicit handoff.
- **Resolution**: in rollup mode, record the reviewed child PR, exact integration
  revision and applicable verification, then close the child once its integration
  acceptance is met. Dependent children may proceed without test deployment. The
  implementation parent remains open for aggregate checks and the one canonical
  PR-to-test delivery; close it only after its full outcome is verified on test.
  In direct mode, child closure requires verified test delivery as before. Follow
  [rollup completion](../../skills/pr-to-test/ROLLUP.md) when all children
  are closed but the parent still awaits delivery. Planning maps retain the
  separate planning/handoff lifecycle above. Promotion is separately requested.

## Fast-lane issues

`next-issue`'s **Fast lane** owns the shape, confirmation and escalation of a
standalone fast-lane issue; it has no label, parent or backlog selection. Create
it with a body file holding `## Problem`, `## Outcome`, `## Acceptance` and
`**Lane:** fast`. After the owner's yes, post the `Fast-lane confirmation`
comment with `gh issue comment`. `gh issue view --json` lacks `lastEditedAt`, so
read the freshness timestamps with GraphQL:
`gh api graphql -f query='query{repository(owner:"<owner>",name:"<repo>"){issue(number:<n>){createdAt lastEditedAt comments(last:100){nodes{createdAt body}}}}}'`.

## Ready Backlog and Triage

`implementation:backlog` identifies an Implementation Specification parent.
`implementation:ready` records the user's approval to admit that prepared parent
for future execution. Create the ready label when needed. The Ready Backlog is
open ready-labelled parents except the currently active parent. Labels do not
activate work; the scoped selection identifies this effort's Active Backlog.
Another effort may have a different active backlog. Preserve its ownership.

Paginate open parent intake, for example:
`gh api repos/<owner>/<repo>/issues --method GET -f state=open -f labels=implementation:backlog --paginate`.
Exclude pull requests. Read children, claims, and native dependencies separately;
blocked children still belong to the approved scope. For other incoming work,
paginate the relevant open issues without filtering out blocked or claimed work.

Triage refines, deduplicates, and orders within approved scope, preserving
claims and dependencies. Group approved small fixes only where the existing
resolved map and approved spec cover them. Otherwise propose the fast lane for an
eligible fix, or use Wayfinder and the spec/ticket owners for a compact plan;
only an explicit scoped operator waiver changes the planning gate. Expanding
scope, moving work between efforts, and admitting prepared parents to the Ready Backlog require a human decision.
Current scope and acceptance live in issue bodies; comments hold evidence.

Triage reads and validates the explicit scope and owner binding before offering
activation. A confirmed absent selection in that scope or a verified closed
selected parent means no active parent for this effort. Missing binding context
is an error. An invalid, unreadable, wrong-repository, or inaccessible selection
is unresolved, not an empty queue. Preserve it while investigating. Offer
activation only when no parent is active in this scope, and carry out explicit approval through the shared
`select/scripts/select.sh backlog` mechanism. Routine triage preserves an open
active parent; explicit `select backlog` may switch it at the user's request.
Completion never selects another parent automatically. Readiness and activation
provide no independent permission to execute work.
