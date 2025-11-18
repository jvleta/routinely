# ROUTINELY

Routinely is an app that I use to generate monthly guitar practice routines. The workflow is defined below:
1. Specify N options for what to practice during a given session
2. Specify how many things to practice per session (4)
3. Specify how many consecutive days you can go without practicing one of the options (default is 2)
4. Specify how many practice sessions to plan (default is 30)
5. Run script and it will output which things to practice for each session. It also will output how many times each option was chosen during the 30 day period.

Create a JSON configuration for steps 1-4 and run `python routinely.py config.json`. Example config:

```json
{
  "options": ["scales", "chords", "songs", "improv", "ear training"],
  "items_per_session": 4,
  "max_gap": 2,
  "sessions": 30
}
```

The script prints the plan for each practice session and how many times every option was chosen.
