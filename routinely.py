#!/usr/bin/env python3
"""Generate a monthly guitar practice routine from a JSON config."""

from __future__ import annotations

import argparse
import datetime
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, NotRequired, Sequence, TypedDict
import hashlib


class Config(TypedDict):
    options: List[str]
    items_per_session: int
    max_gap: int
    sessions: int
    seed: NotRequired[int]


class PracticeLogEntry(TypedDict):
    entry_id: int
    session_index: int
    notes: str
    logged_at: datetime.datetime


class PracticeLog:
    """Store practice logs tied to specific session rows."""

    def __init__(
        self,
        session_count: int,
        entries: Sequence[PracticeLogEntry] | None = None,
        next_id: int = 1,
    ):
        if session_count <= 0:
            raise ValueError("session_count must be positive")

        self._session_count = session_count
        self._entries: List[List[PracticeLogEntry]] = [
            [] for _ in range(session_count)
        ]
        self._entries_by_id: Dict[int, PracticeLogEntry] = {}
        self._next_id = max(1, next_id)

        for entry in entries or []:
            self._store_entry(entry)

        self._next_id = max(
            self._next_id, (max(self._entries_by_id) + 1) if self._entries_by_id else 1
        )

    def _validate_session_index(self, session_index: int) -> None:
        if not 0 <= session_index < self._session_count:
            raise ValueError(
                f"session_index must reference a session row between 0 and "
                f"{self._session_count - 1}"
            )

    def _store_entry(self, entry: PracticeLogEntry) -> None:
        self._validate_session_index(entry["session_index"])
        self._entries[entry["session_index"]].append(entry)
        self._entries_by_id[entry["entry_id"]] = entry

    def add_entry(
        self,
        session_index: int,
        notes: str,
        logged_at: datetime.datetime | None = None,
    ) -> PracticeLogEntry:
        self._validate_session_index(session_index)
        entry: PracticeLogEntry = {
            "entry_id": self._next_id,
            "session_index": session_index,
            "notes": notes,
            "logged_at": logged_at or datetime.datetime.now(),
        }
        self._next_id += 1
        self._store_entry(entry)
        return entry

    def entries_for(self, session_index: int) -> List[PracticeLogEntry]:
        self._validate_session_index(session_index)
        return list(self._entries[session_index])

    def all_entries(self) -> List[PracticeLogEntry]:
        return [self._entries_by_id[key] for key in sorted(self._entries_by_id)]

    def remove_entry(self, entry_id: int) -> PracticeLogEntry:
        entry = self._entries_by_id.pop(entry_id, None)
        if entry is None:
            raise ValueError(f"No log entry with id {entry_id}")

        bucket = self._entries[entry["session_index"]]
        for index, candidate in enumerate(bucket):
            if candidate["entry_id"] == entry_id:
                del bucket[index]
                break

        return entry

    def to_json(self) -> Dict[str, object]:
        return {
            "next_id": self._next_id,
            "entries": [
                {
                    "entry_id": entry["entry_id"],
                    "session_index": entry["session_index"],
                    "notes": entry["notes"],
                    "logged_at": entry["logged_at"].isoformat(),
                }
                for entry in self.all_entries()
            ],
        }


def _default_log_path(config_path: str) -> Path:
    config_file = Path(config_path)
    return config_file.with_suffix(".practice_log.json")


def _default_plan_path(config_path: str) -> Path:
    return Path(config_path).with_suffix(".plan.json")


