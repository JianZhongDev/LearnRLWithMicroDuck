---
name: start-course
description: First session of the Learn RL with MicroDuck course - check that the environment is set up, record the learner's background and language, explain how the course works, and show the course map. Use when LearningProgress/STATE.md says the course has not started, or when the learner invokes start-course.
---

# Start the course

Goal: in one short session the learner knows how the course works, the environment is confirmed working, and the first module is ready to begin. Keep it friendly and brief. This is a welcome, not a lecture.

## 1. Environment

Read `.course/env.json`.

- **Missing:** setup has not been run. Use the `setup-environment` skill now: it agrees a plan with the learner (including where the two MicroDuck repositories go, outside this folder), runs setup, and verifies the result. Then continue here.
- **Present:** run `lab doctor` (quick). Read the result:
  - `READY` → continue.
  - `FAIL` lines → use `setup-environment` to repair before teaching anything.
  - no NVIDIA GPU (`device: cpu`, including Apple Silicon) → tell the learner once: simulation labs run on the CPU, smaller and slower, and training-heavy lessons (from Module 09) become short demonstrations unless they have access to an NVIDIA GPU machine.
  - no renderer → tell them once: labs skip robot GIFs; plots and diagrams still work.

## 2. Learner profile

Ask these in **one** message, as a short numbered list. Say they can answer briefly or reply "skip" to use the defaults. These are setup questions, not a test.

1. What language should I teach in?
2. Programming: how comfortable are you with Python? (new / some / fluent)
3. Math: linear algebra, calculus, probability? (rusty / comfortable)
4. Any machine-learning, RL or robotics experience?
5. What do you want to get out of this course? Any time constraints?

Write the answers to `LearningProgress/LEARNER.md` using [assets/LEARNER_TEMPLATE.md](assets/LEARNER_TEMPLATE.md). Fill the machine section from `.course/env.json`. If they skip, record the defaults and say they can change the file any time.

Adapt everything afterwards to this profile. With less Python or math, plan more, smaller lessons and explain more. With more experience, move faster and offer to skip modules they already know (confirm with one or two concrete questions about what they have built, not a quiz).

## 3. How the course works (about 150 words plus the course map)

Show `LearningPlan/figures/course_map.png`. Then say, in the learner's language:

- You teach; they learn by running labs on a simulated MicroDuck robot and changing one thing at a time.
- Each lesson: a short big-picture explanation → they run a lab → you look at the results together → they change one setting → wrap-up. About 20–40 minutes.
- One agent session per lesson. Progress is saved in files, so they can stop any time.
- They can ask anything at any point, and correct your teaching style: you will adapt.
- `START_HERE.md` lists what to type in each situation.

## 4. Record and hand over

- Update `LearningProgress/STATE.md`: course started (date), environment summary, and next action `plan-module` for Module 00. Or a later module if they are skipping ahead; say which and why.
- Do not start Module 00 in the same message. End with:
  `▶ Next: reply "start" to begin Module 00 now, or come back later: open a new session here and type teach-lesson continue.`
- If they reply "start", use `plan-module` for Module 00 and continue from there.
