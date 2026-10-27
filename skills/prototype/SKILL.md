---
name: prototype
description: Build a throwaway prototype to test a factual design claim or support human judgment about logic, an interface, or a UI.
---

# Prototype

A prototype is **throwaway code that answers a design question**. Make the
question, the available environment, and the evidence needed decide its shape.

## Choose the inquiry

Use [LOGIC.md](LOGIC.md) for behavior, state transitions, data shape, or an API
surface. Use [UI.md](UI.md) for visual hierarchy, interaction, or how a surface
fits its surrounding product. When one question contains both, separate the
decisions or build the smallest artifact that can answer the unresolved part.

State the question and the observation that would resolve it before writing the
artifact. Ask the user when those are not concrete; reuse agreed criteria.

Run already-authorized factual experiments with agreed observable criteria
autonomously. Report what the observations establish and their limits. When an
experiment leaves a preference, tradeoff or scope decision, bring the evidence
to the operator through the owning planning workflow. If execution lacks
authorization or an approved, available environment, keep it pending. An experiment
does not expand authority or replace map-entry dialogue and confirmation.

## Rules that apply to every prototype

1. **Keep it throwaway and task-owned.** Mark the artifact as a prototype and
   place it in an authorized location. Keep it close to the explored module or
   surface when that context is useful; follow the project's route convention
   for a throwaway route. Exclude prototype artifacts and temporary controls from
   production delivery using the project's existing isolation or build mechanism,
   and verify that exclusion.
2. **Use the approved environment.** Choose the smallest format that is easy to
   run or inspect with existing project commands, languages, and runtimes. A
   directly opened self-contained artifact is appropriate only when it needs no
   new environment. Do not add a framework, server, runtime, or toolchain for
   the inquiry.
3. **Use representative context.** Reuse the nearby page, component, domain
   language, read-only data, or authenticated context when it makes the
   decision easier to judge. When that is unavailable or unsafe, use a clearly
   labelled sample or stub and record the resulting limit.
4. **Make the relevant result visible.** Render or print the state,
   transition, selected alternative, error, or other evidence needed to judge
   the question after relevant interaction. Keep persistence in memory unless
   persistence itself is under examination; then use an isolated disposable
   resource.
5. **Verify the question.** Exercise the scenarios that bear on the decision,
   inspect the rendered or observable result, and run applicable local gates.
   Keep verification proportional to a throwaway artifact.
6. **Clean, record the verdict, and hand off.** After the prototype's proof is
   complete or before it pauses, use `cleanup-task-artifacts` with local guidance
   before reporting the verdict. Phase cleanup does not end a continuing task or
   detach its checkout. Capture the question, evidence, decision, and proposed
   implementation seam in the artifact or authorized planning record. Distinguish
   established facts from decisions still awaiting the operator. A
   planning-only prototype ends with a concrete handoff. When implementation is
   already authorized, continue through the normal workflow; the prototype remains
   evidence rather than production code.

## Attribution

Adapted by Agent Team from [Matt Pocock’s prototype](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/engineering/prototype), revision `3cca18b368ae95cdbdebbff572ccafa662551015`. The [MIT notice](LICENSE) covers reused upstream material. Agent Team owns this adaptation.
