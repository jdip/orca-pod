# Curated sources

Use this catalog to find leads for an Orca Pod engineering brief or source
audit. It is a maintained search-priority policy, not a claim-evidence ledger.
Source tiers say where to look first; they do not determine whether a claim is
well supported. Grade each reported claim from its direct evidence.

Start with what practitioners are saying, trying, building, and learning.
Theo Browne, ThePrimeagen, Matt Pocock, Lauren ‘poteto’ Tan, and Peter Steinberger
anchor discovery; the wider catalog supplies additional builders and counterpoints.
Read their social posts, blogs, newsletters, videos, streams, and discussions
first. Follow what they are saying about agentic engineering, including lessons,
disagreements, failures, and changed minds. Repositories substantiate claims from
that conversation; do not mine their commits or patches to manufacture coverage.
When social or video material is inaccessible, report that limit and research
other accessible writing instead of substituting repository activity. Use official
product sources to verify relevant capabilities. A minor
fix in an unused tool earns no coverage merely because it concerns agents.
Select unfamiliar tools for consequential, transferable engineering lessons.
State the actual sample rather than implying every source was monitored.

## Anchor reading channels

Start each person's research with these channels, verified through their own site
or profile. Inspect the substance of posts or transcripts; titles alone do not
establish a position. Discover additional channels from the author's own links.

