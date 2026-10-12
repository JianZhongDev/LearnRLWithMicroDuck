# Bonus course: build a physical robot from first principles

Status: proposed curriculum for an optional companion track. It has not been taught or tested with hardware yet; treat it as a plan to adapt.

## Purpose and practical outcome

A robot needs a structure that carries loads, a power system that supplies its actuators and computer, sensors that report what happened, and software that turns goals into controlled motion. Building one means making these parts work together and finding the cause when they do not.

This optional course teaches that complete process to someone without an electronics, mechanical engineering, embedded systems, or robotics background. Use MicroDuck as a concrete engineering example, while teaching methods that also apply to an arm, wheeled robot, camera mount, or other small mechanism. Understanding how to select, connect, measure, and debug components matters more than remembering MicroDuck's part numbers.

The first physical outcome should be a small, supported one-joint mechanism. The next is an integrated robot with sensing, feedback control, startup, shutdown, and a documented recovery procedure. A wheeled robot or a small fixed-base mechanism is a suitable first independent build. A faithful MicroDuck replica or a new balancing biped is a later extension requiring additional mechanical and electrical documentation and more integration work.

“From scratch” means deriving a design from requirements and assembling and integrating documented components. It does not require designing a processor, battery cells, motor, operating system kernel, or every circuit board. Custom circuit boards and firmware are optional extensions after a working modular prototype.

The final build dossier should allow another person to reproduce the robot: requirements, drawings, parts list, wiring, software versions, configuration, calibration, measurements, operation, known limits, and recovery instructions.

## How this fits the existing course

- This is a companion to [the main learning plan](LEARNING_PLAN.md), not a replacement. The main course position is recorded in `LearningProgress/STATE.md`.
- The learner currently has no physical MicroDuck. Start with source inspection, small models, and design exercises; mark physical measurements as pending until hardware is available.
- Modules 00–04 already supply feedback, physics, kinematics, actuators, and sensing foundations. Reuse their demonstrations where helpful, briefly reintroducing their meaning rather than assuming mastery.
- Main Modules 14–16 cover policy export, runtime simulation, and perception. Coordinate with them to avoid repeating setup or confusing a planned exercise with completed work.
- The deferred motor-bus/system-diagram topic in `LearningProgress/15-runtime-simulation-and-system-architecture/TODO.md` fits bonus units B04 and B07. It can remain deferred until the learner chooses this track.
- Reinforcement learning is optional for a first working physical robot. Establish ordinary feedback control and reliable interfaces before introducing a learned controller.

## What the repositories actually provide

Written against the source commits pinned in `tools/pins.env`. Recheck these before teaching revision-dependent details.

Paths in the source table use these roots:

- **Runtime:** the `microduck` checkout (`runtime_repo` in `.course/env.json`)
- **Training:** the `microduck_rl` checkout (`rl_repo` in `.course/env.json`)

These are source-navigation labels. Inspect only the files needed to answer the lesson's engineering question.

