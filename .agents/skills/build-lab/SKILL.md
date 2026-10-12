---
name: build-lab
description: Write and test a hands-on lab for the MicroDuck course using the shared duckkit library - a script the learner runs with one command and re-runs with one changed setting. Use when preparing a lesson's lab or any learner-run experiment.
---

# Build a lab

A lab lets the learner **run it, look at the result, change one thing and compare**. It lives at `LearningProgress/<module>/lessons/<Lxx-name>/lab.py` and runs with `lab <MM>/<Lxx> [key=value ...]` from the repository root. `lab` means the launcher recorded in `.course/env.json` (`./lab.sh`, or the Windows `lab` command).

## Design first (5 lines in your notes)

- **Question** the lab answers, matching the lesson's key idea.
- **What the learner sees:** a GIF of the robot and/or 1–2 plots, plus a short printed table.
- **Settings** worth changing: 2–4, each with a clear expected effect. Defaults must give a clear, typical result.
- **Real system:** use the MicroDuck environment through `duckkit` unless a toy shows the idea much better. If you use a toy, say why in the docstring.
- **Run time:** under about 3 minutes on the learner's machine. Check `.course/env.json`: on `device: cpu` keep defaults small (2–4 robot copies, a few seconds). The first simulation run compiles code and takes 1–3 minutes; later runs are faster.
- **Works without a GPU or renderer:** do not hard-code `cuda`; always produce a plot, because GIFs are skipped when `mujoco_gl` is `null`.

## Write it

Start from [assets/lab_template.py](assets/lab_template.py). Rules:

- `import duckkit as dk` first, then `run = dk.lab_config({...}, help={...})`. Every setting gets a help string with units.
- Results go in `run.out` (one folder per setting combination). Comparisons across runs go in `run.lab_dir / "results"`.
- Print a short, readable table: column names in words, units, and a few rows. Do not dump tensors.
- Figures: `dk.use_style()`, units on axes, a title that states what to see, and mark events such as resets or falls. Captioned GIFs: `dk.caption_frames` + `dk.save_gif`; use a red caption for key events.
- Read MicroDuck source but never write to it. Change behavior through `make_env(configure=...)` on the config copy, or a wrapper.
- The docstring at the top states: the question, the run command, the change-one-thing command, and each output file.

## Test it (always, before the lesson)

1. Run the default and at least one changed setting.
2. Open every image (GIF frames included) and check it answers the question at a glance.
3. Check numbers against an independent quantity where possible (example: reward terms sum to total reward).
4. Delete your test `results/` folders so the learner starts clean. Record what you verified in `NOTES.md`.

## duckkit API

See [references/duckkit.md](references/duckkit.md) when you need function signatures.
