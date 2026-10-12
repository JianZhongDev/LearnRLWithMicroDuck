# Credits, sources and licenses

This course is built around other people's work. This file says what is used, how, and under which terms. If something is missing or wrong, please open an issue.

## What this repository contains, and its license

This repository contains the course's own material: teaching instructions for AI agents, the curriculum, lesson pages, lab scripts, a small helper library (`duckkit`), setup scripts and documentation. All of it is released under the [MIT License](LICENSE), with no exceptions.

What keeps it that way:

- **No third-party source code is included.** The MicroDuck repositories and all libraries are downloaded to your machine by setup, from their own sources, under their own licenses.
- **No images of the robot are included.** Every picture in this repository is a diagram or a plot made by the course's own scripts (for example `docs/images/make_hero.py`). A rendering of the MicroDuck robot would be a derivative of Pollen Robotics' 3D model, which is licensed under Creative Commons BY-NC-SA (see below), so such images are kept out of the repository. Labs do render the robot on your machine; those files go into `results/` folders, which Git ignores.
- Lesson pages quote a few lines of upstream code or configuration where a lesson needs them, name files and line numbers, and include short pseudocode that paraphrases upstream functions. Each such place names its source.

If you contribute lessons or publish a fork, keep these three points: cite upstream files instead of copying them, and do not commit robot renderings.

## MicroDuck (the worked example)

