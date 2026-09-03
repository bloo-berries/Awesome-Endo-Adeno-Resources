#!/usr/bin/env python3
"""
Translate content pages to target languages using the DeepL API.

Generates translated markdown files in content/translations/{lang}/ that
the existing build pipeline (build.py) automatically picks up.

Usage:
    export DEEPL_API_KEY=your-key-here
    python3 translate_content.py                         # Translate all missing pages
    python3 translate_content.py --lang=es,fr,de         # Specific languages
    python3 translate_content.py --page=diagnosis,about  # Specific pages
    python3 translate_content.py --force                 # Re-translate existing
    python3 translate_content.py --dry-run               # Show work plan + char estimate
    python3 translate_content.py --budget                # Show DeepL usage/remaining chars
    python3 translate_content.py --check-languages       # Show DeepL supported languages
    python3 translate_content.py --workers=3             # Concurrency (default: 3)
    python3 translate_content.py --api=pro               # Use Pro endpoint
    python3 translate_content.py --char-limit=500000     # Hard cap on chars this run

Stdlib only - no pip dependencies.
"""

import argparse
import hashlib
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))

# DeepL language code mapping (site code -> DeepL target code)
DEEPL_LANG_MAP = {
    "es": "ES",
    "fr": "FR",
    "de": "DE",
    "pt": "PT-PT",
    "zh": "ZH-HANS",
    "ar": "AR",
    "hi": "HI",
    "ja": "JA",
    "ko": "KO",
    "ru": "RU",
    "ca": "CA",
    "ga": "GA",
    "it": "IT",  # already human-translated; only used with --force --lang=it
}

# Priority order for budget-constrained runs (it excluded - already human-translated)
LANG_PRIORITY = ["es", "fr", "de", "pt", "ar", "zh", "ja", "ko", "ru", "hi", "ca", "ga"]

FREE_ENDPOINT = "https://api-free.deepl.com"
PRO_ENDPOINT = "https://api.deepl.com"

REQUEST_DELAY = 0.5  # seconds between API calls
CHUNK_THRESHOLD = 30000  # chars before splitting into chunks

CONTENT_DIR = os.path.join(ROOT, "content")
TRANSLATIONS_DIR = os.path.join(CONTENT_DIR, "translations")
TRACKING_FILE = os.path.join(ROOT, "data", "content_translations.json")


# ---------------------------------------------------------------------------
# DeepL API helpers
# ---------------------------------------------------------------------------

def get_endpoint(api_type):
    """Return the base API URL."""
    return PRO_ENDPOINT if api_type == "pro" else FREE_ENDPOINT


def deepl_request(path, api_key, api_type, data=None, method="POST"):
    """Make a request to the DeepL API. Returns parsed JSON."""
    url = get_endpoint(api_type) + path
    headers = {
        "Authorization": f"DeepL-Auth-Key {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "translate_content.py/1.0",
    }

    if data is not None:
        body = json.dumps(data).encode("utf-8")
    else:
        body = None
        if method == "GET":
            headers.pop("Content-Type", None)

    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = ""
        try:
            body_text = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        if e.code == 456:
            raise QuotaExceededError(f"DeepL quota exceeded (HTTP 456): {body_text}")
        if e.code == 429:
            raise RateLimitError(f"Rate limited (HTTP 429): {body_text}")
        raise DeepLError(f"DeepL API error (HTTP {e.code}): {body_text}")


class DeepLError(Exception):
    pass


class QuotaExceededError(DeepLError):
    pass


class RateLimitError(DeepLError):
    pass


def check_usage(api_key, api_type):
    """Query DeepL /v2/usage endpoint. Returns (used, limit)."""
    result = deepl_request("/v2/usage", api_key, api_type, method="GET")
    return result.get("character_count", 0), result.get("character_limit", 0)


def check_supported_languages(api_key, api_type):
    """Query DeepL /v2/languages for target languages. Returns set of codes."""
    result = deepl_request("/v2/languages?type=target", api_key, api_type, method="GET")
    return {lang["language"] for lang in result}


