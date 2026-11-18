# Verification-cost catalog

This catalog is the single source for designing repeated verification cost out
of a repository. It is the standard file of the verification-cost persona
(`verification_cost.md`). That persona, the verification-cost axis of
[`code-review`](../../code-review/SKILL.md), [`tdd`](../../tdd/SKILL.md), the
Repository Standard and the always-loaded global rule link here instead of
restating it. Rules specific to one repository stay in that repository.

Read the part your work needs:

- Writing a test, fixture, wait, build step or CI job: the
  [named structure](#named-structure) and the [rule](#rules) for the pattern you
  are about to write.
- Reviewing a change or a draft: the [review questions](#review-questions).
- Planning a map, or installing rules for a stack: the named structure, then the
  [stanza conventions](#stanza-conventions) and each rule's stanzas.
- Correcting a rule or this file: [rule upkeep](#rule-upkeep) and
  [upstream reports](#upstream-reports).

## Principle

Verification cost has no multipliers. A run does each distinct piece of
expensive work once, waits only for conditions, and queues nothing behind work
it does not depend on.

A component's first fixture, wait, build step and job is a template: later work
copies the nearest example and inherits its cost. Decide its multiplier before
it is written.

Two cures are rejected:

- Time budgets, thresholds or approval gates. Agents exceed or raise them, and
  every legitimately slower test would stall on an approval.
- Parallelism, caching or selective testing as the cure for per-case starts.
  They shrink the delay and keep the multiplication.

## Terms

- Verification cost: what a run of a repository's checks spends on starts,
  waits, builds, installs and queued work.
- Multiplier: a structure that makes verification cost grow with the number of
  cases, elapsed seconds, runs or queued steps. It is a structure, not a
  magnitude.
- Expensive resource: a service a test must wait to become ready and must tear
  down (an application or server process, a container, a database server or
  migrated schema, a browser, a virtual machine or emulator), or an artifact that
  must be built or installed before a test can use it. An in-process object such
  as a client, an in-memory router or a temporary directory is not one. Running
  the product's own command to completion is the behavior under test, not a
  resource.
- Run: one invocation of a check step. Each named configuration starts once in
  it; under a parallel runner, once per worker is the same structure. The number
  of starts never grows with the number of cases.
- Named configuration: a set of settings a resource can take only at start,
  declared by name in the start owner and shared by every case that asks for it.
  Anything the running resource accepts per request or per record is case data,
  not configuration.
- Privileged area: the lifecycle tests or the real-time tests, the only test
  code that may use what the rules ban elsewhere.
- Exempt path: a path the lint configuration names as outside a ban: the two
  privileged areas, the start owner and the wait helper.
- Rule upkeep: how a rule enters, narrows or leaves this catalog or a
  repository's configuration.
- Upstream report: an adopted repository's record that Orca Pod text should
  change.

## Named structure

The named structure is a closed list: start owner, named configuration, wait
helper, lifecycle tests, real-time tests, reuse path, separately invocable check
steps and lint stage. Deciding it before a component's first test is design, not
a speculative framework. Anything beyond the list is a speculative framework.
The Repository Standard says when each item is installed in a repository.

### Start owner

- It starts each expensive resource once per run per named configuration and
  refuses a second start. Cases cannot call it to start anything; they ask for a
  named configuration and receive the running instance.
- Cases share that instance and isolate by their own records, identities and
  credentials.
- It holds the command helper: the one helper through which a case runs the
  product's own command to completion, and which can run only that command.
- It prints a start line for each start (see
  [check-step output](#check-step-output)).

### Named configuration

Each configuration is declared by name in the start owner. A case that needs a
setting the running resource accepts per request or per record passes it as case
data; a setting it can take only at start is a named configuration.

### Wait helper

The one way test code waits for a condition. It returns when its condition
holds, raises at its bound, owns the poll interval and offers no fixed delay.

### Lifecycle tests

The only test code that starts an instance of an expensive resource. A lifecycle
test may start and stop an instance and may wait. Each case cites the lifecycle
state it asserts. A case that needs both privileges is a lifecycle test.

### Real-time tests

A real-time test may wait out a clock no test can control, and starts nothing.
Each case cites that clock. Where a linter's exemption lifts a whole rule, the
real-time path restates the start ban as a source-check line.

Both privileged areas share these properties:

- Each runs as its own named check step, so its case count and elapsed time
  appear in every log.
- Their exempt paths are named when the rules are installed, before the files
  exist. Adding a privileged test then needs no rule edit, and any later edit to
  the list is visible.
- A path is the only exemption. There are no inline suppressions.

Rejected: one combined area (real-time cases would keep their private starts).
Rejected: a third area (anything that seems to need one is a design question for
a map).

### Reuse path

For each check's runner, the place from which work whose pinned inputs have not
changed is restored across runs. Where none is available, the repository's map
records that and why, at the map gate, because a reuse path can need a
credential, a registry or a persistent runner. The absence stays recorded with
its cause until a later map revisits it.

### Separately invocable check steps

- Each check step can be invoked alone and declares what it depends on.
- Independent steps run side by side once the reuse path exists. Building once
  takes precedence (see [independent work](#independent-work-run-one-after-another)).
- A targeted check selects steps by the inputs each declares and never falls
  back to the full gate.

### Lint stage

A stage, not a second ruleset: one linter configuration per stack carries the
pattern rules scoped to test paths, plus a small block of source-check lines for
what the linter cannot express.

- It is the first step of the check script in every mode, including the cheap
  pre-push gate and targeted checks.
- It runs cheapest first.
- It covers test code, fixtures, helpers, fakes, runner configuration, check
  scripts and workflow files.
- Nothing is built or started for tests until the pattern rules pass. The
  pattern rules need no compile and no product build. Linters that need a build,
  such as Clippy, run beside the tests and carry no pattern rule.

Rejected: a second ruleset, linter or plugin, or a generic checker shipped by
Orca Pod (a new mechanism that would put a language in targets and take stack
ownership from them). Rejected: every test job waiting for every linter (a clean
run would queue behind a compile). Rejected: tests never waiting for lint (a
violating change would still start its tests).

## Check-step output

A repository's check script prints:

- one line when each step begins and one when it ends;
- one line per start, naming the resource and the configuration;
- one line per build or install, naming the artifact and whether it was reused.

Nothing counts or compares these lines; readers quote them as evidence. A step
with nothing to run reports that and passes. An empty privileged area or an
empty lint target is not an error.

## Rules

Each rule entry gives its pattern, invariant, homes for legitimate uses, message,
stanzas and the sanitized instance that earned it. The stanzas are the ban: an
adopting repository pastes each into its own configuration and names the
placeholders.

### Stanza conventions

A stanza flags the ordinary forms of its identifiers in its ecosystem, the ones a
test is copied from, so a missing ordinary form is a defect in the stanza. It is
not proof against a deliberate workaround: what a ban by name cannot see, the
[review questions](#review-questions) carry.

Linters. Python uses Ruff `flake8-tidy-imports.banned-api` (rule TID251) with
`per-file-ignores`. TypeScript uses ESLint flat config `no-restricted-imports`
and `no-restricted-syntax`, which need no type information. A target whose stack
uses a different linter, or a stack this catalog has no stanza for, follows the
Repository Standard's no-stanza path.

Source-check lines. Where the ecosystem has no linter, or its linter cannot
express a ban, needs a compile or a product build, or has an exemption that
would lift a whole rule, the stanza gives source-check lines. Rust's pattern
rules are all source-check lines, because Clippy needs a compile. A source-check
line is one POSIX `grep` command, which the repository ports into its own
Tooling language. Above each line:

- `# Scan:` names the files it reads, by placeholder. The check script lists
  them, for example from `git ls-files`, and leaves out the exempt paths the line
  names.
- `# Message:` is the text the step prints with each match.

A line fails its step when it prints a match, and passes when it prints nothing
or has no files to scan. A `grep` exit status above one is a broken check, not a
pass. A line ending in `| grep -v 'serial-cause:'` drops settings whose cause is
stated beside them.

A source-check line reads one line at a time and matches text, not syntax, so it
also flags some lines that hold no banned name. So that a banned name on a later
line cannot pass, it flags a line that opens a grouped import of a banned module
and does not close it, whatever the group holds, and a line that begins an
inline `eslint` comment directive that does not close on that line, whatever the
directive configures; close the group or the comment on that line, or split the
import into separate imports. It also flags a banned name inside a comment, and
a module alias that could hide one, such as `import os as <name>` in a path
where the start ban is restated; reword the comment, or import the module under
its own name. Nor can a line pair an option with a value written on a later
line, as in a list written one item per line, unless it flags the option alone;
write the value attached to its option, such as `--dist=loadscope`. These
matches are properties of the lines, not exemptions: a path stays the only
exemption, and there is still no inline suppression
([real-time tests](#real-time-tests)).

Placeholders. The repository names each one when it installs the rules, before
the files exist, as globs for a linter and as file lists for source-check lines.

| Placeholder | What the repository names |
| --- | --- |
| `<test-paths>` | Every path holding that ecosystem's test code, fixtures, helpers and fakes, including test support kept inside product packages |
| `<lifecycle-path>` | The lifecycle tests |
| `<real-time-path>` | The real-time tests |
| `<start-owner>` | The start owner's files, with its command helper and any runner setting that starts a resource, such as a Playwright configuration holding `webServer`, a Vitest `globalSetup` file, or a check script that starts services |
| `<wait-helper>` | The wait helper's file |
| `<runner-config>` | The ecosystem's runner configuration files |
| `<check-scripts>` | The check script and the scripts its steps run |
| `<workflow-files>` | CI workflow files and the actions they call |

Each exempt path keeps the bans its privilege does not cover: the lifecycle path
keeps neither the start ban nor the wait ban; the real-time path and the wait
helper keep the start ban; the start owner keeps the wait ban.

Path scope. A ban scoped by path cannot see test code outside those paths. Each
row below names the in-file test markers a path scope misses. An in-file test
module holds only in-process cases; a case that needs an expensive resource, a
wait or a clock lives under the test paths, where the stanzas reach it. Review
question A2 governs what the paths miss.

| Ecosystem | Test paths | Runner configuration | In-file test markers |
| --- | --- | --- | --- |
| Python with pytest | `test_*.py`, `*_test.py`, `conftest.py`, and the test directories | `pyproject.toml` (`[tool.pytest.ini_options]`), `pytest.ini`, `tox.ini`, `setup.cfg`, `conftest.py` | Doctests collected by `--doctest-modules` |
| Rust with `cargo test` | `tests/` | `Cargo.toml`, `.cargo/config.toml` | `#[cfg(test)]`, `#[test]`, `#[tokio::test]` in `src/` |
| TypeScript with Vitest and Playwright | `*.test.*` and `*.spec.*` files, and the Playwright test directory | `vitest.config.*`, `vite.config.*` (its `test` key), `playwright.config.*`, `package.json` scripts | `import.meta.vitest` (Vitest in-source tests) |
| Shell check scripts | `<check-scripts>`, `<workflow-files>` | The workflow files | None |

Shell has no in-file tests; its path scope misses a check step written outside
`<check-scripts>`, such as a Makefile target or a `package.json` script, until the
repository names that file there. The Repository Standard's greenfield check
uses these names.

### Shared lint scaffolding

The per-case-starts and waits rules share one Ruff rule and two ESLint rules, so
their entries add lines to this scaffolding. Merge each table or object into the
repository's existing configuration rather than repeating a header.

Python, in `pyproject.toml` (in `ruff.toml`, drop the `tool.ruff.` prefix from
each table name):

```toml
[tool.ruff.lint]
extend-select = ["TID251"]

[tool.ruff.lint.flake8-tidy-imports.banned-api]
# The per-case-starts entry's lines, then the waits entry's lines.

[tool.ruff.lint.per-file-ignores]
# TID251 applies only to <test-paths>. Join every test glob inside this one
# negated key as {first,second}: a second negated key would lift the rule from
# the first one's files.
"!<test-paths>" = ["TID251"]
# Exempt paths. Each lifts all of TID251; the source-check lines restate the ban
# each path keeps.
"<lifecycle-path>" = ["TID251"]
"<real-time-path>" = ["TID251"]
"<start-owner>" = ["TID251"]
"<wait-helper>" = ["TID251"]
```

A repository that already bans product-code APIs through TID251 cannot share the
rule this way, because the negated key would lift those bans. It writes these
bans as source-check lines instead.

TypeScript, in `eslint.config.js` (or `.mjs` or `.ts`):

```js
// startBan: from the per-case-starts entry. waitBan: from the waits entry.
const testPaths = ['<test-paths>'];
const own = { paths: [], patterns: [], syntax: [] };

// One list of modules bans its static imports and re-exports, dynamic import(),
// require() calls and import-equals declarations. An entry with importNames bans
// those names in static imports and re-exports, and its whole module otherwise.
function ban(modules, message, selectors) {
  const entries = modules.map((m) => (typeof m === 'string' ? { name: m } : m));
  return {
    paths: entries.map((entry) => ({ ...entry, message })),
    syntax: [
      ...selectors,
      ...entries.flatMap(({ name }) => [
        { selector: `ImportExpression[source.value='${name}']`, message },
        { selector: `CallExpression[callee.name='require'][arguments.0.value='${name}']`, message },
        { selector: `TSImportEqualsDeclaration[moduleReference.expression.value='${name}']`, message },
      ]),
    ],
  };
}

function rules(...bans) {
  return {
    'no-restricted-imports': [
      'error',
      { paths: [...own.paths, ...bans.flatMap((b) => b.paths)], patterns: own.patterns },
    ],
    'no-restricted-syntax': ['error', ...own.syntax, ...bans.flatMap((b) => b.syntax)],
  };
}

export default [
  // ...the repository's own objects, then:
  {
    files: testPaths,
    ignores: ['<lifecycle-path>', '<real-time-path>', '<start-owner>', '<wait-helper>'],
    rules: rules(startBan, waitBan),
  },
  { files: ['<real-time-path>', '<wait-helper>'], rules: rules(startBan) },
  { files: ['<start-owner>'], rules: rules(waitBan) },
];
```

A later object's options for a rule replace an earlier object's for the same
file, so place these objects last. An existing configuration of either rule for
the same files is kept through `own`: its `paths` entries join `own.paths`, its
`no-restricted-syntax` selectors join `own.syntax`, and its `patterns` stay
under `own.patterns`.

Inline suppressions, and inline ESLint configuration of the two rules, as
source-check lines:

```sh
# Scan: <test-paths> (Python)
# Message: Exemption is by path. Move the case to <lifecycle-path> or <real-time-path>, or use the start owner or the wait helper.
grep -inE 'noqa([^:]|$)|noqa:[^#]*TID251' <files>

# Scan: <test-paths>, <start-owner>, <wait-helper>, <real-time-path> (TypeScript)
# Message: Exemption is by path. Move the case to <lifecycle-path> or <real-time-path>, or use the start owner or the wait helper.
grep -nE 'eslint-disable[^*]*no-restricted-|eslint-disable(-next-line|-line)?[[:space:]]*(\*/|--|$)|(\*|^)[[:space:]]*eslint([[:space:]][^*]*no-restricted-(imports|syntax)|([[:space:]-]([^*]|\*+[^*/])*\**)?$)' <files>
```

### Per-case expensive starts

Pattern: test code starts an expensive resource for a case, directly or through
a helper or fixture that lives as long as the case.

Invariant:

- Test code cannot start an expensive resource.
- The start owner starts each resource once per run per named configuration and
  refuses a second start.
- Cases isolate by their own records, identities and credentials.
- Lifecycle tests are the only test code that starts an instance.
- A case that runs the product's own command to completion does so through the
  command helper.
- Every existing per-case start is converted, and its lifecycle cases move to
  the lifecycle path. The Repository Standard says when.

Homes for legitimate uses:

- A resource a case uses: the start owner, by named configuration. Native forms:
  a session-scoped pytest fixture, which under a parallel plugin starts once per
  worker (see [run](#terms)); a Vitest `globalSetup` file, which runs once before
  the workers and provides values to tests; Playwright's `webServer`, which
  starts one server before the tests, and worker-scoped fixtures; a check script
  that starts services once and passes them to the tests. A pytest fixture of
  narrower scope may hand a case the running instance; it starts nothing.
- In Rust, `cargo test` builds each file under `tests/` as its own binary and
  runs the binaries one after another, so a start owner inside `tests/` starts
  once per binary. Keeping the integration tests in one binary, or starting the
  service in the check script and passing it to the tests, keeps one start per
  run.
- A case that asserts starting or stopping: the lifecycle path.
- The product's own command, run to completion: the command helper.

The stanzas ban by start primitive, so they are deliberately broader than the
invariant: they also flag a command that a test runs to completion and that is
neither an expensive resource nor the product's own command, such as a tool
that builds fixture data or a tool that converts the product's output so a case
can assert on it. Such a command has no home in this catalog. The case does that
work in-process, or the start owner prepares shared data once per run. The
lifecycle path and the command helper do not take it: a lifecycle test
asserts a start or stop, and the command helper runs only the product's own
command. A repository whose product needs such a command per case narrows the
rule through an approved specification that names the command, as
[rule upkeep](#rule-upkeep) says, and files an
[upstream report](#upstream-reports).

Rejected: a fixture-scope rule (the carriers found were helpers, not fixtures,
and case data stays per case). Rejected: an importable general harness as owner
(the first per-case fixture added to it recreates the pattern). Rejected: a
grandfathered offender list (it stops new files, not new cases in old files).
Rejected: a reason string or allowlist entry as permission to start (metadata
does not establish need).

Python with pytest. Add to the shared `banned-api` table:

```toml
"subprocess".msg = "Test code starts no expensive resource. Use the start owner's named configuration and isolate the case by its own records and credentials; run the product's own command through the command helper and build other fixture data in-process; a case that asserts a start or stop goes under <lifecycle-path>."
"os.system".msg = "Test code starts no expensive resource. Use the start owner's named configuration; run the product's own command through the command helper and build other fixture data in-process; a case that asserts a start or stop goes under <lifecycle-path>."
"os.popen".msg = "Test code starts no expensive resource. Use the start owner's named configuration; run the product's own command through the command helper and build other fixture data in-process; a case that asserts a start or stop goes under <lifecycle-path>."
"asyncio.create_subprocess_exec".msg = "Test code starts no expensive resource. Use the start owner's named configuration; run the product's own command through the command helper and build other fixture data in-process; a case that asserts a start or stop goes under <lifecycle-path>."
"asyncio.create_subprocess_shell".msg = "Test code starts no expensive resource. Use the start owner's named configuration; run the product's own command through the command helper and build other fixture data in-process; a case that asserts a start or stop goes under <lifecycle-path>."
"multiprocessing.Process".msg = "Test code starts no expensive resource. Use the start owner's named configuration; a case that asserts a start or stop goes under <lifecycle-path>."
"pexpect".msg = "Test code starts no expensive resource. Use the start owner's named configuration; run the product's own command through the command helper; a case that asserts a start or stop goes under <lifecycle-path>."
"selenium.webdriver.Chrome".msg = "Test code launches no browser. Take the browser from the start owner; a case that asserts a launch goes under <lifecycle-path>."
"selenium.webdriver.Firefox".msg = "Test code launches no browser. Take the browser from the start owner; a case that asserts a launch goes under <lifecycle-path>."
"selenium.webdriver.Edge".msg = "Test code launches no browser. Take the browser from the start owner; a case that asserts a launch goes under <lifecycle-path>."
"selenium.webdriver.Safari".msg = "Test code launches no browser. Take the browser from the start owner; a case that asserts a launch goes under <lifecycle-path>."
"selenium.webdriver.Remote".msg = "Test code launches no browser. Take the browser from the start owner; a case that asserts a launch goes under <lifecycle-path>."
"playwright.sync_api.sync_playwright".msg = "Test code launches no browser. Take the browser from the start owner; a case that asserts a launch goes under <lifecycle-path>."
"playwright.async_api.async_playwright".msg = "Test code launches no browser. Take the browser from the start owner; a case that asserts a launch goes under <lifecycle-path>."
"testcontainers".msg = "Test code starts no container. Use the start owner's named configuration; a case that asserts a start or stop goes under <lifecycle-path>."
"docker".msg = "Test code starts no container. Use the start owner's named configuration; a case that asserts a start or stop goes under <lifecycle-path>."
```

Ruff's exemption for the real-time path and the wait helper lifts this ban with
the wait ban, so this line restates it:

```sh
# Scan: <real-time-path>, <wait-helper>
# Message: Real-time tests and the wait helper start nothing. Use the start owner's named configuration; a case that asserts a start or stop goes under <lifecycle-path>.
grep -nE 'subprocess|os\.(system|popen)|create_subprocess_|multiprocessing|pexpect|sync_playwright|async_playwright|testcontainers|from[[:space:]]+os[[:space:]]+import[^#]*(system|popen|\([^)]*$)|import[[:space:]]+([^#]*,[[:space:]]*)?os[[:space:]]+as|(import|from)[[:space:]]+([^#]*,[[:space:]]*)?docker([^[:alnum:]_]|$)|webdriver(\.|[[:space:]]+import[^#]*)(Chrome|Firefox|Edge|Safari|Remote)([^[:alnum:]_]|$)|webdriver[[:space:]]+(import[^#]*\([^)]*$|as[[:space:]])' <files>
```

A start reached through the repository's own code, such as a fixture that
rebuilds a schema for every case through the repository's schema or migration
API or a wrapper that launches a browser, calls an API no shared stanza can
name. When the stack is known, the repository adds that API to the table as a
local rule.

Rust with `cargo test`:

```sh
# Scan: <test-paths>, except <lifecycle-path> and <start-owner>
# Message: Test code starts no process or container. Use the start owner's named configuration; run the product's own command through the command helper and build other fixture data in-process; a case that asserts a start or stop goes under <lifecycle-path>.
grep -nE 'process::(\{[^}]*)?(Command|$)|process::\*|Command::cargo_bin|assert_cmd|(^|[^[:alnum:]_])(duct|xshell)::|testcontainers|bollard' <files>
```

The line matches a path or import that reaches `Command` through `process::`,
a glob import of a `process` module, and a line that opens a grouped import of
one without closing it, so it skips an unrelated `Command` type. It cannot see a
`process` module imported under another name, such as
`use std::process as proc;`, or a start reached through a crate the line does
not name; review question R1 carries those.

TypeScript with Vitest and Playwright. Define before the shared scaffolding's
`export default`:

```js
const startMessage =
  'Test code starts no process, browser or container. Use the start owner (globalSetup, webServer or a worker-scoped fixture) and isolate the case by its own records and credentials; run the product\'s own command through the command helper and build other fixture data in-process; a case that asserts a start or stop goes under <lifecycle-path>.';
const startBan = ban(
  ['child_process', 'node:child_process', 'execa', 'cross-spawn', 'shelljs', 'shelljs/global', 'zx', 'zx/globals', 'testcontainers', 'dockerode'],
  startMessage,
  [
    { selector: "CallExpression[callee.property.name=/^launch/]", message: startMessage },
    { selector: "[source.value=/^@testcontainers./]", message: startMessage },
    { selector: "CallExpression[callee.name='require'][arguments.0.value=/^@testcontainers./]", message: startMessage },
    { selector: "TSImportEqualsDeclaration[moduleReference.expression.value=/^@testcontainers./]", message: startMessage },
  ],
);
```

The `launch` selector catches a browser type's `launch` calls in test code;
Playwright's own browser and page fixtures need none. The `@testcontainers`
selectors catch the per-service packages, such as `@testcontainers/postgresql`,
in static imports, re-exports, dynamic `import()`, `require()` calls and
import-equals declarations.

Shell check scripts:

```sh
# Scan: <check-scripts>, <workflow-files>, except <start-owner> and <lifecycle-path>
# Message: Start services once in the start owner (<start-owner>) and pass them to the steps that need them.
grep -nE 'docker[[:space:]]+(container[[:space:]]+)?(run|start)([[:space:]]|$)|docker(-|[[:space:]]+)compose([[:space:]].*)?[[:space:]](up|run|start)([[:space:]]|$)|nohup' <files>
```

A server sent to the background with `&` has no token that separates it from
independent steps run side by side, so review question R1 carries it.

Instance: every case of one suite called a helper that started the application
process with its supporting services, waited for readiness and tore it down. A
second suite started a proxy process per case. A server fixture written with no
scope ran per test. In another repository a function-scoped fixture dropped and
rebuilt the database schema for every case, and two browser tests launched a
browser per test function. Rust command-line tests started the service binary
once per test, written to mirror an existing test. For TypeScript and shell no
instance was observed; two homes were observed working: a browser suite's server
started once by the runner's own server setting, and services that a check
script started once and passed to the tests.

### Waits on the wall clock

Pattern: a test waits out real time, so it passes because time ran out.

Invariant: a test never passes because time ran out.

- A wait ends when its condition holds.
- Time the product owns is advanced on a clock the test controls.
- A fake blocks until the test releases it.
- Only real-time tests wait out a clock no test can control.

Homes for legitimate uses:

- The wait helper.
- A released gate for fakes: an event, channel or promise the test releases.
- An advanced clock: Vitest's `vi.useFakeTimers`, Playwright's clock, or Tokio's
  paused clock (`start_paused = true` on `#[tokio::test]`, with the `test-util`
  feature and the current-thread runtime).
- The real-time tests.

Accepted limits:

- A ban by name cannot see a timeout on something that never arrives.
- A controllable clock helps only when the product reads it. Tokio's paused
  clock does not affect `std::time`.
- Python has no built-in virtual clock, so the product takes its clock as a
  parameter where planning decides, or the proof is real-time.

Rejected: banning every timeout or synchronization primitive (it hits readiness
polls and cancellation proofs).

Python with pytest. Add to the shared `banned-api` table:

```toml
"time.sleep".msg = "A test passes when its condition holds. Wait through the wait helper (<wait-helper>), let a fake block on an Event the test sets, or give the product a clock the test advances. Waiting out a clock no test controls goes under <real-time-path>."
"asyncio.sleep".msg = "A test passes when its condition holds. Wait through the wait helper (<wait-helper>), let a fake block on an asyncio.Event the test sets, or give the product a clock the test advances. Waiting out a clock no test controls goes under <real-time-path>."
"anyio.sleep".msg = "A test passes when its condition holds. Wait through the wait helper (<wait-helper>), let a fake block on an anyio.Event the test sets, or give the product a clock the test advances. Waiting out a clock no test controls goes under <real-time-path>."
"trio.sleep".msg = "A test passes when its condition holds. Wait through the wait helper (<wait-helper>), let a fake block on a trio.Event the test sets, or give the product a clock the test advances. Waiting out a clock no test controls goes under <real-time-path>."
```

Ruff's exemption for the start owner lifts this ban with the start ban, so this
line restates it:

```sh
# Scan: <start-owner>
# Message: The start owner waits for readiness through the wait helper (<wait-helper>), never a fixed delay.
grep -nE '(^|[^[:alnum:]_])sleep([^[:alnum:]_]|$)' <files>
```

Rust with `cargo test`:

```sh
# Scan: <test-paths>, except <lifecycle-path>, <real-time-path> and <wait-helper>
# Message: A test passes when its condition holds. Wait through <wait-helper>; under #[tokio::test(start_paused = true)] move time with tokio::time::advance; let a fake wait on a channel the test releases. Waiting out a clock no test controls goes under <real-time-path>.
grep -nE '(thread|time)::(\{[^}]*)?(sleep|$)|(thread|time)::\*' <files>
```

TypeScript with Vitest and Playwright. Define before the shared scaffolding's
`export default`:

```js
const waitMessage =
  'A test passes when its condition holds. Wait through <wait-helper>; advance time with vi.useFakeTimers or Playwright\'s clock; let a fake wait on a promise the test resolves. Waiting out a clock no test controls goes under <real-time-path>.';
const waitBan = ban(
  [
    'timers/promises',
    'node:timers/promises',
    { name: 'timers', importNames: ['setTimeout'] },
    { name: 'node:timers', importNames: ['setTimeout'] },
  ],
  waitMessage,
  [
    { selector: "CallExpression[callee.name='setTimeout']", message: waitMessage },
    { selector: "CallExpression[callee.property.name='setTimeout']", message: waitMessage },
    { selector: "CallExpression[callee.property.name='waitForTimeout']", message: waitMessage },
  ],
);
```

The `timers` entries ban `setTimeout` by its imported name, so an alias cannot
hide it.

Shell check scripts:

```sh
# Scan: <check-scripts>, <workflow-files>, except <lifecycle-path>, <real-time-path> and <wait-helper>
# Message: Wait for a condition through the wait helper (<wait-helper>), which returns when it holds and raises at its bound.
grep -nE '(^|[^[:alnum:]_.-])sleep([[:space:]]|;|$)' <files>
```

Instance: Python cases slept through real session and token lifetimes to prove
renewal and expiry, and a setup helper slept after each statement; one
legitimate use was a fake that blocks on a sleep until the test cancels it,
whose home is a released gate. Rust cases slept through a real idle period,
fakes answered after a fixed delay, and watcher tests waited out real intervals,
while other tests in the same suites already paused the runtime's clock.
TypeScript cases waited on real timers to prove backoff or the absence of a
request, while neighbouring tests used fake timers. Shell check scripts held
only bounded readiness polls, which are the wait helper's legitimate use.

### Builds and installs that repeat or are not reused

Pattern: a run builds, installs, pulls or compiles the same inputs again, or
every run on a clean runner redoes work whose inputs have not changed.

Invariant:

- Within a run, nothing is built, installed, pulled or compiled twice from the
  same inputs.
- Across runs, work whose pinned inputs have not changed is restored from the
  repository's reuse path.
- Where the repository's map has recorded that no reuse path is available,
  rebuilding on each run is permitted, and the absence stays recorded with its
  cause until a later map revisits it.
- Passes with different inputs or outputs are different artifacts.

This rule has no ban: no sound ban exists for an absence. These carry it
instead:

- the start ban, which keeps builds and installs out of test code;
- the reuse path for each check's runner, or its recorded absence, decided at
  the map gate;
- the persona's vectors;
- review question R3;
- the build and install lines of the [check-step output](#check-step-output).

Nothing here requires a cache step. A repository may add a local rule once its
reuse path exists.

Reuse already exists in the native tools: prebuilt binaries in place of
compiling a tool from source, Docker build cache exported and imported in CI,
CI caches keyed and restored by key, builds skipped when their inputs are
unchanged, and snapshots keyed by checksum.

Rejected: a required cache step or other presence check (a no-op step satisfies
it). Rejected: generic bans on install, image-build or cache-bypass commands
(each hits legitimate uses and has no observed instance; one can still enter
through rule upkeep).

Instance: every run on a clean runner compiled a tool from source with
`cargo install`, pulled base images and reinstalled dependencies with `npm ci`
and `uv sync`, and one image was built twice in a run with `docker build` and
`docker compose build`. No workflow had a cache step. Reuse was also observed:
builds skipped when their inputs were unchanged, and snapshots keyed by
checksum.

### Independent work run one after another

Pattern: work that does not depend on other work waits for it.

Invariant: work that does not depend on other work never waits for it.

- Anything that forces one-at-a-time execution states its cause beside the
  setting. Forced-serial settings with no stated cause are banned.
- Check steps are separately invocable and declare what they depend on.
- Independent steps run side by side once the reuse path exists.
- Building once takes precedence over running side by side. Where side-by-side
  execution would repeat a build because no reuse path exists, the steps stay in
  sequence, and the recorded absence of a reuse path is their stated cause.
- A targeted check selects steps by the inputs each declares and never falls
  back to the full gate.
- A serial test runner whose parallel mode needs a new dependency is a decision
  recorded at the map gate. pytest runs cases one after another unless a
  parallel plugin such as pytest-xdist is a dependency, and `cargo test` runs its
  test binaries one after another; neither has a setting to ban.

Homes for legitimate uses: a setting that must stay serial carries its cause in
a comment on the same line, `serial-cause:` followed by the constraint it names,
such as a single server on a fixed port or the recorded absence of a reuse
path. A serial flag in a file that cannot hold a comment, such as `package.json`,
moves to a runner configuration file or check script.

The ban cannot see a single job that runs independent steps in sequence, or a
targeted mode that selects whole suites by changed path; review question S7
carries both.

Rejected: separate clean-runner jobs before a reuse path exists (they repeat
every build). Rejected: selecting individual tests by changed path in CI (it
trades cost for missed regressions). Rejected: mandating a parallel runner, a
clock library or a build cache tool (each needs the target's authorization).

The settings live in configuration and the cause in a comment, which no syntax
rule reads, so every ecosystem's stanza is a source-check line. Each line reads
an option's value after a space, `=`, either quote or a comma, so it also reads
an option split into list items, such as `addopts = ['-n', '1']`, and reads a
key and its value with or without quotes, such as `workers: '1'` or
`'workers': 1`. The lines flag `--numprocesses`, `--dist`, `--test-threads`,
`--workers`, `--maxWorkers` and `--jobs`, and pytest's `-n` as a quoted list
item, when only a closing quote, a comma or a line continuation follows on that
line, whatever value comes next.
They leave `-p` and `-j` unflagged there, since that would flag every plugin load
and every unlimited job count.

Python with pytest:

```sh
# Scan: <runner-config>, <check-scripts>, <workflow-files>
# Message: Let independent work run side by side. A setting that must stay serial states its cause on the same line as a "serial-cause:" comment naming the constraint.
grep -nE -e '-p["'\'',=[:space:]]*no:xdist|(-n["'\'',=[:space:]]*0|--numprocesses["'\'',=[:space:]]*[01])([^0-9]|$)|(^[[:space:]]*|pytest.*|PYTEST.*|addopts.*|["'\''])-n["'\'',=[:space:]]*1([^0-9]|$)|--dist["'\'',=[:space:]]*no([^a-z]|$)|(--(numprocesses|dist)["'\'']?|["'\'']-n["'\'']),?[[:space:]]*\\?$' <files> | grep -v 'serial-cause:'
```

The line counts `-n 1` only after `pytest`, `PYTEST` or `addopts` on the same
line, at the start of a line, as on a continuation line, or right after a quote,
because other commands, such as `head`, take `-n 1`.

Rust with `cargo test`:

```sh
# Scan: <runner-config>, <test-paths>, <check-scripts>, <workflow-files>
# Message: Let independent work run side by side. A setting that must stay serial states its cause on the same line as a "serial-cause:" comment naming the constraint.
grep -nE -e '--test-threads["'\'',=[:space:]]*1([^0-9]|$)|RUST_TEST_THREADS[^0-9]*1([^0-9]|$)|#\[(serial_test::)?(file_)?serial([](]|$)|--test-threads["'\'']?,?[[:space:]]*\\?$' <files> | grep -v 'serial-cause:'
```

TypeScript with Vitest and Playwright:

```sh
# Scan: <runner-config>, <test-paths>, <check-scripts>, <workflow-files>
# Message: Let independent work run side by side. A setting that must stay serial states its cause on the same line as a "serial-cause:" comment naming the constraint.
grep -nE -e '(maxW|w)orkers["'\'']?:([^,]*[?:])?[[:space:]]*["'\'']?1([^0-9.]|$)|(-j|--(maxW|w)orkers)["'\'',=[:space:]]*1([^0-9]|$)|--(maxW|w)orkers["'\'']?,?[[:space:]]*\\?$|fileParallelism["'\'']?:[[:space:]]*["'\'']?false|--fileParallelism=false|--no-file-parallelism|single(Thread|Fork)["'\'']?:[[:space:]]*["'\'']?true|--(([^n[:space:]]|n[^o[:space:]]|no[^-[:space:]])[^[:space:]]*)?single(Thread|Fork)(=["'\'']?true)?([^[:alnum:]_=]|$)|mode["'\'']?:[[:space:]]*.serial.|describe\.serial([^[:alnum:]_]|$)' <files> | grep -v 'serial-cause:'
```

The `workers` pattern also matches a worker count of one chosen by condition,
such as one on CI and the default elsewhere.

Shell check scripts and CI workflows:

```sh
# Scan: <check-scripts>, <workflow-files>
# Message: Let independent work run side by side. A setting that must stay serial states its cause on the same line as a "serial-cause:" comment naming the constraint.
grep -nE -e 'max-parallel["'\'']?:[[:space:]]*["'\'']?1([^0-9]|$)|(-j|--jobs)["'\'',=[:space:]]*1([^0-9]|$)|--jobs["'\'']?,?[[:space:]]*\\?$' <files> | grep -v 'serial-cause:'
```

Instance: a browser suite was forced to one worker; a single server on a fixed
port was the likely cause, and it was recorded nowhere. pytest ran serially
because no parallel runner was a dependency, and `cargo test` ran test binaries
one after another by default. Elsewhere a coverage run and a unit-test run were
forced serial, each with a recorded cause. Lint, type checks, tests, builds and
browser tests ran in sequence in one job with no dependency between them
recorded, and a targeted check ran nearly the whole gate.

## Review questions

Answer each question yes or no, with the file and line that decides it. Yes
passes. In a repository that has not yet converted, answer a question about a
missing structure item "not yet converted" (see
[before a repository upgrades](#before-a-repository-upgrades)).

Applicability:

- A1. Does the change touch a governed path: test code, fixtures, helpers,
  fakes, runner or lint configuration, check or delivery scripts, build files the
  checks use, or CI workflows? If no, the remaining questions are not
  applicable; name the paths that decided it.
- A2. Does each governed change sit inside the path scope of the stanza for its
  rule, with any in-file test module holding only in-process cases?
- A3. Does every change under an exempt path (the privileged areas, the start
  owner and the wait helper) belong there, rather than move code there to escape
  a rule, and is any edit to the exempt-path list named by an approved
  specification?

Named structure:

- S1. Does every expensive resource a changed case outside the lifecycle path
  uses come from the start owner, which cases cannot call to start anything and
  which refuses a second start?
- S2. Is every start-only setting a changed case outside the lifecycle path
  needs declared by name in the start owner, with everything else passed as case
  data?
- S3. Does every changed wait for a condition go through the wait helper, or
  for a fake through a gate the test releases, and does the helper still return
  when its condition holds, raise at its bound and offer no fixed delay?
- S4. Is every changed case that starts or stops an instance under the
  lifecycle path, citing the lifecycle state it asserts?
- S5. Is every changed case that waits out an uncontrollable clock and starts
  nothing under the real-time path, citing that clock?
- S6. Does each changed check that builds, installs or pulls restore unchanged
  pinned inputs from the reuse path, or cite the recorded absence?
- S7. Is each changed check step separately invocable with its dependencies
  declared, running beside independent steps unless a stated cause holds it, and
  does the targeted mode select steps by declared inputs without falling back to
  the full gate?
- S8. Is the lint stage still the first step in every mode, with nothing built
  or started for tests before the pattern rules pass?

Rules:

- R1. Does changed test code outside the lifecycle path start no expensive
  resource and add no case to an existing per-case start?
- R2. Does every changed test pass only when its condition holds, never because
  time ran out?
- R3. Within a run, is each artifact built, installed or pulled once from the
  same inputs, and does its output line say whether it was reused?
- R4. Does every changed setting that forces one-at-a-time execution state, on
  its own line, a cause that names a real constraint?

Marks:

- Mark a finding "rule candidate" when a primitive, import, setting or token
  identifies its pattern, the identification condition of
  [rule upkeep](#rule-upkeep).
- Mark a finding "upstream" when its cause traces to Orca Pod text, a trigger
  for an [upstream report](#upstream-reports).

A finding can carry both marks or neither. The verification-cost persona and
the verification-cost axis of [`code-review`](../../code-review/SKILL.md) mark
their findings this way.

## Rule upkeep

[`reflect`](../../reflect/SKILL.md) owns how a correction becomes enforcement,
its proof and its follow-through. This catalog adds only what is specific to
verification cost: admission conditions, stanzas, homes for legitimate uses and
review questions.

A new rule enters when all of these hold:

- an instance was observed in an adopted repository;
- a primitive, import, setting or token identifies it;
- every legitimate use found has a home;
- the native lint run fails on the instance and passes after conversion (that
  run is the evidence; there is no test of the rule);
- its message says what to do instead.

Anyone can find a candidate: the review axis, the persona, `reflect`, a
conversion or the operator.

- Adding a rule together with conversion of everything it flags needs no new map
  decision. The conversion rides the current task when it is adjacent, and
  otherwise becomes a scoped issue.
- Removing or narrowing a rule, or adding an exempt path, needs an approved
  specification that names it.
- A rule whose mistake can no longer happen is retired.

The loop is seeded with the four rules above, with no up-front sweep for other
patterns. The map that designed this catalog admitted the seed rules. Their
native-run evidence comes from the worked-example repository's conversion. A
stanza for another ecosystem comes from the change that introduces that stack.

Rejected: inline exceptions with an expiry and a human approval (an approval
gate; exemptions here are paths). Rejected: failing only when a change adds
violations to a baseline (existing hits are converted instead).

## Upstream reports

An adopted repository files an upstream report when:

- it adds a local rule or stanza that the catalog lacks;
- it narrows a catalog rule locally;
- a review, persona or reflection traces a cause to Orca Pod text;
- an adoption missed an existing instance.

A report holds the pattern, the ecosystem, the Orca Pod text implicated, what
was done locally, the proposed change, and a public summary. The public summary
is a few generic sentences with no repository name, path, identifier or log.

The originating repository records the report in its own tracker under
`upstream:orca-pod`, the label the Repository Standard's tracker conventions
define. An Orca Pod session pulls reports during
[`whats-next`](../../whats-next/SKILL.md) discovery, under the public-work
policy:

- Intake changes nothing in the originating repository.
- It searches Orca Pod issues, open and closed, for the public summary, and
  Orca Pod's tracker deduplication decides whether a match covers the report.
- It files each new report as a sanitized Orca Pod issue that carries the public
  summary word for word.

Anything urgent or outside this form still needs per-report approval. There is
no scheduled automation.

The originating repository closes its own report. A Standards Upgrade there
closes it once the revision it upgrades to resolves the report, or once Orca Pod
has declined it. Until then the report stays open.

## Before a repository upgrades

Host installation binds sessions started after it. A repository keeps its old
checks until its own upgrade. In that interval:

- New test code in every repository follows the rules: no new per-case start,
  wall-clock wait or forced-serial setting, and no new use of an existing one.
- The review axis and the panel persona report those as findings. They report a
  repository's missing lint stage, privileged paths or start owner as "not yet
  converted", and do not ask an ordinary task to build them.
- Existing instances wait for that repository's Standards Upgrade or its own
  map. The session that finds them lists them once in one scoped issue in that
  repository, under its tracker deduplication.
- A ticket that can only be met by adding to an existing instance is held and
  returns to that repository's planning.
- Host installation converts nothing and authorizes no conversion.

Rejected: nothing binding until a repository upgrades (the patterns would keep
growing in the interval). Rejected: converting existing instances inside
ordinary tasks (it would enlarge them past their approved scope).
