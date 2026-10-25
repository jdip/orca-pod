# Installing Orca Pod

`machine/install.py` sets up a macOS host for Orca Pod: the shared skills, the
generated Claude and Codex roles, the global rules, the managed keys in both
agents' settings, Orca's own skills and Orca's app settings. It owns specific
paths and keys inside the default agent homes (`~/.claude`, `~/.codex`,
`~/.agents`) and never takes over a whole home. It needs Python 3.11+ (standard
library only) and runs on macOS only.

## Usage

Run it from a clean checkout of a published revision, that is, one whose HEAD
is on `origin/test` or `origin/main` (run `git fetch` first):

```bash
python3 machine/install.py              # dry run (the default): print the plan, write nothing
python3 machine/install.py --apply      # install or update
python3 machine/install.py --uninstall  # remove what the installer owns, restoring backups
```

Use `ORCA_POD_PYTHON="$(uv python find 3.13)"` or another 3.11+ interpreter when the
host's `python3` is older.

The dry run lists every action per target (`create`, `update`, `replace (backed
up)`, `adopt`, `remove`), with a diff for each changed configuration file and
replaced file. It also lists the Orca steps, sign-in status, notes and any
refusals. It exits 2 when something is refused; `--apply` then writes nothing.

| Option | Effect |
| --- | --- |
| `--home <dir>` | Resolve every target under `<dir>` instead of `~`. Any other directory is a scratch run, which skips Orca's skills and app settings and the sign-in checks. |
| `--adopt-config` | Move managed keys that `~/.codex/config.toml` defines outside the Orca Pod blocks into those blocks. Without it, such keys are refused. |
| `--skip-orca-settings` | Leave Orca's app settings alone. |
| `--allow-unpublished` | For testing only: install from a dirty or unpublished checkout. |
| `--verbose` | Also list unchanged paths. |

Re-running `--apply` is idempotent: when everything is current it changes no
file, including the manifest. Rerun it after pulling a new Orca Pod revision,
and after an Orca upgrade, which can change Orca's skills and its Codex hooks.

## Managed targets

| Target | What the installer manages |
| --- | --- |
| `~/.agents/skills/<name>/` | A copy of each `skills/<name>/` package in the checkout (every tracked package with a `SKILL.md`). Codex reads this folder directly. |
| `~/.claude/skills/<name>` | A relative symlink to `~/.agents/skills/<name>`. |
| `~/.claude/agents/<role>.md`, `~/.codex/agents/<role>.toml` | Native roles rendered by `roster/generate.py` from `roster/roles.toml`. |
| `~/.codex/orca-pod-sec.config.toml` | The SEC Daybreak profile (`codex --profile orca-pod-sec`), also from the generator. |
| `~/.codex/AGENTS.md`, `~/.claude/rules/orca-pod.md` | The global rules in [`machine/global-rules.md`](../machine/global-rules.md). |
| `~/.codex/config.toml` | Managed blocks only (below): root `model = "gpt-6.1-sol"` and `model_reasoning_effort = "high"`, `[agents] enabled = true`, `[features] hooks = true`, and hook trust for Orca's hooks. Every other line is preserved byte for byte. |
| `~/.claude/settings.json` | `model` and `effortLevel` from the roster's ORC default, `skipDangerousModePermissionPrompt: true`, and `theme: "dark"` only when no theme is set. Orca's hooks and status line, and every other key, are preserved. |
| `~/.claude.json` | First-run keys, set only when missing: `hasCompletedOnboarding: true` and `lastOnboardingVersion` (from `claude --version`). Per-project trust is not seeded; Orca's "Trust the folder" covers the agents it launches. Running Claude sessions rewrite this file, so it is only written when a key is missing. |
| Orca's skills | `orca skills install --skill orca-cli --skill orchestration --agent claude,codex`, then `orca skills update` for the same skills. Orca owns these copies. |
| Orca app settings | `branchPrefix: "custom"` and `branchPrefixCustom: "orca"`, applied by [`machine/orca_settings.py`](../machine/orca_settings.py) (below). |

