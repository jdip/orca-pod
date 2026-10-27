# Orca Pod

Orca Pod maintains the portable, Orca-native AI development setup: skills,
workflows, a Claude and Codex role roster, a repository standard and the host
installer. Skills live under `skills/`.

The canonical GitHub repository is public and is intended to remain public.
Changing visibility or licensing requires explicit owner approval.

Before repository or GitHub writes, follow the
[public-work policy](SECURITY.md#public-repository-work), including outgoing
metadata, logs and attachments.

Work is tracked in GitHub Issues; follow [tracker guidance](docs/agents/issue-tracker.md).
Read [domain guidance](docs/agents/domain.md) before exploring domain terminology.
Follow [development guidance](docs/development.md) for verification.

Classify this repository's skills, roster, installer and delivery helpers as
Tooling. Validate through the small source syntax check and available behavioral
evidence; do not create coverage suites, fake machines, fake environments or
release state machinery. Preserve credentials, unrelated machine state, local
work, and worktrees still backing live Orca agents.

## Languages and environments

Tooling logic uses Python 3.11+ with the standard library only. One named
exception: the `engineering-brief` renderer installs its hash-pinned
Python-Markdown (`skills/engineering-brief/requirements.txt`) into a skill-owned
virtual environment in its private local archive, never globally or through
`machine/install.py`. Bash is accepted
for canonical shell entry points and existing shell helpers; prefer Python for
new logic. Keep this toolchain cohesive. Adding another language, runtime,
build/package toolchain, dependency, or execution/deployment environment
requires explicit user authorization, including JavaScript/Node helpers.
Application, CLI product, and server stacks are not established here; selecting
one requires explicit authorization. See docs/development.md for runtime
requirements. This policy does not authorize rewriting existing tools.

## Checkouts and delivery

Keep the primary local checkout on `test`, refreshed from `origin/test` by
fast-forward only when clean. Reserve the `test` branch for that checkout; never
check it out in a linked worktree. Make all changes on `orca/` feature branches
in separate Orca worktrees. Direct-delivery branches and implementation rollups
start from fresh `origin/test`; rollup child branches start from the current
rollup. Preserve existing local work before switching or updating a checkout.
Detached revision worktrees remain valid for the canonical scripts' verification.

Multi-ticket implementation parents use reviewed child PRs with targeted checks
into their recorded rollup branch, then one final PR to `test` with full CI;
child integration permits continuation, and parent closure requires verified
test delivery. Single-ticket work defaults to direct delivery. Full CI runs only
at PR-to-test and/or separately requested promotion, with equivalent full
evidence reusable under local policy. Follow the rollup path in the local
runbook.

Deliver test-bound changes with the `pr-to-test` skill and the local
[PR-to-test runbook](docs/workflows/pr-to-test.md), invoking
`scripts/pr-to-test.sh` through checks, merge, and verified test delivery.
Use this path even for documentation or small fixes; do not commit or push changes
directly to `test` or bypass branch protections.

Promote only on a separate explicit user request, using the `promote-to-main`
skill and local [promotion runbook](docs/workflows/promote-to-main.md).
Invoke `scripts/promote-to-main.sh` from the clean primary `test` checkout and
complete its verification and main-to-test synchronization. If either canonical
script is missing, check for duplicates and file an implementation issue in this
repository; report the delivery blocker instead of inventing an alternate flow.
