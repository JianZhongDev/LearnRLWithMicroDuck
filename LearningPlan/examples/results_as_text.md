# Results as a number table vs. picture-first results

*A paraphrased case study, not a transcript.*

## The presentation that failed

A lesson computed advantage estimates for a short four-step route, then showed the script's output as text: a table with one row per step (reward, value before, value after, one-step error, combined estimate), followed by three lines comparing the first step's estimate under three settings of one parameter. Column definitions and an interpretation followed in prose.

```text
 step  reward  value_now  value_next  one_step_error  combined_estimate
    0     ...        ...         ...             ...                ...
    1     ...        ...         ...             ...                ...
 setting A: first-step estimate = ...
 setting B: first-step estimate = ...
```

The learner's reaction, in substance: the results had been presented without first giving the physical picture; they should have been shown with pictures or animations instead of plain text; and results should never appear out of nowhere. They asked for those sections to be redone.

Worth noting: the learner had approved the previous lesson and had asked for script results to be shown with a clear description. A table *is* a description, but it was not what they meant.

## The redo that worked

1. **The physical journey first.** A short animation of the robot moving along the route, stop by stop. It was labelled as a constructed replay, not a simulation. Each arrival revealed the reward and the predictions.
2. **A reading guide before the figure:** each row is one movement from the animation; one color is the one-step assessment and the other includes later information; right of zero means better than predicted.
3. **A results picture** mapped to those movements (one horizontal bar pair per movement), with a pointer to the row to read first.
4. **One more picture** for the parameter comparison (running totals as bars), again with a reading guide first.

## What to copy

- Order: physical event → how to read the picture → picture → where to look first → meaning.
- A printed table is a supplement for exact values, never the main presentation.
- In this course the lab produces the GIF and the plot. The lesson's second chat turn shows them with a reading guide.
