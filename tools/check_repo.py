"""Repository self-check. Needs only the Python standard library.

    python tools/check_repo.py            # or: lab py tools/check_repo.py
    python tools/check_repo.py --release  # also require a fresh, not-started course state

Checks:
  1. skill mirrors (.claude/skills) match .agents/skills
  2. every skill has valid front matter (name = folder name, description)
  3. no personal or machine-specific paths in course files
  4. relative links and images in Markdown files resolve
  5. shell scripts use LF line endings
  6. no MicroDuck source code or nested Git checkout inside the repository
  7. no robot renderings (animations, robot*.png) in tracked folders
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import sync_skills  # noqa: E402

SKIP_DIRS = {".git", "external", ".course", ".venv", "results", "verification", "__pycache__", "node_modules"}
TEXT_SUFFIXES = {".md", ".py", ".sh", ".cmd", ".env", ".json", ".yml", ".yaml", ".toml", ".txt"}
PERSONAL = [
    (re.compile(r"/home/[a-z0-9_]+/", re.I), "absolute home path"),
    (re.compile(r"/Users/[A-Za-z0-9_]+/"), "absolute home path"),
    (re.compile(r"\b[A-Z]:\\(?:Workspace|GitRepo|Users)\\", re.I), "absolute Windows path"),
    (re.compile(r"/mnt/[a-z]/(?:Workspace|GitRepo|Users)/", re.I), "absolute WSL path"),
]
ALLOW_PERSONAL = {"tools/check_repo.py"}
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

problems: list[str] = []


def course_files():
    for path in ROOT.rglob("*"):
        if path.is_file() and not (set(path.relative_to(ROOT).parts) & SKIP_DIRS):
            yield path


def check_skills() -> None:
    for mirror in sync_skills.DEFAULT_MIRRORS:
        for line in sync_skills.differences(mirror):
            problems.append(f"skill mirror {mirror.relative_to(ROOT).as_posix()}: {line} (run tools/sync_skills.py)")
    for skill in sorted((ROOT / ".agents" / "skills").iterdir()):
        md = skill / "SKILL.md"
        if not md.exists():
            problems.append(f"{skill.relative_to(ROOT).as_posix()}: missing SKILL.md")
            continue
        text = md.read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---\n", text, re.S)
        front = match.group(1) if match else ""
        name = re.search(r"^name:\s*(.+)$", front, re.M)
        desc = re.search(r"^description:\s*(.+)$", front, re.M)
        if not name or name.group(1).strip() != skill.name:
            problems.append(f"{md.relative_to(ROOT).as_posix()}: front matter 'name' must equal '{skill.name}'")
        if not desc or len(desc.group(1).strip()) < 20:
            problems.append(f"{md.relative_to(ROOT).as_posix()}: front matter needs a real 'description'")


def check_text() -> None:
    for path in course_files():
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        raw = path.read_bytes()
        if path.suffix == ".sh" and b"\r\n" in raw:
            problems.append(f"{rel}: shell script has CRLF line endings")
        text = raw.decode("utf-8", errors="replace")
        if rel not in ALLOW_PERSONAL:
            for pattern, label in PERSONAL:
                for m in pattern.finditer(text):
                    line = text.count("\n", 0, m.start()) + 1
                    problems.append(f"{rel}:{line}: {label}: {m.group(0)}")
        if path.suffix == ".md" and not path.name.endswith("_TEMPLATE.md"):
            in_code = False
            for number, line in enumerate(text.splitlines(), 1):
                if line.lstrip().startswith("```"):
                    in_code = not in_code
                if in_code:
                    continue
                for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
                    if re.match(r"[a-z]+:", target) or target.startswith("#") or "<" in target:
                        continue
                    target = target.split("#")[0]
                    if target and not (path.parent / target).exists():
                        problems.append(f"{rel}:{number}: broken link: {target}")


def check_no_upstream_code() -> None:
    """The MicroDuck repositories must never be stored inside this repository."""
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in {".git", ".course", ".venv"}:
            continue
        if path.name == ".git" and path.parent != ROOT:
            problems.append(f"{rel.parent.as_posix()}: nested Git checkout inside the repository (upstream code must live outside)")
        if path.is_dir() and path.name in {"mjlab_microduck", "duck-control", "robotd"}:
            problems.append(f"{rel.as_posix()}: looks like MicroDuck source code inside the repository")


# Animations and videos are almost always renderings of the robot, which carry the MicroDuck
# model's CC BY-NC-SA license. Only course-drawn schematics listed here may be committed.
ALLOWED_ANIMATIONS = {"docs/images/lab_tilt.gif"}


def check_no_robot_renderings() -> None:
    for path in course_files():
        rel = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() in {".gif", ".mp4", ".webm", ".mov"} and rel not in ALLOWED_ANIMATIONS:
            problems.append(f"{rel}: animation or video in a tracked folder. Robot renderings must stay in results/ "
                            "(CC BY-NC-SA model); add course-drawn schematics to ALLOWED_ANIMATIONS")
        if path.name.lower().startswith("robot") and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
            problems.append(f"{rel}: looks like a robot rendering; keep it in results/, not in the repository")


def check_release() -> None:
    state = (ROOT / "LearningProgress" / "STATE.md").read_text(encoding="utf-8")
    if "not started" not in state:
        problems.append("LearningProgress/STATE.md: a release must ship with the course not started")
    for path in (ROOT / "LearningProgress").rglob("results"):
        if path.is_dir() and any(path.iterdir()):
            problems.append(f"{path.relative_to(ROOT).as_posix()}: lab results present (delete before release)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()
    check_skills()
    check_text()
    check_no_upstream_code()
    check_no_robot_renderings()
    if args.release:
        check_release()
    if problems:
        print(f"{len(problems)} problem(s):")
        for line in problems:
            print("  " + line)
        return 1
    print("check_repo: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
