---
name: teach-lesson
description: Prepare and deliver one hands-on lesson of the MicroDuck robotics/RL course - lesson page with diagrams, a tested lab the learner runs, and short chat turns. Use when the learner says "continue", "next lesson", or asks to learn a course topic.
---

# Teach one lesson

A lesson answers **one question** with **one key idea**, shown with pictures and a lab the learner runs. Follow `LearningPlan/TEACHING_RULES.md`.

## 1. Prepare (before saying anything to the learner)

0. Read `LearningProgress/STATE.md`. If the course has not started, use `start-course` instead. Read `LEARNER.md` (background, language) and `.course/env.json` (launcher, `device`, `mujoco_gl`): they decide how deep to go, which command form to give, and how big the lab can be.
1. Read the module's `MAP.md`. If `STATE.md` says a lesson is in progress, check that lesson's `results/` folders. Folders newer than the last `NOTES.md` entry mean the learner ran labs that were not recorded. Ask in one line whether that lesson is finished; if it is, record it with `session-handoff` before starting the next lesson. If there is no `MAP.md`, the module has not been planned: use `plan-module` first. It creates `MAP.md`, `NOTES.md`, `TODO.md`, `figures/` and `lessons/`.
   **If the lesson already has a `LESSON.md` and `lab.py`** (pre-built, or prepared in an earlier session): do not rewrite it. Run its lab on this machine, compare the page's numbers and claims with the output, fix differences, adapt wording to the learner's profile if needed, run `review-lesson`, then go to section 2.
2. Write down:
   - **Question:** what the learner will be able to answer.
   - **Key idea:** one sentence.
   - **Left out:** what you deliberately skip (add to `TODO.md`).
3. Check the facts you will teach against the MicroDuck checkouts and the installed libraries (`lab py tools/where.py mjlab` prints all their paths), read-only. Quote at most the few lines a lesson needs, with the file path; never copy upstream files into this repository. Note file and line for `NOTES.md`.
4. Build or update the lab with `build-lab`, then **run it** and look at every output image. Fix anything confusing. Size it for this machine: small defaults on `cpu`, and a result that still makes sense without GIFs when `mujoco_gl` is `null`.
5. Make the concept visual(s) with `make-visual`: at least the module map with today's part highlighted, plus one "how it works" diagram or pseudocode.
6. Write `lessons/<Lxx-name>/LESSON.md` from [assets/LESSON_TEMPLATE.md](assets/LESSON_TEMPLATE.md).
7. Run the `review-lesson` checklist on the page and fix what fails.

## 2. Deliver in short turns (each under about 300 words plus one picture)

Write in the learner's language. `<launcher>` below is the `launcher` value from `.course/env.json` (`./lab.sh` or `.\lab`). Write skill names the way the learner's agent expects them (`$name` in Codex, `/name` in Claude Code, plain elsewhere).

**Turn 1: big picture and run.** Show the module map image. Then: the question; the whole process in 2–4 sentences, with where today fits; the key idea; the "how it works" picture or pseudocode; the lab command and what to look at. End with:
`▶ Next: in a terminal in the course folder, run <launcher> <MM>/<Lxx>, then reply "I ran it" with anything you noticed (or reply "run it for me").`

**Turn 2: read the results together.** After the learner runs it, or asks you to run it:
- show the GIF or plot;
- say where to look first;
- connect what is visible to the physical event and to the key idea;
- offer 1–2 "change one thing" commands, each with what to watch.

End with: `▶ Next: run <launcher> <MM>/<Lxx> <key>=<value> and reply "I ran <key>=<value>", or reply "wrap up" to finish the lesson.`

**Turn 3: meaning and transfer.** What the result means and what it does not show (one line). 2–3 transfer bullets. The next lesson's question in one line. Then record progress (section 3) and end with:
`✅ Progress saved. ▶ Next: close this session, start a new one in this folder, and type teach-lesson continue.`
If this was the module's last lesson, say that the next session will start the next module with its overview.

If the learner asks a question at any point, answer that question only, with a picture when useful. Do not advance until they ask. End with `▶ Next:` restating where the lesson stands, for example: `▶ Next: ask another question, or reply "continue" to read the results.`

If the learner simply says "continue" without running the lab, run it yourself and show the results. Their time is the constraint, not the rule.

## 3. Finish (in the same turn as turn 3; do not wait to be asked)

Run `session-handoff` as part of delivering turn 3. Mark the lesson delivered in `MAP.md`, and set `STATE.md`'s next action to the next lesson. A lesson that is not recorded will be repeated by the next session.

If the learner instead says the lesson is finished, or asks for the next lesson, before turn 3: record what actually happened with `session-handoff` first, then continue.

## References

- `LearningProgress/08-microduck-task-lifecycle/lessons/L01-one-env-step/` is a complete, tested example: page, lab and figures. Match its density and tone.
- `LearningPlan/examples/` holds real failed and repaired lessons from this course. Read the one matching your lesson type before writing.
