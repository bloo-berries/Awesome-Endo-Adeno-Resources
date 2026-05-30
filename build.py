#!/usr/bin/env python3
"""Static site builder — stdlib only, no pip dependencies."""
import json, os, re, shutil, datetime, html as html_mod, sys, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

# ── SVG icon paths (from layouts/partials/icon.html) ──
ICONS = {
    "about": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "endometriosis": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "adenomyosis": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "diagnosis": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "co-morbidities": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "healthcare": '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M9 16h6"/><path d="M12 13v6"/>',
    "resources": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
    "education": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "myths": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "research": '<path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><path d="M8.5 2h7"/><path d="M7 16.5h10"/>',
    "notable-people": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "faq": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "mental-health": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M12 13v-2"/><path d="M12 17h.01"/>',
    "fertility": '<path d="M9 12h.01"/><path d="M15 12h.01"/><path d="M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5"/><circle cx="12" cy="12" r="10"/>',
    "medications": '<path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/><path d="m8.5 8.5 7 7"/>',
    "tracker": '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/>',
}

def load_config():
    with open(os.path.join(ROOT, "site.json")) as f:
        return json.load(f)

# ── Frontmatter parser ──
def parse_frontmatter(text):
    """Split YAML frontmatter from markdown body. Returns (meta_dict, body)."""
    text = text.lstrip("\ufeff")  # strip BOM
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 3:].strip()
    meta = {}
    for line in raw.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^(\w+)\s*[:=]\s*(.+)$', line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            # Strip quotes
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            # Parse YAML lists like ["a", "b"]
            if val.startswith("["):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
            # Parse booleans
            elif val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            meta[key] = val
    return meta, body

