# Repository Standard

This directory is the ordinary versioned source for Repository Adoption and
Standards Upgrade. Its Git revision identifies the standard; the application's
semantic version is separate. Apply outcomes to the actual repository rather than
copying an entire scaffolding tree.

## Required outcomes

- A concise project-purpose blurb at the top of every root README, directly below
  the project title. Use `define-project-goal` to agree missing or changed wording
  with the human operator; reuse a clear existing purpose and keep variants
  consistent in meaning. Include approved edits in the adoption or upgrade change.

- Short root AGENTS.md with repository-specific scope, pointers, and the explicit
  checkout and delivery rules below; runbook links alone are insufficient.
- Concrete issue-tracker instructions and commands; GitHub uses the native issue,
  sub-issue, dependency, claim, and remediation deduplication conventions in
  docs/agents/issue-tracker.md. Include search, matching-issue reuse, evidence,
  readback, and blocker links so global filing guidance has a concrete local path.
  Apply the global target-repository write boundary at the tracker write step:
  local remediation stays autonomous; any external destination requires explicit
  operator approval regardless of ownership, with read-only discovery and pending
  drafts preserved.
- Task-relevant domain-documentation pointers like docs/agents/domain.md. Create
  or change domain docs when real terms or decisions emerge, rather than as
  empty scaffolding.
- Actual development and verification instructions, with a local classification
  of Application Code and Tooling by purpose.