| Engineering question | Useful checked-in sources | What they support and what remains to obtain |
|---|---|---|
| How is the system divided? | Runtime `README.md`, `docs/design/architecture.md`, `docs/design/robotd-design.md`, `Cargo.toml` | Physical/software roles, device ownership, service boundaries, control flow. Older design prose must be checked against implementation. |
| What moves and where are the sensors? | Training `src/mjlab_microduck/robot/microduck/robot_walk.xml`, `robot_groundcontact.xml`, `joints_properties.xml`, `sensors.xml`, `assets/`; runtime `kinematics/src/` | Model geometry, frames, mass/inertia, joints, limits, sensor sites. A simulation mesh is not a manufacturing drawing or assembly tolerance specification. |
| Where did the model come from? | Training `src/mjlab_microduck/robot/microduck/config_mjcf_*.json` | Computer-aided design (CAD) export configuration, including an Onshape document reference. External access, revision, licenses, and availability of manufacturable parts still need checking. |
| How are motors and inertial sensing connected logically? | Runtime `duck-control/src/model.rs`, `bus.rs`, `imu.rs`, `io.rs`; `docs/design/robotd-design.md` | Device identities, register transactions, units, bus ownership, sample handling. These do not establish connector pinout, voltage compatibility, or the complete electrical circuit. |
| How are peripherals made visible to Linux? | Runtime `scripts/setup-board.sh`, `deploy/audio/`, `deploy/overlays/`, `tof/src/` | Device-tree configuration, drivers, device naming, sensor access, and board integration examples. Exact board revision and manufacturer electrical documentation are still required. |
| How does the board boot and run the robot? | Runtime `docs/robot/install-dev.md`, `deploy/README.md`, `deploy/robotd.toml`, `robotd/systemd/robotd.service` | Provisioning, persistent configuration, services, permissions, logs. Image versions and board procedures are revision-specific, not universal install instructions. |
| How does a target become motion? | Runtime `robotd/src/control.rs`, `main.rs`, `intents.rs`; `duck-control/src/obs.rs`, `policy.rs`, `safety.rs`, `fall.rs` | Observation/action conversion, scheduling, control ownership, limits, and fault behavior. Software safeguards do not prove mechanical or electrical protection. |
| How can the same software run without hardware? | Runtime `docs/robot/simulation.md`, `scripts/duck-sim`, `duck-control/src/sim.rs`; training `src/mjlab_microduck/sim/` | A simulated body behind the real control interface. Physical wiring, radio, motor electronics, and hardware timing remain outside that validation. |
| How does an actuator model differ from a real motor? | Training `src/mjlab_microduck/robot/microduck_constants.py`, `actuator/friction_dr_bam.py`, `scripts/validate_bam_testbench.py`, `tests/test_infer_policy_bam.py` | Fitted actuator behavior, uncertainty, and comparison methods. Model parameters and randomized voltages are not electrical ratings or a wiring prescription. |
| How is the robot maintained? | Runtime `docs/design/updater-design.md`, `restart-order.md`, `boot-recovery-net.md`, `updater/`, `hooks/`, `deploy/` | Versioned installation, verification, health checks, rollback, and recovery. Tests and dated reports must be separated from validation on the learner's board. |

The inspected checkouts contain substantial electronics integration information. This review did **not** locate a complete board schematic and layout, verified wiring harness drawing, complete bill of materials, battery/charger design, full assembly guide, or the full source of the motor and inertial-board firmware. Their absence from this review is not proof that they do not exist elsewhere. Obtain the matching official hardware sources when a build requires them; keep each unresolved item explicit.

The runtime uses Linux and its own Rust services. Do not equate “robot operating system” with the separate Robot Operating System (ROS) middleware project. Teach the operating system, drivers, application services, and middleware as distinct layers; a ROS comparison can be a later optional topic.

## Teaching guide

Follow [TEACHING_RULES.md](TEACHING_RULES.md) and `docs/ENVIRONMENT.md`; the current position is in `LearningProgress/STATE.md`. Treat this document as a plan, not evidence that the learner has completed anything.

### Start from a beginner's physical picture

Introduce every unfamiliar tool and term by explaining what it does and why it is needed. Advanced programming experience does not imply knowledge of current, torque, connector polarity, grounding, motor drivers, sampling, or boot configuration. Offer a short shell/programming bridge for a learner who also lacks those skills; the current learner can usually skip that bridge.

For each new unit, give a concise overview of its planned lessons and practical outcome. For each teaching response, cover one coherent question:

1. Describe what the mechanism should physically do, what supplies its energy, and what is being measured.
2. Introduce the minimum concepts and a small labeled diagram. Distinguish power wires, signal wires, mechanical connections, and software messages.
3. Work through a simple generic example before a focused MicroDuck source trace.
4. Run one bounded demonstration or give exact, equipment-specific rerun steps. State initial conditions, changed factor, duration, expected observation, and stop conditions.
5. Interpret the evidence and one failure case. Distinguish a calculation, a simulation result, a sensor measurement, and a hypothesis.
6. State what transfers to another robot and what must be looked up or measured again.
7. Record the actual result, artifact paths, unresolved questions, and next action.

Spell out abbreviations on first use in each lesson. Define equation variables and units, including coordinate frames when relevant. Introduce axes and measurement methods before plots. Avoid recurring quizzes, mandatory predictions, visible scores, and file-by-file tours. Use guided work and the learner's naturally offered explanations as evidence.

### Maintain a growing engineering dossier

