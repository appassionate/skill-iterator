#!/usr/bin/env python3
"""show_train.py — Render train.json into a self-contained train.html.

Reads training data (friction entries + execution summary) and embeds it
into the HTML template. The HTML template (assets/train.html) is located
relative to this script.

Usage:
    python show_train.py --input train.json --output train.html
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def generate(input_path: Path, output_path: Path) -> None:
    """Read train.json, embed into HTML template, write train.html."""
    if not input_path.exists():
        print(f"Error: {input_path} does not exist.")
        sys.exit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))

    # Ensure generated_at timestamp
    if "generated_at" not in data:
        data["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    data_json = json.dumps(data, ensure_ascii=False, indent=2)

    # Load HTML template
    template_path = _find_template()
    if not template_path:
        print("Error: Could not find assets/train.html. Searched:")
        print("  - assets/train.html (relative to this script)")
        print("  - ../assets/train.html (relative to this script)")
        sys.exit(1)

    template = template_path.read_text(encoding="utf-8")

    # Embed data into HTML
    html = template.replace("__TRAIN_DATA__", data_json)
    output_path.write_text(html, encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024
    print(f"Generated {output_path} ({size_kb:.1f} KB, data embedded)")


def _find_template() -> Path | None:
    """Locate assets/train.html relative to this script."""
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir.parent / "assets" / "train.html",
        script_dir / "assets" / "train.html",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Render train.json into a self-contained train.html."
    )
    parser.add_argument(
        "--input", type=Path, required=True, help="Path to train.json"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="Output HTML path"
    )
    args = parser.parse_args()
    generate(args.input.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
