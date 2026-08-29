#!/usr/bin/env python3
"""
One-time bootstrap: parse README.md into data/resources.json.

Reads the current hand-edited README and produces a structured JSON file
that serves as the new source of truth for resource data.

Usage:
    python3 parse_readme.py                     # Parse README.md -> data/resources.json
    python3 parse_readme.py --input=OTHER.md    # Parse a different file
    python3 parse_readme.py --output=out.json   # Write to a different path

Stdlib only - no pip dependencies.
"""

import argparse
import json
import os
import re
import sys
from datetime import date


# Sections stored as raw markdown (complex internal structure with tables,
# nested details, mixed content that doesn't fit entry/group patterns)
RAW_SECTION_IDS = frozenset([
    "diagnosis",
    "therapeutic-treatments",
    "potential-co-morbidities",
    # Medical Research has multiple nested <details> blocks, ####-level
    # subsections, and a ### heading inside a <details> block - too complex
    # for structured parsing while maintaining round-trip fidelity
    "medical-research",
])


def slugify(title):
    """Convert a section title to a URL-friendly slug matching GitHub anchors."""
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def make_entry(title, url, description="", suffix=""):
    """Create a standard entry dict."""
    entry = {
        "title": title,
        "url": url,
        "description": description,
        "added": str(date.today()),
        "last_verified": None,
        "status": "ok",
        "tags": [],
        "og_title": None,
        "og_description": None,
    }
    if suffix:
        entry["suffix"] = suffix
    return entry


