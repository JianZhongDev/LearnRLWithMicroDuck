# LearningProgress: your course

This folder is your copy of the course in progress: where you are, what you have covered, and every lesson and lab. The teaching agent writes here. Learners: start with [`../START_HERE.md`](../START_HERE.md).

## Layout

```
LearningProgress/
  STATE.md            current position and next action; the agent reads it first
  LEARNER.md          your background, goals, machine and teaching language
  GLOSSARY.md         plain one-line definitions of course terms
  _shared/
    duckkit/          helper library for labs: robot environments, rollouts, GIFs, diagrams
    selftest.py       simulation self-test, run by `lab doctor --full`
  NN-module-name/
    MAP.md            big-picture diagram, ranked ideas, lesson list
    NOTES.md          dated history: what was taught, run, measured and asked
    TODO.md           parked side topics and unfinished work
    figures/          concept diagrams and the script that makes them
    lessons/Lxx-name/
      LESSON.md       the lesson page: map, key idea, diagram, lab, what it means
      lab.py          the hands-on lab (run it, change one setting, compare)
      results/<settings>/   created when you run the lab, one folder per setting (not in Git)
    questions/        small demos made to answer your questions (created when needed)
```

Module folders start empty. The agent fills each one when you reach it, starting with `MAP.md`. Module 08 ships with five ready-made lessons as the reference for format and depth.

## Running a lab

From the course folder (`lab` = `./lab.sh`, or `.\lab` on Windows):

```
lab list                       # all labs
lab 08/L01                     # default settings
lab 08/L01 help                # settings you can change
lab 08/L01 action_noise=0.3    # change one thing; results are kept separately
```

## Recording rules (for the agent)

- Append dated entries to `NOTES.md`; never rewrite history.
- Keep `STATE.md` short and current.
- Record learner work only when the learner actually did it. Never infer mastery from an explanation or a successful command.