def translate_text(text, target_lang, api_key, api_type):
    """Translate text via DeepL. Returns translated string."""
    data = {
        "text": [text],
        "target_lang": target_lang,
        "source_lang": "EN",
        "tag_handling": "xml",
        "ignore_tags": ["x"],
        "split_sentences": "nonewlines",
        "preserve_formatting": True,
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = deepl_request("/v2/translate", api_key, api_type, data=data)
            translations = result.get("translations", [])
            if translations:
                return translations[0]["text"]
            raise DeepLError("Empty translation response")
        except RateLimitError:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise


# ---------------------------------------------------------------------------
# Markdown protection / restoration
# ---------------------------------------------------------------------------

class PlaceholderManager:
    """Manages placeholder substitution for non-translatable elements."""

    def __init__(self):
        self._counter = 0
        self._store = {}

    def _next_id(self):
        self._counter += 1
        return self._counter

    def store(self, content):
        """Store content, return placeholder XML tag."""
        pid = self._next_id()
        self._store[pid] = content
        return f'<x id="{pid}"/>'

    def store_link(self, url):
        """Store a link URL, return opening anchor id for wrapping text."""
        pid = self._next_id()
        self._store[pid] = url
        return pid

    def get(self, pid):
        """Retrieve stored content by id."""
        return self._store.get(pid, "")


def protect_markdown(text, pm):
    """Replace non-translatable elements with XML placeholders.

    Returns protected text ready for DeepL translation.
    """
    # Order matters: protect larger structures before their sub-components
    # to avoid partial matches on already-protected content.

    # 1. Code blocks (``` ... ```)
    def replace_code_block(m):
        return pm.store(m.group(0))
    text = re.sub(r'```[\s\S]*?```', replace_code_block, text)

    # 2. Inline code (` ... `)
    def replace_inline_code(m):
        return pm.store(m.group(0))
    text = re.sub(r'`[^`\n]+`', replace_inline_code, text)

    # 3. Markdown images ![alt](url) - protect entirely before templates
    # can touch URLs containing {{BASE_URL}}
    def replace_image(m):
        return pm.store(m.group(0))
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, text)

    # 4. All HTML tags (opening, closing, self-closing)
    # Protects tag structure while leaving text content between tags
    # for translation. Handles multi-line tags with attributes.
    def replace_html_tag(m):
        return pm.store(m.group(0))
    # Opening and self-closing tags: <tag ...> or <tag ... />
    # Exclude <x ...> which are our own placeholders from earlier steps
    text = re.sub(r'<(?!x\s)[a-zA-Z][^>]*/>', replace_html_tag, text)
    text = re.sub(r'<(?!x\s)[a-zA-Z][^>]*>', replace_html_tag, text)
    # Closing tags: </tag>
    text = re.sub(r'</[a-zA-Z][^>]*>', replace_html_tag, text)

    # 5. Template markers ({{BASE_URL}}, {{CONTENT_BASE}}, etc.)
    def replace_template(m):
        return pm.store(m.group(0))
    text = re.sub(r'\{\{[A-Z_]+\}\}', replace_template, text)

    # 6. HTML entities (&rarr;, &#39;, etc.)
    def replace_entity(m):
        return pm.store(m.group(0))
    text = re.sub(r'&[#\w]+;', replace_entity, text)

    # 7. Markdown links [text](url) - translate text, preserve URL
    def replace_link(m):
        link_text = m.group(1)
        url = m.group(2)
        pid = pm.store_link(url)
        return f'<a id="{pid}">{link_text}</a>'
    text = re.sub(r'\[([^\]]*)\]\(([^)]+)\)', replace_link, text)

    return text


