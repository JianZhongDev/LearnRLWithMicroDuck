---
name: plan-module
description: Start a new module of the MicroDuck robotics/RL course - big-picture map diagram, ranked core ideas, and a short lesson list with a hands-on lab per lesson. Use before the first lesson of any module or when a module's scope changes.
---

# Plan a module

The output is `LearningProgress/<module>/MAP.md` plus map figures, and a short overview message to the learner. Use [assets/MAP_TEMPLATE.md](assets/MAP_TEMPLATE.md).

## Steps

0. **Create the module's standard files.** From the repository root, run `lab py .agents/skills/plan-module/scripts/scaffold_module.py <NN>`. It creates `MAP.md` (template), `NOTES.md`, `TODO.md`, `figures/` and `lessons/` and never overwrites existing files. Then fill in `MAP.md` with the steps below.
1. If the module already has a filled-in `MAP.md` (Module 08 ships pre-built), do not redo it: check it against the learner's machine and profile, then go to the last step and present it.
   Otherwise read the module's entry in `LearningPlan/LEARNING_PLAN.md`, its `TODO.md`/`NOTES.md` if present, and the previous module's open items in `STATE.md`.
2. Write the module's **big question** in plain words.
3. Draw the **big-picture process** as 4–6 boxes: the system or algorithm this module explains, from input to result. Every lesson must be a part of this picture. If a planned topic does not fit, it is probably a detour.
4. **Rank** the content:
   - **Core** (most of the time): 2–4 ideas the learner must be able to use;
   - **Supporting** (brief, one lesson or less);
   - **Reference only** (look up when needed: exact dimensions, names, config values);
   - **Deferred** (into `TODO.md`).
5. Plan **3–6 lessons**. Each gets one question, one key idea, which box(es) of the map it zooms into, and a lab: what the learner runs and the one thing they change. Prefer labs on the real MicroDuck model or environment through `duckkit`, in the early modules too. Size them for the learner's machine (`.course/env.json`): on `cpu`, plan small simulations and treat training as a short demonstration.
6. Generate one map figure per lesson with that lesson's boxes highlighted. Use `duckkit.flow_diagram` and keep the generating script in `<module>/figures/`.
7. Check that each lab idea is feasible: the API exists, it runs in a few minutes, and the output is visible.
8. If the course stage changed, update the whole-course map: run `lab py LearningPlan/figures/make_course_map.py <stage index 0-5>`.
9. Send the learner the course map (`LearningPlan/figures/course_map.png`), the module map image, the big question, and the numbered lesson list, about 200 words in total. Start lesson 1 only if they ask. End with: `▶ Next: reply "start L01" to begin the first lesson, or ask about the plan.`

## Reference

`LearningProgress/08-microduck-task-lifecycle/MAP.md` and `figures/make_figures.py`.