def parse_link_url(raw_url_part):
    """Extract URL from a markdown link, handling parentheses inside URLs.

    Given text starting after `](`, returns (url, remaining_text).
    Handles balanced parentheses like `https://example.com/path(123)/page`.
    """
    depth = 1  # We start after the opening `(`
    i = 0
    while i < len(raw_url_part) and depth > 0:
        ch = raw_url_part[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        elif ch in (" ", "\t", "\n"):
            break
        i += 1
    return raw_url_part[:i], raw_url_part[i + 1:] if i < len(raw_url_part) else ""


def split_readme(text):
    """Split README into header, TOC block, and section blocks.

    Returns (header_text, toc_text, [(title, body_text), ...])
    """
    lines = text.split("\n")

    # Find ## Contents
    toc_start = None
    for i, line in enumerate(lines):
        if line.strip() == "## Contents":
            toc_start = i
            break

    if toc_start is None:
        print("Error: Could not find '## Contents' in README", file=sys.stderr)
        sys.exit(1)

    header_lines = lines[:toc_start]

    # Find section starts: ## headings NOT inside <details> blocks
    section_starts = []
    details_depth = 0
    for i in range(toc_start + 1, len(lines)):
        line = lines[i]
        # Count opening/closing details tags BEFORE checking for ##
        opens = len(re.findall(r"<details", line))
        closes = len(re.findall(r"</details>", line))

        if line.startswith("## ") and details_depth == 0:
            section_starts.append(i)

        details_depth += opens - closes

    toc_lines = lines[toc_start:section_starts[0]] if section_starts else lines[toc_start:]

    # Extract section blocks
    section_blocks = []
    for idx, start in enumerate(section_starts):
        end = section_starts[idx + 1] if idx + 1 < len(section_starts) else len(lines)
        title = lines[start][3:].strip()
        body = lines[start + 1:end]
        section_blocks.append((title, body))

    return header_lines, toc_lines, section_blocks


def parse_toc(toc_lines):
    """Parse the TOC into structured data."""
    categories = []
    current_category = None

    # Find the index of the last numbered item
    last_numbered_idx = -1
    for i, line in enumerate(toc_lines):
        if re.match(r"^\d+\.\s+\[", line.strip()):
            last_numbered_idx = i

    preamble_parts = []
    postscript_parts = []
    state = "preamble"

    for i, line in enumerate(toc_lines):
        if line.strip() == "## Contents":
            continue

        bold_match = re.match(r"^\*\*(.+?)\*\*$", line.strip())
        numbered_match = re.match(r"^(\d+)\.\s+\[(.+?)\]\(#(.+?)\)", line.strip())

        if state == "preamble":
            if bold_match:
                state = "categories"
                current_category = {
                    "label": bold_match.group(1),
                    "section_ids": [],
                }
                categories.append(current_category)
            elif numbered_match:
                state = "categories"
                current_category = {
                    "label": "",
                    "section_ids": [numbered_match.group(3)],
                }
                categories.append(current_category)
            else:
                preamble_parts.append(line)
        elif state == "categories":
            if bold_match:
                current_category = {
                    "label": bold_match.group(1),
                    "section_ids": [],
                }
                categories.append(current_category)
            elif numbered_match:
                if current_category is not None:
                    current_category["section_ids"].append(numbered_match.group(3))
            elif i > last_numbered_idx and line.strip():
                state = "postscript"
                postscript_parts.append(line)
        elif state == "postscript":
            postscript_parts.append(line)

    return {
        "preamble": "\n".join(preamble_parts).strip(),
        "categories": categories,
        "postscript": "\n".join(postscript_parts).strip(),
    }


def detect_details_wrapper(body_lines):
    """Check if body is wrapped in <details>.

    Returns (summary_text, inner_lines) if wrapped, or (None, body_lines).
    """
    # Strip leading/trailing blank lines for detection
    first_content = -1
    for i, line in enumerate(body_lines):
        if line.strip():
            first_content = i
            break

    if first_content < 0:
        return None, body_lines

    if not body_lines[first_content].strip().startswith("<details"):
        return None, body_lines

    # Find summary
    summary = ""
    summary_end = first_content + 1
    for i in range(first_content + 1, len(body_lines)):
        line = body_lines[i].strip()
        m = re.match(r"<summary>(.*?)</summary>", line)
        if m:
            summary = m.group(1)
            summary_end = i + 1
            break

    # Find matching </details> at the end
    last_content = len(body_lines) - 1
    while last_content >= 0 and not body_lines[last_content].strip():
        last_content -= 1

    # Count details depth to find the matching close
    # The outermost </details> that matches our opening
    depth = 0
    close_idx = None
    for i in range(first_content, len(body_lines)):
        line = body_lines[i]
        depth += len(re.findall(r"<details", line))
        depth -= len(re.findall(r"</details>", line))
        if depth == 0:
            close_idx = i
            break

    if close_idx is None:
        return None, body_lines

    inner = body_lines[summary_end:close_idx]
    return summary, inner


def parse_content_block(lines):
    """Parse a content block (section body or subsection body) into entries.

    Handles:
    - Simple entries: - [Title](URL) / description
    - List-style groups: - GroupLabel / entries indented under it
    - Text-style groups: plain text labels followed by entries

    Returns dict with type, entries/groups, and any formatting metadata.
    """
    entries = []
    groups = []
    current_group = None
    current_entry = None
    group_style = None  # "list" or "text"

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip blank lines
        if not stripped:
            i += 1
            continue

        # Check for entry with URL at various indent levels
        # Use a two-step approach to handle URLs with parentheses
        entry_match = re.match(
            r"^(\s*)-\s+\[(.+?)\]\(",
            line
        )

        if entry_match:
            indent = len(entry_match.group(1))
            title = entry_match.group(2)
            rest = line[entry_match.end():]
            url, after_url = parse_link_url(rest)

            # Only treat as entry if URL is http/https/mailto/anchor
            if not (url.startswith("http") or url.startswith("mailto:") or
                    url.startswith("#")):
                i += 1
                continue

            suffix = after_url.strip()
            entry = make_entry(title, url, suffix=suffix)
            current_entry = entry

            # Assign to group or top-level based on context
            if current_group is not None and (
                (group_style == "text") or  # text groups own all following entries
                (group_style == "list" and indent >= 2)  # list groups own indented entries
            ):
                current_group["entries"].append(entry)
            else:
                # Top-level entry (also resets current group for list-style)
                if group_style == "list" and indent == 0:
                    current_group = None
                entries.append(entry)

            i += 1
            continue

        # Check for description line (indented under previous entry)
        # Pattern: 2+ spaces, dash, text
        desc_match = re.match(r"^(\s{2,})-\s+(.+)$", line)
        if desc_match and current_entry is not None:
            indent = len(desc_match.group(1))
            desc_text = desc_match.group(2).strip()
            # Only treat as description if indent is deeper than entry
            if current_entry["description"]:
                current_entry["description"] += "\n" + desc_text
            else:
                current_entry["description"] = desc_text
            i += 1
            continue

        # Check for list-style group label: - SomeText (no URL)
        list_group_match = re.match(r"^- (.+)$", line)
        if list_group_match and not re.search(r"\[.*?\]\(", line):
            label = list_group_match.group(1).strip()
            group_style = "list"
            current_group = {"label": label, "entries": []}
            groups.append(current_group)
            current_entry = None
            i += 1
            continue

        # Check for text-style group label: plain text not starting with
        # special chars, followed (after blanks) by entries
        if (stripped and
                not stripped.startswith("-") and
                not stripped.startswith("#") and
                not stripped.startswith("<") and
                not stripped.startswith("|") and
                not stripped.startswith("*") and
                not stripped.startswith("[") and
                not re.match(r"^\d+\.", stripped)):
            # Look ahead: is this followed by entries?
            has_entries_ahead = False
            for j in range(i + 1, min(i + 4, len(lines))):
                if re.match(r"^\s*-\s+\[", lines[j]):
                    has_entries_ahead = True
                    break
            if has_entries_ahead:
                group_style = "text"
                current_group = {"label": stripped, "entries": []}
                groups.append(current_group)
                current_entry = None
                i += 1
                continue

        i += 1

    if groups:
        result = {"type": "grouped", "group_style": group_style or "list"}
        result["groups"] = groups
        # Include any top-level entries that weren't under groups
        if entries:
            result["top_entries"] = entries
        return result
    else:
        return {"type": "entries", "entries": entries}


def parse_section_body(title, body_lines):
    """Parse a section body, handling details wrappers and subsections."""
    slug = slugify(title)

    section = {"id": slug, "title": title}

    # Check for raw sections
    if slug in RAW_SECTION_IDS:
        section["type"] = "raw"
        # Trim trailing blank lines
        content = "\n".join(body_lines)
        section["content"] = content.rstrip("\n")
        return section

    # Check for details wrapper
    details_summary, inner_lines = detect_details_wrapper(body_lines)
    if details_summary is not None:
        section["details_summary"] = details_summary

    working_lines = inner_lines if details_summary is not None else body_lines

    # Split into subsections by ### headers
    subsection_blocks = []
    pre_subsection_lines = []
    current_sub_title = None
    current_sub_lines = []

    for line in working_lines:
        sub_match = re.match(r"^###\s+(.+)$", line)
        if sub_match:
            if current_sub_title is not None:
                subsection_blocks.append((current_sub_title, current_sub_lines))
            current_sub_title = sub_match.group(1).strip()
            current_sub_lines = []
        elif current_sub_title is not None:
            current_sub_lines.append(line)
        else:
            pre_subsection_lines.append(line)

    if current_sub_title is not None:
        subsection_blocks.append((current_sub_title, current_sub_lines))

    # Parse content
    if subsection_blocks:
        # Has subsections
        main_content = parse_content_block(pre_subsection_lines)
        section["type"] = main_content.get("type", "entries")

        if main_content["type"] == "entries":
            section["entries"] = main_content.get("entries", [])
        elif main_content["type"] == "grouped":
            section["groups"] = main_content.get("groups", [])
            section["group_style"] = main_content.get("group_style", "list")
            if main_content.get("top_entries"):
                section["top_entries"] = main_content["top_entries"]

        subsections = []
        for sub_title, sub_lines in subsection_blocks:
            sub_content = parse_content_block(sub_lines)
            sub = {"title": sub_title}
            if sub_content["type"] == "grouped":
                sub["groups"] = sub_content.get("groups", [])
                sub["group_style"] = sub_content.get("group_style", "list")
                if sub_content.get("top_entries"):
                    sub["top_entries"] = sub_content["top_entries"]
            else:
                sub["entries"] = sub_content.get("entries", [])
            subsections.append(sub)

        section["subsections"] = subsections
    else:
        # No subsections
        content = parse_content_block(working_lines)
        section["type"] = content.get("type", "entries")

        if content["type"] == "entries":
            section["entries"] = content.get("entries", [])
        elif content["type"] == "grouped":
            section["groups"] = content.get("groups", [])
            section["group_style"] = content.get("group_style", "list")
            if content.get("top_entries"):
                section["top_entries"] = content["top_entries"]

    return section


def parse_readme(text):
    """Parse full README text into structured JSON data."""
    header_lines, toc_lines, section_blocks = split_readme(text)

    header_raw = "\n".join(header_lines).rstrip()
    toc = parse_toc(toc_lines)

    sections = []
    for title, body_lines in section_blocks:
        section = parse_section_body(title, body_lines)
        sections.append(section)

    return {
        "_meta": {
            "version": 1,
            "generated_at": str(date.today()),
        },
        "header": {"raw": header_raw},
        "toc": toc,
        "sections": sections,
    }


def count_entries(section):
    """Count all entries in a section (including subsections and groups)."""
    total = 0
    if section.get("type") == "raw":
        return 0
    for e_list in [section.get("entries", []), section.get("top_entries", [])]:
        total += len(e_list)
    for group in section.get("groups", []):
        total += len(group.get("entries", []))
    for sub in section.get("subsections", []):
        total += len(sub.get("entries", []))
        for group in sub.get("groups", []):
            total += len(group.get("entries", []))
    return total


def main():
    parser = argparse.ArgumentParser(
        description="Parse README.md into data/resources.json"
    )
    parser.add_argument(
        "--input", default="README.md",
        help="Input markdown file (default: README.md)"
    )
    parser.add_argument(
        "--output", default="data/resources.json",
        help="Output JSON file (default: data/resources.json)"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    data = parse_readme(text)

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    total_entries = sum(count_entries(s) for s in data["sections"])
    raw_count = sum(1 for s in data["sections"] if s.get("type") == "raw")
    print(f"Parsed {len(data['sections'])} sections ({raw_count} raw), "
          f"{total_entries} structured entries")
    print(f"Written to {args.output}")


if __name__ == "__main__":
    main()