def _load_practice_log(path: Path, session_count: int) -> PracticeLog:
    path = Path(path)
    if not path.exists():
        return PracticeLog(session_count)

    try:
        with open(path, "r", encoding="utf-8") as log_file:
            raw = json.load(log_file)
    except OSError as exc:  # pragma: no cover - defensive guard
        raise SystemExit(f"Failed to read log file: {exc}") from exc
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
        raise SystemExit(f"Invalid log JSON: {exc}") from exc

    entries: List[PracticeLogEntry] = []
    for raw_entry in raw.get("entries", []):
        try:
            logged_at = datetime.datetime.fromisoformat(raw_entry["logged_at"])
            entry: PracticeLogEntry = {
                "entry_id": int(raw_entry["entry_id"]),
                "session_index": int(raw_entry["session_index"]),
                "notes": str(raw_entry["notes"]),
                "logged_at": logged_at,
            }
        except (KeyError, ValueError) as exc:
            raise SystemExit(f"Malformed log entry in {path}: {exc}") from exc
        entries.append(entry)

    next_id = raw.get("next_id", (max((e["entry_id"] for e in entries), default=0) + 1))
    return PracticeLog(session_count, entries, int(next_id))


def _save_practice_log(path: Path, log: PracticeLog) -> None:
    path = Path(path)
    data = log.to_json()
    try:
        with open(path, "w", encoding="utf-8") as log_file:
            json.dump(data, log_file, indent=2)
            log_file.write("\n")
    except OSError as exc:  # pragma: no cover - defensive guard
        raise SystemExit(f"Failed to write log file: {exc}") from exc


def _config_hash(config_path: str) -> str:
    try:
        content = Path(config_path).read_bytes()
    except OSError as exc:  # pragma: no cover - defensive guard
        raise SystemExit(f"Failed to read config file for hashing: {exc}") from exc
    return hashlib.sha256(content).hexdigest()


def _write_plan_json(
    path: Path,
    plan: Sequence[Sequence[str]],
    picks: Dict[str, int],
    generated_on: str,
    config_path: str,
) -> None:
    data = {
        "generated_on": generated_on,
        "session_count": len(plan),
        "plan": plan,
        "picks": picks,
        "config_hash": _config_hash(config_path),
    }
    try:
        with open(path, "w", encoding="utf-8") as plan_file:
            json.dump(data, plan_file, indent=2)
            plan_file.write("\n")
    except OSError as exc:  # pragma: no cover - defensive guard
        raise SystemExit(f"Failed to write plan JSON: {exc}") from exc


def _normalize_session_index(session_number: int, session_count: int) -> int:
    session_index = session_number - 1
    if session_index < 0 or session_index >= session_count:
        raise SystemExit(
            f"Session must be between 1 and {session_count}, got {session_number}"
        )
    return session_index


def _load_config(path: str) -> Config:
    try:
        with open(path, "r", encoding="utf-8") as config_file:
            data = json.load(config_file)
    except OSError as exc:  # pragma: no cover - defensive guard
        raise SystemExit(f"Failed to read config file: {exc}") from exc
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
        raise SystemExit(f"Invalid JSON: {exc}") from exc

    required = {
        "options": list,
        "items_per_session": int,
        "max_gap": int,
        "sessions": int,
    }
    for key, expected_type in required.items():
        if key not in data:
            raise SystemExit(f"Missing required config key: {key}")
        if not isinstance(data[key], expected_type):
            raise SystemExit(
                f"Config key '{key}' must be of type {expected_type.__name__}"
            )

    options = data["options"]
    if not options:
        raise SystemExit("Config must include at least one practice option")

    if len(options) < data["items_per_session"]:
        raise SystemExit(
            "items_per_session cannot be larger than the number of options"
        )

    if data["max_gap"] < 0 or data["sessions"] <= 0:
        raise SystemExit("max_gap must be >= 0 and sessions must be > 0")

    return data


