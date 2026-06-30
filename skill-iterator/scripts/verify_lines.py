#!/usr/bin/env python3
"""verify_lines.py — Line count verification for iter_skill pipeline.

Counts lines in target_skill/ and optionally compares against a previous
git state. Outputs a delta table for changelog.md / benchmark.md.

Usage:
    python verify_lines.py --current target_skill
    python verify_lines.py --current target_skill --previous target_skill
"""

import argparse
import sys
from pathlib import Path


def count_lines(directory: Path) -> dict[str, int]:
    """Count lines in SKILL.md, references/*.md, and scripts/*.py files."""
    counts = {}
    skill_md = directory / "SKILL.md"
    if skill_md.exists():
        counts["SKILL.md"] = sum(1 for _ in skill_md.open())

    refs_dir = directory / "references"
    if refs_dir.exists():
        for f in sorted(refs_dir.glob("*.md")):
            counts[f"references/{f.name}"] = sum(1 for _ in f.open())

    scripts_dir = directory / "scripts"
    if scripts_dir.exists():
        for f in sorted(scripts_dir.glob("*.py")):
            counts[f"scripts/{f.name}"] = sum(1 for _ in f.open())

    counts["Total"] = sum(v for k, v in counts.items() if k != "Total")
    return counts


def format_delta(current: int, previous: int | None) -> str:
    """Format the delta between current and previous line counts."""
    if previous is None:
        return "—"
    diff = current - previous
    if diff > 0:
        return f"+{diff}"
    elif diff < 0:
        return str(diff)
    return "0"


def verify(current_dir: Path, previous_dir: Path | None = None) -> None:
    """Count and compare line counts."""
    current = count_lines(current_dir)
    previous = count_lines(previous_dir) if previous_dir else None

    # Collect all file keys
    all_keys = list(current.keys())
    if previous:
        for k in previous:
            if k not in all_keys:
                all_keys.append(k)

    # Print table
    has_prev = previous is not None
    if has_prev:
        header = f"  {'File':<35} {'Previous':>8} {'Current':>8} {'Delta':>6}"
        sep = f"  {'─' * 35} {'─' * 8} {'─' * 8} {'─' * 6}"
    else:
        header = f"  {'File':<35} {'Lines':>6}"
        sep = f"  {'─' * 35} {'─' * 6}"

    print(header)
    print(sep)

    for key in all_keys:
        cur = current.get(key, 0)

        if has_prev:
            prev = previous.get(key) if previous else None
            prev_str = str(prev) if prev is not None else "—"
            delta = format_delta(cur, prev)
            print(f"  {key:<35} {prev_str:>8} {cur:>8} {delta:>6}")
        else:
            print(f"  {key:<35} {cur:>6}")

    # Summary
    if has_prev:
        total_cur = current.get("Total", 0)
        total_prev = previous.get("Total", 0) if previous else 0
        delta_total = total_cur - total_prev
        sign = "+" if delta_total > 0 else ""
        print(f"\n  Net change: {sign}{delta_total} lines ({total_prev} → {total_cur})")


def main():
    parser = argparse.ArgumentParser(
        description="Verify line counts in target_skill/ directory."
    )
    parser.add_argument(
        "--current",
        type=Path,
        required=True,
        help="Path to current skill directory (e.g., target_skill)",
    )
    parser.add_argument(
        "--previous",
        type=Path,
        default=None,
        help="Path to previous skill state (for delta comparison)",
    )

    args = parser.parse_args()

    if not args.current.exists():
        print(f"Error: Current directory {args.current} does not exist.")
        sys.exit(1)

    if args.previous and not args.previous.exists():
        print(f"Error: Previous directory {args.previous} does not exist.")
        sys.exit(1)

    verify(args.current.resolve(), args.previous.resolve() if args.previous else None)


if __name__ == "__main__":
    main()
