# How this repository works

A two-minute orientation for AI agents and for people who want to change the course.

## The idea

The repository is a course that an AI coding agent teaches. Three things make that work:

```
 instructions            memory                    tools
 (how to teach)          (where we are)            (how to run things)
 ───────────────         ───────────────────       ─────────────────────
 AGENTS.md               LearningProgress/         setup.sh   -> environment
 .agents/skills/           STATE.md                lab.sh     -> run a lab
 LearningPlan/             LEARNER.md              duckkit    -> robot sim, GIFs, diagrams
   TEACHING_RULES.md       GLOSSARY.md             tools/doctor.py -> what works here
   LEARNING_PLAN.md        <module>/MAP, NOTES,
   examples/               TODO, lessons/
```

A session always goes: read the instructions → read the memory → do one piece of teaching → write the memory back. Nothing depends on chat history, so any agent can continue where another stopped.

## One lesson, end to end

```
learner types "teach-lesson continue"
        │
        ▼
agent reads STATE.md, LEARNER.md, TEACHING_RULES.md, .course/env.json
        │
        ▼
module has no MAP.md? ── yes ─► plan-module: scaffold files, draw the module map, list lessons
        │ no
        ▼
teach-lesson (prepare): check facts in the MicroDuck checkouts → build-lab → make-visual
                        → write LESSON.md → review-lesson checklist
        │
        ▼
teach-lesson (deliver): turn 1 big picture + lab command
                        turn 2 read the learner's results, "change one thing"
                        turn 3 meaning + transfer
        │
        ▼
session-handoff: STATE.md, NOTES.md, MAP.md status, GLOSSARY.md   → "Progress saved"
```

Other entry points: `start-course` (first session), `setup-environment` (get the MicroDuck checkouts and the Python environment working), `ask` (a question that must not move the course), `consolidate-rules` (fold learner feedback into the rules).

## Files and who writes them

| Path | Purpose | Written by |
|---|---|---|
| `AGENTS.md` | Canonical agent instructions, kept short | maintainers |
| `CLAUDE.md`, `GEMINI.md` | Import `AGENTS.md` for agents that look for those names | maintainers |
| `.agents/skills/<name>/SKILL.md` | Procedures; the source of truth for skills | maintainers |
| `.claude/skills/` | Copy of `.agents/skills/` for Claude Code | `tools/sync_skills.py` |
| `LearningPlan/LEARNING_PLAN.md` | Curriculum: 18 modules with goals and lab ideas | maintainers |
| `LearningPlan/TEACHING_RULES.md` | Ranked teaching rules | maintainers; the agent via `consolidate-rules` |
| `LearningPlan/FEEDBACK_LOG.md` | One line per learner correction | the agent |
| `LearningPlan/examples/` | Real failed and repaired lessons, annotated | maintainers |
| `LearningProgress/STATE.md` | Current position and next action (short) | the agent |
| `LearningProgress/LEARNER.md` | Learner profile and teaching language | the agent, the learner |
| `LearningProgress/GLOSSARY.md` | One plain line per term | the agent |
| `LearningProgress/<module>/MAP.md` | Module big picture, ranked ideas, lesson table | the agent (`plan-module`); Module 08 ships pre-built |
| `LearningProgress/<module>/NOTES.md`, `TODO.md` | Dated history; parked topics | the agent |
| `LearningProgress/<module>/lessons/<Lxx-name>/` | `LESSON.md`, `lab.py`, and `results/` (ignored by Git) | the agent; the learner's runs |
| `LearningProgress/_shared/duckkit/` | Lab helper library | maintainers |
| `.course/` | This machine's setup (ignored by Git) | `setup.sh`, `tools/doctor.py` |
| outside this repository | The two MicroDuck checkouts (`rl_repo`, `runtime_repo` in `.course/env.json`), **read-only**; none of their code is stored here | `setup.sh`, or the learner's own clones |

## Design choices worth knowing

- **Short always-loaded instructions, details on demand.** `AGENTS.md` fits on two screens. Procedures live in skills that load only when used. Long rule files were tried first and were forgotten mid-session.
- **Rules are ranked and merged, never stacked.** Learner corrections go to `FEEDBACK_LOG.md` and are folded into existing rules.
- **Lesson pages are the main artifact.** Chat turns stay under about 300 words and link to the page. Pictures are PNG or GIF so they render in any agent or editor.
- **Labs follow one shape:** defaults give a clear result; `key=value` changes one setting; each setting keeps its own results folder; a comparison plot overlays them.
- **Machine differences are data, not prose.** `.course/env.json` holds the launcher, device and renderer. `duckkit` and the agent read it instead of assuming an operating system.
- **Upstream code stays upstream.** This repository stores none of MicroDuck's code. Setup makes or reuses checkouts outside the repository and records their paths. `tools/pins.env` names the tested commits, so line numbers and behavior quoted in lessons stay true; `./setup.sh --latest` opts out. Lessons cite upstream files; they do not copy them. Sources and licenses are in `CREDITS.md`.

## Supporting another agent

All agents share `AGENTS.md` and `.agents/skills/` (the Agent Skills layout: a folder per skill with `SKILL.md` and optional `scripts/`, `references/`, `assets/`).

| Agent | Reads instructions from | Finds skills in | Invocation |
|---|---|---|---|
| Codex | `AGENTS.md` | `.agents/skills/` | `$name` |
| Claude Code | `CLAUDE.md` (imports `AGENTS.md`) | `.claude/skills/` | `/name` |
| Gemini CLI | `GEMINI.md` (imports `AGENTS.md`) | `.agents/skills/` | by name or description |
| Antigravity | `AGENTS.md` / `GEMINI.md` | `.agents/skills/` (older releases: `.agent/skills/`) | by name or description |
| Grok Build | `AGENTS.md` | not confirmed; falls back to reading the file | by name |
| anything else | point it at `AGENTS.md` | reads `SKILL.md` files directly | by name |

`AGENTS.md` tells an agent without skill support to open the `SKILL.md` file and follow it, so the course degrades gracefully. To add a mirror for another agent: `lab py tools/sync_skills.py --also <folder>`.

Only Codex has been used to teach the course so far. If you try another agent, please report what worked.

## Changing the course

- **A skill:** edit it in `.agents/skills/`, then run `python tools/sync_skills.py` (or `lab py tools/sync_skills.py`).
- **A rule:** prefer `consolidate-rules`; keep `TEACHING_RULES.md` under about 150 lines and `AGENTS.md`'s core list in agreement with it.
- **The curriculum:** edit `LearningPlan/LEARNING_PLAN.md`; module folders in `LearningProgress/` are named `NN-topic` and matched by number.
- **A pre-built lesson:** follow the `teach-lesson` and `build-lab` skills yourself, test the lab on a clean results folder, and keep machine-specific paths out of pages. Commit diagrams and plots only: robot renderings carry the MicroDuck model's CC BY-NC-SA license and belong in the ignored `results/` folders.
- **Upstream version:** change `tools/pins.env`, run setup, then `lab doctor --full` and the Module 08 labs; update quoted line numbers.
- **Before committing:** `python tools/check_repo.py` checks skill mirrors, links and stray personal paths. CI runs the same check.
