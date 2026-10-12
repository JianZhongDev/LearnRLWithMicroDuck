---
name: explain-math
description: Explain a formula, derivation, worked calculation, iterative algorithm, or coordinate transform in the MicroDuck course so a beginner can follow every step. Use when a lesson or answer contains equations or numbers derived from a rule.
---

# Explain math readably

The learner is strong at math but new to robotics and RL. Their difficulty is not the algebra. It is **unexplained structure**: numbers before the formula, symbols with no meaning, and steps with no purpose.

## Order (always)

1. **Purpose.** Say in one sentence what this calculation tells us and where it sits in the big picture.
2. **Formula in symbols**, then a table of every symbol: meaning, units, frame or index meaning, scalar/vector/matrix.
3. **Why it has this form.** Give the intuition in 1–3 sentences: what each term does, and what happens at limiting values.
4. **The example**, introduced before its numbers: what it is and where each value comes from (measured, from config at `file:line`, previously computed, or hand-picked for readability).
5. **Expand symbolically** for the example, then substitute, then show each arithmetic step. Keep signs, denominators and rounding visible.
6. **Meaning of the result**, and what it feeds into next.

For a large computation, work one small complete case and say it is a small case. Do not replace a worked step with "the code computes it".

## Keep it light on the page

The main lesson path needs only steps 1–3 and the final meaning. Put steps 4–5 in a `<details>` block unless the arithmetic *is* the lesson. Never cut steps inside the block.

## Special protocols (read when relevant)

- Coordinate frames and transforms: [references/coordinate_transforms.md](references/coordinate_transforms.md)
- Iterative algorithms and stored tables or buffers (value iteration, advantage recursion, storage): [references/iterative_algorithms.md](references/iterative_algorithms.md)
- Mechanisms driven by sensing and physical events (contact detection, odometry, resets): [references/physical_process.md](references/physical_process.md)
