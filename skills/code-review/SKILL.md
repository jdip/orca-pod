---
name: code-review
description: Review a PR, branch, or working-tree diff against repository standards and the requested outcome, including delivery reviews and triggered security reviews.
---

Two-axis review of the requested committed or working-tree changes:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the originating issue / spec?

A third, triggered axis applies when the change crosses a trust boundary:

- **Security**: can the change be reached and abused across a trust boundary, and do existing controls hold? Owned by SEC-REV.

The primary agent selects reviewers per the `roster` skill (skills/roster/SKILL.md) after preparing the review packet below. This applies to explicit reviews and delivery reviews. An already assigned reviewer performs its axes directly and returns findings to the primary; it does not reroute or spawn reviewers. A single reviewer checks Standards and Spec unless assigned only one. Review is read-only: report fixes for the implementation owner.

## Reviewers

Take every role, model and effort from the roster; never select a model here.

- **REV** reviews Standards and Spec on the other provider from the implementer. When the implementer ran on Codex (WRK on Codex, or SEC-WRK), use REV's Claude alternate.
- **REV2** adds an independent second review, in a fresh context, only for high-risk changes. It runs on the provider the roster lists, which can be the implementer's, and never sees REV's findings.
- **SEC-REV** owns the Security axis whenever a trigger below applies, in addition to REV. For a pure security fix, SEC-REV may cover all three axes and REV becomes optional.

Route to SEC-REV when the change touches authentication, sessions or authorization; secrets or credential handling; crypto; sandboxing or permissions; parsing untrusted input; installers or configuration writers that touch home directories; or network-exposed endpoints. Any other roster security-path trigger also applies: a security fix, CI/release credentials or supply chain, a reviewer's safeguard refusal, or the operator's request. Report every re-route.

Launch SEC through the roster's **SEC launch**, never with `--agent`, `--model` or `--effort`: a Daybreak terminal on the reviewed worktree, adopted for supervision.

```bash
orca terminal create --worktree <sel> --title "🛡️ SEC <purpose>" --command "codex --profile orca-pod-sec" --json
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
orca orchestration worker-start --terminal <handle> --worktree <sel> --task-title "🛡️ SEC-REV <purpose>" --spec "$(cat <sec-brief-file>)" --json
```

The receipt proves nothing about an adopted terminal's model: verify Daybreak from the Codex records and tear down as the roster describes.

Give every reviewer the same **review packet**, written per the roster's brief: the exact repository and immutable comparison; the complete requested diff, including work in progress when applicable; requirements; applicable instructions; this skill's assigned axes and smell baseline; and verification evidence with its limits. A reviewer on another provider receives no other context, so name the source files and callers to inspect. Keep credentials and unrelated private material out of the packet.

Before publishing review comments or evidence, follow the target repository's
applicable publication policy.

Read the repository's instructions and available tracker guidance when fetching linked requirements. Missing tracker setup does not block review of requirements already supplied.

## Process

### 1. Pin the fixed point

Use the supplied base and target, including an explicit working-tree scope. Otherwise use the current PR's base or the documented delivery target and state it. Ask only when the intended comparison remains ambiguous after inspection.

Resolve commit refs to immutable SHAs and record the exact comparison. For a branch review, use `git diff <base-sha>...<head-sha>` and `git log <base-sha>..<head-sha> --oneline`. For work-in-progress review, include the requested staged and unstaged changes and inspect relevant untracked files; `...HEAD` alone omits them. Preserve unrelated work. If the requested scope is empty, report that rather than launching reviewers. A bad ref requires investigation.

### 2. Identify the spec source

Use the user's request and supplied assignment acceptance criteria, including later corrections, together with explicitly linked issues or documents. Fetch the originating issue/spec when identified by the assignment, PR, or commit messages; use relevant repository design sources for context. Preserve already supplied answers instead of asking for a separate spec file.

If a requirement is ambiguous or sources conflict, complete independent review and report the exact unresolved decision to the primary agent or user. When no requirements can be established, report the Spec axis as unavailable and still complete Standards review. Do not invent requirements from the implementation itself.

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same rule appears in more than one hunk or file in the change. → consolidate it with its owner when the semantics and reasons to change agree; similar syntax alone does not justify coupling callers.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → consider removing it when callers need no additional knowledge afterward; retain useful naming, policy, or isolation.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Review the assigned axes

Assess the target's applicable publication policy within the assigned axes. Check outgoing
source, metadata and evidence and establish whether this review precedes the
change's first applicable GitHub write. Report any earlier unreviewed publication
as an exposure requiring investigation; a later review is not prevention.

For **Standards**, report violations of documented rules with the source rule and exact changed location. Apply the smell baseline as a heuristic, distinguishing actionable problems from optional improvements. Trace relevant callers and downstream effects. Apply the repository's Application Code/Tooling classification; assess actual required checks and evidence rather than inventing additional test suites or coverage requirements.

For changed tests or test setup, trace the cases through inherited fixtures and
helpers to actual service startup, initialization and teardown. Distinguish needing
native service behavior from needing a fresh instance per case. Flag a test that
bootstraps and discards a stack for an assertion unrelated to that lifecycle when
isolated state or a smaller behavioral boundary suffices. Cite the affected case
and setup path, including implicit fixture scope. Preserve justified fresh instances
for destructive/global-state or lifecycle cases; inspect their consumers before
recommending reuse. Passing tests or coverage do not establish that the setup is
necessary. Apply [TDD's boundary guidance](../tdd/SKILL.md#seams-where-tests-go)
within this review, without starting a separate testing workflow.

For changed CI, delivery or verification steps, and for adoption or upgrade
changes, apply the target's verification policy and, where it declares a Repository
Standard, that revision's Verification evidence and Validation and adoption
outcomes. Flag full suites required or launched for feature-to-rollup integration,
even when each child changes the tree; those checks must be targeted. Also flag a
full suite repeated for an already verified integration context,
evidence reuse without explicit context equivalence, and alignment that edits
guidance while its workflows, CI, tests or fixtures still enforce the retired rule.

For **Spec**, identify missing or partial requirements, unrequested behavior, and incorrect implementations. Cite the supplied requirement and the changed location. Assess correctness, regressions, and relevant security implications within the requested scope; a triggered Security axis goes deeper.

For **Security**, map the trust boundaries the change touches and trace attack paths from their actual entry points. Validate each finding against reachable behavior and existing controls, never a hypothetical caller. Report severity, the practical impact, uncertainty and a focused remediation. Analysis stays defensive and local: never exploit live systems.

For structural cleanup, dependency changes, or claims of simplification, also apply
[maintenance review](maintenance-review.md) within these same axes. Follow that
pointer when the change moves responsibilities, removes a path, or adds/replaces a
dependency, even if the PR does not call itself a refactor.

When the primary splits the axes, give each reviewer the same review packet. Assigned reviewers work directly without recursive delegation. The primary reconciles duplicate findings and remains accountable for coverage of every assigned axis.

### 5. Report

Report Standards, Spec and any Security outcomes separately, with severity, exact file/line evidence, the concrete failure, and a focused correction for each actionable finding. State when an axis has no actionable findings or cannot be assessed. Distinguish review evidence from checks actually executed. Subsequent changes require review only of the changes and affected conclusions; completed evidence remains reusable where it still applies.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other. Security is separate for the same reason: code can match the spec and the standards and still open an attack path.

## Attribution

Adapted by Agent Team from [Matt Pocock’s code-review](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/code-review), revision `3cca18b368ae95cdbdebbff572ccafa662551015`. The [MIT notice](LICENSE) covers reused upstream material. Agent Team owns this adaptation.