# ── Markdown → HTML converter ──
def md_to_html(text, base_url=""):
    """Convert markdown to HTML. Handles headings, bold, italic, links, images,
    lists, tables, code blocks, blockquotes, hr, and raw HTML passthrough."""
    lines = text.split("\n")
    out = []
    in_code = False
    code_buf = []
    in_list = None  # "ul" or "ol"
    in_blockquote = False
    in_table = False
    table_headers = []
    in_para = False
    used_ids = set()

    def flush_para():
        nonlocal in_para
        if in_para:
            out.append("</p>")
            in_para = False

    def flush_list():
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    def flush_blockquote():
        nonlocal in_blockquote
        if in_blockquote:
            out.append("</blockquote>")
            in_blockquote = False

    def flush_table():
        nonlocal in_table, table_headers
        if in_table:
            out.append("</tbody></table>")
            in_table = False
            table_headers = []

    def inline(t):
        """Process inline markdown: bold, italic, code, links, images."""
        # Inline code (must be before bold/italic to avoid conflicts)
        t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
        # Images
        t = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy">', t)
        # Links — external get target="_blank"
        def link_repl(m):
            text, href = m.group(1), m.group(2)
            if href.startswith("http"):
                return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{text}</a>'
            return f'<a href="{href}">{text}</a>'
        t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_repl, t)
        # Bold + italic
        t = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', t)
        t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', t)
        # Strikethrough
        t = re.sub(r'~~(.+?)~~', r'<del>\1</del>', t)
        return t

    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.strip().startswith("```"):
            if in_code:
                flush_para()
                code_text = html_mod.escape("\n".join(code_buf))
                out.append(f"<pre><code>{code_text}</code></pre>")
                code_buf = []
                in_code = False
            else:
                flush_para(); flush_list(); flush_blockquote(); flush_table()
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        stripped = line.strip()

        # Blank line
        if not stripped:
            flush_para(); flush_list(); flush_blockquote(); flush_table()
            i += 1
            continue

        # Raw HTML passthrough (lines starting with <)
        if stripped.startswith("<"):
            flush_para(); flush_list(); flush_blockquote(); flush_table()
            # Collect consecutive HTML lines
            html_buf = [line]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                # Continue if line is HTML or blank (within HTML block)
                if nxt.strip().startswith("<") or (nxt.strip() and not re.match(r'^(#{1,6}\s|[-*+]\s|\d+\.\s|>\s|```|\|)', nxt.strip())):
                    html_buf.append(nxt)
                    i += 1
                    # If we hit a closing tag that matches an opening, check if block is done
                    if nxt.strip().startswith("</"):
                        break
                else:
                    break
            out.append("\n".join(html_buf))
            continue

        # Horizontal rule
        if re.match(r'^[-*_]{3,}\s*$', stripped):
            flush_para(); flush_list(); flush_blockquote(); flush_table()
            out.append("<hr>")
            i += 1
            continue

        # Headings
        hm = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if hm:
            flush_para(); flush_list(); flush_blockquote(); flush_table()
            level = len(hm.group(1))
            text = hm.group(2).strip()
            # Strip trailing # marks
            text = re.sub(r'\s+#+\s*$', '', text)
            slug = re.sub(r'[^\w\s-]', '', text.lower())
            slug = re.sub(r'[\s]+', '-', slug).strip('-')
            # Deduplicate heading IDs
            orig_slug = slug
            counter = 2
            while slug in used_ids:
                slug = f"{orig_slug}-{counter}"
                counter += 1
            used_ids.add(slug)
            out.append(f'<h{level} id="{slug}">{inline(text)}</h{level}>')
            i += 1
            continue

        # Table
        if "|" in stripped and stripped.startswith("|"):
            if not in_table:
                flush_para(); flush_list(); flush_blockquote()
                # Parse header row
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                table_headers = cells
                # Check next line for separator
                if i + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[i+1].strip()):
                    out.append("<table><thead><tr>")
                    for c in cells:
                        out.append(f"<th>{inline(c)}</th>")
                    out.append("</tr></thead><tbody>")
                    in_table = True
                    i += 2  # skip header + separator
                    continue
            else:
                # Table data row
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                out.append("<tr>")
                for c in cells:
                    out.append(f"<td>{inline(c)}</td>")
                out.append("</tr>")
                i += 1
                continue

        # Blockquote
        if stripped.startswith(">"):
            flush_para(); flush_list(); flush_table()
            if not in_blockquote:
                out.append("<blockquote>")
                in_blockquote = True
            text = re.sub(r'^>\s?', '', stripped)
            out.append(f"<p>{inline(text)}</p>")
            i += 1
            continue

        # Unordered list
        ulm = re.match(r'^([-*+])\s+(.+)$', stripped)
        if ulm:
            flush_para(); flush_blockquote(); flush_table()
            if in_list != "ul":
                flush_list()
                out.append("<ul>")
                in_list = "ul"
            out.append(f"<li>{inline(ulm.group(2))}</li>")
            i += 1
            continue

        # Ordered list
        olm = re.match(r'^(\d+)\.\s+(.+)$', stripped)
        if olm:
            flush_para(); flush_blockquote(); flush_table()
            if in_list != "ol":
                flush_list()
                out.append("<ol>")
                in_list = "ol"
            out.append(f"<li>{inline(olm.group(2))}</li>")
            i += 1
            continue

        # Paragraph text
        flush_list(); flush_blockquote(); flush_table()
        if not in_para:
            out.append("<p>")
            in_para = True
        else:
            out.append("<br>")
        out.append(inline(stripped))
        i += 1

    # Flush remaining state
    if in_code:
        out.append(f"<pre><code>{html_mod.escape(chr(10).join(code_buf))}</code></pre>")
    flush_para(); flush_list(); flush_blockquote(); flush_table()

    return "\n".join(out)

