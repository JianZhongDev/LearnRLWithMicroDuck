---
name: make-visual
description: Choose and produce the right teaching visual for the MicroDuck course - big-picture maps, process diagrams, pseudocode, captioned robot GIFs, and result plots that answer one question. Use whenever a lesson or answer explains a process, structure, timing, geometry, or a measured result.
---

# Make a teaching visual

A visual must save the learner reading. If a paragraph describes how something flows, is arranged, or changes over time, it should be a picture or a code block.

## Pick the form

| You are explaining | Use | How |
|---|---|---|
| Where today's topic fits | module map, today highlighted | `dk.flow_diagram(..., highlight=...)` (one per lesson, made by `plan-module`) |
| A process or algorithm (steps in order) | flow diagram **or** pseudocode | `dk.flow_diagram`; or a `python` code block with plain names and comments |
| What happens over time inside a step | timeline with labelled blocks | matplotlib boxes on a time axis (see Module 08 `figures/make_figures.py`, `step_timeline.png`) |
| Data layout (buffers, tensors) | labelled grid, rows and columns named | matplotlib rectangles; or a small markdown table with symbolic entries |
| Robot motion, contact, falling | captioned GIF of the real robot | `dk.rollout(render=True)` → `dk.caption_frames` → `dk.save_gif` |
| A pose or geometry | still render with labels, or a 2D schematic | `dk.model_snapshot`, then annotate with matplotlib |
| A measured result | 1–3 panel plot | units on axes, takeaway title, events marked, legend off the data |
| Comparing settings | overlay or small multiples from saved runs | read `results/*/signals.npz` |

## Rules

- **Concept before result.** Show how it works before showing what happened.
- **Set up before showing.** One sentence each: what question this answers, how to read it, where to look first.
- **Label on the picture**, not only in a legend or the text. Use words, not variable names, plus units.
- **One message per figure.** At most 3 panels. Remove gridlines, colors and decorations that carry no meaning.
- **Link the visual to the physics.** Mark the moment of the key event (fall, reset, contact) the same way in the GIF caption and the plot.
- **Label schematics as schematics.** A drawn replay is not simulation evidence.
- **Robot renderings stay in `results/`.** GIFs and stills of the robot are renderings of Pollen Robotics' 3D model (CC BY-NC-SA). Save them only in a lab's `results/` folder, which Git ignores. Everything in tracked folders (`figures/`, `docs/`, lesson pages) must be a diagram or plot made by the course's own code, so the repository stays MIT throughout. Lesson pages link to the learner's local `results/.../robot.gif` instead of embedding a committed copy.
- **Look at it** after generating (open the image), and fix overlaps, clipped text and unreadable fonts.
- Keep the generating script next to the figure: `<module>/figures/` for concept figures, the lab for results.

## Format notes

- PNG and GIF render everywhere: on lesson pages, on GitHub, and in most agent chats as `![alt](path)`. They are the default.
- Mermaid blocks are fine for quick flowcharts on a lesson page, but VS Code's preview needs the "Markdown Preview Mermaid Support" extension. Also provide a PNG when it matters.
- Pseudocode beats prose for algorithms. Keep it under about 20 lines, use real control flow, and comment *why*, not *what*.
- Plain-text arrows (`obs -> policy -> action`) are fine for a one-line chain in chat.
