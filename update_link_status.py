#!/usr/bin/env python3
"""
Bridge check_links.py to data/resources.json.

Runs check_links.py --json and updates the status and last_verified fields
on matching entries in resources.json.

Usage:
    python3 update_link_status.py                    # Run check and update
    python3 update_link_status.py --report=report.json  # Use existing report
    python3 update_link_status.py --dry-run          # Show changes without writing

Stdlib only - no pip dependencies.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import date


def iter_all_entries(data):
    """Iterate over all structured entries in the data, yielding each entry."""
    for section in data.get("sections", []):
        if section.get("type") == "raw":
            continue
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


def main():
    parser = argparse.ArgumentParser(
        description="Update link status in resources.json from check_links.py"
    )
    parser.add_argument(
        "--data", default="data/resources.json",
        help="Resources JSON file (default: data/resources.json)"
    )
    parser.add_argument(
        "--report", default=None,
        help="Use existing JSON report instead of running check_links.py"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show changes without writing"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.data):
        print(f"Error: {args.data} not found", file=sys.stderr)
        sys.exit(1)

    # Get link check report
    if args.report:
        if not os.path.isfile(args.report):
            print(f"Error: {args.report} not found", file=sys.stderr)
            sys.exit(1)
        with open(args.report, "r", encoding="utf-8") as f:
            report = json.load(f)
    else:
        print("Running check_links.py --json ...")
        result = subprocess.run(
            [sys.executable, "check_links.py", "--json"],
            capture_output=True, text=True
        )
        if result.returncode != 0 and not result.stdout:
            print(f"check_links.py failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        report = json.loads(result.stdout)

    # Build URL status map from report
    url_status = {}
    for entry in report.get("broken_links", []):
        url_status[entry["url"]] = "broken"
    for entry in report.get("bot_blocked_links", []):
        url_status[entry["url"]] = "bot_blocked"
    for entry in report.get("redirected_links", []):
        url_status[entry["url"]] = "redirect"

    # Load resources data
    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Update entries
    today = str(date.today())
    updated = 0
    broken = 0
    bot_blocked = 0

    for entry in iter_all_entries(data):
        url = entry.get("url", "")
        if url.startswith("mailto:") or url.startswith("#"):
            continue

        new_status = url_status.get(url, "ok")
        old_status = entry.get("status", "ok")

        if new_status != old_status or entry.get("last_verified") != today:
            if args.dry_run:
                if new_status != old_status:
                    print(f"  {old_status} -> {new_status}: {url}")
            entry["status"] = new_status
            entry["last_verified"] = today
            updated += 1
            if new_status == "broken":
                broken += 1
            elif new_status == "bot_blocked":
                bot_blocked += 1

    if args.dry_run:
        print(f"\nWould update {updated} entries "
              f"({broken} broken, {bot_blocked} bot-blocked)")
        return

    # Write back
    with open(args.data, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Updated {updated} entries "
          f"({broken} broken, {bot_blocked} bot-blocked)")
    print(f"Report: {report.get('total', '?')} total, "
          f"{report.get('ok', '?')} ok, "
          f"{report.get('broken', '?')} broken, "
          f"{report.get('bot_blocked', '?')} bot-blocked, "
          f"{report.get('redirects', '?')} redirects")


if __name__ == "__main__":
    main()
