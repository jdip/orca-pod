---
name: adopt-standard
description: Adopt the Repository Standard in a new or existing repository, or upgrade an adopted repository from its recorded Repository Standard revision.
---

# Adopt Standard

One workflow with three branches, each carrying out the Standard workflow it names:

- `new`: Greenfield Initialization, for a repository without established product
  behavior or development workflows.
- `existing`: Brownfield Adoption, for a repository with established product
  behavior or workflows, preserving that behavior and useful compatible workflows.
- `upgrade`: Standards Upgrade, for a repository with a valid declaration, from
  its recorded Repository Standard revision to the selected source revision.

The shared gates below apply to every branch. Apply the selected branch's section
at the step it names; its safeguards add to the shared gates.

## Authority and publication

An explicitly approved `whats-next` alignment proposal can supply the target,
source baseline, and authorized scope. Reuse that consent; assessment alone does
not authorize this workflow's edits. Return its verified outcome or unresolved
decision to the coordinator after following this workflow's own gates.

Begin with read-only assessment; implementation follows the target-specific plan
below. Assess the selected standard's visibility and public-work requirements before any
GitHub writes in this workflow, including tracker updates. Verify current visibility,
preserve licensing and owner decisions, and reuse applicable policy for planning
publication. Plan required policy changes with the other outcomes. Resolve required decisions
before dependent publication; continue independent local work. Report actual policy
use and unexercised paths with the delivery evidence.

## Select the branch

Resolve the human's target repository and source request. Inspect the actual
repository and local work first: existing product behavior, workflows, root
instructions, domain docs, dirty state, and the Repository Standard Source/Revision
declaration in root AGENTS.md. Preserve unrelated work, attached checkouts and
existing product behavior. Route by actual state; when it differs from the
requested branch, switch within the same request:

- No declaration and no established product behavior/workflows: `new`.
- No declaration with established product behavior/workflows: `existing`, rather
  than treating the repository as empty.
- A valid declaration, including an operator-confirmed source switch: `upgrade`.

Investigate a malformed, ambiguous, inaccessible, or wrong-source declaration
rather than guessing an adopted SHA.

## Resolve the source

For `new` and `existing`, the source is https://github.com/jdip/orca-pod at a
user-specified revision when supplied, otherwise its default branch. `upgrade`
resolves its recorded source, or an operator-confirmed source switch, and its target
under its own section. Read the selected source's `standard/README.md` and relevant
ordinary templates at one concrete commit. Investigate unavailable or ambiguous
source rather than silently using stale content or switching to another branch.

## Assess and plan

Before selecting the work, read any supplied preparation handoff issue. When
none is supplied, search the target repository's tracker for preparation handoffs
and adoption prerequisites, including closed issues and their comments. Inspect
likely matches against the repository identity, intended workflow, and prepared
branch, commit or baseline, using Git ancestry when continuation has moved to
another branch. Use the matching handoff's findings, preserved decisions, remaining
prerequisites and map/spec links as context within the current authorization.
Resolve competing matches from that evidence; ask only if a material ambiguity
remains. If no handoff exists, continue normal inspection. Report inaccessible or
ambiguous tracker evidence without treating it as an absent handoff; pause only
work whose scope or safety depends on resolving it.

Apply the selected standard's Target assessment and planning and Guidance retirement
outcomes before implementation. Assess actual mechanisms, obsolete process and gaps
against the workflow's goals; use that evidence in the target-owned Wayfinder map.
Resolve the plan and approved specification against the actual purpose,
constraints and workflow goals, reusing covering plans, preparation evidence and
settled decisions. Plan the changes, including executable workflow, CI, test and
fixture alignment, prerequisites, explicit blockers and actual test-delivery
evidence for this target. Recheck target state and plan coverage at execution.

Apply the selected standard's checkout and delivery requirements to the actual
repository and root guidance, including this workflow's own feature worktree and
missing prerequisites within its scope. Preserve local and active work while
preparing that worktree; report unresolved checkout conflicts rather than bypassing
the standard or declaring adoption from text alone.

## Implement

Execute the approved target plan. Establish actual short root guidance/pointers,
tracker conventions, lazy domain guidance, the local Application Code/Tooling
mapping, development commands, minimal canonical delivery shell entry points and
the two fixed local runbooks. Apply the selected standard's language/environment
declaration to each actual component.

For an intentional replacement, migrate callers and guidance and remove obsolete
implementation/configuration within scope; keep no abandoned mechanism behind shims
or duplicate paths. Thin canonical shell entry points around a deliberately
retained implementation are valid.

Use `define-project-goal` to establish the project purpose with the human operator.
Reuse a clear existing blurb; include approved purpose edits at the top of every
root README in this workflow's own change and delivery. The skill owns the
conversation and wording; return here afterward to complete the workflow.

