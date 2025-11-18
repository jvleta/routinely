#!/usr/bin/env python3
"""Generate a monthly guitar practice routine from a JSON config."""

from __future__ import annotations

import argparse
import datetime
import json
import random
import sys
from typing import Dict, List, NotRequired, Sequence, TypedDict

class Config(TypedDict):
    options: List[str]
    items_per_session: int
    max_gap: int
    sessions: int
    seed: NotRequired[int]

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
    max_items = max((len(session) for session in plan), default=0)
    item_headers = [f"Item {idx}" for idx in range(1, max_items + 1)]
    header = "| Session | " + " | ".join(item_headers) + " |" if item_headers else "| Session |"
    separator = "| --- | " + " | ".join(["---"] * len(item_headers)) + " |" if item_headers else "| --- |"

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
        lines.append(f"| {index:02d} | " + " | ".join(padded) + " |")

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


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a randomized practice routine from a JSON config"
    )
    parser.add_argument("config", help="Path to routine configuration JSON file")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional RNG seed for deterministic output",
    )
    parser.add_argument(
        "--markdown",
        metavar="PATH",
        help="Optional Markdown output path for easy PDF conversion",
    )
    args = parser.parse_args(argv)

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

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main(sys.argv[1:]))