# ── CSS variables from config (complete design token set) ──
def build_css_vars(cfg):
    c = cfg["colors"]
    s = c["sidebar"]
    lt = c["light"]
    dk = c["dark"]
    brand = c.get("brand", {})
    gradients = c.get("gradients", {})

    # Build brand token lines
    brand_lines = []
    for key, val in brand.items():
        css_key = key.replace("_", "-")
        brand_lines.append(f"        --color-{css_key}: {val};")
    brand_css = "\n".join(brand_lines)

    # Build gradient token lines
    gradient_lines = []
    for key, val in gradients.items():
        css_key = key.replace("_", "-")
        gradient_lines.append(f"        --gradient-{css_key}: {val};")
    gradient_css = "\n".join(gradient_lines)

    # Semantic layer (Phase 2 addition; coexists with legacy tokens above)
    sem = cfg.get("semantic", {})
    sem_light = sem.get("light", {})
    sem_dark = sem.get("dark", {})
    sem_constant = sem.get("constant", {})
    sem_scale = sem.get("scale", {})

    def emit_tokens(d, indent=8):
        pad = " " * indent
        return "\n".join(f"{pad}--{k}: {v};" for k, v in d.items())

    semantic_light_css = emit_tokens(sem_light)
    semantic_dark_css = emit_tokens(sem_dark)
    semantic_constant_css = emit_tokens(sem_constant)
    semantic_scale_css = emit_tokens(sem_scale)

    return f"""<style>
    body {{
        /* Sidebar tokens */
        --sidebar-bg-color: {s['sidebar_bg_color']};
        --sidebar-img-border-color: {s['sidebar_img_border_color']};
        --sidebar-p-color: {s['sidebar_p_color']};
        --sidebar-h1-color: {s['sidebar_h1_color']};
        --sidebar-a-color: {s['sidebar_a_color']};
        --sidebar-socials-color: {s['sidebar_socials_color']};
        --moon-sun-color: {s['moon_sun_color']};
        --moon-sun-background-color: {s['moon_sun_background_color']};

        /* Theme tokens (light default in body, dark override below) */
        --text-color: {lt['text_color']};
        --bkg-color: {lt['content_bg_color']};
        --post-title-color: {lt['post_title_color']};
        --list-color: {lt['list_color']};
        --link-color: {lt['link_color']};
        --link-hover-color: {lt.get('link_hover_color', lt['link_color'])};
        --heading-color: {lt.get('heading_color', lt['text_color'])};
        --date-color: {lt['date_color']};
        --table-border-color: {lt['table_border_color']};
        --table-stripe-color: {lt['table_stripe_color']};
        --table-header-bg: {lt.get('table_header_bg', 'rgba(0,0,0,0.05)')};
        --code-color: {lt['code_color']};
        --code-background-color: {lt['code_background_color']};
        --code-block-color: {lt['code_block_color']};
        --code-block-background-color: {lt['code_block_background_color']};
        --muted-color: {lt.get('muted_color', lt['date_color'])};
        --surface-color: {lt.get('surface_color', lt['content_bg_color'])};
        --border-color: {lt.get('border_color', 'rgba(0,0,0,0.1)')};
        --scrollbar-thumb: {lt.get('scrollbar_thumb', 'rgba(0,0,0,0.2)')};
        --scrollbar-track: {lt.get('scrollbar_track', 'rgba(0,0,0,0.03)')};

        /* Brand colors */
{brand_css}

        /* Gradients */
{gradient_css}

        /* Design tokens */
        --font-primary: 'Figtree', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-pill: 9999px;
        --focus-color: {brand.get('gold', '#C4982A')};
        --focus-shadow: 0 0 0 3px rgba(196, 152, 42, 0.3);
        --transition-fast: all 0.2s ease;
        --shadow-sm: 0 2px 8px rgba(0,0,0,0.2);
        --shadow-md: 0 4px 16px rgba(0,0,0,0.2);
        --white-subtle: rgba(255,255,255,0.08);
        --white-muted: rgba(255,255,255,0.15);
        --white-soft: rgba(255,255,255,0.2);

        background-color: var(--bkg-color);

        /* === Semantic layer (Phase 2) === */
{semantic_light_css}
{semantic_constant_css}
{semantic_scale_css}
    }}
    body.dark-theme {{
        --text-color: {dk['text_color']};
        --bkg-color: {dk['content_bg_color']};
        --post-title-color: {dk['post_title_color']};
        --list-color: {dk['list_color']};
        --link-color: {dk['link_color']};
        --link-hover-color: {dk.get('link_hover_color', dk['link_color'])};
        --heading-color: {dk.get('heading_color', dk['text_color'])};
        --date-color: {dk['date_color']};
        --table-border-color: {dk['table_border_color']};
        --table-stripe-color: {dk['table_stripe_color']};
        --table-header-bg: {dk.get('table_header_bg', 'rgba(255,255,255,0.05)')};
        --code-color: {dk['code_color']};
        --code-background-color: {dk['code_background_color']};
        --code-block-color: {dk['code_block_color']};
        --code-block-background-color: {dk['code_block_background_color']};
        --muted-color: {dk.get('muted_color', dk['date_color'])};
        --surface-color: {dk.get('surface_color', dk['content_bg_color'])};
        --border-color: {dk.get('border_color', 'rgba(255,255,255,0.1)')};
        --scrollbar-thumb: {dk.get('scrollbar_thumb', 'rgba(255,255,255,0.25)')};
        --scrollbar-track: {dk.get('scrollbar_track', 'rgba(255,255,255,0.05)')};

        /* === Semantic layer (Phase 2) === */
{semantic_dark_css}
    }}
</style>"""

