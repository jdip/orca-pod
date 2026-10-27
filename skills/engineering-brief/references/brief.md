# Editorial selection and brief format

## Choose stories worth the reader's time

The subject is thoughtful contributions to agentic coding and consequential AI
news. Anchor the edition in what real engineers are saying in social posts, blogs,
videos, and discussions: what they are learning, demonstrating, or disputing.
Following a person means following their thinking and experience, not their patch
feed. Repository activity is supporting evidence, not a substitute for that coverage.
Major model, product, and research developments can earn coverage
without an immediate Orca Pod change; explain their broader significance.

For every candidate, establish:

- The contribution: a substantive idea, demonstrated workflow, project, experiment,
  failure, changed position, or major capability shift.
- Why it matters: what an informed engineer understands differently after reading it.
- The support and limits: what is built, observed, argued, or merely predicted.

Rank significance before recency within the rolling two-week discovery horizon.
Distinguish developments since the last brief from newly discovered contributions
that predate it; give their real publication dates. The coverage interval labels
recency; eligibility extends across the discovery horizon.

Before excluding a candidate as already covered, locate the earlier report's
specific claim or mechanism and compare the candidate's changed behavior,
evidence, or consequence. A shared theme alone does not establish repetition.
Evaluate a substantive difference on its significance; a short mention may be
enough when it does not warrant a lead. Keep the comparison and exclusion reason
in Collection notes when relevant to continuity. Without matching prior coverage,
assess the candidate on its merits rather than treating it as a duplicate.

Strong evidence for an unimportant fact does not make it a strong story. Routine patches, dependency
bumps, changelog churn, and minor fixes in unused tools are noise. A fix merits
coverage when it directly affects something used here or exposes a consequential
engineering failure with a transferable lesson. Explain that consequence.

A thoughtful firsthand argument can be worth discussing without a benchmark.
Grade it honestly instead of replacing it with a trivial but easily verified
release note. Famous names, promotional claims, and unsupported productivity
multipliers do not confer importance. Include informed dissent and failed attempts.

## Write a news briefing

Open with a compact dateline containing the edition date, an optional coverage date
range, and optional reading time. Follow it with a short **Overall signal** paragraph:
the most meaningful pattern across the selected work. Make clear when that pattern
is your synthesis rather than a demonstrated result. The next visible section is
the first substantive story; collection mechanics belong in Collection notes near
the end.

Use up to five leading stories with descriptive headlines. Give each enough
connected prose to explain what happened, how the idea or system works, why it
matters, who should care, and its important limitation or counterargument. Explain
whether it challenges or reinforces current practice. Name the engineer whose
work is being discussed. Put compact impact/evidence labels beside the headline;
make the claim type clear in prose or a short label. Cite direct sources near claims.
Place its topic directive after the explanation in the saved Markdown; the HTML
reader converts it to a collapsed, copyable context seed, following
[topic actions](topic-actions.md).

Aim for an 8–12 minute read for a substantial edition, not a word-count quota.
A quiet interval warrants a short update. Use paragraphs for explanation and
lists or tables only for genuinely parallel information. Avoid raw research logs,
commit hashes, repeated caveats, full task prompts, and template-filling fragments
in the reading flow. A heading promises useful content beneath it.

## Coverage areas, not mandatory empty sections

Consider all of these areas while researching. Organize the edition around the
material found; combine or omit empty sections and explain coverage limits once
in Collection notes. Do not repeat a leading story to fill another section.

- **Leading stories / TOP 5:** the most consequential contributions and developments.
- **Major releases:** capabilities and tradeoffs, not a version-number inventory.
- **Techniques and workflows:** how practitioners actually work and what they learned.
- **Skills / plugins / MCP:** meaningful practice, portability, and architectural shifts.
- **Practitioner radar:** additional substantive voices or changed positions.
- **Projects to watch:** what makes the engineering interesting and what remains unproven.
- **Research / evals:** methodology, findings, and limits on generalization.
- **Debates and counterpoints:** actual disagreement, supporting evidence, and open questions.
- **Orca Pod implications:** selected consequences, existing equivalents, and genuine gaps.
- **TRY THIS:** zero to three small, reversible experiments with measurable outcomes.
- **Watchlist:** unresolved questions, promising people, and evidence worth revisiting.
- **Source review:** meaningful curation findings, including the weekly review when due.

Repository implications belong after the reader understands the news. Recognize
what Orca Pod already does; do not propose adopting an existing practice as a
new experiment. Each experiment states uncertainty, baseline/comparison, cost/scope,
measurement/success criterion, and stopping or rollback condition. Avoid forced
experiments where understanding the development is the useful outcome.

## Supporting notes

Put supporting notes at the end of the same saved report inside Markdown `details`
blocks. The main prose should stand alone. Links to notes should identify what the
reader will find.

Use one collapsed block titled `Collection notes` for explanations of the coverage
window or story selection, rolling discovery horizons, source-search reach and
access limits, audit timing or status, exact timestamps, and correction or
supersession provenance. A compact coverage date range may remain in the dateline;
its methodology and bookkeeping belong in Collection notes. Collection notes are
the only home for these collection mechanics. Every visible section carries the
briefing itself.

Put revision/path evidence, the first-edition hypothesis baseline, and optional
duplicate discussion seeds in clearly titled details blocks. Include inaccessible
sources and uninvestigated domains in Collection notes rather than empty status
sections.

## Editorial acceptance before saving

Read the draft as the operator. Can the reader explain the important contributions,
why those particular stories were chosen, and what remains uncertain? Does the
edition reflect actual practitioner discovery and major-news research? Is every
leading story more useful than routine tool maintenance? Are the implications
specific without turning the article into a repository audit? Does the visible
opening move from its compact dateline and Overall signal directly into the first
substantive story, with collection mechanics confined to the collapsed
Collection notes? Remove filler and repetition; resolve missing research before
advancing completed history. Mechanical validation and citation correctness cannot
substitute for this editorial check.
