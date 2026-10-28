# Promote to main

Before GitHub writes, follow the [public-work policy](../../SECURITY.md#public-repository-work)
for outgoing source, metadata and evidence, including approved commit identity.
The script verifies the merge author; inspect that result and the remaining
platform-created metadata against the policy after delivery.

Run only on a separate explicit promotion request. Issue implementation,
including next-issue's continue mode, does not request promotion. Use a clean
checkout of the intended origin/test revision, preserving existing task
checkouts and unrelated work.
Requirements are the same Git/gh/Bash/Python 3.11+ tools as PR-to-test. Read actual
review and test-delivery evidence; review any changes not covered by it.

Run scripts/promote-to-main.sh, optionally supplying --title and --body-file.
It fetches origin, runs the local Git-index privacy gate, snapshots
intended test and main, creates/reuses the test-to-main PR, requires its current
checks, merges the intended head with a merge commit, and verifies the merge's
parents and tree against the integration its passing Validate run tested. It then
creates/reuses a semver:none main-to-test synchronization PR, requires checks,
merges with a merge commit, and attributes that merge the same way. An unchanged
tree and source-check runtime use successful prior integration evidence in the
current Validate job rather than a repeated suite; changed or unproven inputs need validation, and failing
current checks block. Only full Validate runs qualify; rollup children's Targeted
checks runs never do, so without equivalent Validate evidence the full check runs. Branch drift stops for investigation. No deployment, signing,
notarization, or application runtime exists in this repository; do not invent
those completion requirements.

The version baseline is the highest vMAJOR.MINOR.PATCH tag published on origin,
lightweight or annotated (peeled to its commit), that is reachable from the previous
main; local-only tags are ignored. Contributions are canonical task PR merge commits
on test's first-parent history after that tagged commit, oldest first. Each counts
once, including PRs an earlier untagged promotion already carried to main; ancestry
of the tagged main merge excludes what it already versioned. Main-to-test
synchronization wrappers are skipped, and promotion PRs and rollup child integrations
never appear on that history. Apply each major/minor/patch/none label sequentially
to the baseline. All-none makes no new tag. There is no fabricated initial version:
without a baseline, classify incoming PRs since the previous main solely to decide
whether an initial version is needed. If a bump is needed, report unresolved
bookkeeping and ask for that initial version after completing independent authorized work.

A resulting tag is created on the verified main merge and pushed without moving
existing tags. Shallow history, a first-parent test commit without exactly one
merged test PR, missing/conflicting labels, unavailable metadata, or tag failures
are reported as incomplete bookkeeping rather than a guessed version, bypassed real
gates or blocked source delivery. The agent resolves routine label questions from
evidence; do not claim a tag was published without readback. Any future artifact pipeline that
requires a version must document that real prerequisite here before use.

The script is linear. Failures leave actual partial effects for the supervising
agent: inspect PR state, exact branch SHAs, checks, and local/remote tags before
recovery. Never blindly rerun after a merge. Complete remaining already-authorized
steps directly when their state is established. Do not add a journal, rollback
engine, release-state PR, or automatic main promotion.

Complete only after both merged revisions' parents and attributable checks are verified.
Finish safe cleanup as in PR-to-test, retaining attached/shared/uncertain checkouts.
Promotion runtime verification requires an actual promotion request; syntax or
read-only version inspection does not claim a live promotion succeeded.
