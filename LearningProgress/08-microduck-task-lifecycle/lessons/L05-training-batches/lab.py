"""Lab 08/L05: how do steps become training data?

Run: lab 08/L05
Change one thing: lab 08/L05 num_envs=32
Outputs: batch.png (last collected batch), batches.csv, signals.npz,
summary.json, training.log, training/ (local checkpoints and event log),
and ../compare.png (collected records versus completed iterations).
Uses real MicroDuck training through duckkit; five iterations test the
collection/update loop, not walking quality.
"""
import duckkit as dk

run = dk.lab_config(
    {"num_envs": 64, "iterations": 5, "seed": 0},
    help={"num_envs": "parallel robot copies (count, 4 to 128, multiple of 4)",
          "iterations": "collection/update cycles (count, 1 to 5)",
          "seed": "random seed (integer)"},
)
cfg = run.cfg
if not (4 <= cfg.num_envs <= 128 and cfg.num_envs % 4 == 0 and 1 <= cfg.iterations <= 5):
    raise SystemExit("Use 4..128 robots in multiples of 4, and 1..5 iterations.")

from contextlib import redirect_stdout, redirect_stderr
from dataclasses import asdict
from datetime import datetime
import csv
import json
import sys
import time
import numpy as np
import torch
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.rl.runner import MjlabOnPolicyRunner
from mjlab.tasks.registry import load_rl_cfg, load_runner_cls


class Tee:
    def __init__(self, terminal, file):
        self.terminal, self.file = terminal, file

    def write(self, text):
        self.terminal.write(text)
        self.file.write(text)
        return len(text)

    def flush(self):
        self.terminal.flush()
        self.file.flush()

    def isatty(self):
        return False


class CountedEnv(RslRlVecEnvWrapper):
    """Read-only measurements of the real calls made by the trainer."""
    def __init__(self, env, clip_actions):
        super().__init__(env, clip_actions)
        self.step_calls = 0
        self.ending_rows = []

    def step(self, actions):
        result = super().step(actions)
        self.step_calls += 1
        self.ending_rows.append(result[2].detach().cpu().numpy().copy())
        return result


started = time.perf_counter()
rows, done_batches = [], []
with (run.out / "training.log").open("w", encoding="utf-8") as log:
    with redirect_stdout(Tee(sys.stdout, log)), redirect_stderr(Tee(sys.stderr, log)):
        torch.set_num_threads(4)
        env = dk.make_env(num_envs=cfg.num_envs, seed=cfg.seed)
        try:
            agent = load_rl_cfg(dk.DEFAULT_TASK)
            agent.seed = cfg.seed
            agent.logger = "tensorboard"
            agent.upload_model = False
            agent.max_iterations = cfg.iterations
            train_cfg = asdict(agent)
            run.save_json("agent_config.json", train_cfg)
            wrapped = CountedEnv(env, agent.clip_actions)
            task_runner = load_runner_cls(dk.DEFAULT_TASK)

            class LessonRunner(task_runner):
                # Keep training intact; skip the unrelated automatic ONNX export.
                def save(self, path, infos=None):
                    MjlabOnPolicyRunner.save(self, path, infos)

            training_dir = run.out / "training" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            runner = LessonRunner(wrapped, train_cfg, str(training_dir), device=env.device)
            steps = agent.num_steps_per_env
            original_update = runner.alg.update

            def measured_update():
                storage = runner.alg.storage
                iteration = len(rows) + 1
                shape = tuple(storage.rewards.shape)
                dones = storage.dones[..., 0].detach().cpu().numpy().copy()
                assert storage.step == steps
                assert shape == (steps, cfg.num_envs, 1), shape
                assert wrapped.step_calls == iteration * steps
                np.testing.assert_array_equal(dones, np.stack(wrapped.ending_rows[-steps:]))
                for tensor in (storage.rewards, storage.actions, storage.values):
                    assert torch.isfinite(tensor).all()
                assert storage.observations.batch_size == torch.Size([steps, cfg.num_envs])
                done_batches.append(dones)
                # Save the final batch before the trainer clears/reuses its storage.
                np.savez_compressed(
                    run.out / "last_batch.npz",
                    actor=storage.observations["actor"].detach().cpu().numpy(),
                    actions=storage.actions.detach().cpu().numpy(),
                    rewards=storage.rewards.detach().cpu().numpy(), dones=dones,
                )
                result = original_update()
                assert storage.step == 0
                assert all(np.isfinite(float(value)) for value in result.values())
                rows.append({"iteration": iteration, "robots": cfg.num_envs,
                             "steps_per_robot": steps, "records": int(np.prod(shape)),
                             "cumulative_records": wrapped.step_calls * wrapped.num_envs,
                             "episode_endings": int(dones.sum())})
                return result

            runner.alg.update = measured_update
            runner.learn(cfg.iterations, init_at_random_ep_len=False)
            total = wrapped.step_calls * wrapped.num_envs
            assert len(rows) == cfg.iterations
            assert runner.logger.tot_timesteps == total == sum(r["records"] for r in rows)
            dt = env.step_dt
        finally:
            env.close()

