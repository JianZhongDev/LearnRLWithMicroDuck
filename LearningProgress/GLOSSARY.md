# Glossary

One plain line per term, with the module that introduces it. The list is pre-filled so that lessons can link here instead of re-defining terms at length. The agent adds and refines entries in `session-handoff` as terms come up.

## Robotics and simulation

- **actuator** (03): the motor and electronics that move a joint. It has limits (torque, speed, delay), so it does not move instantly to a target.
- **back-EMF** (03): back-electromotive force, the voltage a spinning motor generates against its supply. It makes a motor weaker at high speed.
- **BAM** (03): Better Actuator Models, the motor model MicroDuck's simulator uses (voltage, friction, delay, back-EMF).
- **collision geometry** (01): the simple shapes the physics engine uses for contact. These are separate from the visual mesh you see.
- **damped least squares, DLS** (02): a way to solve inverse kinematics that stays stable near awkward poses by trading a little accuracy for smaller joint moves.
- **decimation** (08): the number of physics steps per policy step (4 for MicroDuck walking).
- **forward kinematics, FK** (02): computing where a body part is from the joint angles.
- **frame** (02): a coordinate system attached to something (world, trunk, camera). The same point has different coordinates in different frames.
- **generalized coordinates, qpos / qvel** (01): the minimal list of numbers that describes the robot's pose and velocity in the simulator.
- **IMU** (04): inertial measurement unit, a sensor that measures rotation rate and acceleration. Used to estimate tilt.
- **inverse kinematics, IK** (02): finding joint angles that put a body part where you want it.
- **Jacobian** (02): a table of how much each joint's small movement moves a point. It turns joint speeds into point speeds.
- **joint target** (08): the angle a joint's motor is told to reach. The joint does not necessarily reach it.
- **MuJoCo** (01): the physics engine used here. mjlab runs many MuJoCo copies on the GPU.
- **odometry** (04): estimating how far the robot moved from its own sensors, for example foot contacts and the IMU. It drifts over time.
- **PD control** (03): proportional-derivative control. The push toward a target grows with the position error and is damped by velocity.
- **physics step** (08): one physics update (5 ms here).
- **projected gravity** (04): the direction of gravity expressed in the robot's own frame. It tells the policy how tilted the robot is.

## Reinforcement learning

- **action** (00): what the policy outputs each step. For MicroDuck: 14 joint-target offsets from the default pose, in radians.
- **actor** (08.L04): the policy that chooses actions from its input, distinct from the critic used to help train it.
- **advantage** (07): how much better an action turned out than what was expected in that situation.
- **critic / value function** (07): a learned prediction of future reward from a situation, used as the reference for the advantage.
- **constant policy** (08.L01): a rule that returns the same action every step, regardless of the observation.
- **discount, γ (gamma)** (05): how much less a reward counts for each step it lies in the future.
- **entropy** (06): how spread out a policy's action choices are. A small bonus keeps it exploring.
- **environment** (08): the simulator plus code that turns it into observations, rewards and episode endings for a policy.
- **episode** (05, 08): one run from reset until it ends.
- **GAE** (07): generalized advantage estimation, which blends one-step and multi-step advantage estimates using λ (lambda).
- **observation** (04): the numbers the policy sees each step (61 for MicroDuck's actor). It is not the full simulator state.
- **observation noise** (08.L04): random changes applied to input readings to imitate imperfect sensing.
- **parallel environments, num_envs** (08): independent robot copies simulated at the same time, each with its own episode.
- **policy** (00): the rule, here a neural network, that maps an observation to an action.
- **policy gradient** (06): changing the policy's parameters in the direction that makes higher-reward actions more likely.
- **policy step** (08): one decision of the policy (20 ms, 50 per second, for MicroDuck walking).
- **privileged information** (08.L04): information available during training that is not supplied to the acting policy, such as this task's direct trunk linear velocity.
- **PPO** (07): Proximal Policy Optimization, a policy-gradient training method that reuses a batch of experience a few times while limiting how far the policy moves.
- **reset** (08): putting a robot copy back at a start state after its episode ends.
- **return** (05): the discounted sum of rewards from a step to the end of the episode.
- **reward** (00, 08): a number per step saying how good the result was. For MicroDuck it is a weighted sum of named terms.
- **reward term** (08.L03): one measurable part of behavior used to build the score, such as uprightness or changes in requested joint targets.
- **reward weight** (08.L03): a signed multiplier controlling how strongly a term contributes; this task also multiplies by step duration.
- **terminated / truncated** (08.L02): an episode reached a task ending condition (failure or success) vs. was cut short by an external limit (for example time ran out).
- **automatic reset** (08.L02): the environment starts a new episode for an ended robot copy inside its step call; the returned observation then describes the new start.
- **transition** (07): one record (observation, action, reward, ended?) from one step of one robot copy.
- **collected training batch** (08.L05): the set of step records gathered from all robot copies for the next policy update.
- **training iteration** (08.L05): one cycle of collecting experience and updating the policy; the update can contain several internal parameter adjustments.
- **baseline** (09 overview): an unchanged reference used to judge later changes fairly.
- **checkpoint** (09 overview): a saved training snapshot containing the controller's learned values and, here, other training state.
- **seed** (09 plan): a number used to initialize random draws so a test can be repeated; it does not guarantee identical results across hardware or software changes.
- **inference** (09.L01): using a learned controller to choose actions without updating its learned values.
- **input scaling / observation normalization** (09.L01): rescaling readings using saved statistics before passing them to the controller; those statistics must be restored with the learned values for replay.