| Person | Read and watch first |
| --- | --- |
| Theo | [X](https://twitter.com/theo), [YouTube](https://youtube.com/@t3dotgg), [site and blog](https://t3.gg/) |
| ThePrimeagen | [X](https://twitter.com/ThePrimeagen), [YouTube](https://youtube.com/ThePrimeagen), [official channel directory](https://linktr.ee/ThePrimeagen) |
| Matt Pocock | [writing](https://www.mattpocock.com/), [social channel](https://www.mattpocock.com/twitter), [YouTube](https://www.youtube.com/c/mattpocockuk) |
| Lauren “poteto” Tan | [X posts and articles](https://x.com/poteto) |
| Peter Steinberger | [blog](https://steipete.me/), [X](https://x.com/steipete) |

## Coverage domains

Use these domains to rotate discovery and report sampled versus uninvestigated
coverage. Select substantive evidence relevant to Orca Pod across the interval;
a run need not find news in every domain.

- Coding-agent harnesses, orchestration, subagents and parallel agents
- Worktrees and isolated workspaces; persistent and remote agents
- Skills, plugins, Agent Skills / `SKILL.md`, MCP and alternatives to MCP
- Context engineering and compaction; repository instructions (`AGENTS.md` / `CLAUDE.md`)
- Specification and planning workflows; verification and reviewer agents
- Testing and runtime validation; evals; model routing; memory; observability
- Permissions and sandboxing; prompt-injection defenses; agent security
- Coding-agent UX; agent-team coordination; long-running tasks
- Practical use of Codex, Claude Code, and similar systems

## Tier A — builders and empirical engineers

These people are watched because they build, maintain, measure, or document
software systems. Their inclusion is not an endorsement of every claim or post.
Aliases are grouped so one person's material is not counted as independent
corroboration.

| Source and canonical links | Relevant specialties | Reason for attention |
| --- | --- | --- |
| [Thorsten Ball](https://thorstenball.com/) — [Register Spill](https://registerspill.thorstenball.com/) | Programming tools, agent-assisted software work | A practicing engineer writing concrete observations about how agents change software work. |
| [Armin Ronacher](https://lucumr.pocoo.org/) / [mitsuhiko](https://github.com/mitsuhiko) | Language/runtime design, open-source maintenance, coding agents | Maintainer perspective on agent harnesses, abstractions, and production tradeoffs. |
| [Mario Zechner](https://mariozechner.at/) / [badlogic](https://github.com/badlogic) | Pi, agent loops, tool design | Builds and publicly iterates on agent tooling; read his writing about agent design, tradeoffs, and practical experience. |
| [Mitchell Hashimoto](https://mitchellh.com/) | Developer tools, terminal UX, isolated environments | Long-running maintainer with practical evidence about developer workflows and tool ergonomics. |
| [Jesse Vincent](https://blog.fsck.com/) | Production operations, workflow systems, durable software | Useful counterweight from a maintainer of long-lived production systems. |
| [Peter Steinberger](https://steipete.me/) / [steipete](https://github.com/steipete) | Mobile engineering, developer tooling, agent workflows | Publishes hands-on agent experiments and open-source tooling. |
| [Boris Cherny](https://github.com/bcherny) | Claude Code, coding-agent product work | Firsthand product and workflow observations; seek the underlying release or documentation where available. |
| [Matt Pocock](https://www.mattpocock.com/) / [mattpocock](https://github.com/mattpocock) | TypeScript, skills, engineering workflows | Maintains reusable workflow material and explains implementation choices in public. |
| [Lauren "poteto" Tan](https://github.com/poteto) | Developer workflow, production software, agent tooling | Follow the practitioner's own projects and firsthand observations; verify authorship before associating separate projects with this source. |
| [Addy Osmani](https://addyosmani.com/) | Web engineering, developer productivity, agent guidance | Combines production engineering experience with accessible technical guidance; prefer code and measured work. |
| [Nicholas Carlini](https://nicholas.carlini.com/) | ML security, adversarial testing, agent security | High-value source for threat models and evidence-led security claims. |
| [Hamel Husain](https://hamel.dev/) | LLM evaluation, production AI systems | Documents evaluation and operational practice with an empirical orientation. |
| [Shreya Shankar](https://www.shreyashankar.com/) | ML systems, evaluation, data quality | Useful for rigorous evaluation methodology and production failure modes. |
| [Kent Beck](https://tidyfirst.substack.com/) | Software design, testing, incremental delivery | Offers an experienced counterpoint for testing, design, and change discipline. |
| [Simon Willison](https://simonwillison.net/) | LLM tooling, prompt injection, reproducible experiments | Publishes reproducible technical investigations and security-relevant observations. |
| [Geoffrey Huntley](https://ghuntley.com/) / [ghuntley](https://github.com/ghuntley) | Developer infrastructure, remote development, agent work | Builder perspective on execution environments and software delivery. |
| [Andrej Karpathy](https://karpathy.ai/) | Model behavior, training, coding-agent practice | Useful for technically grounded model and harness observations; distinguish demos from measured outcomes. |
| [ThePrimeagen](https://github.com/ThePrimeagen) | Developer tooling, editor/terminal workflow | Follow his firsthand experiences, demonstrations, and arguments about agentic development; distinguish observation from opinion. |
| [Theo Browne](https://t3.gg/) / [t3.gg](https://github.com/t3-oss) | Web platforms, developer experience, coding agents | Follow his discussion of agentic development, changing practices, and technical tradeoffs; corroborate empirical claims as needed. |
| [Steve Yegge](https://steve-yegge.blogspot.com/) / [beads](https://github.com/steveyegge/beads) | Developer workflow, task systems, agent coordination | Maintains agent-adjacent workflow tools and supplies a long-horizon engineering viewpoint. |
| [swyx](https://www.swyx.io/) / [Latent Space](https://www.latent.space/) | AI engineering ecosystem, practitioner discovery | A discovery bridge to practitioners and projects; promote only primary evidence into substantive findings. |
| [David Crawshaw](https://crawshaw.io/) | Agent feedback loops, code review, repository knowledge | [How I program with Agents](https://crawshaw.io/blog/programming-with-agents) describes real implementation, authorization/performance failures, and the effect of local code explanations. |
| [Harper Reed](https://harper.blog/) | Daily coding-agent workflows, remote sessions, practical tooling | [Remote Claude Code](https://harper.blog/2026/01/05/claude-code-is-better-on-your-phone/) documents his working setup with persistent terminals and helper configuration; assess individual practices rather than adopting the setup wholesale. |
| [Birgitta Böckeler](https://birgitta.info/) | AI-assisted delivery, architecture, feedback and verification | [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html) connects repository context, deterministic controls, and human steering; distinguish its reasoned framework from measured outcomes. |
| [Graham Dumpleton](https://grahamdumpleton.me/) | Python maintenance, testing, instrumentation, AI-directed implementation | [Introducing wrapture](https://grahamdumpleton.me/posts/2026/08/introducing-wrapture/) documents a domain engineer directing AI implementation of a concrete library with explicit caveats. |

### Tier A discovery criteria

During each ordinary brief, follow substantive references from watched engineers
to collaborators, maintainers, interview guests, technical disagreements, and the
authors of demonstrated work. Look beyond this social circle through project
contributors, technical talks, and maintainer write-ups, especially in ordinary
production software. A mention supplies a lead, not an endorsement.

Inspect the candidate's own artifact and role in it. Look for concrete agentic
engineering contributions: a working project, explained workflow, reproducible
experiment, failure analysis, or a reasoned argument grounded in their practice.
Check sustained engineering work rather than requiring frequent content output.
Popularity, mutual mentions, and a single viral claim do not establish quality.
Preserve substantive skeptics and counterexamples alongside successful builds.

When a candidate earns attention, record their name, canonical channel, specialty,
specific contribution with a direct link, evidence limits, and reason to revisit
in the brief's source review and local watch history. Include candidates
only when supported; no per-run quota. Propose standing catalog additions through
the existing curation workflow. Revisit whether sources continue contributing
useful work; silence is different from a demonstrated decline in quality.

## Tier B — official product sources

Use official documentation, release notes, source repositories, issue trackers,
and discussions to establish a product change. Report behavioral or architectural
changes, not version-number churn.

| Product or ecosystem | Canonical primary sources | Why this lane matters |
| --- | --- | --- |
| OpenAI Codex | [Codex documentation](https://developers.openai.com/codex/) | Coding-agent behavior, harnesses, worktrees, skills, and desktop UX. |
| OpenAI Agents API | [Agents guide](https://platform.openai.com/docs/guides/agents) | Agent tool use, orchestration primitives, and evaluation-adjacent API patterns. |
| OpenAI plugins and Agent Skills | [Build skills](https://learn.chatgpt.com/docs/build-skills) | Skill packaging and discovery relevant to this repository's local skill. |
| Anthropic Claude Code | [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code/overview) | A major coding-agent harness and workflow comparator. |
| Anthropic Skills | [Agent Skills documentation](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview) | Cross-host skill conventions and implementation evidence. |
| Cursor | [changelog](https://cursor.com/changelog) | Editor-integrated agent behavior and product workflow changes. |
| GitHub Copilot | [official documentation](https://docs.github.com/en/copilot) | Repository-hosted agent workflow and reviewer/automation capabilities. |
| GitHub Agentic Workflows / gh-aw | [gh-aw repository](https://github.com/github/gh-aw) | GitHub-native agent workflow implementation and discussions. |
| Gemini CLI | [source repository](https://github.com/google-gemini/gemini-cli) | Open coding-agent CLI implementation and release evidence. |
| Jules | [official site](https://jules.google/) | Remote/asynchronous coding-agent workflow changes. |
| OpenCode | [source repository](https://github.com/anomalyco/opencode) | Open agent harness design and extension patterns. |
| Cline | [source repository](https://github.com/cline/cline) | Agent tool use, MCP integration, and IDE workflow evidence. |
| Roo Code | [source repository](https://github.com/RooCodeInc/Roo-Code) | Open IDE-agent product and configuration patterns. |
| Windsurf | [documentation](https://docs.windsurf.com/) | Editor-agent UX, workflow, and product-change evidence. |
| Amp / Sourcegraph | [Amp](https://ampcode.com/) and [Sourcegraph](https://sourcegraph.com/) | Coding-agent UX and code-intelligence workflow comparison. |
| Aider | [documentation](https://aider.chat/) / [source](https://github.com/Aider-AI/aider) | Terminal agent workflow, benchmarks, and transparent open-source implementation. |
| Devin | [documentation](https://docs.devin.ai/) | Persistent and remote-agent workflow claims; inspect product docs carefully. |
| Factory | [official site](https://www.factory.ai/) | Agent product and enterprise workflow developments. |
| Pi | [source repository](https://github.com/earendil-works/pi) | Lean agent-loop design, skills, extensions, and model-provider abstractions. |
| Superpowers | [source repository](https://github.com/obra/superpowers) | Reusable engineering workflow skill design. |
| Beads / Gas Town | [Beads](https://github.com/steveyegge/beads) and [Gas Town](https://github.com/steveyegge/gastown) | Task tracking and multi-agent coordination mechanisms. |
| OpenHands | [source repository](https://github.com/All-Hands-AI/OpenHands) | Open agent platform, remote execution, and evaluation discussions. |

## Tier C — skills and tooling ecosystem

Treat every reusable skill, plugin, MCP server, workflow library, evaluation
framework, observability product, sandbox, or remote environment as a software
supply-chain input. Before recommending one, inspect its owner, source, release
history, permissions, evaluation/validation practice, and compatibility with
Orca Pod.

| Ecosystem or coverage lane | Canonical starting points | What to investigate |
| --- | --- | --- |
| Agent Skills / `SKILL.md` | [Agent Skills specification](https://agentskills.io/specification) | Portability, composition, versioning, and security boundaries. |
| skills.sh | [skills.sh](https://skills.sh/) | Discovery lead only; follow packages to their maintained repositories. |
| Model Context Protocol | [MCP specification](https://modelcontextprotocol.io/) | Protocol changes, permission boundaries, and tool-server security. |
| Official MCP Registry | [registry](https://registry.modelcontextprotocol.io/) | Publisher identity, release provenance, and server capabilities. |
| Matt Pocock's skills | [source repository](https://github.com/mattpocock/skills) | Reusable engineering workflow implementation and instruction design. |
| Lauren “poteto” Tan / pstack | [social posts](https://x.com/poteto) / [author’s guide](https://github.com/cursor/plugins/blob/main/pstack/README.md) | Read her explanations of context, design, and verification; the Cursor pstack source can substantiate the discussed workflow. |
| Addy Osmani's agent skills | [source repository](https://github.com/addyosmani/agent-skills) | Portable skill design; confirm scope and maintenance activity per proposed use. |
| Superpowers | [source repository](https://github.com/obra/superpowers) | Workflow composition, tests/evals, and adoption constraints. |
| NVIDIA skills | [NVIDIA-Verified Agent Skills](https://docs.nvidia.com/skills) / [source repository](https://github.com/nvidia/skills) | Supply-chain controls, evaluation, signing, and portability practices for skills. |
| Reusable agent workflow and orchestration libraries | [LangGraph](https://github.com/langchain-ai/langgraph) | State, coordination, observability, and deterministic-vs-agent boundaries. |
| Evaluation frameworks | [OpenAI evaluation guide](https://platform.openai.com/docs/guides/evals) | Methodology, task realism, harness/model details, and reproducibility. |
| Plugin systems | No universal canonical source | Start from the product's documented plugin mechanism, then inspect ownership, permissions, isolation, and supply-chain review. |
| Agent observability | [OpenTelemetry GenAI conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) | Trace fidelity, privacy, cost, and operational usefulness. |
| Sandbox infrastructure | [E2B documentation](https://e2b.dev/docs) | Isolation model, network/filesystem permissions, lifecycle, and escape risks. |
| Persistent remote execution | [Daytona documentation](https://www.daytona.io/docs) | Workspace lifecycle, identity, state, and cleanup/retention controls. |

The named sources are starting points, not a closed ecosystem list. Keep an eye on
whether a candidate has tests or evals, versioning and release discipline,
observability, portability and composition, and documented security controls.

## Tier D — discovery sources

Third-party summaries and community reactions supply discovery leads. A
practitioner’s own social post, video, newsletter, or discussion contribution is
primary evidence of their firsthand account or argument; grade that precise claim.
The platform does not determine the tier. Measurements need their conditions and
methodology, but a thoughtful argument does not require a linked repository.

| Discovery source | Canonical entry point | Required next step |
| --- | --- | --- |
| Hacker News | [news.ycombinator.com](https://news.ycombinator.com/) | Find the linked repository, release, experiment, or author account. |
| Reddit | [reddit.com](https://www.reddit.com/) | Treat discussion as anecdotal until a primary source supports the claim. |
| GitHub Trending | [GitHub Trending](https://github.com/trending) | Inspect the repository, maintainer, releases, issues, and actual implementation. |
| GitHub Discussions | [GitHub Explore](https://github.com/explore) | Follow discussion to the owning project and its authoritative decision record. |
| YouTube | [YouTube](https://www.youtube.com/) | Read the transcript or watch the relevant passage; distinguish firsthand experience, argument, and third-party reaction. |
| X / social posts | [X](https://x.com/) | Read the original post and relevant thread; follow supporting links when the specific claim needs corroboration. |
| Podcasts and newsletters | No single canonical source | Attribute the author or speaker and read their contribution; trace secondhand claims to the original source. |
| Discord and other community discussions | No public universal source | Use only accessible, authorized material; do not imply access to private communities. |

## Catalog maintenance

Use [source-audit mode](source-audit.md) when requested to score sources and
propose catalog changes. Deduplicate aliases and syndications so repeated coverage
of one original claim is never misrepresented as independent confirmation.

When a listed link no longer resolves, retain the source name, mark the canonical
link unresolved, and investigate a replacement through the source owner's own
published profile or repository. Do not substitute a search result, a mirror, or
a social repost as canonical without evidence that the source owner controls it.
