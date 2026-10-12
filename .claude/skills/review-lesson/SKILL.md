---
name: review-lesson
description: Check a drafted MicroDuck lesson page or teaching message against the course's teaching rules and rewrite what fails, before the learner sees it. Use before delivering every lesson, module overview, or long explanation.
---

# Review before delivery

Re-read the draft as a beginner who has not seen this conversation. For each item, answer yes or no. Fix every "no" by rewriting, not by adding a caveat. Do not show this checklist to the learner.

## Structure

1. **Map first?** Does the module map (today highlighted) or a big-picture sentence come before any detail, formula or number?
2. **Whole process?** Can a reader say how the whole method goes from input to result, and what today's part changes downstream, using only what is on the page?
3. **One key idea?** Is it stated in one sentence? Does every section serve it? Move anything else to `TODO.md`.
4. **No detours?** Are there no caveats, edge cases or "also note" side topics in the main path? At most one line each, otherwise move them to `NOTES.md`.

## Clarity

5. **Terms introduced?** Is every technical term and abbreviation explained (what and why) before or at first use? Is there no term explained only through other unknown terms?
6. **Examples introduced?** Is every example's purpose and setup given before its numbers? Is each value's source given (measured, from config, or hand-picked)?
7. **Plain words?** Are sentences short? Are there no invented labels? Would a careful beginner trip over any sentence?

## Visual and hands-on

8. **Picture instead of paragraph?** Is every process, structure or timing described in prose replaced by a diagram, table or pseudocode? Is there at least one concept visual before any result plot?
9. **Visual set up?** Before each figure: what it answers, how to read it, and where to look first? Does each result connect to a physical event?
10. **Lab?** Is there a tested command the learner runs, what to look at, and 1–2 "change one thing" commands with what to watch?

## Size and honesty

11. **Short?** Is each chat turn under about 300 words plus one picture? Are long math and source details in `<details>`?
12. **Honest and credited?** Are all numbers from actual runs or source? Are toys and schematics labelled as such? Is no learner understanding claimed? Are the papers, docs and upstream files the lesson relies on named on the page, with no upstream files copied into the repository?
13. **Next step?** Does the message end with a `▶ Next:` line giving the exact command or reply, consistent with `START_HERE.md`?
14. **Fits this learner and machine?** Is it in the learner's language and at their level (`LEARNER.md`)? Does it use their launcher, and do lab defaults suit their device and renderer (`.course/env.json`)?

If items 1–4 fail, restructure: rewrite from the map and the key idea. Do not patch sentences.
