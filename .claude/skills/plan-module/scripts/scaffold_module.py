"""Create the standard files for a course module. Never overwrites existing files.

Run from the repository root:   lab py .agents/skills/plan-module/scripts/scaffold_module.py 09
Options:                        [--dry-run] [--root <LearningProgress path>]

Creates, inside LearningProgress/<NN>-<name>/ (the folder must already exist):
  MAP.md      from assets/MAP_TEMPLATE.md, with the module title filled in
  NOTES.md    header + a "module started" entry to append to
  TODO.md     header
  figures/    for concept diagrams and their generating script
  lessons/    one sub-folder per lesson (LESSON.md + lab.py), created by teach-lesson
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = SKILL_DIR.parents[2] / "LearningProgress"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("module", help="two-digit module number, e.g. 09")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    number = f"{int(args.module):02d}"
    matches = sorted(p for p in args.root.glob(f"{number}-*") if p.is_dir())
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one folder {args.root}/{number}-*, found {matches}")
    module_dir = matches[0]
    title = module_dir.name.split("-", 1)[1].replace("-", " ").capitalize()
    today = dt.date.today().isoformat()

    template = (SKILL_DIR / "assets" / "MAP_TEMPLATE.md").read_text(encoding="utf-8")
    files = {
        "MAP.md": template.replace("<NN>", number).replace("<title>", title),
        "NOTES.md": (
            f"# Module {number} notes — {title}\n\n"
            "Dated history: append entries, never rewrite. Format in the session-handoff skill.\n\n"
            f"## {today} — module started\n\n"
            "- Plan: `MAP.md` (written by plan-module).\n"
            "- Learner did: nothing yet in this module.\n"
        ),
        "TODO.md": (
            f"# Module {number} to-do\n\n"
            "Parked side topics and unfinished work. One line each, with the date and where it came from.\n"
        ),
    }

    for sub in ("figures", "lessons"):
        path = module_dir / sub
        print(("exists   " if path.exists() else "create   ") + str(path))
        if not args.dry_run:
            path.mkdir(exist_ok=True)
    for name, text in files.items():
        path = module_dir / name
        if path.exists():
            print(f"keep     {path}  (already exists, not changed)")
            continue
        print(f"create   {path}")
        if not args.dry_run:
            path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
