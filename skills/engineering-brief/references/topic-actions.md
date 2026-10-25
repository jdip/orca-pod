# Topic discussion seeds

Give each substantive topic a concise, self-contained context seed that the user
can copy into a new Orca Pod task they create. The seed supplies context for a
conversation; it is not an execution plan or a task-creation request.

Include the topic, a short explanation of the contribution or claim, and direct
source links. Add a material caveat or a brief Orca Pod connection only when it
helps someone understand the topic without the original brief. Keep the language
natural and readable.

Do not tell the recipient to create another task, inspect the repository, perform
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
- :codex-followup[Topic name]{prompt="Topic summary and direct source URLs"}
```

Escape backslashes and double quotes inside the prompt. The HTML reader turns this into a collapsed
panel with a Copy prompt button. Keep any duplicate fallback seeds in a details
block titled `Copyable requests for separate topic tasks`; the renderer omits that
duplicate block from the article. Keep that optional duplicate block free of nested details.

Return the article/archive links in chat. Do not emit these directives as native
actions or create discussion tasks automatically. The user creates the destination
task and pastes the copied context there.
