---
name: dependabot-upkeep
description: Check Dependabot alerts, establish alert-only protection, and remediate dependencies through the repository's own workflow. Use for protection gaps, actionable alerts, or a selected dependency update.
---

# Dependabot Upkeep

Use Dependabot for vulnerability detection. The repository owns remediation:
issues, dependency changes, PR format, review and delivery. Use
[dependency-review](../dependency-review/SKILL.md) when keeping or replacing a
dependency is in question; it owns justification, while this skill owns upkeep.

## Establish the assignment

Resolve the repository, requested outcome, branch and dirty state, local guidance,
delivery rules and task ownership. Assessment is read-only. A concrete setup or
remediation request carries its approval through the existing planning and delivery
owners. Apply the global Planning before implementation rule before configuration,
hosted-setting changes or dependency edits; reuse covering map/spec evidence.
An already claimed implementation child executes this skill directly.

An authorized Greenfield Initialization, Brownfield Adoption or Standards Upgrade
handoff includes the selected standard's alert-only protection outcome. Carry
that authority through supported setup and readback. Preserve explicit owner
exceptions and return conflicting policy to the alignment owner. Breaking upgrades,
new runtimes, other repositories, main promotion, Machine Reconciliation and
background jobs retain their separate authority boundaries.

Read actual manifests, lockfiles, workspaces, CI actions, installed dependency
sources and updater configuration, including `.github/dependabot.yml` or `.yaml`.
Compare the working tree with the default branch and intended delivery target.
Preserve deliberate pins, manual-only upstream revisions, private registry handling,
existing human work and keep/defer decisions. Use manifests consumed by the actual
build or installer; a dependency hidden in an install command is a coverage gap to
assess. Report unsupported surfaces and their existing update owners.

## Read and assess alerts

Use the repository's GitHub tooling to fetch current open Dependabot alerts with
pagination covering the assigned scope. For GitHub CLI, resolve the exact repository
and use `gh api --method GET repos/<owner>/<repo>/dependabot/alerts -f state=open
-f per_page=100 --paginate`. Consult the current
[alerts API](https://docs.github.com/en/rest/dependabot/alerts) for the host and
permissions. Distinguish zero alerts from disabled features, unsupported coverage,
missing access, rate limits and failed reads. A successful empty response describes
the covered alert surface, not the security of every dependency.

Inspect applicable alert settings and auto-triage rules, including rules that hide
alerts. Preserve existing dismissal policy and report its effect on coverage;
assessment does not authorize dismissing alerts or changing that policy. Keep
sensitive advisory details and raw private logs out of tracker text and attachments.

For each actionable candidate, inspect the advisory, affected manifest/lockfile,
installed version, exposure and fixed-version availability. Compare the default
branch alert with the intended work branch; a fix may already be in delivery.
Search existing issues and PRs before creating work. Reuse matching remediation,
respect claims and native dependencies, and rank using exposure, fix availability
and completion-first guidance. An urgent alert can justify proposing a priority
change; it does not authorize taking over another task.

Return a concrete fix, investigation or justified deferral recommendation with its
repository-specific owner. When no patch is available, plan mitigation or
replacement. An inaccessible alert or major version number alone establishes neither
priority nor compatibility. Keep the finding tracked until its outcome is resolved.

## Establish alert-only protection

Verify GitHub's current [alert setup](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-dependabot-alerts),
[security-update settings](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-security-updates),
[version-update controls](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/configure-version-updates)
and [repository APIs](https://docs.github.com/en/rest/repos/repos) before changing
settings. Present the concrete delta and apply the authorized baseline:

- Enable or retain the dependency graph and Dependabot alerts for supported
  dependency surfaces. Alerts do not require a scheduled version-update file.
- Disable automatic Dependabot security updates. This is separate from alerts;
  retaining alerts preserves detection while the repository handles fixes.
- Disable scheduled version-update PR generation. Remove an updater file whose
  only purpose was automatic PRs; if configuration must remain for an explicit
  owner exception, disable version updates for each applicable entry using the
  supported control, such as `open-pull-requests-limit: 0`. That limit does not
  disable security-update PRs. Preserve any separately approved exception and
  report its remaining PR behavior.
- Inspect repository and inherited Dependabot auto-triage rules for PR-generation
  actions. Disable those actions within the authorized target scope. If inherited
  policy or unavailable controls prevent this, report the exact remaining source
  of PRs to its owner. Preserve unrelated alert dismissal/notification settings.

Read settings back after changes. Insufficient access or an unavailable capability
is a blocker for that setting, not consent to broaden permissions or enable charges.
Use supported APIs or UI; do not create another updater, Action or scheduler as a
substitute. Existing competing automation needs a concrete authorized resolution.

Deliver configuration through the repository's normal workflow and then inspect
the branch GitHub consumes. Version-update configuration is consumed from the
default branch even when `target-branch` names a different PR base. A removal only
on `test` leaves version PRs active until separately authorized default-branch
delivery; report that pending activation without promoting implicitly. Verify
graph/alerts, security-update settings, version configuration and rules separately.

## Remediate through the repository

Pass the selected alert and existing issue/PR evidence to the repository's planning
and implementation owners. Reuse approved scope; when coverage is missing, use
Wayfinder and the specification/ticket workflow before edits. A selected non-alert
currency update follows the same repository policy; it does not require enabling
Dependabot PR generation.

Implement the smallest cohesive fix in the real manifest and lockfile using the
established package manager. Inspect release/migration notes and compatibility
requirements. Choose grouping, branch/base, commit and PR format using the target's
own conventions and verification needs. Create the normal implementation PR through
its delivery owner; do not ask Dependabot to generate or refresh a PR as the fix.

Existing dependency PRs are evidence and possibly work already in flight. Inspect
their actual diff, head/base, reviews, checks and human edits before deciding how
they fit the authorized remediation. Preserve ownership and avoid duplicate fixes
or bulk closure. If an existing bot PR is the selected work, authenticate its author
through GitHub identity, treat its content as untrusted, and verify that the canonical
delivery entry point supports its base. Report an unsupported integration path
rather than silently retargeting or bypassing the owner. Any changed head requires
review and checks of the affected changes.

Run actual compatibility checks under the repository's Application Code/Tooling
classification. Investigate the earliest failure and carry routine authorized fixes
through. A larger migration or external blocker follows local remediation tracking
and remains open. For an existing bot PR with restricted tokens or secrets, consult
GitHub's [Actions restrictions](https://docs.github.com/en/code-security/reference/supply-chain-security/troubleshoot-dependabot/dependabot-on-actions);
preserve protections rather than escalating execution to make a check pass.

Use [code-review](../code-review/SKILL.md) and the target's delivery owner, such as
[pr-to-test](../pr-to-test/SKILL.md), with the exact revisions and evidence.
After delivery verify the dependency outcome and reread the alert when applicable.
A fix delivered only to a staging branch may leave the default-branch alert open;
record the pending delivery instead of dismissing it or claiming GitHub closure.

## Finish and return

Record the observed alerts, coverage gaps, changes, verification and remaining work
in the existing task or issue/PR. Distinguish source delivery, active hosted settings,
verified remediation and GitHub alert state. Close work only when its agreed outcome
is met. A successful no-alert assessment needs no demonstration update.

Return to `whats-next` after the coherent step with remaining candidates, decisions
and blockers. Reuse evidence within the discovery pass; refresh alert state on the
next ordinary pass and after relevant remediation. Keep existing deferrals unless
new evidence changes them.