# ── Grouped sidebar nav ──
def build_sidebar_nav(cfg, active_slug=None):
    if "nav_groups" not in cfg:
        # Fallback to flat nav
        items = []
        for m in cfg["menu"]:
            icon_svg = ICONS.get(m["icon"], "")
            i18n_attr = f' data-i18n="{m["i18n_nav"]}"' if m.get("i18n_nav") else ""
            active_attr = ' aria-current="page"' if m["slug"] == active_slug else ""
            items.append(
                f'        <li class="nav-item">'
                f'<a href="{cfg["base_url"]}{m["slug"]}/"{active_attr}>'
                f'<svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
                f'{icon_svg}</svg>'
                f'<span{i18n_attr}>{m["name"]}</span></a></li>'
            )
        return '<nav aria-label="Site navigation" class="sidebar-nav">\n    <ul>\n' + "\n".join(items) + "\n    </ul>\n</nav>"

    # Grouped nav
    groups_html = []
    for idx, group in enumerate(cfg["nav_groups"]):
        i18n_key = group.get("i18n_key", "")
        i18n_attr = f' data-i18n="{i18n_key}"' if i18n_key else ""
        group_id = f"nav-group-{idx}"
        list_id = f"nav-group-list-{idx}"
        items = []
        for m in group["items"]:
            icon_svg = ICONS.get(m["icon"], "")
            nav_i18n = f' data-i18n="{m["i18n_nav"]}"' if m.get("i18n_nav") else ""
            active_attr = ' aria-current="page"' if m["slug"] == active_slug else ""
            items.append(
                f'            <li class="nav-item">'
                f'<a href="{cfg["base_url"]}{m["slug"]}/"{active_attr}>'
                f'<svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
                f'{icon_svg}</svg>'
                f'<span{nav_i18n}>{m["name"]}</span></a></li>'
            )
        group_html = (
            f'        <div class="nav-group" data-group-id="{group_id}">\n'
            f'            <h3 class="nav-group-label">\n'
            f'                <button class="nav-group-toggle" aria-expanded="true" aria-controls="{list_id}">\n'
            f'                    <span{i18n_attr}>{group["label"]}</span>\n'
            f'                    <svg class="nav-group-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg>\n'
            f'                </button>\n'
            f'            </h3>\n'
            f'            <ul id="{list_id}">\n'
            + "\n".join(items) + "\n"
            f'            </ul>\n'
            f'        </div>'
        )
        groups_html.append(group_html)
    return '<nav aria-label="Site navigation" class="sidebar-nav">\n' + "\n".join(groups_html) + "\n</nav>"

# ── Footer links (About, etc.) ──
def build_footer_links(cfg):
    links = cfg.get("footer_links", [])
    if not links:
        return ""
    items = []
    for m in links:
        icon_svg = ICONS.get(m.get("icon", ""), "")
        i18n_attr = f' data-i18n="{m["i18n_nav"]}"' if m.get("i18n_nav") else ""
        items.append(
            f'<a href="{cfg["base_url"]}{m["slug"]}/" class="footer-link">'
            f'<svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            f'{icon_svg}</svg>'
            f'<span{i18n_attr}>{m["name"]}</span></a>'
        )
    return '<div class="sidebar-footer-links">' + "\n".join(items) + '</div>'