def restore_markdown(text, pm):
    """Restore placeholders after translation."""
    # 1. Restore link placeholders: <a id="N">translated text</a> -> [translated text](url)
    def restore_link(m):
        pid = int(m.group(1))
        translated_text = m.group(2)
        url = pm.get(pid)
        return f'[{translated_text}]({url})'
    text = re.sub(r'<a id="(\d+)">(.*?)</a>', restore_link, text)

    # 2. Restore <x id="N"/> placeholders
    def restore_placeholder(m):
        pid = int(m.group(1))
        return pm.get(pid)
    # Handle variations: <x id="N"/>, <x id="N" />, <x id="N"></x>
    text = re.sub(r'<x id="(\d+)"\s*/>', restore_placeholder, text)
    text = re.sub(r'<x id="(\d+)">\s*</x>', restore_placeholder, text)

    return text


# ---------------------------------------------------------------------------
# Frontmatter handling
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Split YAML frontmatter from markdown body. Returns (raw_lines, body).

    Returns the raw frontmatter lines (not parsed) so we can selectively
    translate specific fields while preserving the rest exactly.
    """
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return [], text
    end = text.find("---", 3)
    if end == -1:
        return [], text
    raw = text[3:end].strip()
    body = text[end + 3:].strip()
    return raw.split("\n"), body


def translate_frontmatter(lines, target_lang, api_key, api_type):
    """Translate title and description in frontmatter lines.

    Returns new list of frontmatter lines with translated values.
    Keywords stay in English (matching Italian model).
    """
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append(line)
            continue

        m = re.match(r'^([\w-]+)\s*:\s*(.+)$', stripped)
        if not m:
            result.append(line)
            continue

        key = m.group(1)
        val = m.group(2).strip()

        if key in ("title", "description"):
            # Strip quotes for translation
            quote_char = ""
            inner = val
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                quote_char = val[0]
                inner = val[1:-1]

            translated = translate_text(inner, target_lang, api_key, api_type)
            time.sleep(REQUEST_DELAY)

            # Re-quote with double quotes
            # Escape any double quotes in translated text
            translated = translated.replace('"', '\\"')
            result.append(f'{key}: "{translated}"')
        else:
            result.append(line)

    return result


def rebuild_frontmatter(lines, body):
    """Reconstruct the full markdown file from frontmatter lines and body."""
    fm = "\n".join(lines)
    return f"---\n{fm}\n---\n\n{body}\n"


# ---------------------------------------------------------------------------
# Chunking for large pages
# ---------------------------------------------------------------------------

def chunk_text(text, max_chars=CHUNK_THRESHOLD):
    """Split text at paragraph boundaries into chunks under max_chars."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para) + 2  # +2 for the \n\n separator
        if current_len + para_len > max_chars and current:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = para_len
        else:
            current.append(para)
            current_len += para_len

    if current:
        chunks.append("\n\n".join(current))

    return chunks


# ---------------------------------------------------------------------------
# Translation tracking
# ---------------------------------------------------------------------------

def load_tracking():
    """Load the content translations tracking file."""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "_note": "Tracks machine-translated content. Entries with source=deepl need human review.",
        "pages": {}
    }


