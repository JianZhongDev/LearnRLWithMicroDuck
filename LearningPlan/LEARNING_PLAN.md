# Learn robotics and reinforcement learning through worked examples

Audience: the teaching agent (and curious learners).

This curriculum teaches transferable robotics and reinforcement-learning concepts and engineering methods. The `microduck` runtime and `microduck_rl` training repositories ([pollen-robotics](https://github.com/pollen-robotics)), obtained by setup as separate checkouts outside this repository, provide a concrete worked example. The goal is to understand, implement, train, evaluate, and debug control systems and learned policies, then apply those methods to other robots and tasks. Robot-specific specifications and implementation details are reference material, not facts to memorize. Completing a command is not the same as learning the concept.

Teaching emphasis: introduce the general problem, explain a simple model, apply it to MicroDuck, and summarize what transfers and which assumptions must be checked again.

## How to use this file

![Course map](figures/course_map.png)

This is the course *content* plan. How to teach is in [TEACHING_RULES.md](TEACHING_RULES.md) and the skills in `.agents/skills/`. Where we are is in `LearningProgress/STATE.md`. Each module's detailed plan is its `LearningProgress/<module>/MAP.md`, created by the `plan-module` skill from the entry below. The Read/Do/Teach/Evidence notes below are raw material for that plan, not a script to present.

Every lesson has a hands-on lab (`lab <MM>/<Lxx>`, built with `LearningProgress/_shared/duckkit`). The learner runs it and changes one setting. Use the real MicroDuck model or environment whenever the topic allows it, including in the early modules: a single MicroDuck joint, the robot standing or falling, its sensors. Use a small toy model only when it shows the idea more clearly, and then connect it back to the robot. Module 08 ships with five ready-made lessons as a reference for format and depth.

The module entries were written with one particular computer in mind. Read the learner's actual machine from `.course/env.json`: without an NVIDIA GPU, keep simulations small and treat the training-heavy modules (09–13, 17) as short demonstrations unless the learner has access to a GPU.

Pacing is flexible and asynchronous. The module hours below are planning estimates, not a weekly schedule or prerequisite test. Keep each session bounded to the learner's available time, with a concise explanation followed by guided experimentation and interpretation. Rust expertise is not required for the early RL modules.

### Outcomes and assessment

By the end, the learner should be able to:

- Trace observations through a neural policy, action scaling, actuator dynamics, physics, and feedback.
- Explain frames, kinematics, contacts, PD control, sensor noise, delays, and basic state estimation.
- Implement a small RL learner and explain return, value, advantage, policy gradients, GAE, and PPO.
- Formulate a robot-control problem as an RL task, implement it using MicroDuck as the example, train reproducibly, and evaluate behavior beyond its training reward.
- Diagnose reward exploitation, observation errors, unstable optimization, and simulation mismatch.
- Preserve preprocessing and interface semantics when exporting a policy, verify numerical agreement, and rehearse the control stack in simulation; use ONNX, CPU MuJoCo, and the MicroDuck daemon as the concrete tools.
- Explain which failures simulation can reveal and which require physical hardware.
- Apply these methods to a different mechanism or task, identifying which assumptions, measurements, and interfaces need to change.

Use the evidence suggestions below to guide practical work and progress notes, not to administer exams or require a score before continuing. Record observed implementation, reasoning, and diagnosis with references available. Demonstrating transfer can be a short comparison or a changed assumption within the current experiment; it need not require training a second robot.

### First introduction: the reusable control loop

Begin with a familiar problem: making a joint reach a target despite inertia or a disturbance. A controller receives a desired goal and measured feedback, chooses an action, and observes the resulting motion. A learned policy can fill the controller role; RL training adjusts that policy using experience and rewards.

```text
desired goal + measured observation -> controller/policy -> actuator -> physical system
                        ^                                                   |
                        +---------------- sensor feedback -----------------+

Training: collect experience -> evaluate rewards/returns -> update the policy
Inference: use the resulting policy to choose actions in the feedback loop
```

Teach the distinction between state, observation, goal, action, and reward before introducing repository names or tensor dimensions. MicroDuck then supplies a concrete instance of each component. A robot arm or wheeled robot uses the same reasoning pattern, although its sensors, action representation, dynamics, and task objectives can differ.

## The two projects and their connection

Use this section as a source-navigation reference when a lesson needs it. It is not an opening lecture or a repository tour to memorize.

Setup obtains both projects as checkouts **outside this repository** (by default next to it), at the commits listed in `tools/pins.env`. They are used read-only, and none of their code is stored here:

- RL training source: the `microduck_rl` checkout (`rl_repo` in `.course/env.json`). RL source references below are relative to it.
- Robot runtime source (Rust): the `microduck` checkout (`runtime_repo` in `.course/env.json`). Runtime references below are relative to it. Building and running it is only needed from Module 15 and has its own setup step (see `docs/ENVIRONMENT.md`).

Installed libraries such as `mjlab` and `rsl_rl` live in the course Python environment; `lab py tools/where.py mjlab rsl_rl` prints their folders.

```text
Training: command + simulated observation -> actor -> joint targets -> BAM + MuJoCo
                          ^                                      |
                          +--------- next observation -----------+
         rewards + privileged critic data -> PPO update -> checkpoint

Deployment: checkpoint -> repository ONNX exporter -> policy + manifest
                                                    |
                     robotd -> observation builder -> ONNX -> safety/control -> body
                                                                               |
                                                           simulated or physical
```

Training uses a simulator's reward to improve a policy; deployment runs the resulting policy without PPO or a reward calculator. A policy is one component of a robot's control system, alongside sensing, command arbitration, safety, and actuator control.

### Source map: read with a concrete question

| Question | RL source | Runtime source |
|---|---|---|
| What body and actuators are simulated? | `robot/microduck_constants.py`, under `src/mjlab_microduck`; `robot/microduck/robot_*.xml` | `duck-control/src/model.rs`, `kinematics/src/mjcf.rs` |
| What enters and leaves the policy? | `tasks/microduck_velocity_env_cfg.py`, `tasks/mdp.py` | `duck-control/src/obs.rs`, `duck-control/src/policy.rs` |
| How do actions reach joints? | `actuator/friction_dr_bam.py`, action config | `duck-control/src/io.rs`, `bus.rs`, `robotd/src/control.rs` |
| Where do PPO choices live? | walking runner config; installed `rsl_rl` algorithm, storage, runner, and model code | Inference only; do not look for PPO in `robotd` |
| How are failures/reset handled? | termination and event terms in `tasks/`; NaN tests | `duck-control/src/safety.rs`, `fall.rs`, `robotd/src/intents.rs` |
| How is geometry/state estimated? | robot XML, contact sensors, observations | `kinematics/src/`, `odometry/src/lib.rs`, `duck-control/src/imu.rs` |
| How does an export become usable? | `src/mjlab_microduck/export.py`, `publish/`, `scripts/infer_policy.py` | `docs/policy-manifest.md`, `docs/recurrent-policies.md` |
| How can the real control stack run without hardware? | `src/mjlab_microduck/sim/body_server.py`, `camera.py`, `tof.py` | `docs/robot/simulation.md`, `scripts/duck-sim`, `duck-control/src/sim.rs` |

In the first table row, and throughout this file, abbreviated RL paths such as `tasks/mdp.py` mean paths beneath `src/mjlab_microduck/` unless a different prefix is explicit. Locate third-party implementation files from their installed modules, rather than assuming a source layout from a newer online tutorial.

### General interface principles to introduce when needed

- Inputs and outputs have meaning beyond their dimensions: verify units, frames, ordering, scaling, normalization, and availability at inference.
- Generalized coordinates, physical joints, actuators, and policy actions describe different things. Derive their relationships from the model and action representation.
- Actor and critic inputs may differ; privileged training information must not silently leak into deployed actor inputs.
- Physics, sensing, and control may run at different rates. Derive the timing relationship and evaluate delays or filtering as changes to the closed loop.
- Parameter changes matter only if they affect the active dynamics or sensing path. Trace where a value is used and measure its effect.
- Export and deployment must preserve the trained policy's preprocessing and action semantics. Correct shapes alone do not establish compatibility.

Exact MicroDuck values and implementation cautions are in the appendix. Look them up at the point of use and recheck the selected task's source.

## Course sequence

Hours below are active learning estimates; they exclude unattended compute, unexpected installation work, and optional hardware extensions. Approximately 130–175 active hours is a reasonable initial budget.

The **Read**, **Do**, **Teach**, and **Evidence** entries below are teacher planning notes, not the order of presentation. Teach the concept before a source walkthrough. Use only the files and technical details needed for the current question. End with a short transfer summary: for example, joint-control reasoning also applies to an arm, observation-schema validation to a mobile robot, and export parity checks to other learned controllers. State the assumptions and limits of that comparison.

| Module | Project/result | Typical hours |
|---|---|---:|
| 00 | Reproduce the environment and explain the feedback loop | 3–4 |
| 01 | Read a robot model and investigate motion and contact | 4–6 |
| 02 | Compute frames, forward kinematics, and a Jacobian | 6–8 |
| 03 | Tune a joint controller and study actuator dynamics | 6–8 |
| 04 | Build observations and investigate noisy state estimates | 6–8 |
| 05 | Implement tabular RL on a tiny environment | 6–8 |
| 06 | Implement a small neural policy-gradient learner | 6–8 |
| 07 | Compute GAE and inspect/implement a PPO update | 8–10 |
| 08 | Instrument an RL environment's step and reset lifecycle | 5–7 |
| 09 | Reproduce and evaluate a walking baseline | 8–10 |
| 10 | Design rewards and deliberately discover exploitation | 8–10 |
| 11 | Train a new pose/transition task with a curriculum | 8–12 |
| 12 | Test domain randomization, backlash, and transfer gaps | 8–10 |
| 13 | Conduct a controlled optimization/evaluation study | 8–10 |
| 14 | Export and verify a policy in CPU MuJoCo | 6–8 |
| 15 | Rehearse through the Rust runtime in simulation | 8–12 |
| 16 | Connect locomotion to perception and state estimation | 6–8 |
| 17 | Complete and defend a reproducible capstone | 15–20 |

Dependencies: 00–04 provide robotics foundations; 05–07 teach the RL algorithm; 08–10 join them; 11–14 improve and deploy a skill; 15 integrates a runtime control stack; 16 broadens robotics; 17 integrates the evidence. Adapt depth to demonstrated experience, while still covering reward, observation, evaluation, and deployment reasoning. Each module should end with a brief explanation of what transfers and what is specific to the worked example.

### Module 00 — Make the loop real

**Question:** How does feedback produce goal-directed behavior, and what changes when a controller is learned?

**Do:** Start with a small joint-position feedback example: show a target, a measured position, a controller output, and the next measurement. Explain where an RL policy and training reward would fit. Map those roles to one MicroDuck control step. Use `lab doctor` for the environment check; inspect saved training artifacts when distinguishing training from inference. A short training smoke run is optional infrastructure practice, not the conceptual introduction.

**Teach:** Goal vs observation vs action; feedback and dynamics; fixed controller vs learned policy; state/action/reward; training vs inference. Explain environment isolation and CPU/GPU roles as needed for execution. A green smoke test establishes execution, not a walking skill.

**Evidence:** An annotated feedback-loop example, observed motion or a simple trace, and a distinction between a controller acting and a learner updating it. Briefly map the same loop to a robot arm or wheeled robot. Record environment checks separately; if tooling is blocked, continue the conceptual example while diagnosing execution.

### Module 01 — Read a robot model and reason about physics

**Read:** `robot/microduck_constants.py`, `robot/microduck/scene_walk.xml`, `robot_walk.xml`, and `robot_groundcontact_rollers.xml`.

**Do:** First use a pendulum or simple articulated model to connect coordinates, joint constraints, actuation, mass, and contact to motion. Write a reusable model-inspection script, then apply it to MicroDuck with `mujoco.MjModel.from_xml_path`. Generate names, indices, axes, ranges, mass, `nq`, `nv`, and `nu` as a lookup artifact. Place the model in a documented keyframe; step headlessly; plot height, tilt, and contacts. Use a contact-model comparison only to explain a concrete physics question. Open an interactive viewer only after checking that graphics work on this machine.

**Teach:** Generalized position/velocity, free joints, quaternion coordinates, units, mass/inertia, collision geometry vs visual mesh, gravity/contact. `nq`, `nv`, physical joint count, and action count need not be equal.

**Evidence:** A reusable inspection script, an annotated model diagram, and a fall or settle plot interpreted using gravity, constraints, and contact support. Demonstrate the effect of removing a contact geom. Explain how to inspect these same properties on an unfamiliar robot; its exact counts and names can be looked up.

### Module 02 — Frames, kinematics, and motion sensitivity

**Read:** Runtime `kinematics/src/math.rs`, `head.rs`, `mjcf.rs`; RL robot joint definitions.

**Do:** Implement rotations and homogeneous transforms for a two-link planar chain, then compose a small MicroDuck head or leg chain. Compare a site's predicted world position against MuJoCo across five joint configurations. Estimate a Jacobian with finite differences and use a damped least-squares step to move a site toward a reachable target in simulation.

**Teach:** Local/world/body/sensor frames, radians, active/passive rotations, transform composition, joint axes, forward/inverse kinematics, Jacobian, singularity, redundancy. Check quaternion conventions at every API boundary instead of assuming one order everywhere.

**Evidence:** Numerical FK errors, Jacobian finite-difference checks, and a reachable/unreachable target demonstration. Show how a joint axis determines a site's world motion. If frame conventions are confusing, isolate a single rotation before returning to the full chain.

### Module 03 — A neural policy still needs actuators and feedback

**Read:** `actuator/friction_dr_bam.py`, `_BAM_ACTUATOR_KWARGS` in robot constants, `tests/test_infer_policy_bam.py`, and `scripts/validate_bam_testbench.py`.

**Do:** First create a simulated single-joint or pendulum PD step response. Vary proportional gain, damping, inertia, saturation, and delay one at a time. Then inspect the provided BAM/CPU test fixture and compare a small target trajectory under the actual BAM interface with a simple PD example. Keep learning experiments in their own scripts.

**Teach:** Position/velocity feedback, overshoot, settling, torque, voltage, back-EMF, friction, actuator limits, discrete-time sampling, delay. BAM is more than an ideal torque source. A position-like policy target is not a directly commanded physical torque.

**Evidence:** A response plot with units and a measured tradeoff. Explain the causal chain from raw action to movement and why more stiffness or a larger action scale can worsen behavior. If the learner describes only reward tuning, return to this mechanical experiment.

### Module 04 — Observe the robot, not the simulator's answer

**Read:** RL observation config and NaN tests; runtime `duck-control/src/obs.rs`, `imu.rs`, `model.rs`, and `odometry/src/lib.rs`.

**Do:** Begin with a small observation vector containing measured joint position/velocity and a desired goal. Explain each field's meaning, units, frame, and source, and why observation is not complete state. Apply the same schema method to selected MicroDuck signals needed for the experiment; generate the full layout as a reference when validating the complete interface. Derive the action-to-actuator mapping from names and test it with synthetic inputs. Perturb orientation, encoder bias, noise, or delay one at a time. Integrate a biased angular-rate signal to show drift; compare a simple complementary attitude estimate with ground truth.

**Teach:** State vs observation, partial observability, privileged critic information, IMU gravity projection, filtering vs latency, normalization, contact-aided odometry, calibration vs random noise. Do not treat raw accelerometer readings during motion as an exact gravity direction.

**Evidence:** An observation schema and a drift/noise plot. Demonstrate a swapped-channel error and explain why calibration bias is not removed simply by training on symmetric random noise. Summarize how to design and validate observations for another control task without copying this robot's slot layout.

### Module 05 — Build a small RL learner before training the biped

**Do:** Write a tiny finite-state grid or balance abstraction using NumPy, with explicit transitions, actions, rewards, termination, and time limits. Compute discounted returns by hand for a short trajectory. Implement Bellman backups/value iteration for a known model, then tabular Q-learning from experience. Compare to a random policy across seeds.

**Teach:** MDP, policy, trajectory, return, discount, state/action value, Bellman equation, exploration/exploitation, bootstrapping, model-based vs model-free, on-policy vs off-policy. Q-learning is a teaching contrast, not the algorithm used by MicroDuck's PPO.

**Evidence:** A policy/value table and learning curve with a baseline. Explain why an environment is not a supervised dataset and why immediate reward alone can favor the wrong action. Distinguish terminal transitions from a collector's arbitrary time cutoff.

### Module 06 — Learn a policy with gradients

**Do:** Build a small PyTorch network and verify one gradient with finite differences. Implement REINFORCE on the tiny task, first without a baseline and then with one. For continuous actions, build a diagonal Gaussian policy, sample actions, and inspect log probabilities and entropy without driving the full robot.

**Teach:** Tensor shape/batching, autograd, optimizer steps, expectation, log-likelihood, stochastic vs deterministic actions, policy gradient, variance reduction. Sum per-dimension log probabilities for a joint action. Keep sampled old log probabilities detached when later comparing policies.

**Evidence:** A small functioning learner, a gradient check, and a multi-seed comparison. Explain why a critic is not simply a second action network. If losses change but behavior does not, inspect gradients, signs, and action/log-probability correspondence.

### Module 07 — Understand PPO as an executable algorithm

**Read:** Walking runner config plus installed `rsl_rl` PPO, rollout storage, and actor/critic model code. Use the primary references linked below for supplementary explanation, not as an API replacement.

**Do:** Compute TD residuals and GAE on a four-step trajectory in a small script; include termination and truncation cases. Calculate PPO's objective for positive and negative advantages with probability ratios inside/outside the clip interval. Implement a small PPO update or instrument the installed one on a toy task. Trace one real rollout tensor through storage, advantage estimation, mini-batches, optimization, and reset handling.

**Teach:** `delta_t = r_t + gamma * V(next_t) - V(t)` with correct bootstrap masks; GAE's discounted residual sum; value targets; advantage normalization; policy ratio; clipped surrogate; entropy; KL; gradient clipping; epochs and mini-batches. Truncation may bootstrap from the actual final observation, but GAE must not continue into a reset episode. Follow the installed wrapper's timeout treatment.

**Evidence:** Independently reproduce a small advantage calculation and PPO loss, explain both clipping-sign cases, and identify actor/critic inputs. Clipping the objective does not impose a hard bound on every policy change. Explain why reusing stale experience indefinitely is inconsistent with this on-policy training loop. [PPO paper](https://arxiv.org/abs/1707.06347), [GAE paper](https://arxiv.org/abs/1506.02438), [PPO explanation](https://spinningup.openai.com/en/latest/algorithms/ppo.html).

### Module 08 — Translate a control problem into an RL environment

**Read:** `tasks/__init__.py`, `tasks/microduck_velocity_env_cfg.py`, relevant functions in `tasks/mdp.py`.

**Do:** Load the registered walking configuration and inventory scene, action, observation, reward, event, command, termination, and curriculum terms. Step a small batch with controlled actions through the installed environment API. Record reset masks, term rewards, and actor/critic shapes. Draw the reset and step lifecycle; inspect manager-owned configuration rather than assuming the original config remains authoritative.

**Teach:** Vectorized environments, batch vs time axes, control decimation, resets, domain randomization timing, command sampling, reward rates vs per-step quantities, manager copies. Inspect whether reward weights are multiplied by timestep in the framework.

**Evidence:** One annotated step/reset trace and the general accounting rule: transitions = environment count × rollout length × iterations. Use a short smoke-run configuration as a worked calculation, looking up its values. Explain why total parallel experience differs from elapsed steps in an individual environment and why smoke completion cannot certify walking.

### Module 09 — Reproduce a baseline and measure behavior

**Do:** Keep an unchanged walking baseline. First run 64 environments/5 iterations; then choose a modest pilot budget based on measured throughput and free GPU memory. Record the full config and exact checkpoint. Build an evaluation harness with a fixed matrix of commands, starting states, and seeds. Evaluate the same checkpoint deterministically where appropriate; separate training exploration from deployment behavior.

**Teach:** Seeds, repeatability limits, checkpoint selection, training vs evaluation distributions, throughput vs learning efficiency, evaluation leakage, deterministic inference. Never compare rewards from differently scaled reward definitions as if they were identical performance metrics.

**Evidence:** Baseline report with fall rate, command tracking error, episode outcomes, finite-state checks, smoothness proxy, and videos if graphics are available. State what the robot actually does. If it mostly falls, preserve that result and diagnose; do not relabel the smoke checkpoint a trained gait.

### Module 10 — Reward design as a testable specification

**Read:** `AGENTS.md` reward lessons; walking rewards; `tests/test_ground_pick_pose.py`, reward/NaN tests relevant to the selected term.

**Do:** Select one reward or penalty. Evaluate it on synthetic success, failure, and degenerate states before training. Inspect both its raw sign and configured weight. Deliberately construct a failure case such as standing still, flopping, rushing toward a target, or jittering for reward. Compare baseline and one changed reward with equal experience, matched seeds, and the same behavior-based evaluation.

**Teach:** Sparse/dense rewards, shaping, sign conventions, reward scale, reward exploitation, potential-based shaping, regularizers, additive vs multiplicative goals. In discounted settings, policy-invariant potential shaping uses `gamma * Phi(next) - Phi(current)` under its assumptions; an arbitrary progress bonus is not automatically invariant.

**Evidence:** Reward-state table, pre-run hypothesis, and a counterexample the learner discovered. Logged weighted penalty terms should have the intended sign. A higher return with worse movement is a failure of the specification, not proof of better robotics.

### Module 11 — Create a task and stage its difficulty

**Read:** `tasks/microduck_sitstand_env_cfg.py` or `microduck_standup_env_cfg.py`, then the most relevant config tests.

**Do:** Define the goal, observations, actions, resets, rewards, and success criteria for a gentle body-height or pose transition. Implement it using the closest existing factory and preserve the selected policy's interface, consulting its schema. First verify the target equilibrium from perturbed starts, checking tilt and contacts as well as height. Add task/config tests, register a distinct task and experiment name, smoke-test, then introduce a curriculum for one difficulty dimension.

**Teach:** Goal definition, task reset distribution, curriculum, reverse curriculum, commanded transitions, phase/flag semantics, rates vs instantaneous target jumps. Coordinate curriculum transitions with learned behavior rather than elapsed training alone.

**Evidence:** Written success criteria before training, equilibrium evidence, passing tests, and per-start-state results. Diagnose a metric drop at a curriculum boundary. If a new task has no stable target, return to physics before allocating a long run.

### Module 12 — Domain randomization and the transfer gap

**Read:** `tasks/backlash.py`, friction/encoder implementation, `tests/test_infer_policy_bam.py`, and matching base/Backlash task registrations.

**Do:** Hold a policy fixed and sweep one of voltage, friction, mass/CoM, observation bias, delay, or backlash. Create a robustness curve before changing training. Then compare a randomized and non-randomized training recipe on nominal, held-out, and stress conditions. Verify sampled distributions and that repeated resets do not accumulate modifications.

**Teach:** System identification, model uncertainty, disturbance/noise/delay distinctions, randomization ranges, robust performance vs nominal performance. Use matched collision models for a backlash comparison. Rewards and observations referring to the same encoder quantity must use compatible sensor views.

**Evidence:** Robustness curves, explicit train/test parameter ranges, and a table of failure modes. Explain which physical measurements would most improve the model. A broad randomization range is not evidence of real-world safety or calibration correctness.

### Module 13 — Conduct a fair RL experiment

**Do:** Pre-register one question, such as entropy weight, learning rate, advantage handling, or delayed smoothness curriculum. Change one factor. Compare at equal environment transitions; optionally also report equal wall-clock cost. Run a cheap pilot, then use at least three training seeds for the capstone comparison when compute allows, plus a fixed independent evaluation seed set. With fewer seeds, label results exploratory.

**Teach:** KL drift, value error/explained variance, entropy, gradient norms, numerical instability, data correlation, sample complexity, confounding, early stopping, uncertainty. Episode resets and curriculum phases can create apparent improvements unrelated to a better policy.

**Evidence:** Experiment table with budgets, baseline, seeds, metrics, and selection rule; plots with variability; one conclusion the data do not support. Explain why three runs are still a small sample. Do not cherry-pick only the best seed or treat episodes from one seed as independent training replications.

### Module 14 — Export and verify the inference contract

**Read:** `src/mjlab_microduck/export.py`, `scripts/export.py`, `scripts/infer_policy.py`, runtime `duck-control/src/obs.rs`, `policy.rs`, `docs/policy-manifest.md`.

**Do:** Export an explicitly selected local checkpoint using the repository exporter. Inspect ONNX input/output metadata and run plausible observations through it. Compare PyTorch actor output and ONNX output on the same raw observations with normalization applied exactly once. Choose and record a numerical tolerance. Rehearse the exported policy in CPU MuJoCo with BAM; compare observations/actions across the two simulation paths.

**Teach:** Serialization vs export, train/eval modes, normalization, input/output semantics, action scale/reference pose/order, interface metadata, episode lifecycle, and command encoding. Use the selected MicroDuck schema and command modes as examples of choices that must match across training and runtime, not universal conventions. Publishing is a separate activity from local export.

**Evidence:** Checkpoint/hash/config provenance, ONNX parity measurements, and CPU rehearsal outcomes. Debug an intentional observation-order or normalizer mistake in an isolated test. A graph that runs and has the right dimensions can still command the wrong physical joints. Recurrent policies are an optional extension with hidden-state/reset contracts, not a drop-in replacement.

### Module 15 — Run the real control software against a simulated body

**Setup gate:** this module needs the Rust toolchain and a build of the `microduck` runtime checkout, which the course setup does not install. Follow `docs/ENVIRONMENT.md` (section "Module 15") with the learner, and ask before installing anything. Until that works, label this module pending; do not claim it from the RL environment setup.

**Read:** Runtime `CONTRIBUTING.md`, `docs/robot/simulation.md`, `scripts/duck-sim`, `duck-control/src/sim.rs`, `safety.rs`, `robotd/src/control.rs`; RL `sim/body_server.py`.

**Do:** Start with focused kinematics/observation tests. Build the process-based simulator with `DUCK_SIM_RL` pointing to the `microduck_rl` checkout. Use a compatible baseline policy set. Inspect `status`, `ctl health`, `monitor`, and real-time factor. Request a short simulated velocity command, return to idle, then end only this session with `down`. In a controlled simulated session, observe how the system responds to a missing body connection or slow simulation.

**Teach:** Policy/controller/actuator boundaries, JSON-RPC, Unix sockets, daemon lifecycle, watchdogs, command arbitration, real-time deadlines, simulation vs wall-clock time, inference latency. `--fake` can test IPC but is not a dynamics simulation; `--sim` connects the real control logic to MuJoCo.

**Evidence:** A sequence trace from user intent to simulated motion, measured real-time performance, and a documented fault response. Explain what is absent: physical motor bus, radio, camera ISP, NPU, and hardware encoders. Containerized multi-duck/systemd simulation is optional later work, not a prerequisite for learning PPO.

### Module 16 — Extend from locomotion to embodied robotics

**Read:** Runtime `kinematics/src/tof.rs`, `odometry/src/lib.rs`; RL `sim/camera.py`, `sim/tof.py`; runtime simulation and camera documentation.

**Do:** Compare ground-truth motion with contact/IMU odometry during straight walking, turning, and slipping. Add a simulated ToF stream and relate its rays to body/head/world frames. Build a simple high-level stop/turn rule for a simulated obstacle while retaining the learned low-level gait. Compare behavior with and without sensor delay.

**Teach:** Local state estimation, drift, sensing geometry, observability, perception/control timescales, behavior state machines and hierarchical control. Introduce SLAM, model-predictive control, imitation learning, and hierarchical RL as follow-on directions; do not pretend this single course covers every robotics specialty.

**Evidence:** Odometry-error plot and an explanation of one slip failure. Learner traces where an obstacle decision belongs and why an external command client should not bypass the runtime's motor/safety ownership.

### Module 17 — Capstone: improve one behavior and defend the result

Choose one: smoother low-speed walking, a controlled body-height transition, better head-command tracking while walking, or robustness to a measured delay/friction range. Start with an existing task; avoid a dramatic trick until gentle control is understood.

Required deliverables:

1. A one-page task definition, prior baseline, hypothesis, failure criteria, and compute budget.
2. A named branch and reproducible change with tests of the affected invariants.
3. Matched baseline/variant training records and a separate evaluation suite spanning relevant starts/commands/disturbances.
4. Behavior plots and representative success AND failure rollouts, with seed count and uncertainty stated.
5. A selected checkpoint, normalized ONNX export, and parity/contract checks.
6. CPU MuJoCo rehearsal and, once Module 15 is ready, runtime simulation results.
7. A short technical report explaining results, limitations, the next experiment, and how the method would apply to another robot or task, including assumptions that would need revalidation.

Completion evidence includes a reproducible central result, the learner's reasoning about why the intervention was expected to help, and honestly documented limitations. Improvement is desirable, but a well-supported negative result is acceptable. Gather reasoning through normal collaboration, not a required oral examination. If runtime setup is blocked, label the capstone's daemon-rehearsal requirement pending rather than silently omitting it.

## Experiment and compute discipline

Before every GPU training experiment, write: question, baseline, change, predicted effect, budget, measured success/failure, checkpoint selection rule, and stop conditions. Keep accounts offline by default. Learning-plan creation does not authorize future long runs, paid Hugging Face jobs, uploading policies, or physical robot movement.

Use three scales:

- **Wiring:** 64 environments, 5 iterations after a task/config change. This is the repository's required smoke gate.
- **Pilot:** a short, explicitly bounded run chosen after checking GPU memory and throughput. Around 128–512 environments and 50–200 iterations can be an initial experiment design, not a proven capacity guarantee or a promised successful gait.
- **Evidence:** longer runs only after pilots are interpretable and the learner has agreed the local compute/time budget. The repository's 4,096-environment examples are not a requirement for the first lesson.

At the verified 24 rollout steps/environment, transitions = environments × 24 × iterations. Increasing environment count changes the optimization batch and experience distribution; it is not purely a speed setting. Recheck current runner configuration. At `gamma=0.99` and 50 Hz, `1/(1-gamma)` is about 100 steps or 2 s as a rough discount scale, not a hard episode horizon. Curriculum counters may count per-environment steps rather than all parallel transitions.

Stop a learning run on persistent NaNs, invalid observations, an unintended configuration, a clearly wrong reward sign, or its pre-agreed budget. Preserve logs before fixing the cause. Do not kill unrelated training processes. Ensure another workload has enough GPU memory before starting.

For evaluation, define metrics operationally. Examples: command tracking RMSE with units over a specified interval; fraction of episodes with a fall condition; fraction reaching and maintaining a pose for a stated dwell time; action-difference RMS as a smoothness proxy; actual torque/velocity-derived work only if the signals are available and correctly interpreted. Do not call action magnitude “energy.” Use the same evaluation code/config for baseline and variant, with a held-out final test set after tuning.

## Optional physical-robot branch

The entire core path can be learned in simulation. If the learner owns a robot, first identify its exact hardware revision, policy compatibility, calibration state, and official operating/stop procedure. Physical execution is a distinct supervised activity requiring the learner's explicit decision and presence.

Begin with read-only status and model/calibration comparison. Progress to approved bounded movements only after simulation gates and a baseline recovery/stop plan are in place. Compare timestamps, joint signs/offsets, voltage, IMU orientation, command encoding, and action scaling before interpreting a failure as an RL problem. Keep the real robot's protection mechanisms active. Do not perform random exploration or untested policies on hardware as a lesson shortcut. Record hardware measurements as data for system identification, not as proof that simulation safety transfers automatically.

## Appendix — MicroDuck implementation reference

These are recorded project details for lab correctness, not introductory material or memorization targets. Consult only the entries relevant to the current experiment and recheck them against the selected task and checkout. The reusable principles are interface validation, timing analysis, model inspection, and preserving training/runtime behavior.

- Standard feed-forward policies have 61 actor observations and 14 actions. The physical/runtime model has 15 joints: its mouth joint is excluded from these policy actions. Inspect the name mapping; never treat the physical servo count as the action dimension.
- The 61 values are 48 proprioceptive values plus a 13-value command block: twist 3, head pose 4, body pose 6. Verify units, coordinate frame, ordering, scaling, and normalization as part of the interface.
- The smoke-tested walking task had 61 actor and 76 critic values; the latter is task-specific. Privileged critic information must not silently leak into deployed actor inputs.
- The verified walking setup steps physics at 0.005 s and control at 0.02 s: 200 Hz physics, 50 Hz policy, four physics steps per action. Recheck another task's config.
- Passive joints use the `passive_` prefix. Roller/backlash models can interleave them. Use the repository's servo-resolution helpers, not array positions copied from the plain model.
- BAM models XL330 actuator behavior; its friction randomization uses actuator state. Randomizing a zeroed MuJoCo friction field can be ineffective.
- Observation normalization is enabled. Use the repository exporter, which bakes it into ONNX. Simulator playback can conceal a missing normalizer.
- Training policies are unfiltered. Introducing action filtering changes the closed loop and needs matched training/runtime evaluation.
- For Module 14, inspect schema-2 policy metadata and the selected command encoding. `phase`, `posture_flag`, and constant command modes are not interchangeable.
- Preserve restore-then-randomize semantics, correct reward signs, NaN guards, and base/Backlash model parity described in `AGENTS.md`.

## Reading strategy and references

Repository code, tests, and the checked-out docs are the primary authority for exact interfaces. External readings explain theory; current online APIs may differ from the locked installation. Read only what helps the current lab.

- Simulator concepts and modeling vocabulary: [MuJoCo overview](https://mujoco.readthedocs.io/en/stable/overview.html). Use alongside Modules 01–04; validate behavior against MuJoCo 3.10.0 installed locally.
- PPO's motivation and update construction: [Schulman et al., PPO](https://arxiv.org/abs/1707.06347), Module 07.
- Advantage estimation and variance/bias: [Schulman et al., GAE](https://arxiv.org/abs/1506.02438), Module 07.
- A worked PPO explanation: [Spinning Up PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html), Module 07. Its implementation and hyperparameters are not the project's installed `rsl_rl` implementation.
- Practical project-specific physics, reward, curriculum, and transfer lessons: `AGENTS.md` in the `microduck_rl` checkout.
- Runtime architecture/operation: in the `microduck` checkout: `CONTRIBUTING.md`, `docs/design/architecture.md`, `docs/robot/simulation.md`, and `docs/policy-manifest.md`. Older design prose can describe planned behavior; inspect current implementation and tests before treating it as established.

Teaching sessions start from `AGENTS.md` at the repository root and `LearningProgress/STATE.md`. The learner-facing guide is `START_HERE.md`.
