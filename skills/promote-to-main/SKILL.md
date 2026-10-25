---
name: promote-to-main
description: Promote verified test work through the repository’s canonical main promotion and synchronization workflow when explicitly requested.
disable-model-invocation: true
---

# Promote to Main

Before any GitHub write, follow the target repository's applicable publication
policy for outgoing source, metadata and evidence. Inspect approved commit identity
and verify platform-created merge metadata after delivery; report any mismatch.

Require the human's separate promotion request. Implementation, adoption, upgrade,
or successful test delivery alone does not authorize promotion. Preserve the
request's repository, environment, and intended test revision.

Read AGENTS.md, `docs/workflows/promote-to-main.md`, and relevant test-delivery and
review evidence. Use `scripts/promote-to-main.sh` with that runbook's arguments.
Investigate absent or contradictory local guidance; do not invent a release process.
Prepare the intended clean checkout while preserving unrelated work. Review any
submitted changes not covered by sufficient completed review evidence.

Follow actual gates and effects through verification, including deployment,
signing, processing, and user-visible behavior only where the local runbook
requires them. Use merge commits for test-to-main and required main-to-test sync.
Check the intended revisions and investigate drift before including changed scope.

Review task contributions against [Version classification](../pr-to-test/SKILL.md#version-classification)
and the actual delivered changes, resolving routine misclassification before
calculating the promotion version.

Versioning uses each applicable task PR once in merge order: major/minor/patch/none,
with normal resets. Sync contributes none; promotion wrappers do not recount task
changes. All-none retains the version without a new tag. Resolve routine metadata
from evidence; otherwise report uncertainty without fabricating a version, moving
a tag, or turning bookkeeping into an artificial gate. A real artifact pipeline's
version prerequisite remains a genuine prerequisite defined locally.

Inspect actual partial effects after failures before recovering. Do not blindly
replay publication or treat script launch as completion. Continue independent
work. Before pausing or reporting a failure, use `cleanup-task-artifacts` with
local guidance. The promotion authority covers this phase cleanup; preserve the
current task environment and resources needed by a pending gate. Then batch ready
intent-dependent decisions with concrete recommendations. Honor external
approval/processing gates and report them pending until satisfied.

After the locally defined promotion and synchronization results are verified,
use `cleanup-task-artifacts` with local guidance before tracker bookkeeping or
final reporting. Follow its resource and retention policy, then finish tracker
bookkeeping. Report verified results, exact tags actually published, partial
failures, and retained resources.

If the cleanup package is unavailable, use local artifact guidance to stop/remove
only exact task-owned resources proven safe for that action. Preserve active,
shared, uncertain or needed state and attached checkouts; use supported lifecycle
tools. Report the unavailable policy and actual cleanup limits.