Use `dependabot-upkeep` to establish the selected standard's alert-only protection
outcome on the actual target. Pass the alignment setup authority, repository,
dependency surfaces and delivery rules. Verify settings, active alert coverage and
remaining PR-generation behavior, or report the exact unresolved capability.
Return here for delivery.

Use `repository-verification` for its suitability assessment during normal
inspection. Report its include/omit/defer recommendation with the other ready
decisions; run setup only within explicit opt-in, reusing existing consent. Return
here for this workflow's delivery; existing verification opt-in does not require a new guide.

Apply the selected standard's Claude guidance bridge contract to root and applicable
nested repository-owned guidance.

## Validate

Apply the selected standard's Validation and adoption and Verification evidence
outcomes to the target's actual workflows, CI, scripts, tests and fixtures in this
change, verifying them through their relevant proportionate native checks and
available authorized behavioral evidence. Application Code uses rigorous lint,
type checking, validation and meaningful high coverage. Tooling uses proportionate
source checks and available authorized behavioral checks, without fake
infrastructure or recursive tooling tests. Report unexercised future-use scenarios
as limits under the standard's closure policy.

The workflow is complete only when guidance and executable controls agree; an
unresolved design, authorization or capability blocker keeps it explicitly
incomplete. Record application coverage gaps in scoped, deduplicated tracker
issues without claiming unmet coverage is satisfied.

## Decide and deliver

Make routine choices within the approved standard. Investigate substantive
behavior changes, tradeoffs and conflicts. Preserve unanswered decisions rather
than assuming intent. Reuse already-settled standards and routine implementation
details instead of asking the human to restate them.

Write the one Repository Standard section in root AGENTS.md with Source set to the
exact source repository URL and Revision set to the full selected commit SHA, as
specified by the standard. Ship it in the same PR as the change, not a bookkeeping
PR. In an undelivered Git branch the declaration is the intended target, not
completion evidence.

Deliver through shared `pr-to-test`, with sufficient review of every submitted
change, the local runbook's actual completion evidence, actual test deployment when
applicable, and the shared cleanup procedure without orphaning attached task
checkouts. Finish issue bookkeeping. Record verified test delivery, remediation
issues and links, and safe cleanup and retained artifacts. Main promotion is
separately requested and never required to complete this workflow; successful test
delivery permits the next task without resolving non-blocking remediation first.

## `new` branch

- Assess and plan: inspect pre-existing guidance and setup assumptions even without
  product code. Resolve missing planning capabilities before implementation,
  without requiring adoption's own outputs to begin conversational planning.
  Include initial Git branch setup when needed.
- Implement: select or scaffold an application stack, coverage program, CI matrix
  or deployment environment only with explicit user authorization. Application
  linting, type checking, validation and meaningful high coverage grow with actual
  application development.
- Decide and deliver: with no application, report that reality rather than
  inventing a deployment.

## `existing` branch

- Assess and plan: plan what to retain and remove.
- Implement: retain implementations and customizations justified by current needs
  under the standard's guidance-retirement outcome.
- Validate: record unrelated application coverage deficiencies in scoped tracker
  issues after duplicate checks.

## `upgrade` branch

- Select the branch: read the single Repository Standard Source/Revision
  declaration in root AGENTS.md. If it is absent, use `new` or `existing`.
- Resolve the source: resolve the recorded source repository and the full adopted
  commit. For an ordinary upgrade, resolve that source's default-branch HEAD; honor
  an explicitly requested revision instead. Select and report one concrete target
  commit. Do not silently use the current source branch (host installation through
  `machine/install.py` has a different selection rule; see `docs/install.md`), stale
  content, or another repository. Verify both revisions are from the recorded
  source, or from their respective repositories for a source switch, before
  comparing them. An explicitly pinned revision follows the target standard's
  reachability rule for pre-default pins.
- Resolve the source, for an operator-confirmed source switch, where the adopted
  SHA belongs to another standard repository: compare that source's standard at
  its recorded revision with the target standard, and record both repositories and
  revisions in the upgrade evidence. The switch replaces the declaration's Source
  and Revision together.
- Assess and plan: read the target standard and compare the relevant
  adopted-to-target source changes. Apply the assessment to the actual repository,
  including inherited process outside the source delta.
- Implement: recheck before applying the delta, preserving justified
  customizations. Apply the delta in place, without wholesale overwrites of local
  files or a migration engine/compatibility matrix. If the outcome already holds,
  avoid gratuitous implementation changes.
- Validate: reassess the Application Code/Tooling mapping and actual gates.
- Decide and deliver: publish a local preference as a source-standard change only
  with explicit authorization for that change. Update the existing declaration to
  the selected full target SHA.
