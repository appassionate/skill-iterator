#!/usr/bin/env python3
"""setup.py — Workspace scaffolding for iter_skill pipeline.

Sets up a new iteration directory and manages the target_skill/ git branch.
The skill lives in target_skill/ at the workspace root as the single working
copy — no per-iteration skill copies are created.

Usage:
    python setup.py --base <workspace_path> --iter <N>
    python setup.py --base . --iter 7
"""

import argparse
import subprocess
import sys
from pathlib import Path

from _common import count_lines


def ensure_git(target_skill: Path) -> None:
    """Ensure target_skill/ is a git repository."""
    if not (target_skill / ".git").exists():
        subprocess.run(
            ["git", "init"], cwd=target_skill,
            capture_output=True, check=True,
        )
        subprocess.run(
            ["git", "add", "-A"], cwd=target_skill,
            capture_output=True, check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial import"],
            cwd=target_skill, capture_output=True, check=True,
        )
        print("  Initialized git in target_skill/")


def create_branch(target_skill: Path, branch_name: str) -> None:
    """Create iteration branch, deleting existing one if necessary."""
    result = subprocess.run(
        ["git", "branch", "--list", branch_name],
        cwd=target_skill, capture_output=True, text=True,
    )
    if result.stdout.strip():
        subprocess.run(
            ["git", "branch", "-D", branch_name],
            cwd=target_skill, capture_output=True, check=True,
        )
        print(f"  Deleted existing branch: {branch_name}")

    subprocess.run(
        ["git", "checkout", "-b", branch_name],
        cwd=target_skill, capture_output=True, check=True,
    )
    print(f"  Created branch: {branch_name}")


def setup_iteration(base: Path, iter_num: int) -> None:
    """Create iteration directory structure and set up git branch."""
    iter_dir = base / f"iter.{iter_num:04d}"
    branch_name = f"iter.{iter_num:04d}"
    target_skill = base / "target_skill"

    # Verify target_skill/ exists
    if not target_skill.exists():
        print("Error: target_skill/ not found at workspace root.")
        print("Create target_skill/ with the full skill content before running setup.")
        sys.exit(1)

    # Ensure git is initialized
    ensure_git(target_skill)

    # Create iteration directory structure (execute + validation + summarize)
    dirs = [
        iter_dir / "01.train" / "execute",
        iter_dir / "02.validation",
        iter_dir / "03.summarize",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {d.relative_to(base)}")

    # Create git branch for this iteration
    create_branch(target_skill, branch_name)

    # Print line counts from the single working copy
    print()
    counts = count_lines(target_skill)
    print("  target_skill/ line counts:")
    print(f"  {'File':<35} {'Lines':>6}")
    print(f"  {'─' * 35} {'─' * 6}")
    for name, count in counts.items():
        print(f"  {name:<35} {count:>6}")

    print(f"\n  {branch_name} workspace ready.")


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

    args = parser.parse_args()

    if not args.base.exists():
        print(f"Error: Base directory {args.base} does not exist.")
        sys.exit(1)

    setup_iteration(args.base.resolve(), args.iter)


if __name__ == "__main__":
    main()