Each unit adds a concrete artifact to one design: a requirement, drawing, calculation, interface definition, prototype, measurement, or procedure. Use a small generic one-joint mechanism until a build is chosen. MicroDuck supplies examples of engineering decisions, not a parts list to copy blindly.

Tag statements in the dossier as **source-inspected**, **calculated**, **simulated**, **physically measured**, or **unverified**. A useful visual marks these distinctions directly. Every selected component needs a revision and a source for its relevant specifications; unknown compatibility stays unknown.

Before a hardware session, establish the actual equipment, part revisions, wiring, learner experience, available supervision, and intended motion. This planning request does not start purchases, board provisioning, or physical movement. Once a specific session is agreed, proceed through its bounded steps without repeatedly asking for the same permission.

### Connect construction to measurement

Teach tools just before their first use: what a multimeter measures, how its connection changes between voltage and current measurements, what a current-limited supply does, how a logic analyzer observes digital timing, and how mechanical supports constrain motion. Use equipment manuals and a supervised demonstration for unfamiliar bench procedures. Never turn a software-derived pin guess into wiring instructions.

The default first build uses documented low-voltage modules and a compatible commercial power source. Battery cell construction, mains wiring, and custom charging circuits are outside the core beginner build. Teach energy isolation and mechanical support early: releasing torque on an unsupported mechanism can cause it to fall, while a software “stop” may continue holding torque. Establish the intended response for the actual mechanism.

## Course sequence

Plan for **14 units and approximately 40 substantive lessons**. The counts below are pacing estimates. Hardware availability, fabrication, and learner questions can change them. Do not compress an entire unit into one response. B00–B04 prepare a design; B05–B09 integrate computation and control; B10–B13 build, measure, and document the result.

### B00 — Define the robot before selecting parts · 2 lessons

**Question:** What should the robot accomplish, and how will we know it succeeds?

- Lesson 1: Explain the links between task, environment, movement, sensing, energy, and control. Draw one complete action-and-feedback cycle.
- Lesson 2: Turn a small use case into measurable requirements: payload, travel, speed, runtime, footprint, acceptable error, operating surface, and budget. Separate essential behavior from optional features.

**MicroDuck connection:** Read the runtime overview and architecture. Trace one request from an operator to joint movement and back to reported state. Identify which components exist to keep the robot recoverable.

**Practice and evidence:** Produce a one-page design brief, a labeled system diagram, a verification table, and an initial list of unknowns. Choose a provisional small mechanism; no purchase is needed. Success means requirements can be checked, not that the design is already feasible.

### B01 — Mechanical structure, loads, and assembly · 3 lessons

**Question:** Can the structure support the intended motion and load?

- Lesson 1: Introduce links, joints, bearings, supports, degrees of freedom, gravity, torque, and center of mass with a supported arm or hinge.
- Lesson 2: Estimate static load and rotational demand; explain why acceleration, impacts, friction, and leverage change actuator requirements. Separate holding a pose from maintaining balance.
- Lesson 3: Introduce CAD, dimensions, fits, fasteners, alignment, cable routing, strain relief, and access for assembly and repair. Explain how manufacturing variation changes a nominal drawing.

**MicroDuck connection:** Inspect a leg or head chain in the training model and runtime kinematics. Reuse the main course's falling/standing example to distinguish a visual model, collision model, and physical equilibrium.

**Practice and evidence:** A dimensioned sketch or simple CAD part, joint-axis diagram, load estimate with stated assumptions, assembly order, and cable-clearance check. Without hardware, inspect motion envelopes virtually; with hardware, perform an unpowered fit and range inspection. Model geometry alone does not certify strength or manufacturability.

### B02 — Electricity, power distribution, and bench tools · 3 lessons

**Question:** How does energy reach every component without causing resets or damage?

- Lesson 1: Introduce voltage, current, resistance, power, electrical reference, and a closed circuit using a small resistive example. Explain measurement placement before using an instrument.
- Lesson 2: Build separate logic and actuator power budgets. Distinguish average consumption, short peaks, startup demand, heating, and supply regulation.
- Lesson 3: Plan distribution, protection, connectors, conductor ratings, polarity labels, accessible disconnection, and a compatible battery/charger option from manufacturer documentation.

**MicroDuck connection:** Trace voltage and temperature reporting in `duck-control/src/bus.rs` and `model.rs`. Contrast these measurements with the training actuator's simulated supply variation. Locate what the source does not say about the actual power circuit.

