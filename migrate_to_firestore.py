#!/usr/bin/env python3
"""Migrate local Routinely plan + practice logs into Firestore."""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import SERVER_TIMESTAMP


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload a generated plan and practice log JSON to Firestore"
    )
    parser.add_argument(
        "--user-id",
        required=True,
        help="Firestore user id to namespace the data under (users/{user-id}/plans/...)",
    )
    parser.add_argument(
        "--config",
        required=True,
        type=Path,
        help="Path to the routine config JSON used to generate the plan",
    )
    parser.add_argument(
        "--plan-json",
        required=True,
        type=Path,
        help="Path to the generated plan JSON (e.g., config.plan.json)",
    )
    parser.add_argument(
        "--log-json",
        required=True,
        type=Path,
        help="Path to the practice log JSON (e.g., config.practice_log.json)",
    )
    parser.add_argument(
        "--plan-id",
        help="Optional Firestore document id for the plan (defaults to config name + generated_on)",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_plan(path: Path) -> dict:
    data = _load_json(path)
    required = ("generated_on", "session_count", "plan", "picks")
    for key in required:
        if key not in data:
            raise SystemExit(f"Plan JSON missing required key: {key}")
    return data


def _load_log(path: Path) -> Tuple[Dict[int, datetime.datetime | None], List[dict]]:
    raw = _load_json(path)
    done_sessions: Dict[int, datetime.datetime | None] = {}
    entries: List[dict] = []

    for value in raw.get("done_sessions", []):
        if isinstance(value, dict):
            session_index = int(value["session_index"])
            completed_raw = value.get("completed_at")
        else:
            session_index = int(value)
            completed_raw = None
        completed_at = (
            datetime.datetime.fromisoformat(completed_raw) if completed_raw else None
        )
        done_sessions[session_index] = completed_at

    for entry in raw.get("entries", []):
        entries.append(
            {
                "entry_id": int(entry["entry_id"]),
                "session_index": int(entry["session_index"]),
                "notes": str(entry["notes"]),
                "logged_at": datetime.datetime.fromisoformat(entry["logged_at"]),
            }
        )

    return done_sessions, entries


def _plan_id(args: argparse.Namespace, plan: dict) -> str:
    if args.plan_id:
        return args.plan_id
    generated_on_safe = plan["generated_on"].replace(" ", "_")
    return f"{args.config.stem}-{generated_on_safe}"


def migrate(args: argparse.Namespace) -> None:
    plan = _load_plan(args.plan_json)
    done_sessions, entries = _load_log(args.log_json)

    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    plan_doc_id = _plan_id(args, plan)
    plan_ref = (
        db.collection("users")
        .document(args.user_id)
        .collection("plans")
        .document(plan_doc_id)
    )

    plan_ref.set(
        {
            "generatedOn": plan["generated_on"],
            "sessionCount": int(plan["session_count"]),
            "plan": plan["plan"],
            "picks": plan["picks"],
            "configHash": plan.get("config_hash"),
            "sourcePaths": {
                "config": str(args.config),
                "planJson": str(args.plan_json),
                "logJson": str(args.log_json),
            },
            "migratedAt": SERVER_TIMESTAMP,
        }
    )

    sessions = plan_ref.collection("sessions")
    plan_sessions: Sequence[Sequence[str]] = plan["plan"]
    for index, items in enumerate(plan_sessions):
        completed_at = done_sessions.get(index)
        session_ref = sessions.document(f"{index:02d}")
        session_ref.set(
            {
                "sessionIndex": index,
                "items": items,
                "done": completed_at is not None,
                "completedAt": completed_at,
            }
        )

        log_entries = [
            entry for entry in entries if entry["session_index"] == index
        ]
        for entry in log_entries:
            session_ref.collection("logs").document(str(entry["entry_id"])).set(
                {
                    "entryId": entry["entry_id"],
                    "notes": entry["notes"],
                    "loggedAt": entry["logged_at"],
                }
            )

    print(
        f"Migrated plan to users/{args.user_id}/plans/{plan_doc_id} "
        f"with {len(plan_sessions)} sessions and {len(entries)} log entries."
    )


if __name__ == "__main__":
    migrate(_parse_args())
