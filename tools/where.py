"""Print where installed Python packages and the MicroDuck sources live, so an agent can read them.

    lab py tools/where.py mjlab rsl_rl

On Windows (WSL) the Linux path is also shown as a \\\\wsl.localhost\\... path that
Windows file tools can open.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from duckkit import setup as cfg


def windows_path(path: Path) -> str | None:
    distro = os.environ.get("WSL_DISTRO_NAME")
    if not distro:
        return None
    text = str(path)
    if text.startswith("/mnt/") and len(text) > 6 and text[6] == "/":
        return f"{text[5].upper()}:" + text[6:].replace("/", "\\")
    return f"\\\\wsl.localhost\\{distro}" + text.replace("/", "\\")


def show(label: str, path: Path) -> None:
    print(f"{label}: {path}")
    win = windows_path(path)
    if win:
        print(f"{' ' * len(label)}  Windows: {win}")


show("microduck_rl (training source)", cfg.RL_REPO)
show("microduck (robot runtime source)", cfg.RUNTIME_REPO)
for name in sys.argv[1:]:
    spec = importlib.util.find_spec(name)
    if spec is None or not spec.origin:
        print(f"{name}: not installed in this environment")
        continue
    show(name, Path(spec.origin).parent)
