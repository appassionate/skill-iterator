#!/usr/bin/env python3
"""generate_overview.py — Generate overview.html from iteration data.

Scans iter.XXXX directories, collects data_todo.json from each,
reads SKILL.md for metadata, lists scripts and assets, then
generates a self-contained overview.html with embedded data.

Usage:
    python generate_overview.py --workspace iter_skill(skill-iterator) --output overview.html
"""

import argparse
import json
import re
import sys
from pathlib import Path


def find_iterations(workspace: Path) -> list[dict]:
    """Scan workspace for iter.XXXX directories, return sorted list of iteration data."""
    iterations = []
    for d in sorted(workspace.iterdir()):
        if not d.is_dir():
            continue
        m = re.match(r"^iter\.(\d+)$", d.name)
        if not m:
            continue

        json_path = d / "data_todo.json"
        if not json_path.exists():
            continue

        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            data["iteration"] = d.name
            iterations.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not parse {json_path}: {e}")

    return iterations


def parse_skill_md(skill_path: Path) -> dict:
    """Extract name, description, and line count from SKILL.md."""
    info = {"name": "", "description": "", "skill_lines": 0}
    if not skill_path.exists():
        return info

    text = skill_path.read_text(encoding="utf-8")
    info["skill_lines"] = len(text.split("\n"))

    # Extract from YAML frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
        if name_m:
            info["name"] = name_m.group(1).strip()
        desc_m = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        if desc_m:
            info["description"] = desc_m.group(1).strip()

    return info


def build_file_tree(root: Path, max_depth: int = 3) -> str:
    """Build a text-based file tree of the target_skill directory."""
    lines = [root.name + "/"]
    _walk_tree(root, "", lines, max_depth, 0)
    return "\n".join(lines)


def _walk_tree(directory: Path, prefix: str, lines: list, max_depth: int, depth: int) -> None:
    """Recursively walk directory tree and append formatted lines."""
    if depth >= max_depth:
        return
    entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name))
    # Filter out .git and __pycache__
    entries = [e for e in entries if e.name not in (".git", "__pycache__", ".DS_Store")]
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        if entry.is_dir():
            lines.append(f"{prefix}{connector}{entry.name}/")
            extension = "    " if is_last else "│   "
            _walk_tree(entry, prefix + extension, lines, max_depth, depth + 1)
        else:
            lines.append(f"{prefix}{connector}{entry.name}")


def list_scripts(scripts_dir: Path) -> list[dict]:
    """List Python scripts with line counts."""
    scripts = []
    if not scripts_dir.exists():
        return scripts
    for f in sorted(scripts_dir.iterdir()):
        if f.suffix == ".py" and not f.name.startswith("_"):
            lines = len(f.read_text(encoding="utf-8").split("\n"))
            # Extract docstring first line as description
            text = f.read_text(encoding="utf-8")
            desc_m = re.search(r'"""(.+?)(?:\n|$)', text)
            desc = desc_m.group(1).strip() if desc_m else ""
            scripts.append({"name": f.name, "lines": lines, "description": desc})
    return scripts


def list_assets(assets_dir: Path, refs_dir: Path) -> list[dict]:
    """List assets and reference templates with line counts."""
    assets = []
    for d, label in [(assets_dir, "html"), (refs_dir, "md")]:
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if f.is_file():
                lines = len(f.read_text(encoding="utf-8").split("\n"))
                assets.append({
                    "name": f.name,
                    "lines": lines,
                    "type": label,
                })
    return assets


def generate(workspace: Path, output_path: Path) -> None:
    """Generate overview.html from iteration data."""
    target_skill = workspace / "target_skill"

    # Collect data
    iterations = find_iterations(workspace)
    skill_info = parse_skill_md(target_skill / "SKILL.md")
    skill_info["file_tree"] = build_file_tree(target_skill)
    scripts = list_scripts(target_skill / "scripts")
    assets = list_assets(target_skill / "assets", target_skill / "references")

    overview_data = {
        "skill": skill_info,
        "iterations": iterations,
        "scripts": scripts,
        "assets": assets,
    }
    data_json = json.dumps(overview_data, ensure_ascii=False, indent=2)

    # Find template
    template_path = _find_template(workspace)
    if not template_path:
        print("Error: Could not find overview_template.html. Searched:")
        print("  - target_skill/assets/overview_template.html")
        print("  - assets/overview_template.html (relative to script)")
        sys.exit(1)

    template = template_path.read_text(encoding="utf-8")
    html = template.replace("__OVERVIEW_DATA__", data_json)
    output_path.write_text(html, encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024
    print(f"Generated {output_path} ({size_kb:.1f} KB, {len(iterations)} iterations)")


def _find_template(workspace: Path) -> Path | None:
    """Locate overview_template.html."""
    script_dir = Path(__file__).resolve().parent
    candidates = [
        workspace / "target_skill" / "assets" / "overview_template.html",
        script_dir.parent / "assets" / "overview_template.html",
        script_dir / "assets" / "overview_template.html",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate overview.html from iteration data."
    )
    parser.add_argument(
        "--workspace", type=Path, required=True,
        help="Path to iter_skill(name) workspace directory"
    )
    parser.add_argument(
        "--output", type=Path, required=True,
        help="Output HTML path"
    )
    args = parser.parse_args()
    generate(args.workspace.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
