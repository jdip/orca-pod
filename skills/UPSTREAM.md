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
| `domain-modeling` | `skills/engineering/domain-modeling` |
| `setup-matt-pocock-skills` | `skills/engineering/setup-matt-pocock-skills` |
| `codebase-design` | `skills/engineering/codebase-design` |
| `diagnosing-bugs` | `skills/engineering/diagnosing-bugs` |
| `writing-for-agents` | `skills/productivity/writing-for-agents` |
| `wizard` | `skills/engineering/wizard` |
| `wait-what` | `skills/productivity/wait-what` |

Two vendored packages keep upstream's `disable-model-invocation: true`, with
the reason recorded here so their text stays byte-for-byte:
`setup-matt-pocock-skills` stays a deliberately manual upstream package, and
`wait-what` is a human-typed command.

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

Orca Pod adapted these packages itself from the upstream paths at the pin. Each
`SKILL.md` keeps its attribution section.

| Package | Upstream path |
| --- | --- |
| `brainstorm` | `skills/productivity/grilling`, with Wayfinder's chart-the-map passages from `skills/engineering/wayfinder` |
| `improve-codebase-architecture` | `skills/engineering/improve-codebase-architecture` |

`improve-codebase-architecture` keeps upstream's `disable-model-invocation: true`
and `allow_implicit_invocation: false` as a deliberately manual upstream package.

Every other package is original to Agent Team and was imported from its
`machine/skills/` or, for `engineering-brief`, its repository-local
`.agents/skills/`.

## Adapted (Apache-2.0)

`to-spec`'s review lenses and panel rules in `skills/to-spec/review-lenses/`, and
`brainstorm`'s questioning methods in `skills/brainstorm/methods/`, are adapted
from
[google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model)
at the reviewed pin `05f8984cb6e0077b072ba034f66d95ffdde200ee`, under the Apache
License 2.0. Each directory keeps upstream's `LICENSE` verbatim; upstream has no
`NOTICE` file at the pin. Each file opens with its upstream path, the pin, the
license and Orca Pod's modifications. `brainstorm`'s map panel and `to-spec`'s
spec panel load the review lenses; `brainstorm`'s rounds load the questioning
methods.

| File | Upstream path |
| --- | --- |
| `to-spec/review-lenses/comprehension.md` | `agents/comprehension.md` |
| `to-spec/review-lenses/design_critic.md` | `agents/design_critic.md` |
| `to-spec/review-lenses/zoom_out.md` | `agents/zoom_out.md` |
| `to-spec/review-lenses/implementation_readiness.md` | `agents/implementation_readiness.md` |
| `to-spec/review-lenses/zoom-out-standard.md` | `resources/document_standards/zoom-out-standard.md` |
| `to-spec/review-lenses/fidelity_and_grounding.md` | `agents/codebase_details.md` |
| `to-spec/review-lenses/panel.md` | `skills/egm-review-loop/SKILL.md`, `skills/egm-resolve/SKILL.md`, `agents/synthesizer.md` |
| `brainstorm/methods/questioning.md` | `skills/egm-brainstorm/SKILL.md`, `skills/egm-draft/SKILL.md` |