**Practice and evidence:** A labeled power-tree diagram and budget table with every value marked estimated or sourced. When equipment is available, measure the supply at a small documented load before involving a motor. Record where voltage was measured and what changed under load. Firmware voltage thresholds are not substitutes for component ratings or pack protection.

### B03 — Actuators, transmissions, and motor electronics · 3 lessons

**Question:** What must exist between a desired position and physical motion?

- Lesson 1: Compare motor, gearbox, encoder, driver, and controller roles. Contrast a smart servo that contains these functions with a bare motor that needs external electronics.
- Lesson 2: Explain torque versus speed, gearing, efficiency, backlash, thermal limits, and duty cycle. Size an actuator from the B01 load case using current manufacturer data; do not treat stall capability as a continuous operating point.
- Lesson 3: Follow one target through feedback, electrical drive, torque, and movement. Study saturation and delay with a bounded one-joint example.

**MicroDuck connection:** Trace the Dynamixel model and Better Actuator Models (BAM) configuration. Reuse the main Module 03 voltage/friction demonstrations. Distinguish the fitted average electrical model from undocumented internal firmware details.

**Practice and evidence:** An actuator comparison with explicit tradeoffs, an interface diagram, and a predicted response to a small target. Later compare prediction with a supported bench measurement. A good unloaded response is not evidence of adequate loaded performance.

### B04 — Wiring and communication buses · 3 lessons

**Question:** How does the computer address the intended device and receive an intelligible reply?

- Lesson 1: Separate connector shape, pin assignment, voltage levels, electrical signaling, and packet protocol. Introduce a universal asynchronous receiver-transmitter (UART) as a serial interface; it does not by itself specify the external bus wiring.
- Lesson 2: Explain device addresses, request/reply transactions, checksums, shared-bus ownership, turnaround, timeouts, and bandwidth. Introduce Inter-Integrated Circuit (I²C) and Serial Peripheral Interface (SPI) only when comparing a relevant peripheral.
- Lesson 3: Build a wiring and packet trace. Diagnose wrong address, incompatible settings, duplicated identity, missing response, and a second process using the port with recorded or synthetic data.

**MicroDuck connection:** `docs/design/robotd-design.md` describes the shared servo/inertial-board bus; `bus.rs` and `model.rs` implement transactions and mappings. `scripts/setup-board.sh` demonstrates how a Linux login console can conflict with the motor port. Explain any required electrical adapter from its actual schematic, never from the device filename.

**Practice and evidence:** Separate logical-bus and physical-wiring diagrams, a connector table, a device inventory, and a transaction time budget. Hardware practice begins with one documented device and torque disabled where supported; expand only after its identity and replies are verified. Unverified pins remain explicitly unconnected in the build plan.

### B05 — Embedded control and the host-computer boundary · 3 lessons

**Question:** Which decisions belong close to the motor, and which belong on the main computer?

- Lesson 1: Introduce a microcontroller, firmware, timers, interrupts, and a host process through a sampled sensor-and-actuator loop.
- Lesson 2: Allocate functions by timing, required response to faults, and available computation. Explain why the host's target update and a servo's internal feedback loop can run at different rates.
- Lesson 3: Specify a small device protocol with version, units, sequence number, freshness, and fault state. Use a mock device before an optional microcontroller implementation.

**MicroDuck connection:** Trace `RobotIo` in `duck-control/src/io.rs`, inertial packet decoding in `imu.rs`, and the simulation adapter. These expose the host's contract with firmware; they do not provide a complete implementation of the servo or inertial-board firmware.

**Practice and evidence:** A timing/ownership diagram and bounded mock-device program that exposes a stale or malformed sample. Optional hardware extension: a documented development board and sensor, with motor power absent. Keep any future custom firmware in the bonus learning directory.

### B06 — The robot's operating system and startup · 3 lessons

**Question:** How does a powered board become a computer that reliably runs the robot?

- Lesson 1: Explain bootloader, operating system kernel, driver, device file, permissions, and application process. Follow one peripheral from hardware configuration to a readable device.
- Lesson 2: Explain service management with systemd, configuration, logs, startup order, and restart behavior. Read a service file before writing a small example.
- Lesson 3: Design a reproducible board setup: image identity, versions, network access, time synchronization, persistent data, backups, and a recovery route.

