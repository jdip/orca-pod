---
name: standards-upgrade
description: Upgrade an adopted repository from its recorded Repository Standard revision to the selected source revision.
disable-model-invocation: true
---

# Standards Upgrade

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

Read the target repository's root AGENTS.md and its single Repository Standard
Source/Revision declaration. If absent, use Repository Adoption. Investigate a
malformed, ambiguous, inaccessible, or wrong-source declaration rather than guessing
an adopted SHA. Preserve unrelated work and existing product behavior.

Resolve the recorded source repository and the full adopted commit. For an ordinary
upgrade, resolve that source's default-branch HEAD; honor an explicitly requested
revision instead. Select and report one concrete target commit. Do not silently
use the current source branch (host installation through `machine/install.py`
has a different selection rule; see `docs/install.md`), stale content, or another
repository. Verify both revisions are from the
recorded source before comparing them.

Read the target standard and compare the relevant adopted-to-target source changes.
Apply its Target assessment and planning and Guidance retirement outcomes to the
actual repository, including inherited process outside the source delta. Read any
supplied preparation handoff; otherwise search the target tracker, including closed
handoffs and comments, for matching target/workflow/baseline and branch ancestry.
Reuse its findings and map/spec links within current authority. Inaccessible or
ambiguous evidence stays unresolved rather than being treated as absent.

Resolve the target-owned Wayfinder plan and approved specification from that
assessment and the upgrade's goals. Reuse covering decisions; plan changes,
including executable verification alignment, prerequisites, explicit blockers and
delivery evidence for this target. Recheck state
and plan coverage before applying the delta, preserving justified customizations. Do not overwrite local files wholesale or
build a migration engine/compatibility matrix. When replacing a mechanism, migrate
callers and remove obsolete code/configuration within scope rather than accumulating
shims. If the outcome already holds, avoid gratuitous implementation changes.

Use `define-project-goal` to establish the project purpose with the human operator.
Reuse a clear existing blurb; include approved purpose edits at the top of every
root README in this workflow's own change and delivery. The skill owns the
conversation and wording; return here afterward to complete the upgrade.

Use `dependabot-upkeep` to establish the selected standard's alert-only protection
outcome on the actual target. Pass the alignment setup authority, repository,
dependency surfaces and delivery rules. Verify settings, active alert coverage and
remaining PR-generation behavior, or report the exact unresolved capability.
Return here for upgrade delivery.

Use `repository-verification` for its suitability assessment during normal
inspection. Report its include/omit/defer recommendation with the other ready
decisions; run setup only within explicit opt-in, reusing existing consent. Return
here for this workflow's delivery; existing verification opt-in does not require a new guide.

Apply the selected standard's Claude guidance bridge contract to root and applicable
nested repository-owned guidance.

Apply the target standard's checkout and delivery requirements to the actual
repository and root guidance, including the upgrade's own feature worktree.
Establish missing prerequisites within upgrade scope; preserve active checkouts
and report unresolved conflicts rather than declaring adoption from text alone.

Reassess the Application Code/Tooling mapping and actual gates. Apply the selected
standard's Validation and adoption and Verification evidence outcomes to the
target's actual workflows, CI, scripts, tests and fixtures in this upgrade change,
verifying them through proportionate native checks and available authorized
behavioral evidence. Report unexercised future-use scenarios as limits under the
standard's closure policy. The upgrade is complete
only when guidance and executable controls agree; an unresolved design,
authorization or capability blocker keeps it explicitly incomplete. Record
unrelated application coverage gaps in scoped, deduplicated issues.

Complete independent work and batch substantive conflict decisions with concrete
recommendations. Preserve unanswered decisions; do not assume intent or publish a
local preference as a source-standard change without that authorization.

Update the existing Source/Revision declaration to the selected full target SHA
in the same upgrade PR. Use shared `pr-to-test`, with sufficient review of every
submitted change and the local runbook's actual completion evidence. Finish issue
bookkeeping and safe cleanup without orphaning Codex-attached checkouts. Report
verified delivery, remaining remediation, and retained artifacts. Do not promote
main or require promotion before progressing unless separately requested.
