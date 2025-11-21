"""Unit tests for routinely helpers."""

from __future__ import annotations

import json
import os
import random
import tempfile
import unittest

from routinely import _build_plan, _format_markdown, _load_config


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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
