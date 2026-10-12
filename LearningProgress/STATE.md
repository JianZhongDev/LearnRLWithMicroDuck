# Course state

Read this first in every session. Keep it short: history belongs in module `NOTES.md` files.

## Now

- **Status:** the course has **not started**.
- **Next action:** use the `start-course` skill: check the environment, record the learner profile in `LEARNER.md`, show the course map, then plan Module 00 with `plan-module`.
- **Open learner questions:** none.

## Modules

| Module | Topic | Status | Notes |
|---|---|---|---|
| 00 | The feedback loop: goal, observation, action; controller vs learned policy | not started | |
| 01 | Robot model and physics: coordinates, joints, mass, contact | not started | |
| 02 | Frames, forward kinematics, Jacobians | not started | |
| 03 | Actuators and joint control: PD control, motor limits, delay | not started | |
| 04 | Observations, sensors and state estimation | not started | |
| 05 | Tabular RL: returns, value, Q-learning | not started | |
| 06 | Neural policies and policy gradients | not started | |
| 07 | Advantage estimation and PPO | not started | |
| 08 | How a simulator becomes an RL environment | not started | 5 lessons with labs are pre-built: `08-microduck-task-lifecycle/MAP.md` |
| 09 | Walking baseline and evaluation | not started | |
| 10 | Reward design and reward exploitation | not started | |
| 11 | A new task and a curriculum | not started | |
| 12 | Domain randomization and the transfer gap | not started | |
| 13 | Fair RL experiments | not started | |
| 14 | Export a policy and verify it | not started | |
| 15 | Run the real robot software against a simulated body | not started | needs the Rust toolchain; see `docs/ENVIRONMENT.md` |
| 16 | Perception and odometry | not started | |
| 17 | Capstone: improve one behavior and defend the result | not started | |

Status values: not started → planned (MAP.md written) → in progress (lesson Lxx) → finished (date). Record participation, never assumed mastery.

## Where things are

- Learner profile: `LearningProgress/LEARNER.md`. Terms: `LearningProgress/GLOSSARY.md`.
- Rules: `LearningPlan/TEACHING_RULES.md`. Feedback: `LearningPlan/FEEDBACK_LOG.md`. Course plan: `LearningPlan/LEARNING_PLAN.md`.
- This machine: `.course/env.json` (launcher, device, rendering). Lab tools: `LearningProgress/_shared/duckkit`.
