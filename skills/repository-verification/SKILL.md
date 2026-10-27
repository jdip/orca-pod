---
name: repository-verification
description: Assess suitability for optional repository verification during adoption or upgrade; create or audit repository-owned instructions within explicit opt-in and authorized scope.
---

# Repository Verification

Give the next agent a reusable way to exercise important real behavior and
inspect its result. This capability can serve UI, CLI, API, service or library
consumers. Use the requested assessment, setup or audit scope; discovery of a
possible need alone does not authorize adoption. Reuse established consent and
ordinary delivery authority. Apply the global Planning before implementation
rule before setup or drift edits; reuse the invoking workflow's map/spec.
Read-only assessment and already authorized real-use checks can inform planning
without creating another plan for those checks.

## Resolve the target

Read the repository's guidance, approved environment, development commands, current
work and existing verification instructions. A root `Repository verification`
section with a link to the maintained guide records adoption. Follow an equivalent
existing explicit declaration rather than creating a second owner. A file whose
name happens to contain verify is not evidence of opt-in.

Preserve active work and shared instances. Use an established stable baseline;
report unavailable runtime or access prerequisites rather than inventing evidence.
An audit requires adopted instructions. If none exist, report that and recommend
setup when useful; do not silently adopt the capability. An explicit setup request
supplies opt-in for its named repository.

## Assess suitability during adoption or upgrade

Use the normal repository inspection, existing controls/runbooks and concrete
verification friction; do not run a full audit merely to decide suitability.
Recommend **include** when a few reusable real-behavior instructions would fill a
useful gap, **omit** when current controls and guidance already suffice, or
**defer** when actual behavior or prerequisites are insufficient. Give the rationale,
rough effort and, for deferral, a concrete revisit condition. UI is not required.
For an existing adopter, assess whether its guide still serves the need and preserve
its declaration unless removal is explicitly authorized.

Return the recommendation to the adoption/upgrade owner to batch with its other
ready decisions. Inclusion needs explicit repository opt-in; reuse consent already
covering it. An approved adoption alone does not imply inclusion. With inclusion
authorized, follow setup below and return its verified result to the caller's
delivery flow. Omit/defer creates no guide, placeholder or audit obligation.

## Set up reusable instructions

Reuse sufficient existing guides and controls. Put missing instructions in a
repository-owned guide (normally `docs/verification/README.md`) or an existing
supported project-local skill. Add the root declaration and pointer in the same
change, identifying where future agents must maintain the instructions. Do not
replace an existing useful owner or generate a parallel inventory.

Choose a few valuable behaviors from actual routes, commands, APIs, public library
interfaces or repeated verification friction. For each, record consumer entry
points, prerequisites, the existing command/control path and observable success.
Use small linked feature files only when they make a growing guide easier to read.
Include these operational facts where they apply:

- Launch/build command, readiness signal, version or instance health check.
- Auth, seed-data and environment prerequisites without copying secrets.
- Isolation of ports, data and sessions; do not drive a shared instance concurrently.
- Exact actions and expected outcomes, including externally visible side effects.
- Where proof artifacts survive cleanup, and how to remove only state the run owns.

Use existing native tools and the approved runtime. Add a helper only for a
concrete repeated gap; document its invocation and exercise it. Do not introduce a
new runtime, a generic control framework or fake infrastructure. For libraries,
exercise the public consumer path rather than inventing a UI. Preserve real
external-action permissions; a verification label does not authorize live messages,
deletions or production writes.

Follow the resulting instructions on the actual repository where prerequisites
and authority permit: establish readiness, exercise selected behaviors, capture the action and resulting state,
check relevant side effects and verify that evidence remains available. When the
setup or proof phase completes or pauses, use `cleanup-task-artifacts` with local
guidance before reporting. Phase cleanup does not complete a continuing task or
detach its checkout. Fix instruction/control gaps within authorized scope and
repeat only affected proof. Unexecuted or unreachable instructions remain
unverified; name the missing prerequisite. Deliver guide changes under the global
Validation and delivery closure rule, reporting unexercised scenarios as limits.
If actual execution is itself the requested outcome, report any unfinished
operation explicitly rather than claiming it succeeded.

## Audit an adopted guide

Reuse prior evidence to choose the useful audit scope and report what remains
unassessed. For a full audit, cover every mapped behavior; a targeted audit covers
the selected behaviors and makes no whole-guide claim. Read relevant source changes
and check for important unmapped behavior before driving the real paths serially.
Use the guide's readiness, isolation, evidence and cleanup rules. Recheck health
and recover a known state after unexpected behavior before continuing to drive.
Before reporting a completed or paused audit phase, use `cleanup-task-artifacts`
with the guide's local guidance.

Distinguish stale instructions, working behavior the controls cannot reach, and a
product regression. Correct authorized guide/control drift at its owner and check
changed instructions with the available authorized behavioral evidence. File product regressions through the owning
tracker; never rewrite expected results to normalize broken behavior. An audit does
not authorize unrelated product fixes. Report blocked coverage and retain evidence.

## Deliver and maintain

Review and deliver authorized changes through the repository's canonical workflow.
Report assessed behaviors, evidence, corrections, issue links and unverified scope.
A clean audit needs no change or PR. Use an existing issue, PR or task record for
assessment evidence and baseline; do not add a run ledger or telemetry service.

The maintained guide must tell feature authors to update it alongside relevant
behavior changes, preserving the difference between drift and regressions.
Scheduling a background audit is a separate request.
