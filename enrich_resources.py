#!/usr/bin/env python3
"""
Fetch OG metadata for resource entries in data/resources.json.

For each entry URL where og_title is null, fetches the page and extracts
Open Graph metadata (og:title, og:description) plus fallback <title> and
<meta name="description">.

Usage:
    python3 enrich_resources.py                  # Enrich entries missing OG data
    python3 enrich_resources.py --force          # Re-fetch all entries
    python3 enrich_resources.py --section=ID     # Only enrich one section
    python3 enrich_resources.py --workers=5      # Limit concurrency
    python3 enrich_resources.py --dry-run        # Show what would be fetched

Stdlib only - no pip dependencies.
"""

import argparse
import html
import http.client
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

MAX_READ_BYTES = 65536  # Read first 64KB only


def extract_meta(content):
    """Extract OG metadata from HTML content.

    Returns dict with og_title, og_description (may be None).
    Tries in order: og:title > <title>, og:description > meta description.
    """
    result = {"og_title": None, "og_description": None}

    # og:title - handle both attribute orders
    m = re.search(
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
        content, re.IGNORECASE
    )
    if not m:
        m = re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']',
            content, re.IGNORECASE
        )
    if m:
        result["og_title"] = html.unescape(m.group(1)).strip()

    # Fallback: <title>
    if not result["og_title"]:
        m = re.search(r"<title[^>]*>([^<]+)</title>", content, re.IGNORECASE)
        if m:
            result["og_title"] = html.unescape(m.group(1)).strip()

    # og:description
    m = re.search(
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
        content, re.IGNORECASE
    )
    if not m:
        m = re.search(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description["\']',
            content, re.IGNORECASE
        )
    if m:
        result["og_description"] = html.unescape(m.group(1)).strip()

    # Fallback: meta description
    if not result["og_description"]:
        m = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            content, re.IGNORECASE
        )
        if not m:
            m = re.search(
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']',
                content, re.IGNORECASE
            )
        if m:
            result["og_description"] = html.unescape(m.group(1)).strip()

    return result


def fetch_metadata(url, timeout=15):
    """Fetch OG metadata from a URL.

    Returns (url, metadata_dict, error_or_None).
    """
    if url.startswith("mailto:") or url.startswith("#"):
        return url, {}, "skipped"

    headers = {"User-Agent": USER_AGENT}
    ctx = ssl.create_default_context()

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            content = resp.read(MAX_READ_BYTES).decode("utf-8", errors="replace")
            meta = extract_meta(content)
            return url, meta, None
    except urllib.error.HTTPError as e:
        return url, {}, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        reason = str(e.reason) if hasattr(e, "reason") else str(e)
        return url, {}, reason
    except (TimeoutError, http.client.RemoteDisconnected):
        return url, {}, "Timeout"
    except Exception as e:
        return url, {}, str(e)


def iter_entries(data, section_id=None):
    """Iterate (section_id, entry) pairs across all structured sections."""
    for section in data.get("sections", []):
        if section.get("type") == "raw":
            continue
        if section_id and section["id"] != section_id:
            continue

        sid = section["id"]
        for entry in section.get("entries", []):
            yield sid, entry
        for entry in section.get("top_entries", []):
            yield sid, entry
        for group in section.get("groups", []):
            for entry in group.get("entries", []):
                yield sid, entry
        for sub in section.get("subsections", []):
            for entry in sub.get("entries", []):
                yield sid, entry
            for group in sub.get("groups", []):
                for entry in group.get("entries", []):
                    yield sid, entry


def main():
    parser = argparse.ArgumentParser(
        description="Fetch OG metadata for resource entries"
    )
    parser.add_argument(
        "--data", default="data/resources.json",
        help="Resources JSON file (default: data/resources.json)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-fetch all entries, even those with existing OG data"
    )
    parser.add_argument(
        "--section", default=None,
        help="Only enrich entries in this section ID"
    )
    parser.add_argument(
        "--workers", type=int, default=10,
        help="Max concurrent requests (default: 10)"
    )
    parser.add_argument(
        "--timeout", type=int, default=15,
        help="Request timeout in seconds (default: 15)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show URLs that would be fetched without fetching"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.data):
        print(f"Error: {args.data} not found", file=sys.stderr)
        sys.exit(1)

    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Collect entries to enrich
    to_fetch = []
    for sid, entry in iter_entries(data, section_id=args.section):
        url = entry.get("url", "")
        if url.startswith("mailto:") or url.startswith("#"):
            continue
        if not args.force and entry.get("og_title") is not None:
            continue
        to_fetch.append((sid, entry))

    if not to_fetch:
        print("No entries to enrich")
        return

    if args.dry_run:
        print(f"Would fetch {len(to_fetch)} URLs:")
        for sid, entry in to_fetch:
            print(f"  [{sid}] {entry['url']}")
        return

    print(f"Enriching {len(to_fetch)} entries with {args.workers} workers...")

    # Build URL-to-entries mapping (same URL may appear in multiple sections)
    url_entries = {}
    for sid, entry in to_fetch:
        url = entry["url"]
        if url not in url_entries:
            url_entries[url] = []
        url_entries[url].append(entry)

    enriched = 0
    errors = 0
    today = str(date.today())

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(fetch_metadata, url, args.timeout): url
            for url in url_entries
        }
        for future in as_completed(futures):
            url, meta, error = future.result()
            for entry in url_entries[url]:
                entry["last_verified"] = today
                if error:
                    errors += 1
                    print(f"  ERROR {url}: {error}")
                else:
                    if meta.get("og_title"):
                        entry["og_title"] = meta["og_title"]
                    if meta.get("og_description"):
                        entry["og_description"] = meta["og_description"]
                    enriched += 1

    # Write back
    with open(args.data, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nDone: {enriched} enriched, {errors} errors")


if __name__ == "__main__":
    main()