**MicroDuck connection:** Inspect `docs/robot/install-dev.md`, `deploy/README.md`, `scripts/setup-board.sh`, and service files. Use device-tree overlays as examples of describing hardware to Linux. Read provisioning scripts as programs with side effects; old image names are historical evidence until reverified.

**Practice and evidence:** A boot sequence, file-location map, and installation checklist. A disposable virtual machine or suitable container can demonstrate a harmless service; neither validates board drivers. Actual provisioning requires the selected board and storage device to be identified and backed up. The existing Linux training environment does not establish a working Rust runtime.

### B07 — Software architecture and one control owner · 3 lessons

**Question:** How can several user interfaces and services cooperate without fighting over the motors?

- Lesson 1: Separate sensing, estimation, control, behavior, communications, and maintenance responsibilities. Explain a daemon as a long-running service and an interface as an agreed input/output contract.
- Lesson 2: Trace an operator intent through arbitration, control, actuator output, and telemetry. Introduce inter-process communication (IPC) with one concrete request and reply.
- Lesson 3: Explain deadlines, bounded work, queues, stale commands, and isolation of slow tasks such as media processing or downloads.

**MicroDuck connection:** Trace `robotctl` through `duck-ipc-proto`, `robotd/src/intents.rs`, `control.rs`, and `duck-control/src/safety.rs`. Explain why media, configuration, and update services have separate responsibilities. Assemble the previously deferred end-to-end system diagram here.

**Practice and evidence:** A sequence diagram and a minimal controller with a fake body. Inject a delayed client or missing sample and record the observed response. Keep one writer responsible for actuator output. A healthy process or valid message does not by itself mean the mechanism is behaving correctly.

### B08 — Sensors, calibration, and state estimation · 3 lessons

**Question:** What can the robot actually know about itself and its surroundings?

- Lesson 1: Introduce resolution, bias, noise, range, calibration, timestamps, and coordinate frames using a position sensor.
- Lesson 2: Explain an inertial measurement unit (IMU), angular rate, acceleration, gravity direction, and the limitations of integrated orientation. Reuse main Module 04 experiments as appropriate.
- Lesson 3: Add one optional range or camera sensor. Explain mounting geometry, field of view, latency, and the difference between a raw reading and an interpreted obstacle or pose.

**MicroDuck connection:** Inspect `duck-control/src/imu.rs`, `kinematics/src/head.rs`, `tof.rs`, `odometry/src/lib.rs`, the runtime `tof/` crate, and training simulation sensor adapters. Contact-aided odometry assumes a usable support reference; it does not directly observe foot slip.

**Practice and evidence:** A sensor contract containing units, frame, update timing, source, and limits; a calibration record; and one comparison with an independent reference. A stationary/noisy synthetic trace is the no-hardware alternative. Do not label a simulated calibration as a physical calibration.

### B09 — Feedback control and deliberate fault behavior · 3 lessons

**Question:** How does the robot reach a target, and what happens when the loop can no longer do so?

- Lesson 1: Implement position feedback and introduce proportional-derivative control using error and motion to choose a command.
- Lesson 2: Measure tracking, overshoot, settling, saturation, and delay. Change one factor at a time and interpret the physical response.
- Lesson 3: Define command limits, startup states, stale-data handling, watchdogs, restart behavior, and the intended stop/disconnect response for the selected mechanism.

**MicroDuck connection:** Read `control.rs`, `safety.rs`, `fall.rs`, and their call sites. Verify actual behavior: the inspected safety layer rejects nonfinite targets and clamps actuator travel; it is not a complete per-joint mechanical constraint system. A fall report does not independently guarantee torque removal, and a stale command may request standing rather than limp behavior.

**Practice and evidence:** First use a bounded simulated joint, then a supported physical mechanism when ready. Record target, measured position, time, and relevant load/current signals. Produce a fault-response table with measured outcomes. Emergency energy isolation and software behavior require separate verification.

### B10 — Assemble and bring up one subsystem at a time · 3 lessons

**Question:** How can we localize a fault instead of powering an unknown whole system?

