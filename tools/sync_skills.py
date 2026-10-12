"""Mirror the canonical skills in .agents/skills/ to other agents' skill folders.

    lab py tools/sync_skills.py                      # update .claude/skills (Claude Code)
    lab py tools/sync_skills.py --also .agent/skills # also write another mirror (older Antigravity)
    lab py tools/sync_skills.py --check              # exit 1 if a mirror is out of date (used by CI)

Edit skills only in .agents/skills/. Mirrors are plain copies and are overwritten.
Needs only the Python standard library, so plain `python tools/sync_skills.py` works too.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents" / "skills"
DEFAULT_MIRRORS = [ROOT / ".claude" / "skills"]


def files(base: Path) -> set[str]:
    return {p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts}


def differences(mirror: Path) -> list[str]:
    if not mirror.exists():
        return [f"{mirror.relative_to(ROOT)} is missing"]
    src, dst = files(SOURCE), files(mirror)
    out = [f"missing in mirror: {f}" for f in sorted(src - dst)]
    out += [f"extra in mirror: {f}" for f in sorted(dst - src)]
    out += [f"differs: {f}" for f in sorted(src & dst) if not filecmp.cmp(SOURCE / f, mirror / f, shallow=False)]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--also", action="append", default=[], help="extra mirror folder, relative to the repository")
    parser.add_argument("--check", action="store_true", help="only report whether mirrors are up to date")
    args = parser.parse_args()
    mirrors = DEFAULT_MIRRORS + [ROOT / extra for extra in args.also]

    status = 0
    for mirror in mirrors:
        diff = differences(mirror)
        name = mirror.relative_to(ROOT).as_posix()
        if args.check:
            if diff:
                status = 1
                print(f"{name}: OUT OF DATE\n  " + "\n  ".join(diff))
            else:
                print(f"{name}: up to date")
            continue
        if mirror.exists():
            shutil.rmtree(mirror)
        shutil.copytree(SOURCE, mirror, ignore=shutil.ignore_patterns("__pycache__"))
        print(f"{name}: synced {len(files(mirror))} files from .agents/skills")
    if status:
        print("\nRun: python tools/sync_skills.py", file=sys.stderr)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