def _build_plan(
    options: Sequence[str],
    items_per_session: int,
    max_gap: int,
    sessions: int,
    rng: random.Random,
) -> tuple[List[List[str]], Dict[str, int]]:
    plan: List[List[str]] = []
    picks = {opt: 0 for opt in options}
    days_since = {opt: 0 for opt in options}

    for _ in range(sessions):
        urgent = [opt for opt, gap in days_since.items() if gap >= max_gap]
        if len(urgent) > items_per_session:
            raise SystemExit(
                "Cannot satisfy max_gap constraint with the current settings"
            )

        chosen: List[str] = urgent[:]
        remaining_slots = items_per_session - len(chosen)
        if remaining_slots:
            remaining = [opt for opt in options if opt not in urgent]
            rng.shuffle(remaining)
            remaining.sort(key=lambda option: days_since[option], reverse=True)
            chosen.extend(remaining[:remaining_slots])

        rng.shuffle(chosen)
        plan.append(chosen[:])

        selected = set(chosen)
        for opt in options:
            if opt in selected:
                picks[opt] += 1
                days_since[opt] = 0
            else:
                days_since[opt] += 1

    return plan, picks


def _format_markdown(
    plan: Sequence[Sequence[str]], picks: Dict[str, int], generated_on: str
) -> str:
    max_items = max(4, *(len(session) for session in plan)) if plan else 4
    item_headers = [f"Item {idx}" for idx in range(1, max_items + 1)]
    header = "| Session | Date | " + " | ".join(item_headers) + " | Done |"
    separator = "| --- | --- | " + " | ".join(["---"] * len(item_headers)) + " | --- |"

    lines = [
        "# Practice Routine",
        "",
        f"Generated on {generated_on}",
        "",
        "## Sessions",
        header,
        separator,
    ]
    for index, session in enumerate(plan, start=1):
        padded = list(session) + ["" for _ in range(max_items - len(session))]
        lines.append(f"| {index:02d} |  | " + " | ".join(padded) + " |  |")

    lines.extend(
        [
            "",
            "## Selection Counts",
            "",
            "| Option | Count |",
            "| --- | --- |",
        ]
    )
    for option, count in sorted(picks.items()):
        lines.append(f"| {option} | {count} |")

    return "\n".join(lines) + "\n"


def _handle_generate(args: argparse.Namespace) -> int:
    config = _load_config(args.config)
    rng = random.Random(config.get("seed", args.seed))
    generated_on = datetime.date.today().strftime("%B %d %Y")

    plan, picks = _build_plan(
        config["options"],
        config["items_per_session"],
        config["max_gap"],
        config["sessions"],
        rng,
    )

    print(f"Generated on: {generated_on}")
    print("Practice Plan:")
    for index, session in enumerate(plan, start=1):
        print(f"Session {index:02d}:")
        for item in session:
            print(f"  - {item}")

    print("\nSelection Counts:")
    for option, count in sorted(picks.items()):
        print(f"{option}: {count}")

    if args.markdown:
        try:
            with open(args.markdown, "w", encoding="utf-8") as markdown_file:
                markdown_file.write(_format_markdown(plan, picks, generated_on))
        except OSError as exc:
            raise SystemExit(f"Failed to write Markdown output: {exc}") from exc

    plan_json_path: Path | None = None
    if args.plan_json:
        plan_json_path = Path(args.plan_json)
    elif args.markdown:
        plan_json_path = _default_plan_path(args.config)

    if plan_json_path:
        _write_plan_json(plan_json_path, plan, picks, generated_on, args.config)
        print(f"Wrote plan JSON to {plan_json_path}")

    return 0