# ── Socials ──
def build_socials(cfg):
    gh = cfg.get("github_url", "")
    if not gh:
        return ""
    return f'''<a target="_blank" class="social" title="GitHub" href="{gh}">
        <svg xmlns="http://www.w3.org/2000/svg" width="1.2em" height="1.2em" viewBox="-2 -2 24 24">
            <path fill="currentColor" d="M18.88 1.099C18.147.366 17.265 0 16.233 0H3.746C2.714 0 1.832.366 1.099 1.099C.366 1.832 0 2.714 0 3.746v12.487c0 1.032.366 1.914 1.099 2.647c.733.733 1.615 1.099 2.647 1.099H6.66c.19 0 .333-.007.429-.02a.504.504 0 0 0 .286-.169c.095-.1.143-.245.143-.435l-.007-.885c-.004-.564-.006-1.01-.006-1.34l-.3.052c-.19.035-.43.05-.721.046a5.555 5.555 0 0 1-.904-.091a2.026 2.026 0 0 1-.872-.39a1.651 1.651 0 0 1-.572-.8l-.13-.3a3.25 3.25 0 0 0-.41-.663c-.186-.243-.375-.407-.566-.494l-.09-.065a.956.956 0 0 1-.17-.156a.723.723 0 0 1-.117-.182c-.026-.061-.004-.111.065-.15c.07-.04.195-.059.378-.059l.26.04c.173.034.388.138.643.311a2.1 2.1 0 0 1 .631.677c.2.355.44.626.722.813c.282.186.566.28.852.28c.286 0 .533-.022.742-.065a2.59 2.59 0 0 0 .585-.196c.078-.58.29-1.028.637-1.34a8.907 8.907 0 0 1-1.333-.234a5.314 5.314 0 0 1-1.223-.507a3.5 3.5 0 0 1-1.047-.872c-.277-.347-.505-.802-.683-1.365c-.177-.564-.266-1.215-.266-1.952c0-1.049.342-1.942 1.027-2.68c-.32-.788-.29-1.673.091-2.652c.252-.079.625-.02 1.119.175c.494.195.856.362 1.086.5c.23.14.414.257.553.352a9.233 9.233 0 0 1 2.497-.338c.859 0 1.691.113 2.498.338l.494-.312a6.997 6.997 0 0 1 1.197-.572c.46-.174.81-.221 1.054-.143c.39.98.424 1.864.103 2.653c.685.737 1.028 1.63 1.028 2.68c0 .737-.089 1.39-.267 1.957c-.177.568-.407 1.023-.689 1.366a3.65 3.65 0 0 1-1.053.865c-.42.234-.828.403-1.223.507a8.9 8.9 0 0 1-1.333.235c.45.39.676 1.005.676 1.846v3.11c0 .147.021.266.065.357a.36.36 0 0 0 .208.189c.096.034.18.056.254.064c.074.01.18.013.318.013h2.914c1.032 0 1.914-.366 2.647-1.099c.732-.732 1.099-1.615 1.099-2.647V3.746c0-1.032-.367-1.914-1.1-2.647z"/>
        </svg>
    </a>'''

