---
name: resolving-merge-conflicts
description: Resolve an in-progress Git merge or rebase while preserving unrelated work and verifying the intended result.
---

1. **Establish the operation and ownership.** Inspect Git status, the index, conflicts, and history. Identify the actual merge/rebase, its intended source and target, and any available pre-operation dirty-state evidence. Preserve unrelated staged and unstaged changes. If ownership of a change is unclear, investigate before staging or committing it.

2. **Find the primary sources.** Read the commits and relevant PR/issue requirements to understand both sides of each conflict.

3. **Resolve each hunk.** Preserve both intents where possible. When they conflict, use the authorized outcome and explain the tradeoff. Routine resolution remains with the agent. If the outcome cannot settle a substantive choice, keep the operation and independent resolved work intact and report that exact decision. Neither invent behavior nor abort the operation merely to escape the conflict.

4. **Verify the result.** Run the repository's relevant checks and inspect the resolution diff for lost behavior. Repair failures caused by the resolution within scope. Classify Application Code and Tooling according to local guidance; do not add a new test framework for the merge itself.

5. **Finish the authorized operation.** Stage only proven resolution changes. Inspect the entire staged diff before a merge commit or rebase continuation: Git may already have staged cleanly merged files, and unrelated staged work must not be swept into the commit. If unrelated changes cannot safely be separated with known ownership, return the concrete blocker while preserving them. Complete the merge or continue the rebase only within the assignment's Git authority; report resolved files to the primary when that authority was not assigned. Recheck ownership and verification as later rebase conflicts arise. Report the resulting revision and any retained unrelated work.

## Attribution

Adapted by Agent Team from [Matt Pocock’s resolving-merge-conflicts](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/resolving-merge-conflicts), revision `3cca18b368ae95cdbdebbff572ccafa662551015`. The [MIT notice](LICENSE) covers reused upstream material. Agent Team owns this adaptation.
