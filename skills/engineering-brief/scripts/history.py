#!/usr/bin/env python3
"""Resolve brief coverage, allocate per-run scratch and atomically archive completed local reports."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from uuid import uuid4


PREFIX = "<!-- engineering-brief "
SUFFIX = " -->"
DAYS = {"brief": 14, "audit": 30}
WORK = ".work"
RUN_ID = re.compile(r"\d{8}T\d{6}Z-[0-9a-f]{32}")


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamps must be strings")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return result.astimezone(timezone.utc)


def iso(value):
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def archive_root():
    result = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        check=True, capture_output=True, text=True,
    )
    common = Path(result.stdout.strip())
    if common.is_symlink() or not common.is_dir():
        raise ValueError("Git common directory is not a real directory")
    archive = common / "orca-pod-engineering-brief"
    if archive.is_symlink():
        raise ValueError("preserve symlinked archive; resolve its ownership first")
    if archive.exists() and not archive.is_dir():
        raise ValueError("archive path is not a directory")
    return archive


def completed_reports(archive, mode, now):
    folder = archive / mode
    if folder.is_symlink():
        raise ValueError(f"preserve symlinked {mode} report directory")
    if not folder.exists():
        return []
    reports = []
    for path in folder.iterdir():
        if path.suffix != ".md":
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"invalid archived report: {path.name}")
        with path.open(encoding="utf-8") as report:
            header = report.readline().rstrip("\n")
        if not header.startswith(PREFIX) or not header.endswith(SUFFIX):
            raise ValueError(f"missing report metadata: {path.name}")
        data = json.loads(header[len(PREFIX):-len(SUFFIX)])
        if data["mode"] != mode or data["status"] != "complete":
            raise ValueError(f"invalid report status/mode: {path.name}")
        start, end = timestamp(data["coverage_start"]), timestamp(data["coverage_end"])
        completed = timestamp(data["completed_at"])
        if not start <= end <= completed <= now or end - start > timedelta(days=DAYS[mode]):
            raise ValueError(f"invalid report interval: {path.name}")
        reports.append({**data, "path": str(path)})
    return sorted(reports, key=lambda item: (
        timestamp(item["coverage_end"]), timestamp(item["completed_at"]), item["path"],
    ))


def context(archive, mode, now):
    # Read both modes: audits carry curation history but never advance a brief.
    history = {kind: completed_reports(archive, kind, now) for kind in DAYS}
    previous = history[mode][-1] if history[mode] else None
    cutoff = now - timedelta(days=DAYS[mode])
    previous_end = timestamp(previous["coverage_end"]) if previous else None
    start = max(cutoff, previous_end) if mode == "brief" and previous else cutoff
    return {
        "archive": str(archive), "drafts": str(archive / "drafts"), "mode": mode,
        "coverage_start": iso(start), "coverage_end": iso(now),
        "discovery_start": iso(cutoff),
        "previous_report": previous,
        "cutoff_gap": (
            {"start": iso(previous_end), "end": iso(cutoff)}
            if mode == "brief" and previous_end and previous_end < cutoff else None
        ),
        "latest_by_mode": {kind: rows[-1] if rows else None for kind, rows in history.items()},
        "recent_reports": {
            kind: [row for row in rows if timestamp(row["coverage_end"]) >= cutoff]
            for kind, rows in history.items()
        },
    }


def real_directory(info, name):
    if stat.S_ISLNK(info.st_mode):
        raise ValueError(f"preserve symlinked {name}; resolve its ownership first")
    if not stat.S_ISDIR(info.st_mode):
        raise ValueError(f"{name} is not a directory")
    if info.st_uid != os.getuid():
        raise ValueError(f"{name} is not owned by this user")
    return info


def allocation(archive, run_id):
    """Check, without following links, that archive/.work/<run_id> is a real owner-only directory chain."""
    if not RUN_ID.fullmatch(run_id):
        raise ValueError("malformed scratch run id")
    path, chain = archive, []
    for name in (None, WORK, run_id):
        path = path / name if name else path
        chain.append(real_directory(os.lstat(path), path.name))
    if stat.S_IMODE(chain[-1].st_mode) != 0o700:
        raise ValueError("scratch directory is not owner-only")
    return path, chain


def provision(archive, now):
    """Create this run's own scratch directory and return it once its path is validated."""
    run_id = now.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex
    descriptors, created = [os.open(archive.parent, os.O_RDONLY | os.O_DIRECTORY)], []
    try:
        for name in (archive.name, WORK, run_id):
            try:
                os.mkdir(name, 0o700, dir_fd=descriptors[-1])
            except FileExistsError:
                if name == run_id:
                    raise
            real_directory(os.stat(name, dir_fd=descriptors[-1], follow_symlinks=False), name)
            descriptors.append(os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptors[-1]))
            os.fchmod(descriptors[-1], 0o700)
            info = os.fstat(descriptors[-1])
            created.append((info.st_dev, info.st_ino))
    finally:
        for descriptor in descriptors:
            os.close(descriptor)
    path, chain = allocation(archive, run_id)
    if [(info.st_dev, info.st_ino) for info in chain] != created:
        raise ValueError("scratch path changed while it was created; preserve it and inspect")
    return {"archive": str(archive), "work": str(path), "run_id": run_id}