def _handle_log(args: argparse.Namespace) -> int:
    config = _load_config(args.config)
    session_count = config["sessions"]
    log_path = Path(args.log_file) if args.log_file else _default_log_path(args.config)
    log = _load_practice_log(log_path, session_count)

    plan_path = Path(args.plan_json) if args.plan_json else _default_plan_path(
        args.config
    )
    if plan_path.exists():
        try:
            with open(plan_path, "r", encoding="utf-8") as plan_file:
                plan_data = json.load(plan_file)
        except OSError as exc:  # pragma: no cover - defensive guard
            raise SystemExit(f"Failed to read plan JSON: {exc}") from exc
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
            raise SystemExit(f"Invalid plan JSON: {exc}") from exc

        plan_sessions = int(plan_data.get("session_count", 0))
        if plan_sessions != session_count:
            raise SystemExit(
                f"Plan session count {plan_sessions} does not match config sessions "
                f"{session_count}. Regenerate the plan before logging."
            )
        config_hash = plan_data.get("config_hash")
        if config_hash and config_hash != _config_hash(args.config):
            raise SystemExit(
                "Configuration has changed since the plan was generated. "
                "Regenerate the plan before logging."
            )

    if args.log_command == "add":
        notes = args.notes.strip()
        if not notes:
            raise SystemExit("Notes cannot be empty")

        session_index = _normalize_session_index(args.session, session_count)
        entry = log.add_entry(session_index, notes)
        _save_practice_log(log_path, log)
        print(
            f"Added entry {entry['entry_id']} to session {args.session} at "
            f"{entry['logged_at'].isoformat(timespec='seconds')}"
        )
        return 0

    if args.log_command == "list":
        if args.session is None:
            entries = log.all_entries()
        else:
            session_index = _normalize_session_index(args.session, session_count)
            entries = log.entries_for(session_index)

        if not entries:
            if args.session is None:
                print("No log entries found.")
            else:
                print(f"No log entries for session {args.session}.")
            return 0

        for entry in entries:
            timestamp = entry["logged_at"].isoformat(timespec="seconds")
            print(
                f"[{entry['entry_id']}] Session {entry['session_index'] + 1} "
                f"{timestamp}: {entry['notes']}"
            )
        return 0

    if args.log_command == "delete":
        try:
            removed = log.remove_entry(args.entry_id)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc

        _save_practice_log(log_path, log)
        print(
            f"Removed entry {removed['entry_id']} from session "
            f"{removed['session_index'] + 1}"
        )
        return 0

    raise SystemExit("Unknown log command")


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    argv = list(argv)
    if argv and argv[0] not in {"generate", "log"}:
        argv = ["generate"] + argv

    parser = argparse.ArgumentParser(
        description="Generate a randomized practice routine from a JSON config"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser(
        "generate", help="Create a new practice plan"
    )
    generate_parser.add_argument("config", help="Path to routine configuration JSON file")
    generate_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional RNG seed for deterministic output",
    )
    generate_parser.add_argument(
        "--markdown",
        metavar="PATH",
        help="Optional Markdown output path for easy PDF conversion",
    )
    generate_parser.add_argument(
        "--plan-json",
        metavar="PATH",
        help=(
            "Optional JSON output path for structured plan data "
            "(defaults to config.plan.json when --markdown is used)"
        ),
    )

    log_parser = subparsers.add_parser(
        "log", help="Add, list, or delete practice log entries"
    )
    log_parser.add_argument(
        "config", help="Path to the configuration JSON file for the routine"
    )
    log_parser.add_argument(
        "--log-file",
        metavar="PATH",
        help="Path to the practice log JSON file (defaults to alongside config)",
    )
    log_parser.add_argument(
        "--plan-json",
        metavar="PATH",
        help="Path to plan JSON for validation (defaults to alongside config)",
    )

    log_subparsers = log_parser.add_subparsers(dest="log_command", required=True)

    log_add = log_subparsers.add_parser("add", help="Add a practice log entry")
    log_add.add_argument(
        "--session",
        type=int,
        required=True,
        help="1-based session index from the plan table",
    )
    log_add.add_argument("--notes", required=True, help="Notes to attach to the entry")

    log_list = log_subparsers.add_parser("list", help="List practice log entries")
    log_list.add_argument(
        "--session",
        type=int,
        help="Optional 1-based session index to filter entries",
    )

    log_delete = log_subparsers.add_parser("delete", help="Delete a log entry by id")
    log_delete.add_argument(
        "--entry-id",
        type=int,
        required=True,
        help="Identifier of the entry to delete (see the list command)",
    )

    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = _parse_args(argv)
    if args.command == "generate":
        return _handle_generate(args)
    if args.command == "log":
        return _handle_log(args)
    raise SystemExit("Unknown command")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main(sys.argv[1:]))
