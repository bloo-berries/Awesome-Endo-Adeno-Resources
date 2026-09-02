#!/usr/bin/env python3
"""
Link checker for README.md - validates all URLs are reachable.

Usage:
    python3 check_links.py                  # Check all links
    python3 check_links.py --timeout=15     # Custom timeout (seconds)
    python3 check_links.py --workers=5      # Limit concurrency
    python3 check_links.py --retry=2        # Retry transient failures
    python3 check_links.py --json           # Output JSON report
    python3 check_links.py --skip-ok        # Only show problems

Stdlib only - no pip dependencies. Exit code = number of genuinely broken links
(0 = all OK). Known bot-blocking domains (403s from WAFs) are reported separately.
"""

import argparse
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


# Domains that block automated requests or require auth
SKIP_DOMAINS = frozenset([
    "localhost",
    "127.0.0.1",
])

# Domains/suffixes known to block automated HTTP checkers via Cloudflare,
# Akamai, WAFs, or TLS fingerprinting. A 403 from these is expected and
# does not indicate a genuinely broken link.
BOT_BLOCK_DOMAINS = frozenset([
    # Academic publishers
    "sciencedirect.com",
    "pubmed.ncbi.nlm.nih.gov",
    "tandfonline.com",
    "academic.oup.com",
    "mdpi.com",
    "jamanetwork.com",
    "cell.com",
    "thelancet.com",
    "wiley.com",
    "sagepub.com",
    "lww.com",
    "fertstert.org",
    "biorxiv.org",
    "researchgate.net",
    "journals.biologists.com",
    "science.org",
    "jogc.com",
    "ejog.org",
    "whijournal.com",
    "springer.com",
    "nature.com",
    # Social media
    "reddit.com",
    "facebook.com",
    "substack.com",
    # Government / institutional
    "clinicaltrials.gov",
    "congress.gov",
    "nice.org.uk",
])

# User-Agent to avoid bot blocks
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Additional browser-like headers to help with simpler bot detection
BROWSER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

# Regex for markdown links: [text](url) and bare URLs
MD_LINK_RE = re.compile(
    r"\[(?P<text>[^\]]*)\]\((?P<url>https?://[^\s\)]+)\)"
)
BARE_URL_RE = re.compile(
    r"(?<!\()(?<!\[)(?<!\")(?:https?://[^\s\)\]\">]+)"
)


def extract_links(filepath):
    """Extract all HTTP(S) URLs from a markdown file with line numbers.

    Returns list of (url, line_number, link_text_or_None) tuples.
    Deduplicates by URL, keeping the first occurrence.
    """
    seen = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            for m in MD_LINK_RE.finditer(line):
                url = m.group("url").rstrip(".,;:!?")
                if url not in seen:
                    seen[url] = (url, lineno, m.group("text"))
            for m in BARE_URL_RE.finditer(line):
                url = m.group(0).rstrip(".,;:!?")
                if url not in seen:
                    seen[url] = (url, lineno, None)
    return list(seen.values())


def should_skip(url):
    """Check if a URL should be skipped."""
    parsed = urllib.parse.urlparse(url)
    return parsed.hostname in SKIP_DOMAINS


def is_bot_blocked_domain(url):
    """Check if the URL's domain matches a known bot-blocking domain."""
    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()
    for domain in BOT_BLOCK_DOMAINS:
        if hostname == domain or hostname.endswith("." + domain):
            return True
    return False


def check_url(url, timeout=10, retries=1):
    """Check a single URL. Returns (url, status, error_or_None, final_url).

    Tries HEAD first, falls back to GET if HEAD returns 405/403.
    Retries on transient network errors.
    """
    if should_skip(url):
        return url, 0, "skipped", url

    headers = dict(BROWSER_HEADERS)
    ctx = ssl.create_default_context()
    bot_blocked = is_bot_blocked_domain(url)

    for attempt in range(1 + retries):
        try:
            req = urllib.request.Request(url, headers=headers, method="HEAD")
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                status = resp.status
                final = resp.url
                if 200 <= status < 400:
                    return url, status, None, final
                if status in (405, 403):
                    # HEAD not allowed, try GET
                    req2 = urllib.request.Request(url, headers=headers, method="GET")
                    with urllib.request.urlopen(req2, timeout=timeout, context=ctx) as resp2:
                        return url, resp2.status, None, resp2.url
                return url, status, f"HTTP {status}", final
        except urllib.error.HTTPError as e:
            if e.code in (405, 403) and attempt == 0:
                # Try GET fallback
                try:
                    req2 = urllib.request.Request(url, headers=headers, method="GET")
                    with urllib.request.urlopen(req2, timeout=timeout, context=ctx) as resp2:
                        return url, resp2.status, None, resp2.url
                except urllib.error.HTTPError as e2:
                    if e2.code == 403 and bot_blocked:
                        return url, 403, "bot_blocked", url
                    if attempt < retries:
                        time.sleep(1)
                        continue
                    return url, e2.code, f"HTTP {e2.code}", url
                except Exception as e2:
                    if attempt < retries:
                        time.sleep(1)
                        continue
                    return url, None, str(e2), url
            if e.code == 403 and bot_blocked:
                return url, 403, "bot_blocked", url
            if attempt < retries:
                time.sleep(1)
                continue
            return url, e.code, f"HTTP {e.code}", url
        except urllib.error.URLError as e:
            if attempt < retries:
                time.sleep(1)
                continue
            reason = str(e.reason) if hasattr(e, "reason") else str(e)
            return url, None, reason, url
        except (TimeoutError, http.client.RemoteDisconnected) as e:
            if attempt < retries:
                time.sleep(1)
                continue
            return url, None, "Timeout", url
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
                continue
            return url, None, str(e), url

    return url, None, "Max retries exceeded", url


