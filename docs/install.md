# Installing Orca Pod

`machine/install.py` sets up a macOS host for Orca Pod: the shared skills, the
generated Claude and Codex roles, the global rules, the managed keys in both
agents' settings, Orca's own skills, Orca's app settings and two scheduled Orca
automations. It owns specific
paths and keys inside the default agent homes (`~/.claude`, `~/.codex`,
`~/.agents`) and never takes over a whole home. It needs Python 3.11+ (standard
library only) and runs on macOS only.

## Usage

Run it from a clean checkout of a published revision, that is, one whose HEAD
is on `origin/test` or `origin/main` (run `git fetch` first):

```bash
export ORCA_POD_PYTHON="$(command -v python3)"   # any Python 3.11+; see below
"$ORCA_POD_PYTHON" machine/install.py              # dry run (the default): print the plan, write nothing
"$ORCA_POD_PYTHON" machine/install.py --apply      # install or update
"$ORCA_POD_PYTHON" machine/install.py --uninstall  # remove what the installer owns, restoring backups
```

When the host's `python3` is older than 3.11, select another interpreter, for
example `export ORCA_POD_PYTHON="$(uv python find 3.13)"`. The installer runs its
child helpers (`roster/generate.py`, `machine/orca_settings.py`) with
`ORCA_POD_PYTHON` too, falling back to its own interpreter.

The dry run lists every action per target (`create`, `update`, `replace (backed
up)`, `adopt`, `remove`). It shows a diff only for content Orca Pod owns: a file
it wrote, and the owned lines of the managed `config.toml` blocks. Other lines of
`config.toml` are counted (`… N unowned line(s) not shown …`), never printed, and
the JSON files show only the owned keys being set. It also lists the Orca steps,
including each automation it would create, update, adopt or remove, the sign-in
status, notes and any refusals. It exits 2 when something is refused;
`--apply` then writes nothing.

