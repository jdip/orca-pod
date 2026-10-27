# Development and verification

Orca Pod's `skills/` packages, `roster/` definitions and generator, `machine/`
installer, and `scripts/` delivery helpers are Tooling: they maintain machines and
repositories. There is no separate application, server, or deployable product
runtime here. Classify future code by purpose rather than its language.

Requirements: Git, authenticated `gh` for this repository, Bash, and Python 3.11+.
Orca Pod supports macOS hosts; CI runs the same checks on Linux.
Set `ORCA_POD_PYTHON` to select the interpreter when the host's `python3` is
older, for example `ORCA_POD_PYTHON="$(uv python find 3.13)"` on macOS. CI uses 3.12.

Stage intended changes, then run `python3 scripts/check_secrets.py` for the
mandatory pre-push Git-index privacy check (see [SECURITY.md](../SECURITY.md)).
`scripts/check.sh` adds native Python/TOML/shell syntax checks of every relevant
file under `skills/`, `machine/`, `scripts/` and `roster/` for full delivery
validation. `scripts/check.sh --base <commit>` is the targeted form: it checks
only committed source files HEAD adds or modifies since that commit, plus
`git diff --check`, and suits a rollup child, for example
`--base "$(git merge-base HEAD "origin/$rollup")"`. Use `git diff --check` for the
actual change. Exercise each changed helper's authorized operation where
practical; report unexercised scenarios as verification limits.

Hosted CI has two scopes. Validate (`validate.yml`) is the authoritative full source
check for delivery PRs into test and main, run once per pull-request integration;
an unchanged promotion or sync can reuse its prior integration's successful
Validate run when the source tree, runner image and Python version match. PRs into
any other base, such as rollup children, run Targeted checks (`rollup.yml`) on the
synthetic merge instead: after proving its parents are the PR's base and head, the
`targeted` job runs the targeted form against that base, then the privacy check.
Targeted runs never count as Validate evidence, so a completed rollup's PR to test
gets full Validate.
The delivery scripts attribute the current run to each merge by its tested parents
and tree; a changed or unproven merge needs fresh evidence at its applicable scope:
targeted for a child, full for delivery. Source parsing is not evidence of a
working install, a deployment, or successful promotion; those need real runs,
such as an installer run on a host or a real `worker-start` round trip.
Do not fabricate machine homes, forge services, orchestration tests, or coverage
apparatus for Tooling. Reported real failures drive concrete fixes.

Application Code, if introduced, requires rigorous linting, type checking,
validation, and meaningful tests with high coverage across its behavior and failure
paths. Choose and enforce the actual stack's gates and justified coverage targets
when that code exists. No stack, package manager, CI matrix, or numeric floor is
invented in anticipation of a product.