Credentials are never read, copied or written.

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
hook. A statement Codex adds inside a block is kept, outside it, on the next run.
Each rewrite must parse and must leave every other key's value unchanged, or the
installer refuses.

If the file already defines a managed key outside the blocks, the dry run and
`--apply` refuse and list the lines. `--adopt-config` removes those lines, writes
the managed values into the blocks and records the original lines so uninstall
can put them back.

### Codex hook trust

Codex asks for review of any hook in `~/.codex/hooks.json` whose
`[hooks.state."<hooks.json path>:<event>:<group>:<handler>"]` entry has no matching
`trusted_hash`, and that prompt stalls unattended launches. The installer seeds
`enabled = true` and the hash for each command hook Orca wrote (commands that
start with `: orca-agent-hook-form=`), and never for other hooks.

The hash is derived exactly as Codex 0.164 computes it (`hook_hash` in
`codex-rs/hooks/src/engine/discovery.rs`): SHA-256 over the compact JSON, with
sorted keys, of `{"event_name": <snake_case event>, "matcher": <matcher, for
events that take one>, "hooks": [<normalized handler>]}`. The normalized handler
is `type`, `command`, `async` and `timeout`, plus `statusMessage` and a
non-default `additionalContextLimit` when set. The timeout defaults to 600 s, or
for `session_end` and `interrupt` to 1 s, clamped to 1–3 s. The key uses the canonical
(symlink-resolved) path of `hooks.json`. The hash depends only on content, so it
works on a brand-new host. If Orca has not written `hooks.json` yet, nothing is
seeded; run `--apply` again after Orca installs its hooks. A future Codex release
that changes the algorithm shows up as the review prompt returning.

### Orca app settings

Orca has no settings CLI, so the installer launches `machine/orca_settings.py`
detached and waits on its result file under `~/.local/state/orca-pod/`. The
helper is gated on Orca and settings-document versions verified in
[#6](https://github.com/jdip/orca-pod/issues/6). It quits Orca gracefully
(never force-killing it), backs up the profile store, patches the settings
document, relaunches Orca and verifies the values survived startup. Agent
sessions survive the restart. When the values already match, nothing is
restarted. On an unverified Orca version it refuses and changes nothing; set
**Branch prefix** to custom `orca` by hand in Orca's settings and rerun with
`--skip-orca-settings`.

## What stays manual

Sign in to both agents once per host. When `--apply` finds an agent signed out
and runs in a terminal, it starts the login; otherwise it prints the command:

```bash
claude auth login --claudeai
codex login --device-auth
```

## Manifest, backups and recovery

The installer records what it owns in `~/.local/state/orca-pod/manifest.json`:
each owned path with its content hash and backup, each owned key with its
previous value, the directories it created, the source revision and, after an
Orca settings change, the previous Orca values. Before replacing or editing
anything it did not write, it copies the original to
`~/.local/state/orca-pod/backups/<timestamp>/`, mirroring the path under the
home.

`--uninstall`:

- removes every owned path, restoring the backed-up original where one exists;
  a copy you changed since install is backed up first;
- restores `config.toml`, `settings.json` and `~/.claude.json` byte for byte from
  their backups when they are unchanged since the installer last wrote them;
  otherwise it removes only the managed blocks and keys in place, keeping later
  changes and putting adopted original lines back;
- restores the previous Orca app settings through the helper, unless they have
  changed since install;
- removes the directories it created when they are empty, and the manifest.

Orca's own skills stay installed; manage them in Orca. Backups are kept. If
uninstall cannot remove keys cleanly, it reports a problem, keeps the manifest as
`manifest-<timestamp>.incomplete.json` and leaves the backups for manual
recovery: copy the file you need from `backups/<timestamp>/` back into place.
