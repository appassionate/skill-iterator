#!/usr/bin/env python3
"""_common.py — Shared utilities for iter_skill pipeline scripts.

Provides reusable functions for line counting and file inspection.
Imported by setup.py and verify.py to avoid code duplication.
"""

from pathlib import Path


def count_lines(directory: Path) -> dict[str, int]:
    """Count lines in SKILL.md, references/*.md, and scripts/*.py files.

    Uses encoding="utf-8" with errors="replace" for cross-platform safety,
    ensuring CJK and other non-ASCII content does not cause crashes.
    """
    counts = {}
    skill_md = directory / "SKILL.md"
    if skill_md.exists():
        counts["SKILL.md"] = sum(
            1 for _ in skill_md.open(encoding="utf-8", errors="replace")
        )

    refs_dir = directory / "references"
    if refs_dir.exists():
        for f in sorted(refs_dir.glob("*.md")):
            counts[f"references/{f.name}"] = sum(
                1 for _ in f.open(encoding="utf-8", errors="replace")
            )

    scripts_dir = directory / "scripts"
    if scripts_dir.exists():
        for f in sorted(scripts_dir.glob("*.py")):
            counts[f"scripts/{f.name}"] = sum(
                1 for _ in f.open(encoding="utf-8", errors="replace")
            )

    counts["Total"] = sum(v for k, v in counts.items() if k != "Total")
    return counts