| | |
|---|---|
| Project | MicroDuck, a small open-source bipedal robot, by [Pollen Robotics](https://www.pollen-robotics.com/) and contributors |
| Training code and robot model | https://github.com/pollen-robotics/microduck_rl (code: Apache License 2.0) |
| Runtime software | https://github.com/pollen-robotics/microduck (Apache License 2.0) |
| 3D model files | Creative Commons BY-NC-SA, as stated in the `microduck_rl` README ("BY-SA-NC"): attribution, non-commercial, share-alike |
| Used here as | The system every lab simulates and every lesson explains. Setup obtains both repositories as separate checkouts outside this repository, at the commits in `tools/pins.env`, unmodified. |

This course is an independent, unofficial learning project. It is not affiliated with, sponsored by or endorsed by Pollen Robotics. "MicroDuck" and "Pollen Robotics" are used only to identify the upstream project. The upstream `AGENTS.md` and documentation, which lessons point learners to, are their authors' work.

If you use MicroDuck's model or anything derived from it (including rendered images and videos), follow its Creative Commons terms: credit Pollen Robotics, do not use it commercially, and share adaptations under the same license.

## Software the course runs on

Installed by setup into a private Python environment, from the versions locked by `microduck_rl`. None of it is redistributed here.

| Software | By | License | Role in the course |
|---|---|---|---|
| [MuJoCo](https://github.com/google-deepmind/mujoco) | Google DeepMind | Apache-2.0 | Physics engine; rendering of robot images |
| [MuJoCo Warp](https://github.com/google-deepmind/mujoco_warp) | Google DeepMind and NVIDIA | Apache-2.0 | GPU/CPU-parallel version of MuJoCo used for training environments |
| [Warp](https://github.com/NVIDIA/warp) | NVIDIA | Apache-2.0 | Compute framework under MuJoCo Warp |
| [mjlab](https://github.com/mujocolab/mjlab) | the mjlab authors | Apache-2.0 | Robot-learning framework: environments, managers, training scripts |
| [rsl_rl](https://github.com/leggedrobotics/rsl_rl) | Robotic Systems Lab, ETH Zurich, and NVIDIA | BSD-3-Clause | The PPO implementation that trains the robot |
| [BAM, Better Actuator Models](https://github.com/Rhoban/bam) | Rhoban | Apache-2.0 | Servo actuator model used in the simulation |
| [PyTorch](https://pytorch.org/) | the PyTorch Foundation and contributors | BSD-3-Clause | Neural networks and tensors |
| [ONNX Runtime](https://onnxruntime.ai/) | Microsoft | MIT | Running exported policies (Module 14) |
| [NumPy](https://numpy.org/), [SciPy](https://scipy.org/), [Matplotlib](https://matplotlib.org/), [Pillow](https://python-pillow.org/), [imageio](https://imageio.readthedocs.io/) | their communities | BSD-style / Matplotlib license / MIT-CMU / BSD-2-Clause | Numerics, plots, images and GIFs in labs |
| [uv](https://docs.astral.sh/uv/) | Astral | Apache-2.0 or MIT | Creates the Python environment |

Lesson pages in `LearningProgress/08-microduck-task-lifecycle/` describe how mjlab's environment step, termination, reward and observation managers work, with file and line references to mjlab 1.3.0 and to `microduck_rl`, and pseudocode simplified from those functions. That is commentary on Apache-2.0 code for teaching; the code itself is theirs.

## Ideas and methods taught

The course explains established methods. It did not invent them. Main references:

**Referenced directly in the course text**

- J. Schulman, F. Wolski, P. Dhariwal, A. Radford, O. Klimov. *Proximal Policy Optimization Algorithms.* 2017. https://arxiv.org/abs/1707.06347
- J. Schulman, P. Moritz, S. Levine, M. Jordan, P. Abbeel. *High-Dimensional Continuous Control Using Generalized Advantage Estimation.* ICLR 2016. https://arxiv.org/abs/1506.02438
- J. Achiam. *Spinning Up in Deep Reinforcement Learning.* OpenAI, 2018. https://spinningup.openai.com/
- MuJoCo documentation. https://mujoco.readthedocs.io/

**Origins of methods the curriculum covers**

- R. S. Sutton and A. G. Barto. *Reinforcement Learning: An Introduction*, 2nd edition. MIT Press, 2018. http://incompleteideas.net/book/the-book-2nd.html (returns, value functions, Bellman equations, temporal-difference learning; Modules 05–07)
- C. J. C. H. Watkins and P. Dayan. *Q-learning.* Machine Learning 8, 279–292, 1992. (Module 05)
- R. J. Williams. *Simple Statistical Gradient-Following Algorithms for Connectionist Reinforcement Learning.* Machine Learning 8, 229–256, 1992. (REINFORCE; Module 06)
- A. Y. Ng, D. Harada, S. Russell. *Policy Invariance Under Reward Transformations: Theory and Application to Reward Shaping.* ICML 1999. (potential-based shaping; Module 10)
- J. Tobin, R. Fong, A. Ray, J. Schneider, W. Zaremba, P. Abbeel. *Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World.* IROS 2017. (Module 12)
- N. Rudin, D. Hoeller, P. Reist, M. Hutter. *Learning to Walk in Minutes Using Massively Parallel Deep Reinforcement Learning.* CoRL 2021. (the approach behind rsl_rl-style training; Modules 08–09)
- E. Todorov, T. Erez, Y. Tassa. *MuJoCo: A Physics Engine for Model-Based Control.* IROS 2012.
- M. Macklin. *Warp: A High-performance Python Framework for GPU Simulation and Graphics.* NVIDIA GTC, 2022.
- S. R. Buss. *Introduction to Inverse Kinematics with Jacobian Transpose, Pseudoinverse and Damped Least Squares Methods.* 2004. (Module 02)

When a lesson relies on a specific paper, book or documentation page, it should say so on the lesson page. The teaching agent is instructed to do this.

## Conventions for AI agents

- [AGENTS.md](https://agents.md/): the open format for agent instruction files that this repository's `AGENTS.md` follows.
- [Agent Skills](https://agentskills.io/): the `SKILL.md` folder format, originally developed by Anthropic and now an open format, used in `.agents/skills/` and `.claude/skills/`.
- Product names (Codex, Claude Code, Gemini CLI, Antigravity, Grok) belong to OpenAI, Anthropic, Google and xAI. They are mentioned only to say how to use the course with each tool.

## Mascot and banner

- The duck mascot, `docs/assets/drduck_mascot_original.png`, was created by the maintainer with [ComfyUI](https://github.com/comfyanonymous/ComfyUI) and the Z-Image-Turbo image model. The file is the untouched original and still carries its embedded ComfyUI workflow (the prompt, the node graph and model file names), so it can be loaded back into ComfyUI to make variations.
- The banner, `docs/images/banner.png`, is composed from that image by `docs/images/make_banner.py`, with the title set in DejaVu Sans.
- Both are shared under the MIT License with the rest of the repository. The mascot is an original cartoon and is not derived from the MicroDuck robot's 3D model.

## How this course was made

The curriculum, teaching rules, lesson pages, labs and tooling were written with AI coding agents (OpenAI Codex and Anthropic Claude) under the maintainer's direction, and refined through trial teaching. Labs were run and checked as described in the README's "Tested so far" note. AI-written teaching material can contain errors; labs run real code so claims can be checked, and corrections are welcome.

## Reusing this course

You may reuse, adapt, translate and teach with everything in this repository under the MIT License: keep the copyright and license notice. Robot images and videos that the labs generate on your machine are not part of this repository; if you share them, the MicroDuck model's Creative Commons BY-NC-SA terms apply to them.
