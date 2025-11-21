"""Unit tests for routinely helpers."""

from __future__ import annotations

import datetime
import json
import os
import random
import tempfile
import unittest
from unittest import mock

from routinely import (
    PracticeLog,
    _config_hash,
    _build_plan,
    _format_markdown,
    _handle_log,
    _load_config,
    _load_practice_log,
    _save_practice_log,
    _write_plan_json,
)


class RoutinelyTests(unittest.TestCase):
    def _write_config(self, data: dict) -> str:
        temp = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
        json.dump(data, temp)
        temp.close()
        self.addCleanup(lambda: os.remove(temp.name))
        return temp.name

    def test_load_config_returns_parsed_values(self) -> None:
        config = {
            "options": ["Scales", "Chords"],
            "items_per_session": 1,
            "max_gap": 2,
            "sessions": 2,
            "seed": 123,
        }
        path = self._write_config(config)

        loaded = _load_config(path)

        self.assertEqual(loaded, config)

    def test_load_config_missing_required_key_errors(self) -> None:
        path = self._write_config(
            {
                "options": ["Arpeggios"],
                "items_per_session": 1,
                "max_gap": 2,
            }
        )

        with self.assertRaises(SystemExit) as exc:
            _load_config(path)

        self.assertIn("Missing required config key", str(exc.exception))

    def test_build_plan_respects_session_counts(self) -> None:
        rng = random.Random(0)
        plan, picks = _build_plan(["A", "B", "C"], 2, 2, 4, rng)

        self.assertEqual(len(plan), 4)
        self.assertTrue(all(len(session) == 2 for session in plan))
        self.assertEqual(sum(picks.values()), 8)

    def test_build_plan_raises_when_gap_unsatisfied(self) -> None:
        rng = random.Random(0)

        with self.assertRaises(SystemExit):
            _build_plan(["A", "B"], 1, 0, 2, rng)

    def test_format_markdown_outputs_tables(self) -> None:
        plan = [["Warmup", "Scales"], ["Chords"]]
        picks = {"Warmup": 1, "Scales": 1, "Chords": 1}
        generated = "January 01 2024"

        markdown = _format_markdown(plan, picks, generated)

        expected = """# Practice Routine\n\nGenerated on January 01 2024\n\n## Sessions\n| Session | Date | Item 1 | Item 2 | Item 3 | Item 4 | Done |\n| --- | --- | --- | --- | --- | --- | --- |\n| 01 |  | Warmup | Scales |  |  |  |\n| 02 |  | Chords |  |  |  |  |\n\n## Selection Counts\n\n| Option | Count |\n| --- | --- |\n| Chords | 1 |\n| Scales | 1 |\n| Warmup | 1 |\n"""

        self.assertEqual(markdown, expected)

    def test_practice_log_add_and_remove(self) -> None:
        log = PracticeLog(2)
        at = datetime.datetime(2024, 1, 1, 12, 0, 0)

        entry = log.add_entry(0, "Started slow", at)

        self.assertEqual(entry["entry_id"], 1)
        self.assertEqual(log.entries_for(0)[0]["notes"], "Started slow")

        removed = log.remove_entry(entry["entry_id"])

        self.assertEqual(removed["notes"], "Started slow")
        self.assertEqual(log.entries_for(0), [])

    def test_practice_log_round_trip_to_disk(self) -> None:
        log = PracticeLog(3)
        stamp = datetime.datetime(2024, 1, 2, 15, 30, 0)
        log.add_entry(1, "Great session", stamp)
        temp = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
        temp.close()
        self.addCleanup(lambda: os.remove(temp.name))

        _save_practice_log(temp.name, log)
        loaded = _load_practice_log(temp.name, 3)
        entries = loaded.entries_for(1)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["notes"], "Great session")
        self.assertEqual(entries[0]["logged_at"], stamp)

    def test_write_plan_json_includes_config_hash(self) -> None:
        config_data = {
            "options": ["A", "B"],
            "items_per_session": 1,
            "max_gap": 1,
            "sessions": 1,
        }
        config_path = self._write_config(config_data)
        plan = [["A"]]
        picks = {"A": 1}
        temp = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
        temp.close()
        self.addCleanup(lambda: os.remove(temp.name))

        _write_plan_json(temp.name, plan, picks, "Jan 01 2024", config_path)

        with open(temp.name, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        self.assertEqual(data["session_count"], 1)
        self.assertEqual(data["config_hash"], _config_hash(config_path))

    def test_handle_log_rejects_mismatched_plan_sessions(self) -> None:
        config = {
            "options": ["X", "Y"],
            "items_per_session": 1,
            "max_gap": 1,
            "sessions": 2,
        }
        config_path = self._write_config(config)
        plan_temp = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
        plan_temp.close()
        self.addCleanup(lambda: os.remove(plan_temp.name))
        with open(plan_temp.name, "w", encoding="utf-8") as plan_file:
            json.dump({"session_count": 1}, plan_file)
        log_temp = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
        log_temp.close()
        self.addCleanup(lambda: os.remove(log_temp.name))

        args = mock.Mock(
            config=config_path,
            log_file=log_temp.name,
            plan_json=plan_temp.name,
            log_command="list",
            session=None,
        )

        with self.assertRaises(SystemExit):
            _handle_log(args)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
