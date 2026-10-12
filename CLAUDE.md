# Claude Code entry point

The instructions for every agent live in `AGENTS.md`. They are imported here:

@AGENTS.md

## Claude Code specifics

- Skills are mirrored in `.claude/skills/`, so the learner can type `/start-course`, `/teach-lesson continue`, `/ask ...` and so on. The mirror is generated from `.agents/skills/` by `tools/sync_skills.py`; edit skills in `.agents/skills/` only.
- Lesson pages contain images and GIFs. When a picture matters, show the file itself in the chat as well as linking it.
