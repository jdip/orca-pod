#!/usr/bin/env python3
"""Own effort-scoped Wayfinder-map and implementation-backlog selections."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from typing import Any


STATE_VERSION = 1
STATE_DIRECTORY = "orca-pod-selection-scopes"
LEGACY_PATHS = {"map": "orca-pod-wayfinder-map", "backlog": "orca-pod-implementation-backlog"}
LABELS = {"map": "wayfinder:map", "backlog": "implementation:backlog"}
GIT_TIMEOUT_SECONDS = 10
SAFE_OWNER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
SAFE_SCOPE = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
WINDOWS_DEVICES = {"con", "prn", "aux", "nul", *(f"com{number}" for number in range(1, 10)), *(f"lpt{number}" for number in range(1, 10))}


class SelectionError(Exception):
    """A user-actionable selection failure."""


def fail(message: str) -> None:
    raise SelectionError(message)


def safe_owner(value: str, label: str) -> str:
    if not SAFE_OWNER.fullmatch(value) or value in {".", ".."}:
        fail(f"{label} must be a stable identifier containing only letters, digits, '.', '_', ':', or '-'")
    return value


def safe_scope(value: str) -> str:
    if not SAFE_SCOPE.fullmatch(value) or value in WINDOWS_DEVICES:
        fail("scope must be a portable lowercase identifier containing only letters, digits, '_', or '-'")
    return value


def require_text(value: str, label: str) -> str:
    if not value or any(character in value for character in "\r\n\x00"):
        fail(f"{label} must be one nonempty line")
    return value


def positive_generation(value: str) -> int:
    try:
        generation = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("generation must be a positive integer") from error
    if generation < 1:
        raise argparse.ArgumentTypeError("generation must be a positive integer")
    return generation


def common_git_directory() -> Path:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            check=True,
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        fail(
            f"git rev-parse did not finish within {GIT_TIMEOUT_SECONDS} seconds; "
            "inspect the checkout's Git state and running Git processes before retrying"
        )
    except subprocess.CalledProcessError as error:
        fail(f"not inside a Git worktree: {error.stderr.strip() or 'git rev-parse failed'}")
    directory = Path(completed.stdout.strip())
    try:
        info = directory.lstat()
    except FileNotFoundError:
        fail("Git common directory does not exist")
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        fail("Git common directory is not a real directory")
    return directory


def regular_file(path: Path, description: str) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        fail(f"{description} does not exist")
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        fail(f"{description} must be a regular file")


def empty_state(scope: str) -> dict[str, Any]:
    return {"version": STATE_VERSION, "scope": scope, "map": None, "backlog": None}


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def validate_entry(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"url", "issue_id", "title", "owner", "generation"}:
        fail("selection state has an invalid entry")
    for field in ("url", "issue_id", "title", "owner"):
        if not isinstance(value[field], str):
            fail("selection state has an invalid entry")
    require_text(value["url"], "saved issue URL")
    require_text(value["issue_id"], "saved issue identity")
    require_text(value["title"], "saved issue title")
    safe_owner(value["owner"], "saved owner")
    if not isinstance(value["generation"], int) or isinstance(value["generation"], bool) or value["generation"] < 1:
        fail("selection state has an invalid generation")
    return value


def validate_state(value: Any, scope: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"version", "scope", "map", "backlog"}:
        fail("selection state has an invalid shape")
    if (
        not isinstance(value["version"], int)
        or isinstance(value["version"], bool)
        or value["version"] != STATE_VERSION
        or value["scope"] != scope
    ):
        fail("selection state belongs to another scope or version")
    return {
        "version": STATE_VERSION,
        "scope": scope,
        "map": validate_entry(value["map"]),
        "backlog": validate_entry(value["backlog"]),
    }


class StateStore:
    def __init__(self, scope: str) -> None:
        self.scope = safe_scope(scope)
        self.common_dir = common_git_directory()
        self.directory = self.common_dir / STATE_DIRECTORY
        self.path = self.directory / f"{self.scope}.json"
        self.lock_path = self.directory / f"{self.scope}.lock"

    def prepare_directory(self, create: bool) -> None:
        if create:
            try:
                self.directory.mkdir(mode=0o700)
            except FileExistsError:
                pass
        try:
            info = self.directory.lstat()
        except FileNotFoundError:
            fail(f"scope '{self.scope}' has no selection state")
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            fail("selection state directory is not a real directory")

    def acquire_lock(self) -> None:
        self.prepare_directory(create=True)
        deadline = time.monotonic() + 5
        while True:
            try:
                os.mkdir(self.lock_path, 0o700)
                return
            except FileExistsError:
                try:
                    info = self.lock_path.lstat()
                except FileNotFoundError:
                    continue
                if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                    fail("selection lock is not a real directory")
                if time.monotonic() >= deadline:
                    fail(f"selection is busy; inspect lock '{self.lock_path}' and the owning operation before retrying")
                time.sleep(0.05)

    def release_lock(self) -> None:
        try:
            self.lock_path.rmdir()
        except FileNotFoundError:
            pass

    def read(self, required: bool = True) -> dict[str, Any] | None:
        self.prepare_directory(create=False)
        if not self.path.exists() and not self.path.is_symlink():
            if required:
                fail(f"scope '{self.scope}' has no selection state")
            return None
        regular_file(self.path, "selection state")
        try:
            raw = self.path.read_text(encoding="utf-8")
            state = json.loads(raw, object_pairs_hook=unique_object)
        except (OSError, UnicodeDecodeError, ValueError):
            fail("selection state is malformed")
        return validate_state(state, self.scope)

    def write(self, state: dict[str, Any]) -> None:
        state = validate_state(state, self.scope)
        if self.path.exists() or self.path.is_symlink():
            regular_file(self.path, "selection state")
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.scope}.", suffix=".tmp", dir=self.directory, text=True
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as temporary:
                json.dump(state, temporary, sort_keys=True, separators=(",", ":"))
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.chmod(temporary_path, 0o600)
            os.replace(temporary_path, self.path)
        except OSError as error:
            temporary_path.unlink(missing_ok=True)
            fail(f"could not save selection state: {error}")

    def mutate(self, mutation: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
        self.acquire_lock()
        try:
            state = self.read(required=False) or empty_state(self.scope)
            result = mutation(state)
            self.write(result)
            return result
        finally:
            self.release_lock()


def tracker_issue(target: str, kind: str, allow_closed: bool) -> dict[str, str]:
    require_text(target, "issue URL")
    try:
        repository = subprocess.run(
            ["gh", "repo", "view", "--json", "url"], check=True, capture_output=True, text=True
        )
        repository_url = json.loads(repository.stdout)["url"]
        issue = subprocess.run(
            ["gh", "issue", "view", "--json", "id,title,url,state,labels", "--", target],
            check=True,
            capture_output=True,
            text=True,
        )
        fields = json.loads(issue.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        fail("could not read the tracker issue in the current repository")
    url = fields.get("url")
    issue_id = fields.get("id")
    title = fields.get("title")
    state = fields.get("state")
    labels = fields.get("labels")
    if not all(isinstance(item, str) for item in (url, issue_id, title, state)) or not isinstance(labels, list):
        fail("tracker returned malformed issue data")
    if not url.startswith(f"{repository_url}/issues/"):
        fail(f"{kind} must be an issue in the current repository: {repository_url}")
    if not allow_closed and state != "OPEN":
        fail(f"{kind} is not open: {title}")
    if LABELS[kind] not in {label.get("name") for label in labels if isinstance(label, dict)}:
        fail(f"issue is not labelled {LABELS[kind]}: {title}")
    return {"url": url, "issue_id": issue_id, "title": title}


def legacy_issue(store: StateStore, kind: str) -> dict[str, str]:
    path = store.common_dir / LEGACY_PATHS[kind]
    regular_file(path, "legacy selection pointer")
    try:
        contents = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        fail("legacy selection pointer cannot be read")
    lines = contents.splitlines()
    if len(lines) != 1 or not lines[0] or "\r" in lines[0]:
        fail("legacy selection pointer must contain exactly one URL line")
    return tracker_issue(lines[0], kind, allow_closed=True)


def selection_output(scope: str, kind: str, entry: dict[str, Any]) -> None:
    print(json.dumps({"scope": scope, "kind": kind, **entry}, sort_keys=True))


def revalidate_entry(entry: dict[str, Any], kind: str) -> None:
    current = tracker_issue(entry["url"], kind, allow_closed=True)
    if current["issue_id"] != entry["issue_id"]:
        fail(f"saved {kind} no longer resolves to the expected issue identity")


def expected_entry(
    state: dict[str, Any], kind: str, owner: str, generation: int | None, absent: bool
) -> dict[str, Any] | None:
    entry = state[kind]
    if absent:
        if entry is not None:
            fail(f"{kind} selection already exists in scope '{state['scope']}'")
        return None
    if entry is None:
        fail(f"scope '{state['scope']}' has no {kind} selection")
    if entry["owner"] != owner:
        fail(f"{kind} selection belongs to '{entry['owner']}', not '{owner}'")
    if generation is None or entry["generation"] != generation:
        fail(f"{kind} selection generation does not match the established binding")
    return entry


def command_select(arguments: argparse.Namespace) -> None:
    owner = safe_owner(arguments.owner, "owner")
    target = tracker_issue(arguments.issue_url, arguments.kind, allow_closed=False)
    store = StateStore(arguments.scope)

    def mutation(state: dict[str, Any]) -> dict[str, Any]:
        previous = expected_entry(state, arguments.kind, owner, arguments.generation, arguments.expect_absent)
        state[arguments.kind] = {
            **target,
            "owner": owner,
            "generation": 1 if previous is None else previous["generation"] + 1,
        }
        return state

    state = store.mutate(mutation)
    selection_output(store.scope, arguments.kind, state[arguments.kind])


def command_show(arguments: argparse.Namespace) -> None:
    owner = safe_owner(arguments.owner, "owner")
    store = StateStore(arguments.scope)
    state = store.read()
    entry = state[arguments.kind]
    if entry is None:
        fail(f"scope '{store.scope}' has no {arguments.kind} selection")
    if entry["owner"] != owner:
        fail(f"{arguments.kind} selection belongs to '{entry['owner']}', not '{owner}'")
    revalidate_entry(entry, arguments.kind)
    selection_output(store.scope, arguments.kind, entry)


def command_check(arguments: argparse.Namespace) -> None:
    owner = safe_owner(arguments.owner, "owner")
    store = StateStore(arguments.scope)
    state = store.read()
    entry = expected_entry(state, arguments.kind, owner, arguments.generation, absent=False)
    assert entry is not None
    revalidate_entry(entry, arguments.kind)
    selection_output(store.scope, arguments.kind, entry)


def command_import_legacy(arguments: argparse.Namespace) -> None:
    owner = safe_owner(arguments.owner, "owner")
    store = StateStore(arguments.scope)
    target = legacy_issue(store, arguments.kind)

    def mutation(state: dict[str, Any]) -> dict[str, Any]:
        expected_entry(state, arguments.kind, owner, None, absent=True)
        state[arguments.kind] = {**target, "owner": owner, "generation": 1}
        return state

    state = store.mutate(mutation)
    selection_output(store.scope, arguments.kind, state[arguments.kind])


def command_refresh(arguments: argparse.Namespace) -> None:
    if arguments.kind != "map":
        fail("refresh is available only through the map selector")
    owner = safe_owner(arguments.owner, "owner")
    require_text(arguments.expected_issue_node_id, "expected issue node ID")
    store = StateStore(arguments.scope)
    state = store.read()
    entry = expected_entry(state, "map", owner, arguments.generation, absent=False)
    assert entry is not None
    if entry["issue_id"] != arguments.expected_issue_node_id:
        fail("saved map no longer has the expected issue identity")
    target = tracker_issue(entry["url"], "map", allow_closed=True)
    if target["issue_id"] != arguments.expected_issue_node_id:
        fail("saved map no longer resolves to the expected issue identity")

    def mutation(current: dict[str, Any]) -> dict[str, Any]:
        existing = expected_entry(current, "map", owner, arguments.generation, absent=False)
        assert existing is not None
        if existing["issue_id"] != arguments.expected_issue_node_id:
            fail("saved map no longer has the expected issue identity")
        current["map"] = {**target, "owner": owner, "generation": existing["generation"] + 1}
        return current

    result = store.mutate(mutation)
    selection_output(store.scope, "map", result["map"])


def transfer_kinds(arguments: argparse.Namespace) -> list[str]:
    return ["map", "backlog"] if arguments.kinds == "both" else [arguments.kinds]


def command_transfer(arguments: argparse.Namespace) -> None:
    source_owner = safe_owner(arguments.from_owner, "source owner")
    recipient_owner = safe_owner(arguments.to_owner, "recipient owner")
    if source_owner == recipient_owner:
        fail("transfer source and recipient must be different task owners")
    require_text(arguments.approval_ref, "approval reference")
    require_text(arguments.source_stopped_ref, "source-stopped reference")
    kinds = transfer_kinds(arguments)
    generations = {"map": arguments.map_generation, "backlog": arguments.backlog_generation}
    for kind in kinds:
        if generations[kind] is None:
            fail(f"transfer of {kind} requires --{kind}-generation")
    for kind in set(generations) - set(kinds):
        if generations[kind] is not None:
            fail(f"--{kind}-generation is only valid when transferring {kind}")
    store = StateStore(arguments.scope)

    def mutation(state: dict[str, Any]) -> dict[str, Any]:
        for kind in kinds:
            entry = expected_entry(state, kind, source_owner, generations[kind], absent=False)
            assert entry is not None
            revalidate_entry(entry, kind)
            state[kind] = {**entry, "owner": recipient_owner, "generation": entry["generation"] + 1}
        return state

    result = store.mutate(mutation)
    print(json.dumps({"scope": store.scope, "transferred": {kind: result[kind] for kind in kinds}}, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Manage an explicitly scoped, task-owned map or backlog selection."
    )
    result.add_argument("--kind", required=True, choices=("map", "backlog"), help=argparse.SUPPRESS)
    commands = result.add_subparsers(dest="command", required=True)

    def scope_owner(command: argparse.ArgumentParser) -> None:
        command.add_argument("--scope", required=True, help="stable effort scope")
        command.add_argument("--owner", required=True, help="task identity")

    select = commands.add_parser("select", help="select an open issue with an explicit generation expectation")
    scope_owner(select)
    expectation = select.add_mutually_exclusive_group(required=True)
    expectation.add_argument("--expect-absent", action="store_true", help="require no current selection")
    expectation.add_argument("--generation", type=positive_generation, help="require this owner generation")
    select.add_argument("issue_url")
    select.set_defaults(handler=command_select)

    show = commands.add_parser("show", help="read the current owned selection and establish its generation")
    scope_owner(show)
    show.set_defaults(handler=command_show)

    check = commands.add_parser("check", help="verify an established owner and generation binding")
    scope_owner(check)
    check.add_argument("--generation", required=True, type=positive_generation)
    check.set_defaults(handler=command_check)

    legacy = commands.add_parser("import-legacy", help="copy a validated legacy pointer into an empty scoped selection")
    scope_owner(legacy)
    legacy.add_argument("--expect-absent", action="store_true", required=True)
    legacy.set_defaults(handler=command_import_legacy)

    refresh = commands.add_parser("refresh", help="refresh an owned map after a repository rename")
    scope_owner(refresh)
    refresh.add_argument("--generation", required=True, type=positive_generation)
    refresh.add_argument("--expected-issue-node-id", required=True)
    refresh.set_defaults(handler=command_refresh)

    transfer = commands.add_parser("transfer", help="transfer one or both selections within this scope")
    transfer.add_argument("--scope", required=True, help="stable effort scope")
    transfer.add_argument("--from-owner", required=True, help="source task identity")
    transfer.add_argument("--to-owner", required=True, help="recipient task identity")
    transfer.add_argument("--kinds", required=True, choices=("map", "backlog", "both"))
    transfer.add_argument("--map-generation", type=positive_generation)
    transfer.add_argument("--backlog-generation", type=positive_generation)
    transfer.add_argument("--approval-ref", required=True, help="human approval evidence reference")
    transfer.add_argument("--source-stopped-ref", required=True, help="source quiescence evidence reference")
    transfer.set_defaults(handler=command_transfer)
    return result


def main() -> int:
    if sys.version_info < (3, 11):
        print("error: Python 3.11 or newer is required", file=sys.stderr)
        return 2
    arguments = parser().parse_args()
    try:
        arguments.handler(arguments)
    except SelectionError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
