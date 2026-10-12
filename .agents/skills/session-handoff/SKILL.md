---
name: session-handoff
description: Record a finished MicroDuck lesson or experiment so the next session can continue without chat history - update STATE.md, append to the module NOTES.md, update MAP.md lesson status, GLOSSARY.md and TODO.md. Use at the end of every lesson or substantive experiment.
---

# Hand off to the next session

Files are the only memory between sessions. Keep them short and accurate.

If the module folder lacks `MAP.md`, `NOTES.md` or `TODO.md`, create them first with the `plan-module` scaffold script (`lab py .agents/skills/plan-module/scripts/scaffold_module.py <NN>` from the repository root).

## 1. `LearningProgress/STATE.md` (rewrite the "Now" section; it stays under about 40 lines)

- Active module and lesson, and the lesson status (planned / ready / delivered / learner ran lab).
- **Next action:** one concrete sentence, for example "Deliver 08/L02: page and lab are ready and tested".
- Open learner questions, verbatim if short.
- Keep the module table current. Do not let the file grow into a log; history goes in NOTES.

## 2. `<module>/NOTES.md` (append, never rewrite history)

```
## YYYY-MM-DD — Lxx <title>
- Question / key idea:
- Delivered: page path, figures, lab path; what was verified and how
- Learner did: commands they ran, settings they changed, questions they asked (only what happened)
- Results: key numbers with units, artifact paths
- Source facts used: file:line
- Problems / feedback: what confused the learner and what was changed
```

## 3. Other files

- `<module>/MAP.md`: update the lesson's status column.
- `LearningProgress/GLOSSARY.md`: add new terms (one plain line each, plus the lesson where introduced).
- `<module>/TODO.md`: parked side topics and unfinished work.
- `LearningPlan/FEEDBACK_LOG.md`: one dated line if the learner corrected the teaching.
- `LearningProgress/LEARNER.md`: add lasting preferences or background you learned about the learner (one line each).

## Tell the learner

End your message with `✅ Progress saved.` and a `▶ Next:` line. After a finished lesson: `close this session, start a new one in this folder, and type teach-lesson continue`. After a mid-lesson pause: `next time, start a new session and type teach-lesson continue; it resumes at <turn>`.

## Rules

- Record only what actually happened. A teacher's explanation or a successful command is not learner mastery.
- Write in plain sentences, not compressed tokens like `p0.5->0.505`.