def save_tracking(data):
    """Save the content translations tracking file."""
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def content_hash(text):
    """SHA256 hash of content for staleness detection."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Page discovery
# ---------------------------------------------------------------------------

def discover_pages():
    """Find all non-draft content pages. Returns list of slug strings."""
    pages = []
    for fname in sorted(os.listdir(CONTENT_DIR)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(CONTENT_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        with open(fpath, encoding="utf-8") as f:
            text = f.read()
        fm_lines, _ = parse_frontmatter(text)
        # Check for draft
        is_draft = False
        for line in fm_lines:
            if re.match(r'^\s*draft\s*:\s*true\s*$', line.strip(), re.IGNORECASE):
                is_draft = True
                break
        if is_draft:
            continue
        slug = fname[:-3]  # remove .md
        pages.append(slug)
    return pages


def estimate_chars(slug):
    """Estimate translatable character count for a page."""
    fpath = os.path.join(CONTENT_DIR, slug + ".md")
    with open(fpath, encoding="utf-8") as f:
        text = f.read()
    fm_lines, body = parse_frontmatter(text)

    # Frontmatter: only title + description
    fm_chars = 0
    for line in fm_lines:
        m = re.match(r'^(title|description)\s*:\s*(.+)$', line.strip())
        if m:
            val = m.group(2).strip().strip('"').strip("'")
            fm_chars += len(val)

    return fm_chars + len(body)


# ---------------------------------------------------------------------------
# Core translation logic
# ---------------------------------------------------------------------------

def translate_page(slug, lang, deepl_lang, api_key, api_type, chars_tracker):
    """Translate a single page. Returns (success, chars_used)."""
    fpath = os.path.join(CONTENT_DIR, slug + ".md")
    with open(fpath, encoding="utf-8") as f:
        source_text = f.read()

    fm_lines, body = parse_frontmatter(source_text)

    # Translate frontmatter (title + description)
    translated_fm = translate_frontmatter(fm_lines, deepl_lang, api_key, api_type)
    fm_chars = sum(
        len(re.match(r'^(?:title|description)\s*:\s*(.+)$', l.strip()).group(1).strip().strip('"').strip("'"))
        for l in fm_lines
        if re.match(r'^(?:title|description)\s*:\s*', l.strip())
    )
    chars_tracker["used"] += fm_chars

    # Translate body in chunks
    chunks = chunk_text(body)
    translated_chunks = []

    for i, chunk in enumerate(chunks):
        if chars_tracker.get("limit") and chars_tracker["used"] >= chars_tracker["limit"]:
            print(f"  Character limit reached during {slug}")
            return False, chars_tracker["used"]

        pm = PlaceholderManager()
        protected = protect_markdown(chunk, pm)
        chunk_chars = len(protected)

        translated = translate_text(protected, deepl_lang, api_key, api_type)
        time.sleep(REQUEST_DELAY)

        restored = restore_markdown(translated, pm)
        translated_chunks.append(restored)
        chars_tracker["used"] += chunk_chars

        if len(chunks) > 1:
            print(f"    Chunk {i + 1}/{len(chunks)} done ({chunk_chars} chars)")

    translated_body = "\n\n".join(translated_chunks)

    # Validate
    validate_translation(body, translated_body)

    # Write output
    out_dir = os.path.join(TRANSLATIONS_DIR, lang)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, slug + ".md")

    output = rebuild_frontmatter(translated_fm, translated_body)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output)

    # Update tracking
    tracking = load_tracking()
    if lang not in tracking["pages"]:
        tracking["pages"][lang] = {}
    tracking["pages"][lang][slug] = {
        "source": "deepl",
        "translated_at": str(date.today()),
        "source_hash": content_hash(source_text),
        "reviewed": False,
    }
    save_tracking(tracking)

    return True, chars_tracker["used"]


def validate_translation(original, translated):
    """Basic validation of translated output."""
    # Check heading markers preserved
    orig_headings = len(re.findall(r'^#{1,6}\s', original, re.MULTILINE))
    trans_headings = len(re.findall(r'^#{1,6}\s', translated, re.MULTILINE))
    if orig_headings != trans_headings:
        print(f"  Warning: heading count mismatch (original: {orig_headings}, translated: {trans_headings})")

    # Check table row pipes
    orig_pipes = len(re.findall(r'^\|', original, re.MULTILINE))
    trans_pipes = len(re.findall(r'^\|', translated, re.MULTILINE))
    if orig_pipes != trans_pipes:
        print(f"  Warning: table row count mismatch (original: {orig_pipes}, translated: {trans_pipes})")


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def build_work_plan(langs, pages, force):
    """Build list of (lang, slug) pairs that need translation."""
    plan = []
    for lang in langs:
        for slug in pages:
            out_path = os.path.join(TRANSLATIONS_DIR, lang, slug + ".md")
            if os.path.exists(out_path) and not force:
                continue
            plan.append((lang, slug))
    return plan


def run_dry_run(plan, pages):
    """Show what would be translated and estimated character counts."""
    if not plan:
        print("Nothing to translate - all pages already exist.")
        print("Use --force to re-translate existing files.")
        return

    # Group by language
    by_lang = {}
    for lang, slug in plan:
        by_lang.setdefault(lang, []).append(slug)

    total_chars = 0
    for lang in sorted(by_lang.keys()):
        slugs = by_lang[lang]
        lang_chars = sum(estimate_chars(s) for s in slugs)
        total_chars += lang_chars
        print(f"\n  {lang} ({DEEPL_LANG_MAP.get(lang, '?')}): {len(slugs)} pages, ~{lang_chars:,} chars")
        for s in slugs:
            chars = estimate_chars(s)
            print(f"    {s}.md ({chars:,} chars)")

    print(f"\n  Total: {len(plan)} page-translations, ~{total_chars:,} chars")
    print(f"  DeepL Free tier: 500,000 chars/month")
    months = total_chars / 500000
    if months > 1:
        print(f"  Estimated: ~{months:.1f} months on free tier")


def main():
    parser = argparse.ArgumentParser(
        description="Translate content pages via DeepL API"
    )
    parser.add_argument(
        "--lang",
        help="Comma-separated language codes (default: all in DEEPL_LANG_MAP)"
    )
    parser.add_argument(
        "--page",
        help="Comma-separated page slugs (default: all non-draft pages)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-translate even if translation file exists"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show work plan and character estimates without translating"
    )
    parser.add_argument(
        "--budget", action="store_true",
        help="Show DeepL API usage and remaining characters"
    )
    parser.add_argument(
        "--check-languages", action="store_true",
        help="Show DeepL supported target languages"
    )
    parser.add_argument(
        "--workers", type=int, default=3,
        help="Reserved for future concurrent processing (default: 3)"
    )
    parser.add_argument(
        "--api", choices=["free", "pro"], default="free",
        help="DeepL API tier (default: free)"
    )
    parser.add_argument(
        "--char-limit", type=int, default=0,
        help="Hard cap on characters to translate this run"
    )
    args = parser.parse_args()

    api_key = os.environ.get("DEEPL_API_KEY", "")

    # Determine target languages
    if args.lang:
        langs = [l.strip() for l in args.lang.split(",")]
        unknown = [l for l in langs if l not in DEEPL_LANG_MAP]
        if unknown:
            print(f"Error: unknown language codes: {', '.join(unknown)}")
            print(f"Supported: {', '.join(sorted(DEEPL_LANG_MAP.keys()))}")
            sys.exit(1)
    else:
        langs = [l for l in LANG_PRIORITY if l in DEEPL_LANG_MAP]

    # Determine pages
    all_pages = discover_pages()
    if args.page:
        pages = [p.strip() for p in args.page.split(",")]
        unknown = [p for p in pages if p not in all_pages]
        if unknown:
            print(f"Error: unknown page slugs: {', '.join(unknown)}")
            print(f"Available: {', '.join(all_pages)}")
            sys.exit(1)
    else:
        pages = all_pages

    # Build work plan
    plan = build_work_plan(langs, pages, args.force)

    # --dry-run: just show the plan
    if args.dry_run:
        print("Dry run - translation plan:")
        print(f"  Languages: {', '.join(langs)}")
        print(f"  Pages: {len(pages)} non-draft content pages")
        run_dry_run(plan, pages)
        return

    # Commands requiring API key
    if not api_key:
        print("Error: DEEPL_API_KEY environment variable not set")
        print("  export DEEPL_API_KEY=your-key-here")
        sys.exit(1)

    # --budget: show usage
    if args.budget:
        used, limit = check_usage(api_key, args.api)
        remaining = limit - used
        pct = (used / limit * 100) if limit else 0
        print(f"DeepL API usage ({args.api} tier):")
        print(f"  Used:      {used:>12,} chars")
        print(f"  Limit:     {limit:>12,} chars")
        print(f"  Remaining: {remaining:>12,} chars ({100 - pct:.1f}%)")
        return

    # --check-languages: show supported targets
    if args.check_languages:
        supported = check_supported_languages(api_key, args.api)
        print(f"DeepL supports {len(supported)} target languages:")
        our_langs = {}
        for site_code, deepl_code in sorted(DEEPL_LANG_MAP.items()):
            status = "supported" if deepl_code in supported else "NOT SUPPORTED"
            our_langs[site_code] = status
            print(f"  {site_code} -> {deepl_code}: {status}")

        unsupported = [k for k, v in our_langs.items() if v != "supported"]
        if unsupported:
            print(f"\nWarning: {len(unsupported)} languages not supported by DeepL: {', '.join(unsupported)}")
        return

    # No work to do?
    if not plan:
        print("Nothing to translate - all pages already exist.")
        print("Use --force to re-translate existing files.")
        return

    # Verify supported languages before starting
    try:
        supported = check_supported_languages(api_key, args.api)
    except DeepLError as e:
        print(f"Error checking supported languages: {e}")
        sys.exit(1)

    plan_langs = sorted(set(lang for lang, _ in plan))
    skipped_langs = []
    for lang in plan_langs:
        deepl_code = DEEPL_LANG_MAP[lang]
        if deepl_code not in supported:
            print(f"Warning: {lang} ({deepl_code}) not supported by DeepL, skipping")
            skipped_langs.append(lang)

    plan = [(lang, slug) for lang, slug in plan if lang not in skipped_langs]
    if not plan:
        print("No translatable work after removing unsupported languages.")
        return

    # Check budget
    try:
        used, limit = check_usage(api_key, args.api)
    except DeepLError as e:
        print(f"Error checking usage: {e}")
        sys.exit(1)

    remaining = limit - used
    print(f"DeepL budget: {remaining:,} chars remaining of {limit:,}")

    # Estimate total chars
    total_estimate = sum(estimate_chars(slug) for _, slug in plan)
    print(f"Estimated chars needed: ~{total_estimate:,}")
    if total_estimate > remaining:
        print(f"Warning: estimated chars exceed remaining budget")
        print(f"  Will translate in priority order until budget runs out")

    char_limit = args.char_limit if args.char_limit > 0 else None

    # Group plan by language for sequential processing within each language
    by_lang = {}
    for lang, slug in plan:
        by_lang.setdefault(lang, []).append(slug)

    # Process languages - each language's pages are done sequentially,
    # but we can process multiple languages concurrently
    chars_tracker = {"used": 0, "limit": char_limit}
    total_done = 0
    total_failed = 0
    stop_flag = False

    # Sort languages by priority
    ordered_langs = [l for l in LANG_PRIORITY if l in by_lang]
    ordered_langs += [l for l in by_lang if l not in ordered_langs]

    print(f"\nTranslating {len(plan)} pages across {len(ordered_langs)} languages...\n")

    for lang in ordered_langs:
        if stop_flag:
            break

        slugs = by_lang[lang]
        deepl_lang = DEEPL_LANG_MAP[lang]
        print(f"--- {lang} ({deepl_lang}): {len(slugs)} pages ---")

        for slug in slugs:
            if stop_flag:
                break
            if char_limit and chars_tracker["used"] >= char_limit:
                print(f"Character limit ({char_limit:,}) reached, stopping.")
                stop_flag = True
                break

            est = estimate_chars(slug)
            print(f"  Translating {slug}.md (~{est:,} chars)...")

            try:
                success, _ = translate_page(
                    slug, lang, deepl_lang, api_key, args.api, chars_tracker
                )
                if success:
                    total_done += 1
                    print(f"  Done: content/translations/{lang}/{slug}.md")
                else:
                    total_failed += 1
                    stop_flag = True
            except QuotaExceededError:
                print(f"  DeepL quota exceeded, stopping.")
                total_failed += 1
                stop_flag = True
            except DeepLError as e:
                print(f"  Error translating {slug}: {e}")
                total_failed += 1

    print(f"\nComplete: {total_done} translated, {total_failed} failed")
    print(f"Characters used this run: ~{chars_tracker['used']:,}")

    remaining_plan = len(plan) - total_done - total_failed
    if remaining_plan > 0:
        print(f"Remaining: {remaining_plan} pages not attempted (budget/limit)")


if __name__ == "__main__":
    main()
