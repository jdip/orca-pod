# Implementation rollups

Read for a parent using rollup delivery, including resuming an all-closed child
list whose parent still awaits test delivery. `next-issue` owns child execution;
`pr-to-test` owns final delivery. The planning map remains a separate design record
and closes at its normal handoff before implementation.

## Establish the delivery boundary

Multi-ticket implementation parents use one rollup; single-ticket parents
default to direct PR-to-test. Record the mode, exact repository and named `orca/`
rollup branch in the approved specification. Reuse an established mode on resume;
do not silently convert an active backlog because its remaining child count changed.
Early test delivery or a change to an approved delivery boundary requires an
explicit operator decision recorded in the existing specification.

The parent owns aggregate acceptance, full CI and test deployment. Child acceptance
covers reviewed integration and targeted tests/validation; deployment-dependent
acceptance remains explicit on the parent. Preserve named workflow exceptions,
such as a preparation child ending at a local handoff. Never close an unmet child
requirement merely to unblock another ticket.

Read the local delivery runbook's feature-to-rollup path, including actual required
checks and deployment triggers. Child checks cover changed behavior and affected
integration paths only, with mandatory privacy checks, proportionate Tooling
checks and available behavioral evidence. Full suites belong to the final PR to
test and separately requested promotion,
with equivalent full evidence reusable under the target's verification policy.
Keep targeted and full results distinguishable; targeted evidence cannot satisfy
full delivery acceptance.

Confirm rollup pushes and child PRs cannot deploy to test or launch full CI before
publishing them. Align conflicting CI triggers, required-check configuration and
runbook obligations within authorized scope, or report the concrete blocker.
Never bypass protection, substitute a full-suite fallback for missing targeted
checks, or count cancelled/skipped full runs as successful evidence. A branch name,
a missing check or an unprotected rollup is not proof of success; require the actual
checks even when hosting rules do not enforce them. Missing or conflicting local
mechanisms need investigation before mutation, not an invented delivery framework.

Create the rollup from fresh `origin/test`, preserving existing worktrees. Record
its initial revision and owning parent in the parent issue. Resolve existing remote
and local refs before reuse; matching names alone do not establish ownership.
After confirming the remote ref is absent, push the initial rollup without force,
fetch it back and verify its SHA against the intended baseline before any child PR.
For an existing owned rollup, fetch and verify its recorded history instead of
reinitializing it. Record the remote branch and verified revision on the parent.
Start each child's isolated feature branch from the current fetched rollup. Keep
claims, the scoped selection binding and the whole-map Design gate in force.

## Integrate a child

1. Implement and verify the child under `next-issue`. Review its complete diff
   against the intended rollup base and satisfy the targeted local/CI checks.
   Preserve required user/hosted reviews; agent review does not waive them.
2. Push the feature branch and create or reuse its PR with the exact rollup base.
   Link the child and parent without auto-closing the parent. The local runbook
   supplies a native Git/forge path or its existing helper; the test-delivery script
   is reserved for the completed rollup.
3. Require the actual current targeted PR checks to register and pass. Recheck
   head, base, draft/review state and merge readiness before a merge commit pinned to the
   intended head. Serialize integrations within the parent. If the rollup changes,
   update the feature through normal merging and repeat affected review/targeted checks;
   do not reuse evidence for a different integration tree.
4. Fetch and verify the merge commit, its intended parents and its reachability in
   the recorded rollup. Attribute the PR's passing targeted integration run to the merge
   through the local runbook's provenance check; a merge whose parents or tree
   differ from the tested integration needs fresh targeted validation. Recheck
   ownership and design, then record PR/review/check evidence and close the child
   only when its integration acceptance is met. State that test delivery is pending
   on the parent. This permits dependent children to proceed.

No child contribution is counted toward the test version independently. Labels on
integration PRs are not release events. Keep the rollup and any needed evidence
until aggregate delivery; apply `cleanup-task-artifacts` to proven disposable child
resources without removing attached/shared checkouts.

## Complete the implementation parent

The executor finishing the last child, or resuming the undelivered parent, performs
this work under existing implementation authority. It is part of parent completion,
not a new ticket or permission request. Record the final-delivery owner in the
existing parent evidence and check for concurrent work before merging. A paused
owner must hand off through the existing selection/claim rules.

Recheck the selection binding and Design gate, every child's acceptance and PR
integration evidence, and the parent's full outcome. Verify all required child
commits remain in the rollup; closed issues alone are insufficient. An explicitly
accepted workflow exception needs its own completion evidence. Preserve separate
scope decisions rather than silently excluding unfinished work.

Fetch current test. Merge any new test changes into the rollup using ordinary merge
commits; investigate conflicts, review resolutions and repeat affected checks. Review
aggregate behavior and the complete test-bound diff, reusing child reviews only
where they cover the final result. Resolve target drift through the local runbook.

Classify the combined change once through `pr-to-test`'s Version classification.
Invoke the canonical `scripts/pr-to-test.sh` from the completed named rollup branch
with the local runbook's arguments and authoritative full CI for the combined
change. Verify the exact merged revision and actual test deployment/processing
where applicable. Only this rollup-to-test PR contributes to
version arithmetic; child PRs are not counted again. This does not promote main.

Record the final PR, merged revision and aggregate acceptance evidence on the parent,
then clean proven-owned resources and close the implementation parent. When delivery
fails, keep it open and preserve the rollup. Inspect actual partial effects before
recovery: after a successful merge, complete missing verification/bookkeeping without
opening a duplicate PR. Completed integration children stay closed unless their own
acceptance is invalidated. A reopened design still pauses associated implementation.
