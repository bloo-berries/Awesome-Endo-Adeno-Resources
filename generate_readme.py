#!/usr/bin/env python3
"""
Generate README.md from data/resources.json.

Renders the structured resource data back into the hand-editable README
format. The output should be identical to the original README.md.

Usage:
    python3 generate_readme.py                      # Write to README.md
    python3 generate_readme.py --output=other.md    # Write to another file
    python3 generate_readme.py --output=/dev/stdout  # Print to stdout
    python3 generate_readme.py --validate            # Check schema integrity

Stdlib only - no pip dependencies.
"""

import argparse
import json
import os
import sys


def load_data(path="data/resources.json"):
    """Load the resources JSON file."""
    if not os.path.isfile(path):
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_data(data):
    """Validate schema integrity and check for duplicate URLs."""
    errors = []

    if "_meta" not in data:
        errors.append("Missing _meta field")
    if "header" not in data:
        errors.append("Missing header field")
    if "toc" not in data:
        errors.append("Missing toc field")
    if "sections" not in data:
        errors.append("Missing sections field")

    # Check for duplicate URLs across all entries
    seen_urls = {}
    for section in data.get("sections", []):
        if section.get("type") == "raw":
            continue
        for entry in iter_all_entries(section):
            url = entry.get("url", "")
            if url in seen_urls:
                errors.append(
                    f"Duplicate URL: {url} (in '{section['title']}' "
                    f"and '{seen_urls[url]}')"
                )
            else:
                seen_urls[url] = section["title"]

    # Check section IDs match TOC references
    section_ids = {s["id"] for s in data.get("sections", [])}
    for cat in data.get("toc", {}).get("categories", []):
        for sid in cat.get("section_ids", []):
            if sid not in section_ids:
                errors.append(f"TOC references non-existent section: {sid}")

    return errors


def iter_all_entries(section):
    """Iterate over all entries in a section (including groups and subsections)."""
    for entry in section.get("entries", []):
        yield entry
    for entry in section.get("top_entries", []):
        yield entry
    for group in section.get("groups", []):
        for entry in group.get("entries", []):
            yield entry
    for sub in section.get("subsections", []):
        for entry in sub.get("entries", []):
            yield entry
        for group in sub.get("groups", []):
            for entry in group.get("entries", []):
                yield entry


def render_entry(entry, indent=0):
    """Render a single entry as markdown lines."""
    prefix = " " * indent
    lines = []
    suffix = entry.get("suffix", "")
    suffix_part = f" {suffix}" if suffix else ""
    lines.append(f"{prefix}- [{entry['title']}]({entry['url']}){suffix_part}")
    if entry.get("description"):
        for desc_line in entry["description"].split("\n"):
            lines.append(f"{prefix}  - {desc_line}")
    return lines


def render_group_entries(group, style="list", indent=0):
    """Render a group (label + entries) as markdown lines."""
    lines = []
    if style == "list":
        lines.append(f"- {group['label']}")
        for entry in group.get("entries", []):
            lines.extend(render_entry(entry, indent=2))
    elif style == "text":
        lines.append(group["label"])
        lines.append("")
        for entry in group.get("entries", []):
            lines.extend(render_entry(entry, indent=0))
    return lines


def render_subsection(sub):
    """Render a subsection (### heading + entries/groups)."""
    lines = []
    lines.append(f"### {sub['title']}")

    if sub.get("groups"):
        style = sub.get("group_style", "list")
        if style == "list":
            lines.append("")
        for i, group in enumerate(sub["groups"]):
            rendered = render_group_entries(group, style=style)
            lines.extend(rendered)
    else:
        lines.append("")
        for entry in sub.get("entries", []):
            lines.extend(render_entry(entry))

    return lines


def render_section(section):
    """Render a complete section as markdown lines."""
    lines = []
    lines.append(f"## {section['title']}")

    if section["type"] == "raw":
        # Raw content already includes its own leading blank line
        lines.append(section["content"])
        return lines

    lines.append("")

    has_details = "details_summary" in section
    if has_details:
        lines.append("<details>")
        lines.append(f"  <summary>{section['details_summary']}</summary>")
        lines.append("")

    # Render main entries
    if section["type"] == "entries":
        for entry in section.get("entries", []):
            lines.extend(render_entry(entry))
    elif section["type"] == "grouped":
        style = section.get("group_style", "list")
        for i, group in enumerate(section["groups"]):
            rendered = render_group_entries(group, style=style)
            lines.extend(rendered)
            if style == "text" and i < len(section["groups"]) - 1:
                lines.append("")

        # Top-level entries (after groups)
        if section.get("top_entries"):
            for entry in section["top_entries"]:
                lines.extend(render_entry(entry))

    # Render subsections
    if section.get("subsections"):
        has_main = bool(section.get("entries") or section.get("groups"))
        for i, sub in enumerate(section["subsections"]):
            # Don't add blank line before first subsection if preceded
            # by details summary (which already added one)
            if i > 0 or has_main:
                lines.append("")
            lines.extend(render_subsection(sub))

    if has_details:
        lines.append("")
        lines.append("</details>")

    return lines


def render_toc(toc, sections):
    """Render the Table of Contents."""
    lines = []
    lines.append("## Contents")
    lines.append("")

    if toc.get("preamble"):
        lines.append(toc["preamble"])
        lines.append("")

    # Build section title lookup for TOC entries
    section_map = {}
    for s in sections:
        section_map[s["id"]] = s["title"]

    counter = 1
    for cat in toc["categories"]:
        if cat["label"]:
            lines.append(f"**{cat['label']}**")
            lines.append("")

        for sid in cat["section_ids"]:
            title = section_map.get(sid, sid)
            lines.append(f"{counter}. [{title}](#{sid})")
            counter += 1

        lines.append("")

    if toc.get("postscript"):
        lines.append(toc["postscript"])

    return lines


def generate(data):
    """Generate complete README markdown from data."""
    lines = []

    # Header
    lines.append(data["header"]["raw"])
    lines.append("")

    # TOC
    lines.extend(render_toc(data["toc"], data["sections"]))
    lines.append("")

    # Sections
    for section in data["sections"]:
        lines.extend(render_section(section))
        lines.append("")

    # Close main tag
    lines.append("</main>")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate README.md from data/resources.json"
    )
    parser.add_argument(
        "--data", default="data/resources.json",
        help="Input JSON file (default: data/resources.json)"
    )
    parser.add_argument(
        "--output", default="README.md",
        help="Output file (default: README.md)"
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Validate data integrity and exit"
    )
    args = parser.parse_args()

    data = load_data(args.data)

    if args.validate:
        errors = validate_data(data)
        if errors:
            print(f"Validation failed with {len(errors)} error(s):")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
        else:
            total = sum(1 for s in data["sections"]
                        for _ in iter_all_entries(s))
            print(f"Validation passed: {len(data['sections'])} sections, "
                  f"{total} entries, no issues")
            sys.exit(0)

    output = generate(data)

    if args.output == "/dev/stdout":
        sys.stdout.write(output)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
