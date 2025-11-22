# ROUTINELY

Routinely is an app that I use to generate monthly guitar practice routines.

## Usage

- Generate a plan: `python routinely.py generate config.json --markdown plan.md` (also writes `config.plan.json` unless you set `--plan-json PATH`).
- Mark a session done (stores timestamp): `python routinely.py log config.json done --session 3` (defaults to `config.practice_log.json`).
- Manage practice log notes: `python routinely.py log config.json add --session 1 --notes "Played at 80bpm"`. Use `list`/`delete` likewise.
- Render Markdown with completion marks from an existing plan + log: `python routinely.py render config.json --plan-json config.plan.json --markdown plan.md`.

## Example config:
```json
{
  "options": ["scales", "chords", "songs", "improv", "ear training"],
  "items_per_session": 4,
  "max_gap": 2,
  "sessions": 10
}
```

## Example Output:


### Practice Routine

Generated on November 18 2025

#### Sessions
| Session | Date | Item 1 | Item 2 | Item 3 | Item 4 | Done |
| --- | --- | --- | --- | --- | --- | --- |
| 01 |  | songs | scales | chords | improv |  |
| 02 | 2025-11-19 | ear training | scales | songs | chords | **X** |
| 03 |  | improv | ear training | songs | scales |  |
| 04 |  | ear training | improv | scales | chords |  |
| 05 | 2025-11-23 | scales | ear training | chords | songs | **X** |
| 06 |  | chords | improv | songs | ear training |  |
| 07 |  | scales | songs | ear training | chords |  |
| 08 |  | scales | improv | chords | songs |  |
| 09 |  | scales | chords | improv | ear training |  |
| 10 |  | songs | ear training | improv | chords |  |

#### Selection Counts

| Option | Count |
| --- | --- |
| chords | 9 |
| ear training | 8 |
| improv | 7 |
| scales | 8 |
| songs | 8 |
