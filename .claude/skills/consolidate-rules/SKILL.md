---
name: consolidate-rules
description: Fold new learner feedback from LearningPlan/FEEDBACK_LOG.md into LearningPlan/TEACHING_RULES.md without growing or duplicating the rules. Use when the feedback log has unprocessed entries or the learner asks to improve the teaching rules.
---

# Consolidate teaching rules

Stacking a new "strict" section for every correction made the old rules long, repetitive and easy to forget. This skill keeps the rules short.

## Steps

1. Read `LearningPlan/FEEDBACK_LOG.md` (entries without `[merged]`) and `LearningPlan/TEACHING_RULES.md`.
2. For each entry, decide:
   - **Already covered:** the rule exists but was not followed. Make the existing rule clearer or move it higher, or add the item to the `review-lesson` checklist. Do not add a duplicate.
   - **New preference:** add it to the single best existing rule, as a sentence or a short "Failure:" example.
   - **Lesson-specific:** fix the lesson or skill instead of the rules.
3. Keep `TEACHING_RULES.md` under about 150 lines and keep the ranking meaningful. If it grows, merge or cut.
4. Write rules in plain, positive form ("Do X"), with one short real example of the failure where it helps. No dates in headings, and no references that a fresh agent cannot resolve.
5. Mark processed log entries `[merged YYYY-MM-DD]`.
6. If a change affects `AGENTS.md`'s core list or a skill, update it there too, so the core list and the rules never disagree.
7. Show the learner the diff summary in 3–5 lines.
