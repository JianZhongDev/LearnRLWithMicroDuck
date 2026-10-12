# Module 08 — How a simulator becomes an RL environment

![Module map](figures/map_L01.png)

**Big question:** When we "train MicroDuck in simulation", what exactly happens on each step, how do episodes start and end, and how does that become training data?

**Why it matters:** Modules 00–04 built the physics and sensing pieces; Modules 05–07 built the learning algorithm. This module joins them. Every later module (rewards, new tasks, robustness, export) changes one box of this loop, so you need to see the whole loop working first.

## The process this module explains

A robot copy starts from a **reset** pose. Each step, the environment turns sensor readings into an **observation** (a list of numbers). The **policy** turns it into an **action** (joint targets). The physics engine **simulates** 20 ms, and the environment **scores** the result with a reward and checks whether the episode should end. A robot that ended goes back to reset. Many copies run this loop in parallel, and their steps become a training batch.

## What we spend time on

| Rank | Idea | Lesson |
|---|---|---|
| Core | One `env.step()`: what goes in, what comes out, and how much time passes | L01 |
| Core | Episodes end (fell over vs time up) and each robot copy resets on its own | L02 |
| Core | Reward is a sum of named, weighted terms, and it is a specification you can inspect | L03 |
| Core | Many robots × many steps = one training batch for PPO | L05 |
| Supporting | Where the observation numbers come from (actor vs critic view) | L04 |
| Reference only | Exact term names, weights, observation slot layout, config class names | look up with `describe_env` |
| Deferred | Timeout value-bootstrap integration question from Module 07 (see its TODO) | optional check inside L02 |

## Lessons

| Lesson | Question | Key idea | Lab: run, then change one thing | Status |
|---|---|---|---|---|
| L01 | What happens in one `env.step()`? | One step = action in → 4 × 5 ms of physics → reward + ended? + new observation out. | Watch 4 robots hold the default pose; change `action_noise`, `config=play` | ready (pre-built, tested) |
| L02 | How do episodes end and restart? | Keep the ending reason and reset only the copies that ended. | Timeline of endings for 16 robots; shorten `episode_seconds` | ready (pre-built, tested) |
| L03 | Where does the reward number come from? | Reward is the sum of named contributions (term × weight × step duration here). | Inspect contributions with fixed vs random joint targets; change `action_noise` | ready (pre-built, tested) |
| L04 | What does the policy actually see? | The policy receives selected, processed readings and commands; the training critic can receive more information. | Inspect actor/critic pieces and plot gravity readings during a fall; change `gravity_noise` | ready (pre-built, tested) |
| L05 | How do steps become training data? | A batch holds one record per robot per collected step; robot count changes data per update. | Run 64 robots for 5 training iterations; inspect the batch grid and log, then change `num_envs=32` | ready (pre-built, tested) |

## Practical outcome

You can open any mjlab or Gym-style robot environment and answer: what is in an observation and an action, how often decisions happen, how episodes end, what the reward pays for, and how much experience one training update uses. You can check all of this by running the environment, not only by reading the config.
