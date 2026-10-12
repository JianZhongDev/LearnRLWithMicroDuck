"""Whole-course map.

Run from the repository root:  lab py LearningPlan/figures/make_course_map.py [stage]

`stage` is the index (0-5) of the stage to mark "YOU ARE HERE"; omit it for no marker.
"""

import sys
from pathlib import Path

import duckkit as dk

stage = int(sys.argv[1]) if len(sys.argv) > 1 else None
dk.flow_diagram(
    [
        ("Robot basics", "00-04: physics, frames, motors, sensors"),
        ("Learning algorithm", "05-07: tabular RL to PPO"),
        ("Robot as an RL task", "08-10: env loop, baseline, rewards"),
        ("Better skills", "11-13: new task, robustness, experiments"),
        ("Deploy & integrate", "14-16: export, runtime, perception"),
        ("Capstone", "17: improve and defend one skill"),
    ],
    highlight=stage,
    highlight_tag="YOU ARE HERE",
    title="Course map: from robot physics to a deployed learned skill",
    path=Path(__file__).resolve().parent / "course_map.png",
    box_width=2.7,
    gap=0.6,
)
