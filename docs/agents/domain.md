# Domain documentation

For domain terminology, start with the glossary below, then consult the relevant
existing `CONTEXT.md`; use `CONTEXT-MAP.md` when present to locate the affected
context. For design decisions, read applicable ADRs in `docs/adr/` or the
component's own ADR directory, and the resolved planning map
([#1](https://github.com/jdip/orca-pod/issues/1)).

Use the glossary's terms in code, issues, and explanations. Surface a conflict with
an existing decision by naming the ADR or map decision and the proposed change. Use
`domain-modeling` when a real terminology gap or changed domain relationship needs
resolution. Missing domain documents alone need no action; create them only when
there is an actual term or decision to record.

## Glossary

### Repository and work model

- **Repository Standard**: the shared conventions a repository adopts: root
  instructions, tracker and domain guidance, development guidance, `test`/`main`
  branches and the canonical delivery scripts. Orca Pod follows it and will carry
  its sources; how adopted repositories migrate to it is not yet specified.
- **Tooling**: code that maintains machines and repositories, such as skills,
  the roster generator, the installer and the delivery helpers. It is verified by
  source checks plus real behavioral evidence, not coverage suites or fakes.
  Classify code by its purpose, not its language.
- **Application Code**: a product, server or CLI that others run. None exists
  here; introducing it requires explicit authorization and its own rigorous gates
  (see [development guidance](../development.md)).
- **Map**: a Wayfinder planning issue labelled `wayfinder:map` that holds the
  agreed direction, decisions so far and remaining fog. It is resolved and
  closed before executable tickets are published.
- **Spec**: an Implementation Specification, the open `implementation:backlog`
  parent issue that owns approved scope and acceptance. Its native sub-issues are
  the ordered work set.
- **Backlog**: the work selected for execution. The Active Backlog is the spec
  selected in an effort's scope; the Ready Backlog is the open
  `implementation:ready` parents waiting for activation.
- **Rollup**: an `orca/` branch, cut from fresh `origin/test`, that collects a
  spec's reviewed child PRs (each with targeted checks) before one final PR to
  `test` with full CI.

### Orca

- **Workspace / worktree**: an Orca workspace is a Git worktree that Orca tracks
  together with its terminals, agents and linked issues or PRs. Each change gets
  its own worktree on an `orca/` branch; the primary checkout stays on `test`.
- **Run**: a lightweight Orca orchestration session bound to one coordinator. It
  groups the tasks, dispatches and messages of one supervised effort.
- **Task**: a unit of work recorded in a Run, with a status the coordinator
  updates.
- **Dispatch**: one assignment of a task to a worker terminal. Its dispatch ID
  scopes heartbeats, questions and the final `worker_done`, so a late message
  from a failed attempt cannot complete a retry.
- **Coordinator (ORC)**: the agent the operator talks to in an Orca pane. It owns
  the dialogue, approvals, tracker writes, Git integration, model selection and
  final acceptance. Fan-out comes only from the coordinator.
- **Worker**: a supervised agent started with `orca orchestration worker-start`.
  It works within the authority its brief grants, reports through orchestration
  messages, and does not commit, push, merge, publish or delegate further unless
  explicitly assigned.
- **Roster role**: a named role (for example WRK, REV, TST, SEC) defined once in
  `roster/roles.toml` with its purpose, standing instructions, provider, model,
  effort, authority and layer. Review and independent bug proof run on the other
  provider from the implementer.
- **Launch receipt**: the record `worker-start` returns, including requested and
  effective launch fields. The effective model and effort are verified from the
  receipt and provider records, never from a worker's self-report.
- **Security path**: the routing that sends work touching a trust boundary,
  security fixes, or defensive-security content to the SEC role, as reviewer,
  independent proof or worker, launched in a Daybreak-enabled terminal.