Before reading or writing anything, every target, state and backup path is
checked to lie below the selected home with no symlinked or non-directory
component; a symlinked `~/.codex`, for example, is refused. A target or backup
that is a regular file with more than one hard link is refused too, before it is
read, backed up or replaced, because its contents also live outside the managed
path. `--uninstall` runs the same checks on every path in the manifest, and
refuses a manifest entry that is absolute, contains `..` or lies outside the
managed roots. Every run also refuses, before reading or writing anything, a
manifest that records a JSON key other than those in [Managed targets](#managed-targets)
(plus the top-level `effortLevel` earlier revisions owned, and the
`modelSettings.<model>.effortLevel` of any Claude model id), or a record not in
the shape the installer writes. An automation record must be exactly an Orca
automation UUID and an `adopted` flag under a plain name, with no id recorded twice.

| Option | Effect |
| --- | --- |
| `--home <dir>` | Resolve every target under `<dir>` instead of `~`. Any other directory is a scratch run, which skips Orca's skills and app settings and the sign-in checks, and lists the automations as planned without reading or changing Orca's live automations. |
| `--adopt-config` | Move managed keys that `~/.codex/config.toml` defines outside the Orca Pod blocks into those blocks. Without it, such keys are refused. |
| `--skip-orca-settings` | Leave Orca's app settings and automations alone. |
| `--allow-unpublished` | For testing only: install from a dirty or unpublished checkout. |
| `--verbose` | Also list unchanged paths. |

Re-running `--apply` is idempotent: when everything is current it changes no
file, including the manifest. An owned JSON key that a newer revision no longer
sets, such as the top-level `effortLevel` earlier revisions wrote, gets its
previous value back on the next `--apply` and leaves the manifest, unless it
changed since install. Rerun it after pulling a new Orca Pod revision,
and after an Orca upgrade, which can change Orca's skills and its Codex hooks.

## Managed targets

| Target | What the installer manages |
| --- | --- |
| `~/.agents/skills/<name>/` | A copy of each `skills/<name>/` package in the checkout (every tracked package with a `SKILL.md`). Codex reads this folder directly. |
| `~/.claude/skills/<name>` | A relative symlink to `~/.agents/skills/<name>`. |
| `~/.claude/agents/<role>.md`, `~/.codex/agents/<role>.toml` | Native roles rendered by `roster/generate.py` from `roster/roles.toml`. |
| `~/.codex/orca-pod-sec.config.toml` | The SEC Daybreak profile (`codex --profile orca-pod-sec`), also from the generator. |
| `~/.codex/AGENTS.md`, `~/.claude/rules/orca-pod.md` | The global rules in [`machine/global-rules.md`](../machine/global-rules.md). |
| `~/.codex/config.toml` | Managed blocks only (below): root `model = "gpt-6.1-sol"` and `model_reasoning_effort = "high"`, `[agents] enabled = true`, `[features] hooks = true`, and hook trust for Orca's hooks. Every other line, comment and the end of the file are preserved byte for byte. |
| `~/.claude/settings.json` | Top-level `model` and the nested `modelSettings.<model>.effortLevel`, both from the roster's ORC default, `skipDangerousModePermissionPrompt: true`, and `theme: "dark"` only when no theme is set. Claude Code takes a session's default effort from that model's `modelSettings` entry; it treats a top-level `effortLevel` as a legacy value and does not apply it at startup, so the installer does not own one. Other `modelSettings` entries, and other fields of the model's entry, are left alone; uninstall removes the entry, or `modelSettings`, only when the installer created it and nothing else is left in it. Orca's hooks and status line, and every other key, keep their order and values; the file keeps its indent style and final newline, though JSON spelling such as escapes may be normalized. |
| `~/.claude.json` | First-run keys, set only when missing: `hasCompletedOnboarding: true` and `lastOnboardingVersion` (from `claude --version`). Running Claude sessions rewrite this file, so it is only written when a key is missing. |
| Orca's skills | `orca skills install --skill orca-cli --skill orchestration --agent claude,codex`, then `orca skills update` for the same skills. Orca owns these copies. |
| Orca app settings | `branchPrefix: "custom"`, `branchPrefixCustom: "orca"` and `agentPermissionDefault: "full-access"`, applied by [`machine/orca_settings.py`](../machine/orca_settings.py) (below). |
| Orca automations | The automations in [`machine/automations.toml`](../machine/automations.toml), through `orca automations create/edit/remove` (below). |

Credentials are never copied or written. `config.toml`, `settings.json` and
`~/.claude.json` can hold credentials and private state, so the installer never
backs them up whole: the manifest keeps only the previous values of the keys and
blocks it owns.

Claude per-project trust is not seeded. Orca's "Trust the folder" setting applies
to every agent Orca launches, including orchestration workers and automations;
[#14](https://github.com/jdip/orca-pod/issues/14) verifies that unattended
launches start without a trust prompt.

### Codex config blocks

The standard library has no TOML writer, so the installer owns clearly marked
blocks in `~/.codex/config.toml`:

```toml
# >>> orca-pod managed: root >>> machine/install.py rewrites this block; edit roster or rerun instead
model = "gpt-6.1-sol"
model_reasoning_effort = "high"
# <<< orca-pod managed: root <<<
```

The root block sits before the first table. The `agents` and `features` blocks
go inside an existing `[agents]` or `[features]` table, or carry their own
header at the end of the file. The `hooks.state` block holds one table per Orca
hook. A statement, comment or blank line added inside a block is kept byte for
byte, in order, just after the block on the next run and on uninstall.
A block that carries its own table header keeps that header on uninstall when a
foreign key inside or just after it still needs it, so such keys stay in their
table. Markers count only as comment lines between statements, never as text
inside a multi-line string, and an unknown `orca-pod managed` block is refused.
Each rewrite, and each uninstall, must parse and must equal the original parsed
file with only the owned keys changed, or the installer refuses.

If the file already defines a managed key outside the blocks, the dry run and
`--apply` refuse and list the lines. `--adopt-config` removes those lines, writes
the managed values into the blocks and records the original lines so uninstall
can put them back.

### Codex hook trust

Codex asks for review of any hook in `~/.codex/hooks.json` whose
`[hooks.state."<hooks.json path>:<event>:<group>:<handler>"]` entry has no matching
`trusted_hash`, and that prompt stalls unattended launches. The installer seeds
`enabled = true` and the hash only for a hook that exactly matches a known Orca
hook: `install.py` pins known sets of Orca's Codex hooks, each giving the
complete command, event and timeout of every handler, taken from Orca's hook
generator (Orca 1.4.240; 1.4.241 writes the same set). Trust follows content,
not the Orca version, so an Orca update that leaves its hooks unchanged needs no
repository change. The handler must equal its event's pinned handler field for
field, in a group with no matcher. Any other hook, including one whose command
merely starts with Orca's marker, gets no new trust and is listed in a note.

When an Orca update changes a hook, the installer does not silently untrust it.
A trust entry the installer already owns whose hook no longer matches keeps its
recorded hash and is listed in a note; that hash does not match the changed
hook, so Codex asks for review of it until a new pinned set is added for the
changed handlers. Uninstall removes kept entries with the rest.

The hash is derived exactly as Codex 0.164 computes it (`hook_hash` in
`codex-rs/hooks/src/engine/discovery.rs`): SHA-256 over the compact JSON, with
sorted keys, of `{"event_name": <snake_case event>, "matcher": <matcher, for
events that take one>, "hooks": [<normalized handler>]}`. The normalized handler
is `type`, `command`, `async` and `timeout`, plus `statusMessage` and a
non-default `additionalContextLimit` when set. The timeout defaults to 600 s, or
for `session_end` and `interrupt` to 1 s, clamped to 1–3 s. The key uses the canonical
(symlink-resolved) path of `hooks.json`. The hash depends only on content, so it
works on a brand-new host. If Orca has not written `hooks.json` yet, nothing new
is seeded; run `--apply` again after Orca installs its hooks. A future Codex release
that changes the algorithm shows up as the review prompt returning.

### Orca app settings

Orca has no settings CLI, so the installer launches `machine/orca_settings.py`
detached and waits on its result file under `~/.local/state/orca-pod/`. The
helper is gated on the settings schema verified in
[#6](https://github.com/jdip/orca-pod/issues/6) and
[#38](https://github.com/jdip/orca-pod/issues/38), not on the Orca version: it
requires a supported settings `domain_version` (1 today) and a read-only check
that each target key exists with the expected type and, for `branchPrefix` and
`agentPermissionDefault`, one of the values Orca accepts, for both the current
and the new value. It repeats the check after quitting Orca, before the backup and
write. The Orca version is informational: the helper's result file and the
manifest record it. The installer first records the previous values in the
manifest. The helper quits Orca gracefully (never
force-killing it), saves the previous `settings` document (its payload, hash,
revision and timestamp, nothing else from the profile store) to an owner-only
file under `backups/<timestamp>/`, patches the document, relaunches Orca and
verifies the values survived startup. If anything fails after the write, it
restores the saved document before Orca starts again, quitting Orca first when
the failure shows up after the relaunch. The installer keeps the restoration
record in the manifest until the change is verified as applied or as restored.
Agent sessions survive the restart. When the values already match, nothing is
restarted. When the schema check fails it refuses and changes nothing; set
**Branch prefix** to custom `orca` and the default agent permission to full
access by hand in Orca's settings and rerun with `--skip-orca-settings`.

### Orca automations

[`machine/automations.toml`](../machine/automations.toml) declares two
automations. Each names a roster role, and runs with that role's default
provider, model and effort from [`roster/roles.toml`](../roster/roles.toml),
passed as `--extra-agent-args`:

| Automation | Schedule (host local time) | Role · provider · model · effort | Runs |
| --- | --- | --- | --- |
| `Orca Pod: daily cleanup sweep` | `30 6 * * *`, daily at 06:30 | OPS · Codex · `gpt-6.1-sol` · high (`--model gpt-6.1-sol -c model_reasoning_effort=high`) | The `cleanup-task-artifacts` daily sweep as a dry run. It reports Orca-owned leftovers and their dispositions and removes nothing; its prompt grants no removal authority. |
| `Orca Pod: engineering brief` | `0 7 * * 1,4`, Mondays and Thursdays at 07:00 | WRK · Claude · `claude-opus-5-5` · high (`--model claude-opus-5-5 --effort high`) | The `engineering-brief` skill's scheduled edition, with the weekly watchlist review when it is due. Every draft, note, report and render output stays in the archive the skill's `history.py context` returns. It authorizes no topic workspaces, repository changes, commits, pushes, publication, tracker writes or prerequisite repairs elsewhere. Its renderer writes no bytecode or pip cache and keeps its temporary files in the archive. |

The sweep is operational diagnosis on the host, which is the OPS role. The brief
is researched writing with its own acceptance check, saved to the skill's
private archive. That makes it a bounded piece of owned output, which is the WRK
role, and map #1 found Opus 5.5 leads document work. OPS's
`workspace-write` sandbox is not passed, since Orca accepts only model and effort
as extra arguments. Each run gets Orca's default Codex permission instead.

Both run in the repository's primary checkout as an existing workspace
(`--workspace-mode existing`, a fresh session per run). The installer resolves
that checkout from the Git common directory of the checkout it runs from, then
finds it in `orca repo list` and its main worktree in `orca worktree list`. If
Orca does not know the checkout, the dry run and `--apply` refuse; add it with
`orca repo add --path <primary checkout>` and rerun.

Each run compares Orca's live automations (`orca automations list`) with the
manifest:

- Orca Pod owns an automation only when the manifest records its id and Orca's
  live automation with that id still has the recorded name. Orca's CLI offers no
  field that could carry an installer marker, so the name and id together are the
  ownership check. When the names differ, the dry run and `--apply` refuse and
  change nothing: rename the automation back in Orca, or remove its record from
  the manifest. `--apply` rereads the automation with `orca automations show` just
  before each edit or removal and refuses if its name no longer matches.
- An automation the manifest owns is left alone when its name, prompt, provider,
  extra arguments, trigger, workspace and session mode match. Otherwise `--apply`
  updates it in place with `orca automations edit`.
- An owned automation that is gone from Orca is created again.
- A new automation is created enabled. Disabling it in Orca is kept; the dry run
  notes it.
- An automation with the same name that the manifest does not own is adopted
  when it already matches the definition and sets none of the options the table
  does not declare: no precheck (or precheck timeout), the host's own timezone,
  Orca's default missed-run grace window, the local host, and no base branch or
  setup decision. Otherwise the installer refuses, since adopting it would either
  keep configuration Orca Pod does not manage or silently clear it: rename or
  remove it in Orca, then rerun.
- An owned automation the table no longer declares is removed. An adopted one is
  only dropped from the manifest.

The manifest records each owned automation's id as soon as it is created or
adopted. `--apply` handles the automations before the Orca settings patch, which
restarts Orca.

On-demand runs stay available. Run an automation now with
`orca automations run <id>`, using the full id from `orca automations list`, and
follow it with `orca automations runs --id <id>`. You can also invoke either
skill directly in an agent session.

## What stays manual

Sign in to both agents once per host. When `--apply` finds an agent signed out
and runs in a terminal, it starts the login; otherwise it prints the command:

```bash
claude auth login --claudeai
codex login --device-auth
```

## Manifest, backups and recovery

The installer records what it owns in `~/.local/state/orca-pod/manifest.json`:
each owned path with its content hash and backup, each owned key and block with
its previous value, the directories it created, the source revision, the id of
each automation it owns and, around an Orca settings change, the previous Orca
values. Before replacing a whole file
it did not write, it copies the original to
`~/.local/state/orca-pod/backups/<timestamp>/`, mirroring the path under the
home. The state and backup directories are owner-only (0700) and their files
0600; the manifest and helper results are written to a fresh temporary file and
renamed into place.

`--uninstall`:

- first removes the Orca automations it created, keeping adopted ones, so no
  schedule outlives the skills and rules it runs. Each removal is checked against
  the recorded name as above. With a scratch `--home` or `--skip-orca-settings`,
  when Orca's automations cannot be listed, when a name does not match or when a
  removal fails, it stops before changing any file, key or Orca setting and keeps
  the manifest, so a rerun can finish the uninstall;
- removes every owned path, restoring the backed-up original where one exists;
  a copy you changed since install is backed up first;
- removes only the managed blocks and keys from `config.toml`, `settings.json`
  and `~/.claude.json`, restoring their previous values and putting adopted
  original lines back, and keeps every later change; a file the installer created
  is removed only when nothing but its owned keys and blocks is left in it,
  otherwise the rest stays in place and is reported as kept;
- restores the previous Orca app settings through the helper, unless they have
  changed since install;
- removes the directories it created when they are empty, and the manifest.

Orca's own skills stay installed; manage them in Orca. Backups are kept. If
uninstall cannot remove keys cleanly, it leaves that file as is, reports a
problem, keeps the manifest as `manifest-<timestamp>.incomplete.json` (with the
previous key values) and leaves the backups for manual recovery: copy a replaced
file back from `backups/<timestamp>/`.

## Limits

The containment checks inspect each path just before using it, but the installer
still opens and renames by path. A process running as the same user that
atomically swaps a directory or link in the home while the installer runs (for
example with `renamex_np` and `RENAME_SWAP`) can redirect a write. Such a process
can already change anything in that account, so this race is accepted, as for
the roster generator ([#9](https://github.com/jdip/orca-pod/issues/9)).

Orca keeps no ownership marker on an automation, so the installer recognizes the
automations it owns by the ID and name recorded in its private manifest, and
re-reads each one just before changing it. It only ever creates, edits or removes
automations whose name starts with `Orca Pod: `, so a tampered manifest cannot
reach your other automations. A process that can rewrite the manifest runs as you
and could change any automation directly, so the remaining case (a forged record
for another `Orca Pod: ` automation) is accepted like the race above.