- Lesson 1: Review the assembly drawing, part revisions, wiring, protection, cable travel, and measurement plan. Perform unpowered mechanical and wiring checks using the relevant manuals.
- Lesson 2: Bring up logic power and read-only sensing/communications, then one supported actuator with explicitly bounded travel and duration.
- Lesson 3: Add mechanical load and further joints in stages. Calibrate identity, sign, zero/reference, range, and repeatability before closing the full loop.

**MicroDuck connection:** Use model/bus mappings, startup procedures, calibration-related parameters, and `docs/project/slice-2-bringup.md` as examples of evidence-driven integration. A documented startup command may move motors or change persistent registers; inspect it before use.

**Practice and evidence:** An assembly record and bring-up log for each stage: expected result, actual measurement, fault, diagnosis, and next action. Establish equipment-specific voltage/current/temperature and motion bounds before energizing, using actual ratings. Stop on unexpected motion, heating, supply behavior, or communication loss according to the agreed procedure. A no-hardware walkthrough remains a plan, not completed bring-up.

### B11 — Compare the physical robot with its model · 3 lessons

**Question:** Which differences between prediction and measurement matter for the task?

- Lesson 1: Align joint names, units, signs, reference pose, timing, and control representation before comparing trajectories.
- Lesson 2: Replay a small bounded input in simulation and on the mechanism. Plot tracking error, delay, and repeatability; identify which parameter could explain a discrepancy.
- Lesson 3: Test one explanation at a time, then repeat the comparison under a changed load or target. Introduce system identification as estimating a model from measurements.

**MicroDuck connection:** Use `scripts/validate_bam_testbench.py`, model parameters, and `tests/test_infer_policy_bam.py` as method examples. Distinguish model fitting from domain randomization, which exposes training to a range of modeled conditions.

**Practice and evidence:** A versioned input trajectory, aligned data, before/after plot, and a conclusion with limitations. Do not infer physical torque or energy from arbitrary policy action magnitude. Learned control remains optional; adding it later requires validated observation/action semantics and exported-policy agreement.

### B12 — Reliable operation, updates, and maintenance · 3 lessons

**Question:** Can someone operate, diagnose, and recover the robot after the developer leaves?

- Lesson 1: Define useful health and telemetry: what should be observed, which faults prevent operation, and which measurements are only descriptive.
- Lesson 2: Explain versioned software/configuration, integrity verification, compatibility, health checks after installation, and rollback.
- Lesson 3: Practice diagnosis and recovery on a fake or simulated robot, then write an operator procedure covering startup, normal operation, stop, shutdown, inspection, and component replacement.

**MicroDuck connection:** Trace `updater/`, deployment configuration, restart-order documentation, and boot recovery. Inspect tests and implementation alongside design claims. Distinguish update health from electrical protection and motion quality.

**Practice and evidence:** A release/configuration manifest, saved calibration, diagnostic decision tree, and a rehearsed recovery procedure. Use an isolated simulation for intentional process failures; power-loss and update-failure experiments on physical equipment need a separately designed recovery setup.

### B13 — Build and hand over an independent robot · 2 lessons

**Question:** Can the learner apply the method to a mechanism whose design choices differ from MicroDuck?

- Lesson 1: Integrate the chosen small robot and run its predefined acceptance checks, including representative loads, repeated operation, and agreed fault responses.
- Lesson 2: Diagnose the largest remaining limitation and complete a reproducible handover. Compare the final design with the original requirements and explain the tradeoffs.

**Deliverables:** Requirements; versioned parts list with specification sources; dimensioned mechanical design; power and wiring diagrams; interface contracts; software and configuration; assembly and calibration procedures; test data; operating/recovery guide; unresolved issues and next revision.

**Completion evidence:** The physical robot performs the agreed bounded task, and its measurements and procedures support that claim. A design dossier with simulation is a useful intermediate outcome, but physical completion stays pending. A measured negative result and a justified redesign are valuable engineering work. Never infer learner understanding solely from teacher-written code or a successful run.

## Optional extensions after the first working build

