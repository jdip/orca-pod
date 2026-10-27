# Topic discussion seeds

Give each substantive topic a concise, self-contained context seed that opens a
discussion in a new Orca workspace. The seed supplies context for a
conversation; it is not an execution plan or a workspace-launch request.

Include the topic, a short explanation of the contribution or claim, and direct
source links. Add a material caveat or a brief Orca Pod connection only when it
helps someone understand the topic without the original brief. Keep the language
natural and readable.

Do not tell the recipient to launch another workspace, inspect the repository, perform
an investigation, produce an experiment proposal, or follow a prescribed workflow.
Do not add role assignments, permission checklists, mandatory output formats,
repository inventories, or implementation gates. The user decides the direction
of the discussion after pasting the context.

For example:

> Topic: Using prototypes to resolve uncertainty in agent-assisted planning.
> Lauren “poteto” Tan describes grounding work in the existing system and trying
> concrete alternatives before committing to a design. The interesting question
> is when a prototype gives better evidence than a longer written plan.
> Sources: [the original post] and [the author's explanation].

## Store and present

In the saved Markdown, use the existing topic directive as a data container for
the renderer, with a descriptive label and the complete context in `prompt`:

```text
- :topic-seed[Topic name]{prompt="Topic summary and direct source URLs"}
```

Archived Agent Team-era reports use the same form named `:codex-followup`; the
renderer still reads it, so never rewrite archived reports to rename it.

Escape backslashes and double quotes inside the prompt. The HTML reader turns this into a collapsed
panel with a Copy prompt button. Keep any duplicate fallback seeds in a details
block titled `Copyable requests for separate topic tasks` (a legacy title kept so
archived reports render unchanged); the renderer omits that
duplicate block from the article. Keep that optional duplicate block free of nested details.

Return the article/archive links in chat. Do not emit these directives as native
actions or launch discussion workspaces automatically. When the user picks a topic
in conversation, launch it as a new Orca workspace with its seed as the opening
prompt, using the agent the user names:

```sh
orca worktree create --repo <selector> --name <topic-slug> --no-parent \
  --agent <claude|codex> --prompt "<topic seed>" --json
```

Report the new workspace from the result. The user can instead copy a seed from
the HTML panel into a workspace they create.