def main():
    parser = argparse.ArgumentParser(description="Check links in README.md")
    parser.add_argument(
        "file", nargs="?", default="README.md", help="Markdown file to check"
    )
    parser.add_argument(
        "--timeout", type=int, default=10, help="Request timeout in seconds"
    )
    parser.add_argument(
        "--workers", type=int, default=10, help="Max concurrent requests"
    )
    parser.add_argument(
        "--retry", type=int, default=1, help="Number of retries for failures"
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output", help="Output JSON report"
    )
    parser.add_argument(
        "--skip-ok", action="store_true", help="Only print warnings and errors"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: {args.file} not found", file=sys.stderr)
        sys.exit(1)

    links = extract_links(args.file)
    total = len(links)

    if not args.json_output:
        print(f"Checking {total} unique links in {args.file}...")
        print()

    results = {"ok": [], "broken": [], "bot_blocked": [], "skipped": [],
                "redirect": []}
    url_to_line = {url: (lineno, text) for url, lineno, text in links}

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(check_url, url, args.timeout, args.retry): url
            for url, _, _ in links
        }
        done = 0
        for future in as_completed(futures):
            url, status, error, final_url = future.result()
            lineno, text = url_to_line[url]
            done += 1

            entry = {
                "url": url,
                "line": lineno,
                "text": text,
                "status": status,
                "error": error,
                "final_url": final_url if final_url != url else None,
            }

            if error == "skipped":
                results["skipped"].append(entry)
            elif error == "bot_blocked":
                results["bot_blocked"].append(entry)
                if not args.json_output and not args.skip_ok:
                    label = f"[{text}]" if text else ""
                    print(f"  BOT403  L{lineno}: {url} {label}")
            elif error:
                results["broken"].append(entry)
                if not args.json_output:
                    label = f"[{text}]" if text else ""
                    print(f"  BROKEN  L{lineno}: {url} {label}")
                    print(f"          {error}")
            elif final_url and final_url != url:
                results["redirect"].append(entry)
                if not args.json_output and not args.skip_ok:
                    print(f"  REDIR   L{lineno}: {url}")
                    print(f"          -> {final_url}")
            else:
                results["ok"].append(entry)
                if not args.json_output and not args.skip_ok:
                    print(f"  OK      L{lineno}: {url}")

    # Sort by line number
    results["broken"].sort(key=lambda e: e["line"])
    results["bot_blocked"].sort(key=lambda e: e["line"])
    results["redirect"].sort(key=lambda e: e["line"])

    if args.json_output:
        report = {
            "file": args.file,
            "total": total,
            "ok": len(results["ok"]),
            "broken": len(results["broken"]),
            "bot_blocked": len(results["bot_blocked"]),
            "redirects": len(results["redirect"]),
            "skipped": len(results["skipped"]),
            "broken_links": results["broken"],
            "bot_blocked_links": results["bot_blocked"],
            "redirected_links": results["redirect"],
        }
        print(json.dumps(report, indent=2))
    else:
        print()
        print(f"{'=' * 50}")
        print(f"  Total:       {total}")
        print(f"  OK:          {len(results['ok'])}")
        print(f"  Broken:      {len(results['broken'])}")
        print(f"  Bot-blocked: {len(results['bot_blocked'])}")
        print(f"  Redirects:   {len(results['redirect'])}")
        print(f"  Skipped:     {len(results['skipped'])}")
        print(f"{'=' * 50}")

        if results["broken"]:
            print()
            print("Broken links:")
            for e in results["broken"]:
                label = f" [{e['text']}]" if e["text"] else ""
                print(f"  L{e['line']}: {e['url']}{label}")
                print(f"         {e['error']}")

        if results["bot_blocked"]:
            print()
            print(f"Bot-blocked links ({len(results['bot_blocked'])} - not counted as broken):")
            for e in results["bot_blocked"]:
                label = f" [{e['text']}]" if e["text"] else ""
                print(f"  L{e['line']}: {e['url']}{label}")

    # Only genuinely broken links count toward exit code
    sys.exit(len(results["broken"]))


if __name__ == "__main__":
    main()
