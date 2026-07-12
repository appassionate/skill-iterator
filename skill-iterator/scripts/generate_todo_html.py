#!/usr/bin/env python3
"""generate_todo_html.py — Parse todo.md into data and render todo.html.

Two-file output architecture:
  todo.md          -> parse -> todo.html       (self-contained HTML with embedded data)
                            -> data_todo.json  (structured data for tooling)

Section names (current): start, end, validation-system, validation-user.
Section names (legacy): begin, after — supported for backward compatibility.

Usage:
    python generate_todo_html.py --input todo.md --output todo.html
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_todo_md(text: str) -> dict:
    """Parse todo.md into structured data dict."""
    data = {
        "iteration": "",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "start": {"items": []},
        "end": None,
        "validation_system": None,
        "validation_user": None,
    }

    lines = text.strip().split("\n")

    # Extract iteration name from H1
    for line in lines:
        m = re.match(r"^#\s+Todo:\s*(.+)", line)
        if m:
            data["iteration"] = m.group(1).strip()
            break

    sections = _split_sections(lines)

    # Parse start/begin section (prompt + items)
    for key in ("start", "begin"):
        if key in sections:
            start = _parse_start_section(sections[key])
            data["start"] = start
            break

    # Parse end/after section
    for key in ("end", "after"):
        if key in sections:
            end = _parse_end_section(sections[key])
            if end["items"] or end["walkthrough"] or end["friction"]:
                data["end"] = end
            break

    # Parse validation - system
    for key in ("validation - system", "validation-system"):
        if key in sections:
            items = _parse_val_system_table(sections[key])
            if items:
                data["validation_system"] = {"items": items}
            break

    # Parse validation - user
    for key in ("validation - user", "validation-user"):
        if key in sections:
            items = _parse_val_user_table(sections[key])
            if items is not None:
                data["validation_user"] = {"items": items}
            break

    # Clean up None values
    if data["validation_system"] is None:
        del data["validation_system"]
    if data["validation_user"] is None:
        del data["validation_user"]

    return data


def _split_sections(lines: list[str]) -> dict[str, list[str]]:
    """Split lines into sections by ## headings."""
    sections = {}
    current_section = None
    current_lines = []

    for line in lines:
        m = re.match(r"^##\s+(.+)", line)
        if m:
            if current_section is not None:
                sections[current_section] = current_lines
            current_section = m.group(1).strip().lower()
            current_lines = []
        else:
            if current_section is not None:
                current_lines.append(line)

    if current_section is not None:
        sections[current_section] = current_lines

    return sections


def _parse_start_section(lines: list[str]) -> dict:
    """Parse start/begin section: extract prompt text and items table."""
    start = {"items": []}

    prompt_lines = []
    in_prompt = False
    for line in lines:
        if re.match(r"^\*\*Original Prompt:?\*\*", line.strip()):
            in_prompt = True
            continue
        if in_prompt:
            if line.strip().startswith("|"):
                break
            prompt_lines.append(line)

    if prompt_lines:
        start["prompt"] = "\n".join(prompt_lines).strip()

    start["items"] = _parse_items_table(lines)
    return start


def _parse_end_section(lines: list[str]) -> dict:
    """Parse the end/after section into walkthrough, friction, and items."""
    end = {"walkthrough": "", "friction": [], "items": []}

    subsections = {}
    current_sub = None
    current_lines = []

    for line in lines:
        m = re.match(r"^###\s+(.+)", line)
        if m:
            if current_sub is not None:
                subsections[current_sub] = current_lines
            current_sub = m.group(1).strip().lower()
            current_lines = []
        else:
            if current_sub is not None:
                current_lines.append(line)

    if current_sub is not None:
        subsections[current_sub] = current_lines

    if "walkthrough summary" in subsections:
        end["walkthrough"] = "\n".join(
            l for l in subsections["walkthrough summary"] if l.strip()
        ).strip()

    if "friction and resolution" in subsections:
        end["friction"] = _parse_friction_table(subsections["friction and resolution"])

    if "items" in subsections:
        end["items"] = _parse_items_table(subsections["items"])
    else:
        items = []
        for key in ("review", "validation generated"):
            if key in subsections:
                items.extend(_parse_items_table(subsections[key]))
        end["items"] = items

    return end


def _normalize_source(raw: str) -> str:
    """Normalize source label: 'validation' -> 'system'."""
    raw = raw.strip().lower()
    if raw == "validation":
        return "system"
    return raw


def _strip_id_prefix(raw_id: str) -> str:
    """Strip letter prefixes (V1->1, U1->1) from IDs."""
    stripped = re.sub(r"^[A-Za-z]+", "", raw_id.strip())
    return stripped if stripped else raw_id.strip()


def _detect_headers(row: list[str]) -> tuple[bool, bool]:
    """Detect Status and Priority columns from header row."""
    headers = [c.strip().lower() for c in row]
    return "status" in headers, "priority" in headers


def _parse_items_table(lines: list[str]) -> list[dict]:
    """Parse items table. Supports multiple formats via header detection.

    Possible columns: #, Source, [Priority], [Status], Content
    """
    rows = _extract_table_rows(lines)
    items = []

    has_status, has_priority = False, False
    for row in rows:
        if all(re.match(r"^[-:]+$", c.strip()) for c in row):
            continue
        has_status, has_priority = _detect_headers(row)
        break

    for i, row in enumerate(rows):
        if i == 0:
            continue
        if all(re.match(r"^[-:]+$", c.strip()) for c in row):
            continue

        # Build column index map based on detected headers
        cols = [c.strip() for c in row]
        if len(cols) < 3:
            continue

        item = {"id": _strip_id_prefix(cols[0])}
        idx = 1

        # Source column (always present in items tables)
        if idx < len(cols):
            item["source"] = _normalize_source(cols[idx])
            idx += 1

        # Optional Priority column
        if has_priority and idx < len(cols):
            item["priority"] = cols[idx]
            idx += 1

        # Optional Status column
        if has_status and idx < len(cols):
            item["status"] = cols[idx]
            idx += 1

        # Content column (always last)
        if idx < len(cols):
            item["content"] = cols[idx]
        else:
            continue

        items.append(item)
    return items


