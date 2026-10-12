# Explaining an iterative algorithm or a stored data structure

This order was refined with a learner on value iteration (Module 05) and on how a trainer keeps experience separated (Module 07). Lessons that skipped it were rejected as confusing.

Explain the **organizing structure before any example values**:

1. **What is stored.** Name each table, buffer or array, and what one entry means in words.
2. **How it is indexed and owned.** For example: rows are collection steps, columns are robot copies, and one cell is one transition. Draw it as a labelled grid.
3. **Initialization.** What every entry holds before the first update, and why.
4. **One update.** What it reads, what it computes, and what it writes. Show the read set and the write set explicitly. Keep "old table" and "new table" separate if the algorithm does.
5. **Order and boundaries.** What runs forwards or backwards in time, and where it must stop (episode end, reset). Say what is *not* allowed to mix.
6. **Who consumes the result** next, and when.
7. Only then give one worked update with symbolic labels or small numbers, then the full history if useful.

Pseudocode is usually the clearest form for steps 3–6. A diagram of the grid is usually the clearest form for steps 1–2.