- Verification policy held by the target's native CI, script and runbook owners
  under [verification evidence](#verification-evidence), with executable
  alignment completed under [validation and adoption](#validation-and-adoption).
- Guidance retirement under the outcome below, including inherited process that
  adds unjustified complexity without directly contradicting another rule.
- A target-specific plan under Target assessment and planning below, resolved
  before implementing preparation, adoption or upgrade changes.
- A root language/environment declaration for each existing component, following
  the policy below; component classification alone does not select its stack.
- Dependency-alert protection and repository-owned remediation under the
  [dependency upkeep](#dependency-upkeep) outcome below.
- Discoverable current repository visibility, with licensing and publication
  safeguards under [visibility and public work](#visibility-and-public-work).
- Executable scripts/pr-to-test.sh and scripts/promote-to-main.sh, paired with
  docs/workflows/pr-to-test.md and docs/workflows/promote-to-main.md.
- Owner-confirmed branch protection on `test` and `main`, with catch-up delivery,
  under [checkouts and delivery](#checkouts-and-delivery).
- One source/revision declaration in root AGENTS.md, delivered in the adoption or
  upgrade PR, using the exact fields below.

```markdown
## Repository Standard

- Source: https://github.com/jdip/orca-pod
- Revision: <full adopted commit SHA>
```

Replace the placeholder with a real commit from this source. The declaration in a
working branch is the intended target, not proof of delivery. Source authorship
alone is not adoption; Orca Pod also records its declaration in root AGENTS.md.
Unmarked repos
need Repository Adoption; ordinary upgrades use the recorded source's default
branch unless the user requests a revision. Select one concrete revision and apply
its relevant delta, preserving unrelated work.

The default branch carries this standard from `v0.1.0`, so ordinary adoption and
upgrades use its HEAD. A target explicitly pinned to a pre-default revision, such
as a rollup or `test` commit, depends on that commit staying reachable: verify it
is reachable from a source branch before selecting it, and keep source delivery to
merge commits only so later integration retains it.

## Target assessment and planning

Preparation, Greenfield Initialization, Brownfield Adoption and Standards Upgrade
begin with a proportionate read-only assessment of the actual target. Establish
its identity and starting state, purpose, chosen workflow and exact source baseline;
inspect relevant code, guidance, current mechanisms, constraints, capabilities and
existing preparation/map/spec evidence against that workflow's required outcomes.
An empty-looking repository or a source revision delta does not replace assessment.

Carry the target's accepted behavior, inspected baseline, outcome evidence and
unassessed scope through planning and delivery using the bounded
[outcome assessment](../skills/whats-next/maintenance.md#outcome-assessment).
Reuse the target's sufficient verification guides and controls; its acceptance
definitions remain locally owned.

For the selected workflow, require actionable native failure evidence at its
existing helper/check boundary: responsible stage, safe operation identity and
revision, native cause/result, verified effects, uncertain attempts and retained
evidence or next verification. Preserve the target's failure behavior and privacy
rules. Plan a missing mechanism locally; a capability or authorization block is an
explicit prerequisite, not evidence of a source defect.

For a selected native enforcement remedy, carry its motivating violation, valid
neighboring behavior, required invocation and justified residual guidance through
planning and verification using [reflect's follow-through](../skills/reflect/SKILL.md#record-and-follow-through).
Keep the mechanism at its existing target type, lint, schema, test, runtime or data
boundary, under that target's covering plan and authority.

Conduct or resume Wayfinder with that evidence, starting new work through
`brainstorm`'s full entry before charting, to resolve how this target should
reach the workflow's goals. The target owns the map and specification, including
when preparation is driven from Orca Pod. Reuse covering plans and settled
decisions; one plan may cover preparation and subsequent adoption/upgrade while
preserving each phase's authorization and completion boundary. If the target
tracker is unavailable, continue conversational planning and resolve the artifact
location before implementation. Follow publication policy for planning writes.

Before implementation, resolve the map and obtain an approved specification and
executable breakdown, as `to-spec` defines approval, through the existing
planning owners, unless the operator explicitly waives planning. A workflow
invocation carries its normal authorized outcome; it does not waive planning. Keep small plans brief. Plan actual changes, including
executable verification alignment, prerequisites, explicit blockers, separately
owned work and evidence for the target's completion boundary, rather than create
a universal bootstrap program. Research and planning records may precede approval;
target guidance/configuration changes and adoption setup follow the approved plan.
Use the existing selection owners with explicit effort/task bindings for saved
maps and backlogs. Independent efforts retain separate selections, including in
a shared checkout; approved handoff identifies source, recipient and included
claims, verifies source quiescence, and stops stale source continuation. Preserve
legacy state for explicit migration. Use the backlog selection and `next-issue`
owners for child claims and resolution in the target tracker. Resolve their
scoped selection binding and execution context from
the target checkout, even when this session starts elsewhere. A direct workflow
invocation hands its target, approved child and authority to that executor before
edits; within an already claimed child, execute the named skill without recursive
handoff. The skill supplies implementation and its completion boundary, then returns
evidence for child resolution. Preparation completes its documentation child at the
verified local handoff; separately scoped adoption/delivery children remain open.

At execution and handoff, verify that the target state, baseline and scope still
match the plan. Refresh affected evidence; substantive changes return to Wayfinder,
while routine covered choices remain with the implementer. Include map/spec links
and the assessed target/baseline in the existing handoff or delivery evidence.
Missing capabilities or unresolved decisions remain explicit rather than becoming
silent implementation.

## Guidance retirement

For instruction authoring and review, use `writing-for-agents` and the
global instruction conventions.
Evaluate the baseline itself as well as target guidance. Preserve explicit
requirements and their reasons: maps/specs/ticket handoffs provide durable context,
and main promotion requires a separate explicit operator request. Simplification
improves how these requirements are expressed and reached, not their force.
Current [OpenAI instruction guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
informs this assessment; model-specific advice is evidence to assess against the
target's actual agent audience, not authority to override operator decisions.

Preparation, adoption and upgrades assess repository-owned guidance by purpose and
effect. Inspect the repository broadly, including unlinked documents, embedded
instructions, hidden agent/editor rules, skills and templates; follow references
and copied rules into their current owners. Names and keywords are discovery clues,
not a scope checklist. Report exclusions and inaccessible surfaces; preserve
separately owned content and Unmanaged Local State.

Treat inherited development manifestos, bootstrap programs, process decision
compilations, milestone machinery and enforcement roadmaps as highly suspect.
Judge what they make agents do against the selected standard's minimalist intent:
each retained obligation must serve a concrete current need with proportionate
complexity. Compatibility, prior adoption, historical labels, incoming links and
existing enforcement alone do not justify retention. Challenge unnecessary ceremony,
speculative infrastructure, duplicated principles and accumulated exceptions even
when no pair of sentences directly conflicts. Apply the same test to the Orca Pod
baseline itself. If a source requirement fails it, record the concrete mismatch
with the source owner and resolve the intended change through Wayfinder rather than
silently importing the requirement or creating a local policy fork.

Favor complete removal of obsolete process artifacts, including records and
tombstones. Extract only indispensable current facts or still-valid decisions into
their existing owners; remove dubious process from otherwise useful documents.
Git history normally supplies the archive. A disclaimer, renamed file or relocated
rule does not retire an obligation. Preserve current product requirements,
necessary safety controls and justified repository constraints; resolve substantive
unsettled decisions with the operator rather than infer them from old plans.

Retire an obsolete obligation at every owner that enforces it. Trace affected
callers and enforcement: adoption and upgrades change the target's workflows, CI,
scripts, tests and fixtures together with its guidance, under
[validation and adoption](#validation-and-adoption). Guidance whose executable
controls still enforce the retired requirement is not aligned. Classify by purpose:
application tests remain application tests when invoked by tooling. Preserve
necessary application/security checks and the canonical delivery route.
Preparation retains its documentation-only local-branch handoff boundary and hands
each required executable change to the adoption or upgrade plan as named scope.

Reassess the final guidance across the discovered scope for surviving obsolete
obligations and inbound references, including content migrated into another owner.
Report removals, justified retention and unresolved mismatches in the existing
handoff or delivery evidence, without a new inventory framework. Complete independent
authorized guidance cleanup before batching decisions, keeping unresolved guidance
and actual delivery blockers explicit. Preparation readiness covers its
documentation outcome and names the executable alignment adoption or upgrade makes.

## Visibility and public work

Greenfield Initialization, Brownfield Adoption and Standards Upgrade establish
the target's current visibility in root guidance or a directly linked policy.
Verify the exact remote and actual GitHub visibility when available. Record current
public/private state separately from any intended future publication. An absent
remote, inaccessible hosting state, or conflicting declaration leaves visibility
unresolved: obtain the owner's intended state and resolve actual state before
dependent publication. Adoption and upgrade authority never changes visibility.

For public targets, inspect existing licensing and provenance, preserve required
third-party notices, and establish an appropriate owner-approved license. Reuse
settled licensing decisions. Missing or conflicting licensing requires an owner
decision before publication; adoption does not grant relicensing authority.

Establish a repository-owned public-work policy for public targets, linked from
root agent guidance. Preserve an adequate existing policy and deliberate local
choices. Private targets still exclude credentials and can apply an explicitly
approved public-work policy during preparation for future publication.

The policy requires review before the first applicable GitHub write, including
issue/PR creation, comments, pushes and uploads. Cover source and relevant history,
credentials, private identifiers and contact details, attribution, commit identity,
branch/tag names, CI output, logs, screenshots, attachments and linked evidence.
Establish approved commit identity and verify platform-created merge metadata.
Preserve explicit public attribution and legitimate upstream authorship. Sanitize
outgoing evidence; retain necessary unsanitized originals only in an established
private destination. If none exists, resolve that destination before retaining or
sharing such material. Automated checks supplement review, not complete privacy
clearance; editing after publication does not retract earlier exposure.

Wire the policy into the target's tracker instructions, review requirements and
both delivery runbooks, so the adoption or upgrade itself follows it before any
applicable publication. Reuse existing mechanisms instead of a separate publishing
system. Complete independent local work while visibility or licensing decisions
are pending; keep dependent writes paused. Verify actual declaration, license and
policy handling through authorized real use, reporting unexercised paths and
unresolved decisions without claiming publication approval.

## Dependency upkeep

Authorized Greenfield Initialization, Brownfield Adoption and Standards Upgrade
include establishing supported dependency protection through `dependabot-upkeep`.
For GitHub targets, enable the dependency graph and Dependabot alerts where
available, while disabling automated Dependabot security updates and scheduled
version updates. This keeps alerts available without having GitHub create update
pull requests. `whats-next` reads current alerts during ordinary discovery and
routes actionable findings through the repository's own planning, dependency
edits, pull-request conventions, review and delivery. This is part of alignment,
not a separate optional assessment. Preserve deliberate owner-approved exceptions;
resolve conflicting policy with the owner.

Use manifests consumed by the real build or install path. A dependency hidden in
an installation command is a coverage gap to assess, not automatically exempt;
prefer exposing the existing pin through that installer's native manifest without
duplicating its owner. Preserve deliberate manual pins and report unsupported
sources such as manually reviewed external Git revisions through their existing
update owner.

Verify the actual hosted graph and alert settings, and that automatic security and
version pull-request creation is disabled. Distinguish delivered configuration
from active service. Record coverage, justified exceptions and exact blocked
capabilities in the existing alignment evidence. Missing permissions or unavailable
hosting features leave protection explicitly incomplete; continue independent
alignment work. Configuration awaiting separately authorized default-branch
delivery can finish verified test delivery with activation reported as pending.
Dependabot alerts cover only the default branch, so a target that delivers to
`test` and promotes rarely has no alert coverage of code delivered since its last
promotion. Record that gap, with the default-branch revision alerts cover, in the
alignment evidence. Do not claim active coverage or require promotion merely to
complete source delivery or close the gap.
Additional credentials, paid features, visibility changes and separately required
main promotion retain their own approval boundaries. Do not widen permissions,
change hosting or invent a new updater to claim completion.

## Optional repository verification

Greenfield Initialization, Brownfield Adoption and Standards Upgrade assess whether
reusable real-behavior verification would benefit the repository and recommend
include, omit or defer, using `repository-verification`'s suitability assessment.
The assessment is required; inclusion is explicit opt-in, not a baseline requirement.
Preserve sufficient existing controls and guides. Deferral names a revisit condition;
UI, a new runtime, a helper framework and a separate guide are not prerequisites.

For an opted-in repository, root guidance declares adoption and links its maintained
instructions. Keep them current alongside relevant behavior changes, with proven
controls, observable outcomes and evidence/cleanup rules. `repository-verification`
owns setup and audits. `whats-next` considers useful audits alongside hygiene on a
stable baseline, using prior evidence, churn and friction rather than repeating
unchanged audits. No background scheduling is implied.

## Claude guidance bridges

Adoption and upgrades create a relative `CLAUDE.md -> AGENTS.md` symlink beside the
root guidance and each applicable nested `AGENTS.md`, whether or not Claude is
installed on the current machine. An applicable nested file is repository-owned
guidance for a scoped component; do not traverse symlinked directories or create
bridges in vendor, generated, submodule, independent-repository, or other worktree paths.

Confirm the sibling `AGENTS.md` is a regular file. Investigate reversed links or
cycles and preserve the guidance before changing link direction. Inspect each
existing `CLAUDE.md` before changing it. Retain a correct relative link. A file, a
different link, or any other conflicting content requires investigation before
replacement. Verify every created or retained bridge with
`readlink` and Git's staged `120000` symlink mode, confirming that its target is the
sibling `AGENTS.md`. The bridge makes repository guidance discoverable; it does not
install Claude or prove session loading.

## Languages and environments

Record each actual component's approved implementation language, runtime,
build/package toolchain, and execution/deployment environment in root guidance
or a directly linked authoritative section. Cover CLI, app, server, and Tooling
only where they exist; do not invent
stacks for absent components. Derive existing choices from source, callers, and
build configuration, preserving their scope rather than treating any language
found anywhere in the repo as approved for every component.

Require explicit user authorization before adding a language, runtime, build/
package toolchain, or execution/deployment environment, including helper scripts
and adoption tooling. Prefer reuse of one existing language across components
where practical. A feature or adoption
request does not implicitly approve a new environment. Greenfield choices without
an approved stack require a concrete recommendation and explicit authorization;
brownfield adoption and upgrades preserve established choices. This policy does
not authorize migrations or language consolidation of existing code.

## Validation and adoption

Application Code implements product behavior, including a CLI that is itself the
product. Require rigorous linting, type checking, validation, and meaningful tests
with high coverage across all application behavior. Each repository selects and
enforces appropriate stack-specific gates and coverage targets. Do not use a local
target as permission for weak coverage or inflate numbers with meaningless tests.

Tooling supports development, validation, delivery, and machine/repository maintenance.
Validate it with proportionate checks and the behavioral evidence available
for the changed operation. No tooling coverage targets, fake environments,
conformance suites, tests of tests, or resumable workflow engines. Running application
checks through a shell wrapper does not turn those checks into prohibited Tooling tests.

Greenfield Initialization establishes only the needed organization, guidance, tracker
conventions, and minimal shell entry points. Application tooling grows with actual
application development.

Adoption and upgrades align the target's executable verification, not only its
guidance. This includes selecting targeted checks for feature-to-rollup PRs and
full CI for delivery PRs by their actual destination, with matching required-check
configuration and evidence handling. The target-owned plan names the workflow,
CI, script, test and fixture
changes that retire obsolete enforcement, such as Tooling suites, fake environments,
duplicate verification runs and unjustified per-case service startup, and how each
change is verified. Apply [TDD's test boundaries](../skills/tdd/SKILL.md#seams-where-tests-go)
when changing application tests and fixtures. Routine repairs
within that scope ship in the alignment change under its existing authority.
Preserve mechanisms justified by current needs: meaningful application behavior
and native-contract tests, fresh per-case data and isolated credentials, and
dedicated services for destructive or lifecycle cases. Alignment changes how
verification runs and is reused; it is not an application rewrite. A substantive
missing design, authorization or external capability stays an explicit blocker and
leaves adoption or upgrade incomplete. Application coverage gaps unrelated to that
alignment remain scoped, deduplicated issues with their own owner and do not block
adoption. Actual delivery prerequisites still apply.

## Verification evidence

Record the target's verification policy with its native owners: CI configuration,
delivery scripts, development guidance and the local runbooks. Scope verification
to the delivery boundary:

- Feature to rollup: run only targeted tests and validation for the changed
  behavior and affected integration paths, plus review. A new cumulative tree
  needs fresh targeted evidence, not a full suite.
- PR to test, from a direct feature or completed rollup: run authoritative full CI
  for the combined change and verify actual test deployment/processing.
- Separately requested promotion to main and its synchronization: use equivalent
  prior full evidence where proven; otherwise run full CI for the changed inputs,
  along with the actual promotion acceptance.

Within that scope, run one authoritative verification per distinct integration
and relevant context, such as a runtime matrix entry, data service or deployment
target. Hosted CI is authoritative where it exists; at full-delivery boundaries,
full local runs are optional unless the runbook names a local-only gate.
Cheap pre-publication privacy checks stay mandatory before each push, and changed
Tooling uses proportionate checks and available behavioral evidence.

Targeted evidence never satisfies a full-suite gate. Keep the scopes distinguishable
in native CI results and delivery lookup. A conflicting full child requirement
must be corrected at its CI, protection or runbook owner within authorized scope;
otherwise report the blocker. Missing targeted checks do not justify a full-suite
fallback, protection bypass or treating a cancelled/skipped full run as successful.

Reuse within a verification scope requires a successful native run attributable
to the content and relevant
configuration, environment and data inputs being checked. Attribute a PR run to
its resulting merge by verifying the intended parents and comparing the merged
tree with the tested integration. Promotion or synchronization with unchanged
content and relevant context uses lightweight provenance instead of a repeated
suite, while separately verifying its own intended parents. Changed or unproven
inputs need fresh validation at the applicable scope, and a failed or pending
current check stays blocking regardless of earlier evidence. Attribute evidence
through native run identities and Git objects. Each target defines equivalence from
its actual inputs: an application whose results depend on configuration, services
or data includes them rather than keying reuse to the source tree alone.

Exact head/base/parent pins, review, branch protection and real deployment or
processing acceptance remain separate gates. Reused build or test evidence never
satisfies deployment acceptance.

Under non-admin access, GitHub returns 404 for branch protection and the
[Dependabot settings](../skills/dependabot-upkeep/SKILL.md#establish-alert-only-protection),
so 404 does not separate disabled from forbidden. Report such a setting as
unreadable, not disabled, and give the owner its readback or set step, such as
the [branch protection](#checkouts-and-delivery) readback.

## Checkouts and delivery

Keep the primary local checkout on `test`, refreshed from `origin/test` by
fast-forward only when clean. Reserve `test` for that checkout; never check the
branch out in a linked worktree. Make all changes, including adoption, upgrades,
documentation, and small fixes, on `orca/` feature branches in separate worktrees
based on fresh `origin/test` for direct delivery or rollup creation. Rollup child
branches start from the current rollup. Preserve unrelated local work and attached checkouts.
Detached revision worktrees are valid for canonical verification.

The two primary workflows are:

- Single-issue work: feature branch -> PR to test -> separately requested promotion to main.
- Multi-issue packet: feature branches -> named rollup branch -> PR to test ->
  separately requested promotion to main.

Root guidance must require the global `pr-to-test` skill with the local
`docs/workflows/pr-to-test.md` and `scripts/pr-to-test.sh` through checks, merge,
and verified test delivery. A parent with multiple executable children uses
one named `orca/` rollup branch from fresh `origin/test`, recorded in its
approved specification: reviewed feature PRs with targeted checks merge into it
with merge commits, then one final rollup PR follows the canonical route. A child can close
after verified rollup integration; the parent closes only after final verified
test delivery. A one-child parent defaults to direct delivery, and early test delivery from
a rollup needs an explicit operator decision. Shared [rollup delivery](../skills/pr-to-test/ROLLUP.md)
owns detailed branch and CI rules. Direct commits or pushes to `test` and
protection bypasses are not delivery alternatives. Separately requested promotion
uses the global `promote-to-main` skill, `docs/workflows/promote-to-main.md`, and
`scripts/promote-to-main.sh` from the clean primary `test` checkout, completing
verification and main-to-test synchronization.

Protect `test` and `main`: require a pull request, the target's full CI check or
checks and up-to-date branches; disable force pushes and deletions; and turn on
"Do not allow bypassing the above settings". Approvals follow the target's review
policy, defaulting to none. Drastic recovery is a deliberate, one-time disable of
the no-bypass setting, re-enabled afterwards. Agents usually lack admin, so
adoption gives the owner these exact settings and a readback of
`gh api repos/<owner>/<repo>/branches/<branch>/protection` for each branch:
`required_pull_request_reviews` present, `required_status_checks.strict` true with
the full CI contexts, `allow_force_pushes` and `allow_deletions` disabled, and
`enforce_admins` enabled. The outcome is complete only after the owner confirms it.
Already-adopted targets adopt it at their next Standards Upgrade.

The PR-to-test script catches up by merging the latest `test` into the task branch
before the first push and whenever `test` moves during its wait. It bounds
catch-ups and waits, with limits chosen and recorded in the target runbook, stops
on conflict with the branch unchanged, and never bypasses protection.

Root guidance must direct agents to `cleanup-task-artifacts` before launching
temporary compute to establish ownership and teardown, and before reporting at
major phase boundaries: completed validation/proof, verified delivery/promotion,
substantial phase end, failure/waiting, and final handoff. The skill owns the
resource and retention policy; phase cleanup does not end an incomplete task or
detach its checkout.

Adoption and upgrades establish these outcomes in both the actual checkout layout
and root guidance. If required branches are absent, establish them from the target
repository's intended baseline; resolve ambiguous history before changing refs.
An empty repository needs an initial baseline before feature worktrees and PRs can
be used. This setup does not authorize product changes directly on `test`.
Missing canonical scripts are part of adoption/upgrade scope: implement the real
local entry points and runbooks before claiming completion. During ordinary work,
root guidance must instead direct agents to check for duplicates, file an
implementation issue for a missing script, and report the delivery blocker rather
than invent an alternate flow. Preserve active/attached worktrees; unresolved
checkout conflicts or missing delivery prerequisites mean adoption is incomplete.

## Delivery and versions

Shared human-invoked skills read the fixed local runbooks and call the repository's
fixed scripts. Ordinary toolchain and operational differences belong locally; do
not fork shared skills, duplicate machine model/role configuration, or add a plugin
framework. Thin wrappers are sufficient; implement the actual happy path and return
unexpected conditions to the supervising agent with partial effects visible.

Use merge commits for task-to-test, test-to-main, and main-to-test synchronization.
Review every submitted change; reuse prior evidence only when it covers all changes
and findings are resolved or explicitly accepted. No review ledger is required.
Completion means the local runbook's verified result, including real deployment or
processing when applicable. Close delivered work at that point under the
global closure rule: unexercised
scenarios requiring future use are reported limits, not open-issue gates, while observed
failures and unfinished requested effects stay actionable. Verified rollup
integration permits the next eligible child; final verified test delivery
completes its parent. Promotion is separately
requested. Do not make promotion a per-task gate.

Use semver:major, semver:minor, semver:patch, and semver:none labels. Classify
delivered behavior through the shared
[Version classification](../skills/pr-to-test/SKILL.md#version-classification)
guidance and the repository's explicit compatibility policy. Count each
applicable direct-delivery PR or final rollup PR once in deterministic merge
order. A rollup's one contribution reflects its combined delivered change;
feature-integration PRs contribute none. Synchronization contributes none;
promotion wrappers do not recount component changes. All-none promotion keeps the
existing version without a new tag. Use existing tags and Git/GitHub evidence,
never a ledger.

Bookkeeping is advisory: resolve routine missing/conflicting labels from the actual
change, otherwise report uncertainty without guessing a version or moving tags.
Version metadata cannot waive real application/delivery gates or invent an artificial
blocker. A real artifact pipeline's version prerequisite and initial version are
local runbook decisions.

Use `cleanup-task-artifacts` at the required phase boundaries. Its policy governs
safe task-resource cleanup and retention; daily cleanup adds no authority beyond it.
Automatic archival also requires proven completion, unpinned/inactive state, and
more than seven days since an observed last turn. Missing evidence means skip.
