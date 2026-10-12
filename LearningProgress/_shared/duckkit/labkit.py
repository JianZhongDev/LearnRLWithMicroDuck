"""Support for the lab rhythm: run it, change one thing, run it again.

A lab declares its adjustable settings once:

    run = lab_config(
        {"steps": 100, "noise": 0.0},
        help={"noise": "std-dev of random joint-target offsets (policy action units)"},
    )

The learner changes a setting from the command line without editing code:

    lab 08/L01 noise=0.3

Each distinct setting combination gets its own result folder, so earlier runs
stay available for side-by-side comparison:

    results/default/        results/noise=0.3/
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _parse_value(text: str, default: Any) -> Any:
    if isinstance(default, bool):
        if text.lower() in {"1", "true", "yes", "on"}:
            return True
        if text.lower() in {"0", "false", "no", "off"}:
            return False
        raise ValueError(f"expected true/false, got {text!r}")
    if isinstance(default, int):
        return int(text)
    if isinstance(default, float):
        return float(text)
    return text


@dataclass
class LabRun:
    cfg: SimpleNamespace
    changed: dict[str, Any]
    name: str
    out: Path
    lab_dir: Path
    defaults: dict[str, Any] = field(repr=False)

    def save_json(self, filename: str, data: dict) -> Path:
        path = self.out / filename
        path.write_text(json.dumps(data, indent=2, default=float), encoding="utf-8")
        return path

    def other_runs(self) -> list[Path]:
        """Result folders from earlier runs of this lab, for comparisons."""
        return sorted(p for p in (self.lab_dir / "results").iterdir() if p.is_dir() and p != self.out)


def lab_config(
    defaults: dict[str, Any],
    help: dict[str, str] | None = None,
    argv: list[str] | None = None,
) -> LabRun:
    """Parse `key=value` arguments against `defaults` and prepare a result folder."""
    argv = sys.argv[1:] if argv is None else argv
    help = help or {}
    lab_dir = Path(sys.argv[0]).resolve().parent

    if any(a in {"-h", "--help", "help"} for a in argv):
        print("Settings you can change (key=value):")
        for key, value in defaults.items():
            print(f"  {key}={value!r:<10} {help.get(key, '')}")
        raise SystemExit(0)

    values = dict(defaults)
    changed: dict[str, Any] = {}
    for arg in argv:
        if "=" not in arg:
            raise SystemExit(f"Expected key=value, got {arg!r}. Use 'help' to list settings.")
        key, text = arg.split("=", 1)
        if key not in defaults:
            raise SystemExit(f"Unknown setting {key!r}. Known: {', '.join(defaults)}")
        values[key] = _parse_value(text, defaults[key])
        if values[key] != defaults[key]:
            changed[key] = values[key]

    name = "default" if not changed else ",".join(f"{k}={v}" for k, v in changed.items())
    out = lab_dir / "results" / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "settings.json").write_text(
        json.dumps({"settings": values, "changed_from_default": changed}, indent=2), encoding="utf-8"
    )

    print("=" * 64)
    print(f"Lab: {lab_dir.name}")
    for key, value in values.items():
        marker = "  <- changed" if key in changed else ""
        print(f"  {key} = {value!r}{marker}")
    print(f"Results folder: {out}")
    print("=" * 64)
    return LabRun(SimpleNamespace(**values), changed, name, out, lab_dir, defaults)
