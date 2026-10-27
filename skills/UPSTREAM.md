# Upstream provenance

Upstream-derived packages come from
[mattpocock/skills](https://github.com/mattpocock/skills) at the reviewed pin
`3cca18b368ae95cdbdebbff572ccafa662551015`. Each package keeps the upstream MIT
notice in its own `LICENSE`. Review and deliberately change the pin for updates;
never float upstream content.

## Vendored

These packages are byte-for-byte copies of the upstream path at the pin, plus
the upstream root `LICENSE`.

| Package | Upstream path |
| --- | --- |
| `grilling` | `skills/productivity/grilling` |
| `domain-modeling` | `skills/engineering/domain-modeling` |
| `setup-matt-pocock-skills` | `skills/engineering/setup-matt-pocock-skills` |
| `codebase-design` | `skills/engineering/codebase-design` |
| `diagnosing-bugs` | `skills/engineering/diagnosing-bugs` |
| `improve-codebase-architecture` | `skills/engineering/improve-codebase-architecture` |
| `writing-for-agents` | `skills/productivity/writing-for-agents` |
| `wizard` | `skills/engineering/wizard` |
| `wait-what` | `skills/productivity/wait-what` |

Three vendored packages keep upstream's `disable-model-invocation: true`, with
the reason recorded here so their text stays byte-for-byte:
`setup-matt-pocock-skills` and `improve-codebase-architecture` stay deliberately
manual upstream packages, and `wait-what` is a human-typed command.

## Adapted

Agent Team adapted these packages from the upstream path at the pin. Orca Pod
imported them from Agent Team. Each `SKILL.md` keeps its attribution section.

| Package | Upstream path |
| --- | --- |
| `code-review` | `skills/engineering/code-review` |
| `prototype` | `skills/engineering/prototype` |
| `research` | `skills/engineering/research` |
| `resolving-merge-conflicts` | `skills/engineering/resolving-merge-conflicts` |
| `tdd` | `skills/engineering/tdd` |
| `to-spec` | `skills/engineering/to-spec` |
| `to-tickets` | `skills/engineering/to-tickets` |
| `triage` | `skills/engineering/triage` |
| `wayfinder` | `skills/engineering/wayfinder` |

Every other package is original to Agent Team and was imported from its
`machine/skills/` or, for `engineering-brief`, its repository-local
`.agents/skills/`.
