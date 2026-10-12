# Scattered lesson vs. structure-first repair

*A paraphrased case study, not a transcript.*

## The lesson that failed

Topic: how a trainer keeps experience from different robot copies and different episodes apart.

The lesson *followed* many rules. It stated a question, started from a physical picture, defined its symbols, worked the arithmetic with symbols first, showed a figure, and gave a rerun command. It still failed. Its outline:

```
Question: how does the trainer keep experience from different robots and episodes apart?
Physical picture: two robots, one resets partway through collection (figure)
1. Store time and robot identity separately       - a table of array shapes
2. Stop the return calculation at a true ending   - two formulas, then arithmetic for robot 0,
                                                    then a "change a reward after the reset" test
3. A full buffer is not an episode ending          - arithmetic for robot 1
4. A time-out needs special care                   - a finding about how the installed code
                                                    corrects time-outs, with two competing numbers
Results: a three-panel figure (a grid of values, an isolation test, the time-out comparison)
What happens when training starts: mini-batches and shuffling
```

The learner's reaction, in substance: the lesson was confusing and felt like a pile of separate descriptions. They asked for one thing only: an explanation of the algorithm and its data structures. They also pointed out that the numerical example had been dropped in without being introduced.

### Why it failed

- **No organizing structure first.** Four mechanisms (storage layout, episode boundaries, collection cutoff, time-out correction) plus shuffling, each with its own numbers. Nothing told the reader how they fit together.
- **A detour in the main path.** The time-out finding was interesting but was not the question. It belonged in the notes or the to-do list.
- **Numbers before meaning.** Values appeared for robots and steps whose roles had not been set up.
- **One figure summarizing three different things.** A three-panel figure for three sub-questions is a sign of three lessons.

## The repair that worked

It opened by naming the whole structure in three lines:

> The trainer keeps experience organized with three mechanisms:
> 1. a fixed index for each robot copy;
> 2. a marker on the step that ended an episode, which calculations may not cross;
> 3. one shared record index, so an observation, its action, its reward and its training target always stay together.

Then it showed **one** data structure, as a grid (rows are collection steps, columns are robot copies, one cell is one record) and as aligned arrays:

```python
observations[step, robot]
actions[step, robot]
rewards[step, robot]
episode_ended[step, robot]
```

Then **one** algorithm as pseudocode (collect, then store every field under the same indices), and the backward pass in five plain steps, including "if this record ended an episode, drop the correction carried from the next row".

Its example was **symbolic**: robot copies A and B, with a row labelled "A's last record: ending marker set". There were no arbitrary numbers.

It ended with one sentence that ties it together:

> Keep time order while computing advantages; only then shuffle complete, aligned records for training.

### What to copy

1. Name the parts of the structure in the first lines (a numbered list).
2. One picture or grid of the data, one pseudocode block of the algorithm.
3. Symbolic labels instead of numbers unless numbers *are* the point.
4. One closing sentence that states the key idea.
5. Everything else (the time-out detail, exact array shapes) goes to `NOTES.md` or `TODO.md`.
