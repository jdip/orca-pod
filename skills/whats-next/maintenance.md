# Maintenance and alignment

Use this branch when dependency upkeep, hygiene, adopted repository verification
or Orca Pod alignment is a plausible next action. Before any implementation,
apply the coordinator's Plan the selected change step; assessment consent and a
small cleanup batch do not waive map/spec coverage. Pass covering plans to the
named owner, using the existing executor for approved child claims and
resolution. Consider missing assessment history, relevant changes since earlier
evidence, and visible friction. Inspect enough to make a useful proposal with
rough effort; compare it with other candidates instead of performing a full
audit to rank them. Age, missing history, and a newer standard revision are
signals, not proof of a defect. Reuse existing findings and keep/defer decisions
unless evidence changes.

## Outcome assessment

For a selected improvement or explicitly authorized target sample, name the
accepted target behavior and inspect available issue, PR, check and runtime
evidence. Choose a relevant subset of accepted results, escaped defects,
reversions and user friction. For cycle time, identify the measured endpoints;
issue/PR elapsed time is not implementation effort. Use measured cost when
available and leave unsupported values unknown. PR volume measures activity.

Record the inspected baseline, supporting evidence, unassessed scope and a
keep/defer/change recommendation in the existing task or issue. Compare expected
benefit and rough effort with other candidates; a valid no-change outcome needs
no implementation. Reuse unchanged evidence and dispositions.

Distinguish maintained-source delivery, effective installation and actual target
acceptance. The target owns its purpose, signal definitions and checks. Use its
existing verification controls within their current authority; assessment alone
does not authorize driving a runtime, adoption or unrelated fixes.

When an authorized on-demand sample selects incident learning or missed patterns,
inspect its bounded outcome evidence, including relevant unflagged results, and
use [reflect's follow-through](../reflect/SKILL.md#record-and-follow-through) for
native proof and deduplicated local/shared disposition.

## Establish a stable baseline

Get active code tasks, implementation PRs, and unfinished local code changes through
verified delivery to `test` before hygiene, verification audits or intrusive
alignment assessment/changes.
Preserve others' active work; do not take over just to clear this gate. Old parked
branches do not automatically block an assessment. A quick declaration/status read
can still identify alignment as a future candidate while code is moving.

A greenfield or unadopted repository may lack `test` and delivery tooling. Establish
its actual stable starting state and use the adoption owner's baseline/bootstrap
rules; do not require adoption's own outputs before it can start. Unfinished or
uncertain local work still needs preservation and resolution. This exception does
not make an in-flux codebase ready for hygiene.

## Dependency upkeep

Use [dependabot-upkeep](../dependabot-upkeep/SKILL.md#read-and-assess-alerts) to
read current open alerts with pagination during ordinary discovery. This lightweight
read precedes the stable-baseline gate; active code work does not hide alert intake.
Distinguish a successful empty result from disabled features, missing access or
unsupported coverage. Reuse current-pass evidence and refresh on the next pass.

Compare actionable alerts and protection gaps with ordinary work candidates.
Deduplicate against existing issues and PRs, respecting claims, native dependencies,
completion-first ranking and keep/defer decisions. Existing dependency PRs are work
to assess, not an expected output of GitHub automation. An urgent alert can justify
proposing a priority change; it does not authorize taking over another task.

Apply the stable-baseline gate before protection configuration changes or broad
upkeep. Existing remediation is implementation work: assess its ownership and actual
conflicts alongside other PRs instead of requiring it to finish before eligibility.

Hand the selected scope, alert/configuration/issue/PR evidence, delivery target and
existing authorization to `dependabot-upkeep`. It owns alert-only protection and
remediation through the repository's planning, dependency tooling, PR conventions,
review and delivery. Assessment is read-only; selected changes require covering
approval and plans. Keep dependency justification with `dependency-review`.

After the coherent upkeep step, return to ordinary selection with actual verification,
remaining alerts and pending default-branch delivery. Preserve existing deferrals
unless new evidence changes them; a quiet PR queue does not establish alert health.

## Hygiene

Use `codebase-hygiene` for the selected authorized assessment. It owns dependency
justification through `dependency-review`, including used packages, and structural
investigation. Valid keep/no-change outcomes are useful.

For proposed edits, present a concrete cleanup batch: changes, expected benefit,
rough effort, and material risks. Reuse consent already covering that batch;
otherwise obtain it before edits. The owner chains `code-simplification`, required
review, and verified test delivery. Return to the coordinator after the batch.

## Adopted repository verification

Check the root opt-in declaration and maintained guide before considering an audit.
For adopters, use prior issue/PR/task evidence, relevant behavior/control churn and
observed friction to propose a bounded audit alongside hygiene and alignment.
Missing history is a candidate signal; age alone does not require a run. Reuse a
recent unchanged assessment, and avoid a full audit just to rank candidates.
Repositories without opt-in have no audit obligation; suitability belongs to the
adoption/upgrade assessment below.

For the selected authorized audit, use `repository-verification` with the scope,
stable baseline and existing evidence. It owns actual execution, drift correction,
regression filing and delivery. Reuse existing edit authority; an assessment alone
does not approve unrelated changes. Return here after the result and record it in
the existing task/issue/PR, without a new ledger. Reconsider at later meaningful
completion boundaries when evidence changes; do not create a background schedule.

## Orca Pod alignment

Inspect the repository's actual guidance/workflow state and Repository Standard
Source/Revision declaration. Distinguish absent from malformed, conflicting, or
inaccessible evidence; investigate uncertainty rather than guessing adoption status.
Route by actual state:

- No declaration and no established product behavior/workflows: `greenfield-init`.
- No declaration with established product behavior/workflows: `brownfield-adoption`.
- Valid declaration: `standards-upgrade` for relevant alignment changes.

Use the selected owner first for read-only target assessment and resolve one exact
source baseline under its rules.
Honor an explicit revision; ordinary upgrades use the recorded source's default
branch, not the current Orca Pod working branch. Compare relevant changes and
actual repository outcomes; a declaration in an undelivered branch is only an
intended target. A current, aligned repository needs no change.

Before implementation, conduct or resume the target-owned Wayfinder session using
the assessment and the selected workflow's goals. Follow the selected standard's
Target assessment and planning outcome through a resolved map and approved spec.
Reuse covering plans; if the target tracker is unavailable, continue conversational
planning and resolve artifact location before implementation.

Carry established authorization into the concrete
proposed alignment work: target, selected baseline, changes, benefit, rough effort,
and material risks. An assessment request alone is insufficient. Carry existing
approval through the appropriate owner, including `define-project-goal` for concise
root README purpose. Preserve local constraints and separately required environment
choices. The adoption/upgrade owner performs review and verified delivery, after
which the coordinator refreshes.

If obsolete or conflicting guidance requires `prepare-repository`, resolve its explicit target
and preparation scope first. That owner edits guidance and ends at a local branch
handoff; it is not a read-only scan or adoption itself. Complete independent work
before presenting needed preparation and subsequent adoption/upgrade approvals,
which may be granted together for a concrete proposal. Reuse an existing matching
preparation handoff. If the current host/session cannot satisfy that owner's
boundary, preserve the affected work and report the actionable handoff rather than
silently taking another role or creating a task. Return here after authorized
preparation and continue only the approved downstream work.
