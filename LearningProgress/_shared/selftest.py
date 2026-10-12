"""Check that duckkit can build, step, record and render the MicroDuck environment.

Run:  lab doctor --full      (or: lab py LearningProgress/_shared/selftest.py)
Outputs go to .course/selftest-output/.
"""

import json
import time

import duckkit as dk
from duckkit.setup import COURSE_DIR
from duckkit.sim import describe_env

OUT = COURSE_DIR / "selftest-output"
OUT.mkdir(parents=True, exist_ok=True)

t0 = time.time()
dk.flow_diagram(
    [("Observe", "sensors -> numbers"), ("Policy", "numbers -> action"),
     ("Actuators", "action -> torque"), ("Physics", "torque -> motion")],
    highlight=1, loop_label="next observation", title="Diagram check", path=OUT / "diagram.png",
)

print(f"simulation device: {dk.default_device()}   torch device: {dk.torch_device()}   rendering: {'on' if dk.can_render() else 'off'}")
env = dk.make_env(num_envs=2, render=True, seed=0)
try:
    info = describe_env(env)
    print(json.dumps(info, indent=2))
    traj = dk.rollout(env, dk.zero_policy(env), steps=40, render_every=2)
finally:
    env.close()

print("reward shape", traj.reward.shape, "frames", len(traj.frames))
print("height first/last (m)", traj.base_height[0], traj.base_height[-1])
print("tilt first/last (deg)", traj.tilt_deg[0], traj.tilt_deg[-1])
mismatch = float(abs(sum(traj.reward_terms.values()) - traj.reward).max())
print("max |sum(reward terms) - reward|", mismatch)
assert mismatch < 1e-4, "reward terms do not add up to the returned reward"
assert traj.reward.shape == (40, 2)
captions = [f"t = {(s + 1) * traj.step_dt:4.2f} s" for s in traj.frame_steps]
dk.save_gif(dk.caption_frames(traj.frames, captions), OUT / "robot.gif")
(OUT / "env_summary.json").write_text(json.dumps(info, indent=2))
print(f"selftest OK in {time.time() - t0:.1f} s  (outputs: {OUT})")
