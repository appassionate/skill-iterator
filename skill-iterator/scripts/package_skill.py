#!/usr/bin/env python3
"""package_skill.py — Package target_skill/ as a distributable zip archive.

Creates a zip snapshot of the target skill directory, excluding .git/.
The zip always uses the same filename, overwriting the previous iteration.

Usage:
    python package_skill.py --target target_skill/ --output skill-iterator.zip
    python package_skill.py --target /path/to/target_skill --output my-skill.zip
    python package_skill.py --target target_skill/   # auto-names from directory
"""

import argparse
import sys
import zipfile
from pathlib import Path


def package(target_dir: Path, output_zip: Path) -> None:
    """Create a zip archive of target_dir, excluding .git/ directory."""
    if not target_dir.exists():
        print(f"Error: Target directory {target_dir} does not exist.")
        sys.exit(1)

    if not (target_dir / "SKILL.md").exists():
        print(f"Warning: No SKILL.md found in {target_dir}")

    # Collect files, excluding .git/
    files = []
    for f in sorted(target_dir.rglob("*")):
        if f.is_file() and ".git" not in f.parts:
            files.append(f)

    if not files:
        print("Error: No files found to package.")
        sys.exit(1)

    # Create zip
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            arcname = f"{target_dir.name}/{f.relative_to(target_dir)}"
            zf.write(f, arcname)

    size_kb = output_zip.stat().st_size / 1024
    print(f"Packaged {len(files)} files → {output_zip} ({size_kb:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(
        description="Package target_skill/ as a distributable zip archive."
    )
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Path to the target skill directory (e.g., target_skill/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output zip file path (default: {target_dir_name}.zip in CWD)",
    )

    args = parser.parse_args()

    target = args.target.resolve()
    if args.output:
        output = args.output.resolve()
    else:
        output = Path.cwd() / f"{target.name}.zip"

    package(target, output)


if __name__ == "__main__":
    main()