def _parse_val_system_table(lines: list[str]) -> list[dict]:
    """Parse validation-system table.
    New format (4-col): #, Source, Priority, Content
    Old format (5-col): #, Source, Status, Priority, Content
    """
    rows = _extract_table_rows(lines)
    items = []

    has_status = False
    for row in rows:
        if all(re.match(r"^[-:]+$", c.strip()) for c in row):
            continue
        has_status, _ = _detect_headers(row)
        break

    for i, row in enumerate(rows):
        if i == 0:
            continue
        if all(re.match(r"^[-:]+$", c.strip()) for c in row):
            continue

        cols = [c.strip() for c in row]
        if has_status and len(cols) >= 5:
            items.append({
                "id": _strip_id_prefix(cols[0]),
                "source": _normalize_source(cols[1]),
                "priority": cols[3],
                "content": cols[4],
            })
        elif not has_status and len(cols) >= 4:
            items.append({
                "id": _strip_id_prefix(cols[0]),
                "source": _normalize_source(cols[1]),
                "priority": cols[2],
                "content": cols[3],
            })
    return items


def _parse_val_user_table(lines: list[str]) -> list[dict]:
    """Parse validation-user table.
    New format (3-col): #, Priority, Content
    Old format (2-col): #, Content
    Old format (3-col): #, Status, Content
    """
    rows = _extract_table_rows(lines)
    items = []

    has_status, has_priority = False, False
    for row in rows:
        if len(row) < 2:
            continue
        if all(re.match(r"^[-:]+$", c.strip()) for c in row):
            continue
        has_status, has_priority = _detect_headers(row)
        break

    for i, row in enumerate(rows):
        if i == 0:
            continue
        if all(re.match(r"^[-:]+$", c.strip()) for c in row):
            continue

        cols = [c.strip() for c in row]

        if has_priority and len(cols) >= 3:
            items.append({
                "id": _strip_id_prefix(cols[0]),
                "priority": cols[1],
                "content": cols[2],
            })
        elif has_status and len(cols) >= 3:
            items.append({
                "id": _strip_id_prefix(cols[0]),
                "content": cols[2],
            })
        elif len(cols) >= 2:
            items.append({
                "id": _strip_id_prefix(cols[0]),
                "content": cols[1],
            })
    return items


def _parse_friction_table(lines: list[str]) -> list[dict]:
    """Parse friction table: # Rawdata Item Difficulty Root Cause Resolution."""
    rows = _extract_table_rows(lines)
    friction = []
    for i, row in enumerate(rows):
        if len(row) < 5:
            continue
        if i == 0:
            continue
        if all(re.match(r"^[-:]+$", c.strip()) for c in row):
            continue
        if all(c.strip() in ("\u2014", "-", "\u2013", "") for c in row[1:]):
            continue
        friction.append({
            "item": row[1].strip(),
            "difficulty": row[2].strip(),
            "root_cause": row[3].strip(),
            "resolution": row[4].strip(),
        })
    return friction


def _extract_table_rows(lines: list[str]) -> list[list[str]]:
    """Extract all table rows (as lists of cell strings) from markdown lines."""
    rows = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and "|" in stripped[1:]:
            cells = [c for c in stripped.split("|")[1:-1]]
            rows.append(cells)
    return rows


def generate(input_path: Path, output_path: Path) -> None:
    """Parse todo.md, embed data into HTML, and write data_todo.json."""
    if not input_path.exists():
        print(f"Error: {input_path} does not exist.")
        sys.exit(1)

    md_text = input_path.read_text(encoding="utf-8")
    data = parse_todo_md(md_text)
    data_json = json.dumps(data, ensure_ascii=False, indent=2)

    # Write data_todo.json
    json_path = output_path.parent / "data_todo.json"
    json_path.write_text(data_json, encoding="utf-8")
    print(f"Generated {json_path} ({json_path.stat().st_size} bytes)")

    # Load HTML template
    template_path = _find_template(input_path)
    if not template_path:
        print("Error: Could not find todo_template.html. Searched:")
        print("  - assets/todo_template.html (relative to this script)")
        print("  - ../assets/todo_template.html (relative to this script)")
        sys.exit(1)

    template = template_path.read_text(encoding="utf-8")

    # Embed data into HTML
    html = template.replace("__TODO_DATA__", data_json)
    output_path.write_text(html, encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024
    print(f"Generated {output_path} ({size_kb:.1f} KB, data embedded)")


def _find_template(input_path: Path) -> Path | None:
    """Locate todo_template.html, searching relative to the script and input."""
    script_dir = Path(__file__).resolve().parent

    candidates = [
        script_dir / "assets" / "todo_template.html",
        script_dir.parent / "assets" / "todo_template.html",
        input_path.parent / "assets" / "todo_template.html",
    ]

    for path in candidates:
        if path.exists():
            return path
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Parse todo.md into data_todo.json and render todo.html."
    )
    parser.add_argument("--input", type=Path, required=True, help="Path to todo.md")
    parser.add_argument("--output", type=Path, required=True, help="Output HTML path")
    args = parser.parse_args()
    generate(args.input.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
