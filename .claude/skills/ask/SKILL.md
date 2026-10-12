---
name: ask
description: Answer a learner's question about MicroDuck course material (any module, a lesson page, a lab result, a term, or the MicroDuck source) without starting or advancing a lesson. Use when the learner invokes ask or asks a question outside an active lesson.
---

# Answer a course question

The learner wants an answer, not a lesson. Do not advance the course and do not change `STATE.md`'s next action.

## Find the context first (quietly)

1. Read `LearningProgress/STATE.md` to see where the learner is.
2. Find the material the question refers to. Use `GLOSSARY.md` for terms. For topics, read the module's `MAP.md`, the lesson's `LESSON.md`, and `NOTES.md`; search `LearningProgress` for the topic if needed. For results, look at the learner's `results/` folders. Check the MicroDuck source (the `rl_repo` and `runtime_repo` checkouts in `.course/env.json`, read-only) when the question is about how the robot or trainer actually works.
3. If the question depends on a lesson the learner has not reached, answer briefly at the level they have reached, and say which upcoming lesson covers it in depth.

## Answer

- **Lead with the direct answer** in 1–3 plain sentences. Then give only the context needed to make it make sense, starting with where it sits in the big picture (which box of the module map, or which stage of the course).
- **Show it** when a picture beats words: reuse an existing figure or GIF, or draw a quick diagram, table or pseudocode. Follow `TEACHING_RULES.md` (plain words, terms explained, symbols before numbers).
- **If running something answers it best**, use a small `duckkit` script. Save it with its outputs in `LearningProgress/<module>/questions/<YYYY-MM-DD>-<short-topic>/`, run it, show the result, and give the rerun command. Keep it to a few minutes.
- If you find that an earlier lesson page was wrong or unclear, say so plainly, fix the page, and note the fix.
- Keep it under about 300 words plus one picture unless the learner asks for depth.
- End with `▶ Next:`, for example: `ask a follow-up, or start a new session and type teach-lesson continue to resume the course at <lesson>.`

## Record

Append a short dated entry to the relevant module's `NOTES.md`: the question (verbatim if short), the answer's key point, any artifact paths, and any page fixes. Add new terms to `GLOSSARY.md`. If the question shows that a lesson was confusing, add one line to `LearningPlan/FEEDBACK_LOG.md`. Do not record the learner as having understood the answer.