# ── Structured data JSON-LD ──
def build_structured_data(cfg, page=None):
    base = cfg["base_url"]
    brand = cfg["brand"]
    desc = cfg["description"]
    if page is None:  # homepage
        return f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "{brand}",
  "description": "{desc}",
  "url": "{base}",
  "potentialAction": {{
    "@type": "SearchAction",
    "target": "{base}?q={{search_term_string}}",
    "query-input": "required name=search_term_string"
  }}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{brand}",
  "url": "{base}",
  "description": "{desc}",
  "sameAs": ["{cfg.get('github_url', '')}"]
}}
</script>'''
    # Article page
    title = html_mod.escape(page.get("title", ""))
    pdesc = html_mod.escape(page.get("description", desc))
    purl = page.get("permalink", base)
    date = page.get("date", "2025-01-27")
    lastmod = page.get("lastmod", date)
    keywords = page.get("keywords", [])
    kw_str = f',\n  "keywords": "{", ".join(keywords)}"' if keywords else ""
    result = f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{pdesc}",
  "url": "{purl}",
  "datePublished": "{date}T00:00:00Z",
  "dateModified": "{lastmod}T00:00:00Z",
  "publisher": {{
    "@type": "Organization",
    "name": "{brand}"
  }},
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{purl}"
  }}{kw_str}
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "{base}"
    }},
    {{
      "@type": "ListItem",
      "position": 2,
      "name": "{title}",
      "item": "{purl}"
    }}
  ]
}}
</script>'''
    # FAQ page: add FAQPage schema
    if page.get("slug") == "faq":
        html_content = page.get("html", "")
        faq_pairs = re.findall(r'<summary>(.*?)</summary>.*?<p>(.*?)</p>', html_content, re.DOTALL)
        if faq_pairs:
            qa_items = []
            for q, a in faq_pairs:
                q_clean = html_mod.escape(re.sub(r'<[^>]+>', '', q).strip())
                a_clean = html_mod.escape(re.sub(r'<[^>]+>', '', a).strip())
                qa_items.append(f'{{"@type":"Question","name":"{q_clean}","acceptedAnswer":{{"@type":"Answer","text":"{a_clean}"}}}}')
            result += '\n<script type="application/ld+json">\n{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[' + ','.join(qa_items) + ']}\n</script>'
    return result

# ── Search index ──
def build_search_index(pages, cfg):
    index = []
    for slug, page in pages.items():
        if page.get("draft"):
            continue
        # Honor `search: false` frontmatter (e.g., take-action, privacy, graphic-images)
        if str(page.get("search", "true")).lower() == "false":
            continue
        plain = re.sub(r'<[^>]+>', '', page.get("html", ""))
        plain = re.sub(r'\s+', ' ', plain).strip()
        index.append({
            "title": page.get("title", ""),
            "permalink": page.get("permalink", ""),
            "summary": plain[:300],
            "content": plain,
            "tags": page.get("tags", []),
        })
    return json.dumps(index, ensure_ascii=False)

# ── Sitemap ──
def build_sitemap(pages, cfg):
    base = cfg["base_url"]
    urls = []
    # Homepage
    urls.append(f'  <url>\n    <loc>{base}</loc>\n    <priority>1.0</priority>\n  </url>')
    for slug, page in sorted(pages.items()):
        if slug == "_index" or page.get("draft"):
            continue
        lastmod = page.get("lastmod", page.get("date", "2025-01-27"))
        urls.append(
            f'  <url>\n    <loc>{base}{slug}/</loc>\n'
            f'    <lastmod>{lastmod}</lastmod>\n'
            f'    <priority>0.8</priority>\n  </url>'
        )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n")

# ── CSS/JS Minification ──
def minify_css(text):
    # Strip block comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    # Collapse whitespace around structural chars
    text = re.sub(r'\s*([{}:;,])\s*', r'\1', text)
    # Collapse multiple whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def minify_js(text):
    # Strip block comments (but not URLs with //)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    # Strip single-line comments (only at start of line or after semicolons)
    lines = text.split('\n')
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        out.append(line)
    text = '\n'.join(out)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# ── Table of Contents ──
def build_toc(html_content, min_headings=4):
    headings = re.findall(r'<h([23]) id="([^"]*)">(.*?)</h\1>', html_content)
    if len(headings) < min_headings:
        return ""
    items = []
    for level, hid, text in headings:
        # Strip inline HTML tags from heading text
        clean = re.sub(r'<[^>]+>', '', text)
        indent = ' toc-h3' if level == '3' else ''
        items.append(f'<li class="toc-item{indent}"><a href="#{hid}">{clean}</a></li>')
    return ('<nav class="toc" aria-label="Table of contents">\n'
            '<h3 class="toc-heading" data-i18n="toc_title">On this page</h3>\n'
            '<ul>\n' + '\n'.join(items) + '\n</ul>\n</nav>')