- **Custom electronics:** Read a complete reference schematic; derive a small interface circuit; introduce component ratings, circuit simulation, electrical-rule checks, printed circuit board (PCB) layout, manufacturing outputs, soldering, inspection, and board bring-up. Begin with a non-power-critical interface. Obtain missing MicroDuck hardware sources before claiming to reproduce one of its boards.
- **Custom firmware:** Implement the B05 contract on a documented microcontroller. Add bounded timing, freshness checks, startup state, and fault reporting; verify it with a mock host before attaching an actuator.
- **A MicroDuck replica or a new biped:** Obtain the correct hardware revision's manufacturing, assembly, wiring, calibration, and power documents; revisit balance, contact, joint load, and fall management. An exported simulation model is insufficient as the complete build package.
- **ROS middleware:** Map the existing sensing, command, and telemetry contracts to another middleware architecture after the original interfaces are understood. Do not present the checked-in runtime as ROS-based.
- **Learned behavior:** Join main Modules 09–15 once ordinary control, measurements, and recovery are established. Verify policy compatibility and model-to-hardware differences before any physical rehearsal.

## Source and equipment policy for future lessons

Repository implementation and tests are the primary evidence for what this checkout does. For actual electrical ratings, wiring, connectors, firmware registers, board flashing, fabrication, and instrument operation, obtain current primary documentation from the manufacturer or hardware designer. Record the exact component variant and document revision.

At the relevant lesson, resolve these missing inputs:

| Needed input | Preferred authority | When needed |
|---|---|---|
| Actuator voltage, current, duty, connector, and control-table information | Exact actuator manufacturer's manual and datasheet | B02–B04 and before actuator selection or connection |
| Board pinout, signal levels, power input, and supported image | Exact board manufacturer's documentation and image maintainer | B04–B06 and before wiring or provisioning |
| Adapter/inertial-board schematic and firmware contract | Board designer's hardware and firmware sources | Before reproducing its wiring or interface |
| Battery, protection, and charger compatibility | Pack and charger manufacturers | Before selecting or connecting stored-energy power |
| Printable/machinable parts, tolerances, fasteners, and assembly instructions | Revision-matched mechanical design package | Before fabrication or assembly |
| Instrument connections and operating limits | Instrument manufacturer's manual | Before unfamiliar measurements |

Select tools and parts only after the build's requirements, existing equipment, region, and budget are known. Tool categories to introduce as needed include measuring tools, hand tools, a multimeter, a suitable current-limited supply, a documented communication adapter, and optional soldering or logic-analysis equipment. This is not a purchase list or a claim that every tool is necessary.

## Workspace, reproducibility, and progress

The MicroDuck checkouts live outside this repository and remain read-only. Never run a lesson command that writes builds, exports, logs, or caches into them. Source examples that provision boards or start services must be adapted to the actual authorized learning environment before execution.

Keep this durable plan under `LearningPlan`. Create each unit's working directory only when starting its lessons:

```text
LearningProgress/
  bonus-build-a-physical-robot/
    B00-requirements/
      NOTES.md
      TODO.md
      ...lesson scripts, diagrams, and evidence...
    B01-mechanics/
    ...one directory per active bonus unit...
```

Keep teacher-created code, firmware, CAD, configurations, logs, build output, caches, and measurements inside the applicable unit directory. For a tool that writes beside its input, use a copied fixture there. Read and adapt the environment runbook rather than copying old source-root output paths. Preparing this course does not establish the currently pending Rust runtime, graphical viewer, or daemon simulation setup.

Before a session, read the main progress ledger and the active bonus unit's notes. After a substantive lesson, append dated notes and add a concise bonus-track line to `LearningProgress/STATE.md`, keeping the main-course position explicit. Record:

- the question, physical setup, source revisions, and component identities;
- the concept explained and the genuine MicroDuck connection;
- commands, configuration, bounded duration, and artifact paths;
- actual measurements and their interpretation, uncertainty, and limits;
- what the teacher supplied and what the learner actually did or explained;
- pending hardware/source requirements, process cleanup, and next action.

Keep hardware-dependent work marked pending until performed. Preserve earlier measurements and corrections rather than rewriting history. These records should support continuation by another teacher without implying mastery or physical validation that has not occurred.

## First session when the learner chooses this track

Begin B00 with: **“What must happen between asking a robot to move and observing that it moved correctly?”** Draw a generic supported joint with its power source, actuator, sensor, controller, and operator. Trace one target through the physical feedback loop, then identify the corresponding MicroDuck components. Produce the first system diagram and requirements draft in the B00 learning directory. Leave detailed component selection and the next lesson for a later response.
