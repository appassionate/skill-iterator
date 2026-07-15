#!/usr/bin/env python3
"""show_validation.py — Render validation JSON into a self-contained HTML.

Reads structured JSON data and embeds it into the selected HTML template.
Templates (assets/automation.html, generalization.html, benchmark.html)
are located relative to this script.

Usage:
    python show_validation.py --template automation --input automation.json --output automation.html
    python show_validation.py --template generalization --input generalization.json --output generalization.html
    python show_validation.py --template benchmark --input benchmark.json --output benchmark.html
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_TEMPLATES = ("automation", "generalization", "benchmark")


def generate(template_name: str, input_path: Path, output_path: Path) -> None:
    """Read JSON data, embed into HTML template, write output."""
    if template_name not in VALID_TEMPLATES:
        print(f"Error: Invalid template '{template_name}'. Choose from: {', '.join(VALID_TEMPLATES)}")
        sys.exit(1)

    if not input_path.exists():
        print(f"Error: {input_path} does not exist.")
        sys.exit(1)

    data = json.loads(input_path.read_text(encoding="utf-8"))

    if "generated_at" not in data:
        data["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    data_json = json.dumps(data, ensure_ascii=False, indent=2)

    template_path = _find_template(template_name)
    if not template_path:
        print(f"Error: Could not find assets/{template_name}.html. Searched:")
        print(f"  - assets/{template_name}.html (relative to this script)")
        print(f"  - ../assets/{template_name}.html (relative to this script)")
        sys.exit(1)

    template = template_path.read_text(encoding="utf-8")
    html = template.replace("__DATA__", data_json)
    output_path.write_text(html, encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024
    print(f"Generated {output_path} ({size_kb:.1f} KB, data embedded)")


def _find_template(name: str) -> Path | None:
    """Locate assets/{name}.html relative to this script."""
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir.parent / "assets" / f"{name}.html",
        script_dir / "assets" / f"{name}.html",
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Render validation JSON into a self-contained HTML."
    )
    parser.add_argument(
        "--template", type=str, required=True,
        choices=VALID_TEMPLATES,
        help="Validation template name"
    )
    parser.add_argument(
        "--input", type=Path, required=True, help="Path to JSON data file"
    )
    parser.add_argument(
        "--output", type=Path, required=True, help="Output HTML path"
    )
    args = parser.parse_args()
    generate(args.template, args.input.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
