# UI prototype

Use this branch when the question concerns visual hierarchy, interaction, or
how a proposed surface works beside the rest of the product.

## Choose the context and comparison

State the design question, the decision criteria, and the observation that will
select a direction. Prefer the nearest real page or component when its header,
navigation, data density, or surrounding workflow affects the decision. A
clearly marked throwaway route, component, or static artifact is appropriate
when no existing surface can host the inquiry. Follow the project's established
routing and rendering conventions.

Use one rendition when the question is whether a proposed direction works in
context. Build multiple alternatives when the decision is genuinely comparative.
Choose the number and degree of difference from the decisions being tested,
then make each alternative disagree meaningfully about hierarchy, layout, or
primary interaction. Avoid alternatives that only change cosmetic details.

## Build for judgment

Reuse the product's existing components, styling system, read-only data, and
context where that gives an honest view of the surface. If a safe representative
context is unavailable, make the sample data and missing conditions visible.
Keep prototype mutations stubbed or isolated.

Provide controls only when they help a reviewer inspect the alternatives or
state being tested. A single rendition may need no selector; a comparison may
use the project's normal navigation, a shareable parameter, tabs, buttons, or
another small temporary control. Make the current alternative and relevant UI
state visible, keep the control out of the design being evaluated, and use an
artifact-local mechanism that can be discarded with the prototype.

## Verify and decide

Inspect each rendition in the relevant states, viewport sizes, and surrounding
context that bear on the question. Record the selected direction, evidence, and
concrete implementation handoff. Retain the prototype only when its planning
record is authorized; implement the chosen design through the repository's
normal workflow rather than promoting prototype code directly.

## Boundaries

Keep each alternative free to explore the decision under test. Shared domain
data or small common elements can provide context; a shared layout should not
pre-decide the alternatives' hierarchy. Use only approved languages, runtimes,
and project commands, and keep the artifact visibly throwaway.
