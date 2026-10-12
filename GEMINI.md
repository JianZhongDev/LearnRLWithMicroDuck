# Gemini CLI and Antigravity entry point

The instructions for every agent live in `AGENTS.md`. They are imported here:

@AGENTS.md

If the import above did not load, read `AGENTS.md` now, before doing anything else.

## Gemini specifics

- Skills are in `.agents/skills/<name>/SKILL.md`, which Gemini CLI and current Antigravity releases discover. The learner can say, for example, "start-course" or "teach-lesson continue". If skills are not loaded automatically in your version, open the SKILL.md file and follow it.
- Older Antigravity releases look in `.agent/skills/` (singular). `lab py tools/sync_skills.py --also .agent/skills` creates that mirror.
