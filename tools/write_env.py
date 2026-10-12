"""Write .course/env.json (called by setup.sh). Keeps fields the doctor has already recorded."""

import json
import pathlib
import sys

root, os_kind, arch, distro, launcher, python, wsl, rl_repo, runtime_repo = sys.argv[1:10]


def windows_path(path: str) -> str | None:
    """A path Windows tools can open, when running inside WSL."""
    if not wsl:
        return None
    if path.startswith("/mnt/") and len(path) > 6 and path[6] == "/":
        return f"{path[5].upper()}:" + path[6:].replace("/", "\\")
    return f"\\\\wsl.localhost\\{wsl}" + path.replace("/", "\\")


path = pathlib.Path(root, ".course", "env.json")
try:
    env = json.loads(path.read_text(encoding="utf-8"))
except (OSError, ValueError):
    env = {}
env.update(
    {
        "schema": 2,
        "os": os_kind,              # linux | wsl | macos
        "arch": arch,
        "distro": distro,
        "launcher": launcher,       # what the learner types to run a lab
        "python": python,
        # MicroDuck checkouts live outside this repository and are used read-only.
        "rl_repo": rl_repo,
        "runtime_repo": runtime_repo,
        "rl_repo_windows": windows_path(rl_repo),
        "runtime_repo_windows": windows_path(runtime_repo),
        "wsl_distro": wsl or None,
    }
)
path.write_text(json.dumps(env, indent=2), encoding="utf-8")
print(f"    wrote {path}")