# ── Breadcrumbs ──
def build_breadcrumbs(cfg, title):
    return (
        '<nav class="breadcrumbs" aria-label="Breadcrumb">\n'
        '    <ol>\n'
        f'        <li><a href="{cfg["base_url"]}" data-i18n="nav_home">Home</a></li>\n'
        f'        <li aria-current="page">{html_mod.escape(title)}</li>\n'
        '    </ol>\n'
        '</nav>'
    )

# ── Read all content pages ──
def load_pages(cfg):
    pages = {}
    content_dir = os.path.join(ROOT, "content")
    for fname in os.listdir(content_dir):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(content_dir, fname)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        meta, body = parse_frontmatter(text)
        if meta.get("draft") is True:
            continue
        slug = fname.replace(".md", "")
        if slug == "_index":
            slug = "_index"
        html_content = md_to_html(body, cfg["base_url"])
        permalink = cfg["base_url"] if slug == "_index" else f'{cfg["base_url"]}{slug}/'
        pages[slug] = {
            "title": meta.get("title", slug),
            "description": meta.get("description", cfg["description"]),
            "date": meta.get("date", "2025-01-27"),
            "lastmod": meta.get("lastmod", meta.get("date", "2025-01-27")),
            "tags": meta.get("tags", []),
            "keywords": meta.get("keywords", []),
            "draft": meta.get("draft", False),
            "search": meta.get("search", True),
            "toc": meta.get("toc", True),
            "html": html_content,
            "permalink": permalink,
            "slug": slug,
        }
    return pages

# ── Render a page using base template ──
def render_page(base_tpl, cfg, inner_html, page_meta=None):
    year = str(datetime.datetime.now().year)
    base_url = cfg["base_url"]
    brand = cfg["brand"]

    if page_meta:
        title = f'{brand} - {page_meta.get("title", "")}'
        desc = page_meta.get("description", cfg["description"])
        page_url = page_meta.get("permalink", base_url)
        structured = build_structured_data(cfg, page_meta)
        og_type = "article"
    else:
        title = brand
        desc = cfg["description"]
        page_url = base_url
        structured = build_structured_data(cfg)
        og_type = "website"

    og_image = base_url + cfg.get("og_image", "social-preview.png")

    active_slug = page_meta.get("slug") if page_meta else None
    sidebar_nav = build_sidebar_nav(cfg, active_slug)
    socials = build_socials(cfg)
    css_vars = build_css_vars(cfg)
    footer_links = build_footer_links(cfg)

    out = base_tpl
    out = out.replace("{{BASE_URL}}", base_url)
    out = out.replace("{{META_TITLE}}", html_mod.escape(title))
    out = out.replace("{{BRAND}}", html_mod.escape(brand))
    out = out.replace("{{DESCRIPTION}}", html_mod.escape(desc))
    out = out.replace("{{PAGE_URL}}", page_url)
    out = out.replace("{{CSS_VARIABLES}}", css_vars)
    out = out.replace("{{STRUCTURED_DATA}}", structured)
    out = out.replace("{{SIDEBAR_NAV}}", sidebar_nav)
    out = out.replace("{{FOOTER_LINKS}}", footer_links)
    out = out.replace("{{SOCIALS}}", socials)
    out = out.replace("{{YEAR}}", year)
    out = out.replace("{{OG_IMAGE}}", og_image)
    out = out.replace("{{OG_TYPE}}", og_type)
    out = out.replace("{{CSS_BUNDLE}}", cfg.get("_css_bundle", "css/bundle.css"))
    out = out.replace("{{JS_BUNDLE}}", cfg.get("_js_bundle", "js/app.js"))
    out = out.replace("{{PAGE_CONTENT}}", inner_html)
    return out

