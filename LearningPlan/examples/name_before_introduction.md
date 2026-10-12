# Naming a method before introducing it vs. whole-cycle first

*A paraphrased case study, not a transcript.*

## The lesson that failed

The module on Proximal Policy Optimization (PPO) began with an overview that listed component names: policy ratios, clipping, value predictions, advantage estimation, a complete update. The first lesson then went straight to the first component. It asked why we compare the current policy with the policy that collected the experience, defined a probability ratio, computed two example values, and derived a logarithm form and a reweighted expected return.

The learner's reaction, in substance: had PPO itself ever been introduced? They said that dropping an unfamiliar name or concept into a lesson without at least a brief introduction makes it very hard to follow. Two lessons later the same problem came back in another form, and they asked for the big picture of the whole method before any detail. The module was restarted.

### Why it failed

- The method's name was expanded as an abbreviation but never explained: what problem it solves, and what its steps are.
- The lesson answered "why compare policies?" before the learner knew that training *updates* a policy using a score, a gradient and fresh data.
- The module overview was a list of component names. That is a table of contents, not a big picture.

## The version that worked

It started from the robot: a simulated MicroDuck trying to walk at a requested speed. It posed the training problem in one line and gave PPO's purpose in plain words: learn from recent experience while discouraging changes that are too large. Then it walked through the **five connected steps** of the whole cycle. For each step it said what goes in, what is done, and why:

```
1. Collect experience with the current policy (weights fixed; record actions and their probabilities)
2. Estimate which actions deserve more or less preference (compare the outcome with what was expected)
3. Turn those assessments into a training score for the policy being adjusted
4. Use the score's sensitivity to each weight (its gradient) to change the weights
5. Collect fresh experience after a limited amount of updating
```

It stated the connection that had been missing:

> Recorded outcomes define the training score. The score's sensitivity to the weights guides the update. The changed weights alter future action choices.

Ratios and clipping came **four lessons later**, placed inside step 3.

### What to copy

- The first lesson of a method is the whole cycle, drawn as a diagram, each step with input → operation → output.
- Components come later, always shown inside the cycle diagram ("today: the highlighted box").
- This is rule 1, and it is why every lesson opens with the module map.
