# Local HTML reader

The completed Markdown reports remain canonical history. The reusable templates
in `templates/` generate a derived, private blog archive with article pages, source
links, a history index, previous/next navigation, and collapsed discussion prompts.
A small browser-only JavaScript handler copies discussion prompts. It requires
no Node/npm, new package, server, or public hosting. The shell entrypoint
currently supports macOS and other POSIX hosts; native Windows is not verified.

After saving a checked brief or audit, run the package's `scripts/render.sh` from
inside Orca Pod, selecting Python 3.11+ through `ORCA_POD_PYTHON` when needed.
The entrypoint owns its isolated Python environment in the local archive and
installs only the package's declared `requirements.txt`. Do not install dependencies
globally or add this skill to Machine Reconciliation.

```sh
ORCA_POD_PYTHON=python3.13 <skill-directory>/scripts/render.sh
```

Use the returned index and article paths. Open the HTML through the host's file or
browser capability; verify readable typography, narrow-window layout, working
source/history links, and collapsed prompts after a template or rendering change.
For a new edition, inspect its main article and topic panels before reporting it as
ready. Disclose missing browser coverage rather than claiming visual verification.

The renderer reads validated completed history and does not alter its metadata,
coverage boundaries, or canonical Markdown. Rebuild the index after correcting an edition or explicitly removing an archived
report. Previously generated pages remain on disk; when the operator requests
disposal, include those exact derived pages in the approved removal. A failed render leaves the
completed Markdown intact; fix the rendering problem and rebuild, never save a
second completed brief merely to retry presentation. Preserve private archive and
environment state during task cleanup.

## Conversation handoff

Return a short editorial summary, a link to the current HTML article, a link to
the archive. Topic context follows [discussion seeds](topic-actions.md).
Do not paste the full article and fallback prompts into chat. Source links remain
in the article. Each HTML discussion panel includes a copy icon beside the prompt
toggle, available while the prompt is collapsed. It
copies only that panel’s text, reports completion after clipboard success, and
selects the text for manual copying when access is unavailable. Copying does not
create a task; the user creates a new Orca Pod task and pastes the context. Do not invent desktop deep-link URLs or
introduce a bridge/service to simulate direct HTML task creation.
