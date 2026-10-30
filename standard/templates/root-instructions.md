# Root AGENTS.md outline

Adapt this outline to the actual repository. Replace descriptive placeholders;
do not publish a placeholder declaration or duplicate machine-level settings.

```markdown
# <Repository name>

<Repository-specific purpose, scope, and invariants.>

- For issue tracking and handoffs, use docs/agents/issue-tracker.md.
- For domain terminology and decisions, use docs/agents/domain.md.
- For implementation and verification, use docs/development.md for the actual
  environment, Application Code/Tooling classification, checks, and verification
  evidence reuse.

## Visibility and publication

<Record verified current public/private visibility, separately from future intent.
For public targets, link the repository-owned public-work policy and approved
license. Private preparation may use an explicitly approved public-work policy.
Resolve unknown or conflicting state; replace this placeholder with actual guidance.>

Follow the applicable repository publication policy before GitHub writes,
including source, metadata and evidence. Changes to visibility or licensing require
the owner's explicit authorization.

## Languages and environments

<Declare the approved language, runtime, build/package toolchain, and
execution/deployment environment for each existing component, such as CLI, app,
server, or Tooling. Omit absent components
and replace this placeholder with actual choices or a direct authoritative link.>

Use each component's approved environment. Adding a language, runtime, build/
package toolchain, or execution/deployment environment requires explicit user
authorization, including for helpers and tooling; a feature request does not
imply it. Prefer the same existing language
across components where practical. Preserve established code; this preference does
not authorize a migration or rewrite.

## Checkouts and delivery

Keep the primary local checkout on `test`, refreshed from `origin/test` by
fast-forward only when clean. Reserve `test` for that checkout; never check it out
in a linked worktree. Make all changes on `orca/` feature branches in separate
worktrees. Direct-delivery branches and implementation rollups start from fresh
`origin/test`; rollup child branches start from the current rollup. Preserve local work and attached checkouts
before switching or updating. Detached revision worktrees are valid for verification.
On each host, Orca's default base ref for this repository is `origin/test`: set it
with `orca repo set-base-ref` and read back `worktreeBaseRef` from `orca repo show`.

Multi-ticket implementation parents use reviewed child PRs with targeted tests and
validation into their recorded rollup branch, then one final PR to `test` with
full CI. Verified rollup integration permits child closure and continuation;
parent closure requires the
combined verified test delivery. Single-ticket work defaults to direct delivery.
Full CI runs only at PR-to-test and/or separately requested promotion, with
equivalent full evidence reusable under local policy. Follow the local runbook's
rollup integration path and actual CI/deployment gates.

Use the global `pr-to-test` skill with `docs/workflows/pr-to-test.md` and invoke
`scripts/pr-to-test.sh` through checks, merge, and verified test delivery, including
for documentation and small fixes. Do not commit or push changes directly to
`test` or bypass branch protections.

Promote only on a separate explicit user request. Use the global `promote-to-main`
skill with `docs/workflows/promote-to-main.md` and invoke
`scripts/promote-to-main.sh` from the clean primary `test` checkout through
verification and main-to-test synchronization. If either canonical script is
missing, check for duplicates, file an implementation issue in this repository,
and report the delivery blocker instead of inventing an alternate flow.

## Repository Standard

- Source: https://github.com/jdip/orca-pod
- Revision: <full adopted commit SHA>
```

Retain only guidance justified by current needs after the selected standard's
guidance-retirement assessment. Use the actual selected source revision and ship
its declaration with the adoption/upgrade implementation. The source repository's
scripts and runbooks are a small working example in its own Python Tooling; build
the [targeted/full split](../../skills/pr-to-test/ROLLUP.md#establish-the-delivery-boundary)
and privacy check in the target's approved Tooling language, and adapt actual
application gates, evidence equivalence and deployment effects locally rather than
importing assumptions.
