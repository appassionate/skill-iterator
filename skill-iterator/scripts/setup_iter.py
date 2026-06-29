#!/usr/bin/env python3
"""setup_iter.py — Workspace scaffolding for iter_skill pipeline.

Creates the directory structure for a new iteration and copies the skill
from the previous iteration's 03.output/. Prints initial line counts.

Usage:
    python setup_iter.py --base <workspace_path> --iter <N>
    python setup_iter.py --base . --iter 7
    python setup_iter.py --base /path/to/iter_skill(target)/ --iter 3 --skill-name my-skill
"""

import argparse
import os
import shutil
import sys
from pathlib import Path


def count_lines(directory: Path) -> dict[str, int]:
    """Count lines in SKILL.md and all references/*.md files."""
    counts = {}
    skill_md = directory / "SKILL.md"
    if skill_md.exists():
        counts["SKILL.md"] = sum(1 for _ in skill_md.open())

    refs_dir = directory / "references"
    if refs_dir.exists():
        for f in sorted(refs_dir.glob("*.md")):
            counts[f"references/{f.name}"] = sum(1 for _ in f.open())

    counts["Total"] = sum(counts.values())
    return counts


def setup_iteration(base: Path, iter_num: int, skill_name: str | None = None) -> None:
    """Create iteration directory structure and copy skill from previous output."""
    iter_dir = base / f"iter.{iter_num:04d}"
    prev_iter_dir = base / f"iter.{iter_num - 1:04d}"

    # Determine source: previous 03.output or installed skill
    if prev_iter_dir.exists():
        source = prev_iter_dir / "03.output"
        if not source.exists():
            print(f"Error: {source} does not exist. Previous iteration incomplete?")
            sys.exit(1)
    else:
        # First iteration — look for installed skill
        home = Path.home()
        name = skill_name or base.name.replace("iter_skill(", "").rstrip(")")
        source = home / ".qoderworkcn" / "skills" / name
        if not source.exists():
            print(f"Error: No previous iteration found and no installed skill at {source}")
            sys.exit(1)

    # Create directory structure
    dirs = [
        iter_dir / "01.train" / "skill" / "references",
        iter_dir / "01.train" / "execute",
        iter_dir / "02.validation",
        iter_dir / "03.output",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {d.relative_to(base)}")

    # Copy skill files
    skill_src = source / "SKILL.md"
    skill_dst = iter_dir / "01.train" / "skill" / "SKILL.md"
    if skill_src.exists():
        shutil.copy2(skill_src, skill_dst)

    refs_src = source / "references"
    refs_dst = iter_dir / "01.train" / "skill" / "references"
    if refs_src.exists():
        for f in refs_src.glob("*.md"):
            shutil.copy2(f, refs_dst / f.name)

    # Print line counts
    print(f"\n  Source: {source}")
    print(f"  Destination: {iter_dir.relative_to(base)}/01.train/skill/")
    print()

    counts = count_lines(iter_dir / "01.train" / "skill")
    print("  Initial line counts:")
    print(f"  {'File':<35} {'Lines':>6}")
    print(f"  {'─' * 35} {'─' * 6}")
    for name, count in counts.items():
        print(f"  {name:<35} {count:>6}")

    print(f"\n  iter.{iter_num:04d} workspace ready.")


def main():
    parser = argparse.ArgumentParser(
        description="Set up workspace for a new iter_skill iteration."
    )
    parser.add_argument(
        "--base",
        type=Path,
        required=True,
        help="Base workspace directory (e.g., iter_skill(target-skill)/)",
    )
    parser.add_argument(
        "--iter",
        type=int,
        required=True,
        help="Iteration number (e.g., 7 for iter.0007)",
    )
    parser.add_argument(
        "--skill-name",
        type=str,
        default=None,
        help="Skill name for first iteration (defaults to base directory name)",
    )

    args = parser.parse_args()

    if not args.base.exists():
        print(f"Error: Base directory {args.base} does not exist.")
        sys.exit(1)

    setup_iteration(args.base.resolve(), args.iter, args.skill_name)


if __name__ == "__main__":
    main()