with (run.out / "batches.csv").open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
np.savez_compressed(run.out / "signals.npz", dones=np.stack(done_batches),
                    cumulative_records=[r["cumulative_records"] for r in rows])
run.save_json("summary.json", {"robots": cfg.num_envs, "steps_per_robot": steps,
    "iterations": cfg.iterations, "records_per_batch": rows[0]["records"],
    "total_records": total, "step_seconds": dt, "batch_seconds_per_robot": steps * dt,
    "wall_seconds": time.perf_counter() - started, "checks_passed": True,
    "batches": rows, "training_dir": str(training_dir)})

dk.use_style()
fig, ax = plt.subplots(figsize=(11, 5.3))
ax.imshow(np.ones((steps, cfg.num_envs)), cmap=ListedColormap(["#dcecff"]),
          aspect="auto", interpolation="nearest", extent=(-0.5, cfg.num_envs-.5, steps+.5, .5))
for x in np.arange(-.5, cfg.num_envs, 1):
    ax.axvline(x, color="white", linewidth=.55)
for y in np.arange(.5, steps+1, 1):
    ax.axhline(y, color="white", linewidth=.55)
ended_steps, ended_copies = np.nonzero(done_batches[-1])
ax.scatter(ended_copies, ended_steps+1, c=dk.COLORS["red"], marker="x", s=22, linewidths=1.2)
ax.set(xlabel="Robot copy (index)", ylabel="Collected step within this batch (count)",
       yticks=[1, 6, 12, 18, 24], xticks=sorted(set([0, cfg.num_envs//2, cfg.num_envs-1])))
ax.set_title(f"One cell = one record: {cfg.num_envs} robots × {steps} steps = {rows[0]['records']:,} records",
             fontsize=14, pad=26)
ax.text(.5, 1.025, f"Measured batch {cfg.iterations} | Read down one column: one robot's steps",
        transform=ax.transAxes, ha="center", fontsize=10)
ax.legend(handles=[Line2D([], [], color=dk.COLORS["red"], marker="x", linestyle="None",
                         label="Episode ended; the next step uses a reset robot")],
          loc="upper center", bbox_to_anchor=(.5, -.15), frameon=False, fontsize=10)
dk.save_fig(fig, run.out / "batch.png")

fig, ax = plt.subplots(figsize=(9, 4.8))
for summary_path in sorted((run.lab_dir / "results").glob("*/summary.json")):
    data = json.loads(summary_path.read_text())
    records = [0] + [row["cumulative_records"] for row in data["batches"]]
    ax.plot(range(len(records)), records, "o-", label=f"{summary_path.parent.name}: {data['robots']} robots")
ax.set(xlabel="Completed collection/update cycles (count)", ylabel="Collected records (count)",
       title="More robots collect more records before each policy update")
ax.set_xticks(range(cfg.iterations+1))
ax.legend(fontsize=9)
dk.save_fig(fig, run.lab_dir / "results" / "compare.png")

print("\nEach row is one collection/update cycle (all quantities are counts).")
print("Cycle   Robots   Steps/robot   Records in batch   Total records   Endings")
for row in rows:
    print(f"{row['iteration']:5} {row['robots']:8} {steps:13} {row['records']:18} "
          f"{row['cumulative_records']:15} {row['episode_endings']:9}")
print("Checks passed: full storage, recorded endings, update count, and trainer total agree.")
print("Open batch.png first, then ../compare.png. Five cycles do not establish walking quality.")