def release(archive, work):
    """Delete exactly one scratch directory this helper allocated, never its parent or siblings."""
    if work.parent != archive / WORK:
        raise ValueError(f"not a scratch allocation under {archive / WORK}")
    path, _ = allocation(archive, work.name)
    if not shutil.rmtree.avoids_symlink_attacks:
        raise ValueError("this platform cannot remove scratch without following symlinks")
    shutil.rmtree(path)
    return {"removed": str(path)}


def save(archive, mode, start, end, draft, now):
    start, end = timestamp(start), timestamp(end)
    if not start <= end <= now or end - start > timedelta(days=DAYS[mode]):
        raise ValueError("coverage must be chronological, not future, and within the mode's cutoff")
    # Existing unreadable/corrupt history must not silently become a fresh archive.
    context(archive, mode, now)
    if draft.is_symlink():
        raise ValueError("preserve symlinked draft; use the actual report file")
    body = draft.read_text(encoding="utf-8")
    if not body.strip() or body.startswith(PREFIX):
        raise ValueError("provide a nonempty report draft without completion metadata")
    data = {
        "mode": mode, "status": "complete", "coverage_start": iso(start),
        "coverage_end": iso(end), "completed_at": iso(now),
    }
    archive.mkdir(exist_ok=True, mode=0o700)
    folder = archive / mode
    folder.mkdir(exist_ok=True, mode=0o700)
    name = end.strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex + ".md"
    target = folder / name
    descriptor, temporary = tempfile.mkstemp(prefix=".pending-", dir=folder)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as report:
            report.write(PREFIX + json.dumps(data, sort_keys=True) + SUFFIX + "\n\n")
            report.write(body.rstrip() + "\n")
            report.flush()
            os.fsync(report.fileno())
        # Publish a complete inode without replacing any existing report.
        os.link(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {**data, "path": str(target)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    read = commands.add_parser("context", help="read history and calculate a coverage interval")
    read.add_argument("--mode", choices=DAYS, default="brief")
    write = commands.add_parser("save", help="archive a checked, complete report")
    write.add_argument("--mode", choices=DAYS, required=True)
    write.add_argument("--start", required=True)
    write.add_argument("--end", required=True)
    write.add_argument("draft", type=Path)
    commands.add_parser("work", help="create this run's owner-only scratch directory under the archive")
    clean = commands.add_parser("clean-work", help="remove one scratch directory that `work` returned")
    clean.add_argument("work", type=Path)
    args = parser.parse_args()
    try:
        archive, now = archive_root(), datetime.now(timezone.utc)
        if args.command == "context":
            result = context(archive, args.mode, now)
        elif args.command == "work":
            result = provision(archive, now)
        elif args.command == "clean-work":
            result = release(archive, args.work)
        else:
            result = save(archive, args.mode, args.start, args.end, args.draft, now)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"history: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
