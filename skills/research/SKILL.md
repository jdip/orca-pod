---
name: research
description: Investigate a question against high-trust primary sources. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Investigate the question against primary sources and return evidence that lets the
user or supervising agent assess the answer.

When independent research can proceed alongside other work, the primary agent may
delegate a bounded assignment with its scope, expected evidence, and ownership.
The assigned agent investigates directly and returns its findings to the primary
agent; delegation does not require a further research agent.

1. Investigate against **primary sources**: official documentation, source code,
   specifications, or first-party APIs. Follow each material claim to the source
   that owns it.
2. Return findings with citations and the practical limits of the evidence.
3. Write a Markdown research artifact only when the user requests one or the
   assignment authorizes one and the writer owns an authorized checkout. Match the
   repository's existing research convention. Otherwise, return the findings
   directly to the user or supervising agent.

## Attribution

Adapted by Agent Team from [Matt Pocock’s research](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/research), revision `3cca18b368ae95cdbdebbff572ccafa662551015`. The [MIT notice](LICENSE) covers reused upstream material. Agent Team owns this adaptation.
