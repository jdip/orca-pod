# Orca Pod

Orca Pod is the portable, Orca-native AI development setup. It carries the
skills, workflows, a Claude and Codex role roster, a repository standard and an
installer that sets up a host with one command plus the two sign-ins. It
replaces Agent Team.

Work is tracked in [GitHub Issues](https://github.com/jdip/orca-pod/issues).

## Set up a new host

Orca Pod supports macOS hosts.

1. Install [Orca](https://github.com/stablyai/orca),
   [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview),
   [Codex](https://developers.openai.com/codex/), Git, the GitHub CLI (then
   `gh auth login`) and Python 3.14+.
2. Clone this repository and keep the checkout on `test`, a published branch the
   installer accepts. This is your primary checkout; the scheduled automations run
   in it.

   ```bash
   gh repo clone jdip/orca-pod && cd orca-pod
   git switch test
   orca repo add --path "$PWD"
   ```

3. Run the installer: a dry run first, then `--apply`. It installs the skills,
   roles, global rules, managed agent settings, Orca's settings and two scheduled
   automations, and starts (or prints) any missing Claude or Codex sign-in.

   ```bash
   export ORCA_POD_PYTHON="$(uv python find 3.14)"   # any Python 3.14+
   "$ORCA_POD_PYTHON" machine/install.py
   "$ORCA_POD_PYTHON" machine/install.py --apply
   ```

[docs/install.md](docs/install.md) owns the details: what the installer manages,
refusals, uninstall and recovery. Rerun `--apply` after pulling a new Orca Pod
revision and after an Orca upgrade. Credentials stay on the host; see
[SECURITY.md](SECURITY.md).

## Use it in a repository

Add the repository to Orca (`orca repo add --path <checkout>`) and open an agent in
it. That agent is the coordinator: it owns your dialogue, approvals, tracker
writes and Git integration, and dispatches workers through the
[roster](skills/roster/SKILL.md).

A repository first adopts the [Repository Standard](standard/README.md): `test`
and `main` branches, a short root `AGENTS.md`, tracker and domain guidance,
development guidance and the canonical delivery scripts. Invoke `adopt-standard`
by name, `/adopt-standard` in Claude Code or `$adopt-standard` in Codex. It takes
the branch that fits the target:

- `new` for a new repository with no product behavior yet;
- `existing` for an existing repository;
- `upgrade` for a repository that already records a Repository Standard revision.

When the target carries obsolete or conflicting process guidance, run
`prepare-repository` from this checkout first; it leaves a local preparation
branch for the adoption to continue from. `adopt-standard` assesses the target,
plans with you, then delivers on an `orca/` branch through `pr-to-test`. That adoption
PR is the repository's first delivered change.

## Everyday workflow: whats-next

Work from the repository you want to advance and ask: **"Use whats-next in this
repository."** Add an outcome or constraint when you have one. You don't need to
remember the order of the other skills; [whats-next](skills/whats-next/SKILL.md)
calls them:

1. **Orient.** It reads the project purpose, the selected map and backlog,
   issues, PRs, local changes, Orca ownership (`orca worktree ps` and each
   issue's linked workspaces) and dependency alerts. Work another Orca agent owns
   is left alone.
2. **Choose.** Approved work continues. When paths compete or approval is
   missing, it offers options with rough effort and a recommendation; reply with
   your choice and the scope you authorize.
3. **Plan.** New work starts with a `brainstorm` dialogue: rounds of numbered
   questions, each with a recommendation. For a full map or a new mechanism, a
   panel of isolated reviewers on the other provider checks the drafted map
   first; its judgment findings come to you as questions, and you see its
   fresh-reader paraphrase before you confirm the shared understanding and
   `wayfinder` records the map. That confirmation is
   your one planning approval: a panel of isolated reviewers on the other
   provider then checks the spec and its tickets against the map until two
   rounds in a row come back clean, and you get a short report with the spec
   link. You are asked again only when the panel churns or reaches five rounds,
   a finding changes a map decision, or the scope changes. If you waive
   the map, you approve the spec and tickets directly instead. A small fix to
   an existing mechanism can take the fast lane: you say yes to one tracking
   issue, it skips the map, spec and panels, and it keeps the real checks,
   review on the other provider and normal delivery. A real decision moves it
   to the full flow.
4. **Run.** Approved tickets are claimed, implemented in their own Orca
   worktrees, reviewed on the other provider and delivered. Your approval carries
   across these handoffs; you don't repeat it per ticket.
5. **Answer and reassess.** It returns with real decisions or blockers and
   reassesses after each completed step. Steer or stop it at any time.
6. **Maintain.** When tracked work runs out, it considers dependency upkeep,
   hygiene and standard alignment, and checks the outcome against the project
   purpose. An empty queue is not proof the purpose is met.

A later session picks up where you left off: invoke whats-next again. Main
promotion, host installation and background scheduling are separate requests.

## How work flows

- **Plan before implementing.** Every change, documentation included, needs a
  resolved map and an approved spec, a fresh fast-lane confirmation of an
  eligible fix, or your explicit planning waiver for a stated scope. Small work
  keeps the map and spec brief. `wayfinder` charts the map (a
  `wayfinder:map` issue); `to-spec` drafts the spec parent and its executable
  children; `to-tickets` publishes them as an `implementation:backlog` parent
  with native sub-issues and dependencies.
- **Select, then execute.** `triage` admits prepared parents to the Ready Backlog
  (`implementation:ready`); `select backlog` selects one for your effort.
  Publication, admission and selection do not by themselves authorize
  execution. `next-issue` claims and delivers one eligible child, and its
  continue mode works through the parent. A reopened map pauses its
  whole backlog until the decision is settled.
- **Deliver.** A one-child parent goes straight to a PR into `test`. A parent with
  several children uses one named `orca/` rollup branch cut from fresh
  `origin/test`: each child is a reviewed PR with targeted checks, merged with a
  merge commit, and the finished rollup goes to `test` in one PR with full CI.
  Verified test delivery closes the parent. The shared
  [rollup contract](skills/pr-to-test/ROLLUP.md) owns the branch and CI rules;
  each repository's `docs/workflows/pr-to-test.md` owns its commands.
- **Promote separately.** `promote-to-main` runs only on an explicit request.
- **Clean up.** `cleanup-task-artifacts` releases task-owned resources at phase
  boundaries and keeps anything active or uncertain.

[Tracker guidance](docs/agents/issue-tracker.md) and
[selection scope and handoff](skills/select/SELECTIONS.md) cover labels, claims
and moving an effort between tasks.

## Skill guide

Ask the agent to use a skill by name, with the target and the outcome you want,
for example **"Use dependency-review for this repository's TOML parser."** Use
whats-next for coordination and a specialist when you know the step you want;
direct calls follow the same planning rule. Each skill's `SKILL.md` owns its
behavior. Skills marked † are name-only: no agent or workflow invokes them, so
call them yourself. Skills marked ‡ are explicit-only in Codex, which doesn't pick
them on its own; Claude can, and the authorized workflow that owns them hands off
to them in either host.
Every skill is installed for both Claude and Codex.

| Area | Skills |
| --- | --- |
| Repository setup | `prepare-repository`, `adopt-standard` ‡, `repository-verification` (optional verification instructions), `define-project-goal` (agree the README purpose) |
| Choosing and planning | `whats-next`, `brainstorm`, `wayfinder`, `select map`, `next-waypoint`, `research`, `prototype`, `to-spec`, `to-tickets`, `wait-what` † (re-explain the last answer) |
| Implementing and delivering | `triage`, `select backlog`, `next-issue`, `tdd`, `diagnosing-bugs`, `resolving-merge-conflicts`, `code-review`, `pr-to-test` ‡, `promote-to-main` ‡, `cleanup-task-artifacts` ‡ |
| Delegation | `roster` (role, model and effort for each delegated task); Orca's own `orchestration` and `orca-cli` |
| Maintenance | `codebase-hygiene`, `dependency-review`, `dependabot-upkeep`, `code-simplification`, `reflect` (turn a lesson into an issue), `audit-agent-instructions` |
| Design and writing | `codebase-design`, `domain-modeling`, `improve-codebase-architecture` †, `writing-for-agents`, `wizard` (a guided script for human-only steps), `setup-matt-pocock-skills` † |
| News | `engineering-brief`, also run twice weekly by an installed automation |

Provenance for upstream-derived skills is in [skills/UPSTREAM.md](skills/UPSTREAM.md).

## Changing Orca Pod

Follow [AGENTS.md](AGENTS.md) and [development guidance](docs/development.md),
and the [public-work policy](SECURITY.md#public-repository-work) before any
repository or GitHub write. Changes reach `test` through the
[PR-to-test workflow](docs/workflows/pr-to-test.md);
[promotion to main](docs/workflows/promote-to-main.md) is separately requested.

## License

Orca Pod is released under the [MIT License](LICENSE). Upstream-derived skills
keep their MIT notices in each package's `LICENSE`.
