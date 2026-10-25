---
name: define-project-goal
description: Collaboratively define or refine a project's purpose with its human operator and record the agreed blurb at the top of root READMEs. Use when project direction is missing or unclear, or an adoption workflow needs its purpose established.
---

# Define Project Goal

Agree on the project's enduring purpose with the human operator. The artifact is
a concise blurb at the top of every root README, immediately below the project
title. It guides future choices; implementation scope and execution criteria
remain with their existing specifications and workflows.

## Establish purpose

Resolve the target repository and read its root READMEs, relevant project context,
and the operator's supplied direction. Root README variants describe the same
project; nested component READMEs are outside this repository-level assignment.
Use a clear existing purpose as the baseline. Reuse settled wording and answers;
a valid existing blurb can complete this step without edits or another interview.

When purpose is missing, unclear, conflicting, or the operator requests a change,
use `grilling` to work through the unresolved questions with the operator. Ground
options in available repository facts; ask what the project should serve rather
than inferring intent solely from what it happens to implement today. Batch
independent questions when useful and wait for the human's actual answers.

Draft a short paragraph, usually one to three sentences, describing who the
project serves, what it enables, and why it exists where those distinctions help.
Present concrete wording for refinement and approval, together with the root
README locations to update. Carry existing approval forward when it covers that
wording and recording action. Keep the purpose concise; do not expand it into a
separate vision document, task checklist, or agent execution prompt.

## Record and return

Purpose dialogue and draft wording may inform planning. Before shipping README
edits, apply the global Planning before implementation rule; reuse the adoption
or other invoking workflow's covering map/spec. A standalone wording approval
does not waive that gate.

After approval, preserve unrelated README content and place the purpose directly
below the title, before setup and detailed sections. Keep root README variants
consistent in meaning and appropriate to their language. If no root README exists,
create a minimal README with the project title and approved purpose. Investigate
conflicting variants rather than choosing the project's direction on the human's
behalf.

Use the invoking workflow's authorized branch and delivery scope. Greenfield
Initialization, Brownfield Adoption, and Standards Upgrade include purpose edits
in their own change and own its eventual review and delivery; return the approved
wording and changed files to that workflow without starting a separate PR. For
standalone work, follow the target repository's normal authorized documentation
delivery path. A missing skill or unavailable prerequisite is reported to the
caller with the remaining work preserved.

Report the agreed purpose, affected READMEs or the no-change result, and any
pending human decision. Return to the invoking workflow so it can continue within
its existing authority. Purpose approval does not authorize unrelated project
implementation or changing an already agreed purpose to justify new work.