# ── Main build ──
def main():
    cfg = load_config()
    # Allow --base-url override for local dev
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--base-url" and i < len(sys.argv) - 1:
            cfg["base_url"] = sys.argv[i + 1]
        elif arg.startswith("--base-url="):
            cfg["base_url"] = arg.split("=", 1)[1]
    base_url = cfg["base_url"]

    # Clean dist
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)

    # Load templates
    def read_tpl(name):
        with open(os.path.join(ROOT, "templates", name), encoding="utf-8") as f:
            return f.read()

    base_tpl = read_tpl("base.html")
    home_tpl = read_tpl("home.html")
    page_tpl = read_tpl("page.html")
    four04_tpl = read_tpl("404.html")

    # Concat + minify CSS
    css_dir = os.path.join(DIST, "css")
    os.makedirs(css_dir, exist_ok=True)
    css_parts = []
    for f in cfg["css_files"]:
        path = os.path.join(ROOT, "assets", f)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                css_parts.append(fh.read())
    css_content = minify_css("\n".join(css_parts))
    css_hash = hashlib.md5(css_content.encode()).hexdigest()[:8]
    css_bundle_name = f"css/bundle.{css_hash}.css"
    cfg["_css_bundle"] = css_bundle_name
    with open(os.path.join(css_dir, f"bundle.{css_hash}.css"), "w", encoding="utf-8") as f:
        f.write(css_content)

    # Concat + minify JS into app.js bundle
    js_dir = os.path.join(DIST, "js")
    os.makedirs(js_dir, exist_ok=True)
    js_parts = []
    for f in cfg["js_files"]:
        path = os.path.join(ROOT, "assets", f)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                js_parts.append(fh.read())
    js_content = minify_js("\n".join(js_parts))
    js_hash = hashlib.md5(js_content.encode()).hexdigest()[:8]
    js_bundle_name = f"js/app.{js_hash}.js"
    cfg["_js_bundle"] = js_bundle_name
    with open(os.path.join(js_dir, f"app.{js_hash}.js"), "w", encoding="utf-8") as f:
        f.write(js_content)

    # Copy static assets
    static_src = os.path.join(ROOT, "static")
    if os.path.exists(static_src):
        for item in os.listdir(static_src):
            s = os.path.join(static_src, item)
            d = os.path.join(DIST, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

    # Load content pages
    pages = load_pages(cfg)

    # Build search index
    with open(os.path.join(DIST, "index.json"), "w", encoding="utf-8") as f:
        f.write(build_search_index(pages, cfg))

    # Build sitemap
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(build_sitemap(pages, cfg))

    # Build homepage
    home_inner = home_tpl.replace("{{BASE_URL}}", base_url)
    home_html = render_page(base_tpl, cfg, home_inner)
    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
        f.write(home_html)

    # Build individual pages
    for slug, page in pages.items():
        if slug == "_index":
            continue
        breadcrumbs = build_breadcrumbs(cfg, page["title"])
        toc = build_toc(page["html"]) if page.get("toc", True) else ""
        inner = page_tpl
        inner = inner.replace("{{BREADCRUMBS}}", breadcrumbs)
        inner = inner.replace("{{TOC}}", toc)
        inner = inner.replace("{{PAGE_CONTENT}}", page["html"])

        page_html = render_page(base_tpl, cfg, inner, page)
        page_dir = os.path.join(DIST, slug)
        os.makedirs(page_dir, exist_ok=True)
        with open(os.path.join(page_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page_html)

    # Build 404 page
    four04_inner = four04_tpl.replace("{{BASE_URL}}", base_url)
    four04_html = render_page(base_tpl, cfg, four04_inner, {"title": "404 Not Found", "description": "Page not found", "permalink": f"{base_url}404.html"})
    with open(os.path.join(DIST, "404.html"), "w", encoding="utf-8") as f:
        f.write(four04_html)

    # Write .nojekyll
    with open(os.path.join(DIST, ".nojekyll"), "w") as f:
        pass

    # Write robots.txt
    with open(os.path.join(DIST, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {base_url}sitemap.xml\n")

    # Count output
    html_count = sum(1 for r, d, files in os.walk(DIST) for fn in files if fn.endswith(".html"))
    print(f"Built {html_count} pages to {DIST}/")

if __name__ == "__main__":
    main()
