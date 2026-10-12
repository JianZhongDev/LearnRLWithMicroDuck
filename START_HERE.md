# Start here: how to learn with this course

Your AI coding agent is the teacher. You never need to remember lesson numbers or long prompts: the course keeps track of where you are in `LearningProgress/STATE.md`, and every message from the agent ends with a **▶ Next** line that tells you exactly what to do.

## 1. Set up once

| Your system | Run in the course folder |
|---|---|
| Windows 10/11 | `.\setup` in PowerShell (uses WSL 2; the script tells you how to install it if it is missing) |
| Linux (Ubuntu, Fedora, …) | `./setup.sh` |
| macOS (Apple Silicon) | `./setup.sh` (simulation on the CPU, Apple GPU for neural-network lessons; see `docs/ENVIRONMENT.md`) |

Setup gets the two MicroDuck repositories as separate checkouts **outside this folder** (next to it by default; `--sources <folder>` to choose, and existing clones are reused untouched), builds a private Python environment (several GB, 10–30 minutes), then checks your compute and rendering. It ends with `READY`. Run `lab doctor` any time to re-check.

Prefer to be guided? Open the folder in your agent and type `setup-environment` (with your agent's prefix, see below). The agent explains each step, asks where the checkouts should go, and runs setup with you.

## 2. Start the course

Open the course folder in your agent and type the start command:

| Agent | First message | Later sessions |
|---|---|---|
| Codex (app, CLI, IDE) | `$start-course` | `$teach-lesson continue` |
| Claude Code | `/start-course` | `/teach-lesson continue` |
| Gemini CLI, Antigravity, Grok, others | `start-course` | `teach-lesson continue` |

The names are the same everywhere; only the prefix differs. If your agent does not react to a name, say: *"Read AGENTS.md and follow the start-course skill."*

## 3. The lesson loop

```
 new agent session ──► teach-lesson continue
                            │
                            ▼
   Turn 1  big picture + key idea + lab command
                            │   you run:  lab 08/L02
                            ▼
   Turn 2  read your results together + "change one thing"
                            │   you run:  lab 08/L02 something=value
                            ▼
   Turn 3  what it means + what transfers   (the agent saves progress itself)
                            │
                            ▼
                close the session; next lesson = new session
```

- Use **one new session per lesson**, opened in the course folder. That keeps the agent focused and its memory fresh.
- Ask questions any time. The agent answers that question and does not move on until you say so.
- No quizzes and no grades. If you are short on time, say "run it for me".

## What to type

Write the skill name with your agent's prefix (`$` in Codex, `/` in Claude Code, nothing elsewhere).

| Situation | Type |
|---|---|
| Start or continue the course | `teach-lesson continue` |
| Set up, move or repair the environment | `setup-environment` |
| You ran the lab and want to discuss it | `I ran it` (add what you noticed or found odd) |
| You want the agent to run the lab for you | `run it for me` |
| You tried a different setting | `I ran action_noise=0.3` (use the setting you changed) |
| Finish the current lesson | `wrap up` |
| Something in **the current lesson** is unclear | just ask in the same session |
| A question about **anything else** (an earlier module, a term, a result, how MicroDuck works) | new session: `ask <your question>` |
| "Show me what happens if …" | new session: `ask show me what happens if …` |
| The lesson is finished but the agent did not say "progress saved" | `session-handoff this lesson is finished` |
| You have to stop in the middle of a lesson | `session-handoff pausing mid-lesson` |
| Start the next module (the agent usually suggests this itself) | `plan-module start module 09` |
| The teaching does not suit you | say what was wrong and what you want instead; it is logged in `LearningPlan/FEEDBACK_LOG.md` |
| Turn your logged corrections into permanent rules (every few weeks) | `consolidate-rules` |
| A lesson message feels confusing or too long | `review-lesson redo the last message` |
| Change your profile or teaching language | edit `LearningProgress/LEARNER.md`, or tell the agent |

## Running labs

`lab` below means `./lab.sh` on Linux and macOS, and `.\lab` on Windows. Run it in a terminal in the course folder.

```
lab list                     # all available labs
lab 08/L01                   # run a lab with default settings
lab 08/L01 help              # settings you can change
lab 08/L01 action_noise=0.3  # change one thing (kept as a separate result)
lab doctor                   # check the environment
```

Results are saved in `LearningProgress/<module>/lessons/<lesson>/results/<settings>/`. `results/compare.png` puts every setting you tried side by side. Open the `.gif` and `.png` files in your editor or an image viewer. The lesson page `LESSON.md` is in the same lesson folder; open it with your editor's Markdown preview.

The first simulation run takes a few minutes (simulation code compiles); later runs are faster.

## When something goes wrong

| Problem | Fix |
|---|---|
| A lab or setup fails | run `lab doctor` and paste the lines marked `FAIL` to the agent; see `docs/ENVIRONMENT.md` |
| The agent repeats a lesson you already finished | `session-handoff <lesson> is finished: I ran <settings>`, then a new session with `teach-lesson continue` |
| The agent does not know the skills | make sure the session is opened in the course folder (the one with `AGENTS.md`); otherwise say "read AGENTS.md" |
| The agent answers in the wrong language | set "Teaching language" in `LearningProgress/LEARNER.md` and start a new session |
| No robot GIFs | your machine has no working renderer; plots still work. See "Rendering" in `docs/ENVIRONMENT.md` |
| Labs are very slow | you are on the CPU; ask the agent for smaller settings, or use a machine with an NVIDIA GPU for the training modules |
| You want to see where you are | open `LearningProgress/STATE.md`, or the module's `MAP.md` |
| You want to start over | see "Starting over" in `README.md` |

## Where things are

- `LearningProgress/STATE.md`: where you are and what comes next.
- `LearningProgress/<module>/MAP.md`: the module's big picture and lesson list.
- `LearningProgress/<module>/lessons/<lesson>/LESSON.md`: the lesson page.
- `LearningProgress/GLOSSARY.md`: plain definitions of every term.
- `LearningPlan/LEARNING_PLAN.md`: the whole curriculum.
- `LearningPlan/TEACHING_RULES.md`: how the agent is told to teach. Your corrections end up here.
