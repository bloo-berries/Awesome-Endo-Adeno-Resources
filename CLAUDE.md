# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Product context

1in7.info is an endometriosis and adenomyosis awareness campaign. The long-term plan is to distribute QR code stickers in cities, meaning users will arrive phone-first on cellular data, often on mid-range devices. **Mobile performance is the top priority** - every feature decision should weigh mobile impact first. Ambient effects, heavy animations, and large assets must be gated behind tablet-or-wider breakpoints or `prefers-reduced-motion` checks.

## Build / Serve / Deploy

```bash
# Build site (outputs to dist/)
python3 build.py

# Build for local serving (rewrites internal URLs to /)
python3 build.py --base-url=/

# Serve locally
python3 -m http.server 8000 --directory dist
```

Deployed via **GitHub Pages** through `.github/workflows/deploy.yml` (push to `main` triggers build). Also configured for **Cloudflare Pages** via `wrangler.toml` (project name: `one-in-seven`, custom domain: `1in7.info`). `base_url` in `site.json` points to the GitHub Pages URL; override with `--base-url=` for other deploys.

## Architecture

**Standalone static site** - no framework, no npm, no bundler. A single Python build script (stdlib only) converts Markdown content + HTML templates into static pages. All CSS/JS is vanilla. **Self-hosted Figtree** (OFL 1.1) - no Google Fonts call, no IP leak.

The site went through a full UI/UX overhaul (Phases 1–5) documented under `design/`. The current state is "v2": three-journey IA, mobile-first CSS, semantic token layer, off-canvas sidebar + top bar + bottom nav shell.

### Build pipeline (`build.py`)

| Function | Purpose |
|---|---|
| `load_config()` | Read `site.json` |
| `parse_frontmatter(text)` | Split `---` frontmatter from body; supports `title`, `description`, `date`, `lastmod`, `draft`, `tags`, `keywords`, `search`, `toc` |
| `md_to_html(text, base_url)` | Markdown→HTML: headings (auto-IDs), bold/italic, links (external→`target="_blank"`, internal rewritten with `base_url`), images, lists, tables, code blocks, blockquotes, hr, raw HTML passthrough |
| `build_css_vars(cfg)` | Emit `<style>` block: legacy color tokens + semantic layer from `site.json:semantic` (light/dark/constant/scale) |
| `build_sidebar_nav(cfg, active_slug)` | Grouped `<nav>` with `<div class="nav-group">` sections, each with a `<button class="nav-group-toggle">` controlling its `<ul>`; sets `aria-current="page"` on the active link |
| `build_footer_links(cfg)` | Generates footer links (About, FAQ, Take action, Privacy) for the sidebar bottom |
| `build_structured_data(cfg, page)` | JSON-LD for SEO |
| `build_search_index(pages, cfg)` | `dist/index.json` - title, permalink, summary, content, tags. Excludes pages with `search: false` frontmatter (`/take-action/`, `/privacy/`) |
| `build_sitemap(pages, cfg)` | `dist/sitemap.xml` |
| `build_toc(html, min_headings=4)` | Per-page TOC from H2/H3 (only emitted if ≥4 headings). Suppressed when `toc: false` in frontmatter |
| `minify_css(text)` / `minify_js(text)` | Whitespace/comment stripping |
| `load_pages(cfg)` | Walk `content/`, parse markdown, propagate frontmatter fields (including `search`, `toc`) |
| `render_page(base_tpl, cfg, inner, page_meta)` | Apply `base.html` with all `{{...}}` markers replaced |
| `main()` | Clean `dist/`, concat+minify CSS→`dist/css/bundle.<hash>.css`, JS→`dist/js/app.<hash>.js`, build all pages, copy `static/*` (incl. self-hosted fonts) to `dist/`, write `.nojekyll`, `robots.txt`, `sitemap.xml`, `index.json`, `404.html` |

Bundles are content-hashed for cache busting; filenames injected via `cfg["_css_bundle"]` / `cfg["_js_bundle"]` and exposed through `{{CSS_BUNDLE}}` / `{{JS_BUNDLE}}`.

### JS systems

JS modules in `assets/js/` are listed in `site.json:js_files`, concatenated and minified into `dist/js/app.<hash>.js`. Page-shell scripts (sidebar open/close, theme toggle, back-to-top, bottom-nav current-page marker) live inline in `templates/base.html`.

| System | Location | What it does |
|---|---|---|
| Codeblock copy | `assets/js/codeblock.js` | Copy button for `<pre>` blocks |
| Client-side search | `assets/js/search.js` | Loads `/index.json`. Empty-state suggestions (6 i18n keys). Debounced search (200ms). Synonym expansion. Weighted scoring. ↑/↓/Enter/Esc keyboard nav. `aria-live="polite"` on results panel |
| Client-side i18n | `assets/js/i18n.js` | Loads `/i18n/translations.json`, 26 languages, `data-i18n` attributes, localStorage persistence (`site-language`), `dir="rtl"` for Arabic. Exposes `window.__i18nTranslations` for other modules |
| Image carousel | `assets/js/carousel.js` | Multi-instance: inits all `.carousel-section` containers independently. Auto-rotates 4s. Disabled if `prefers-reduced-motion: reduce` OR `hover: none` (touch). Reacts to live motion-pref changes. ARIA-roledescription + per-slide labels + `aria-hidden`. Supports NSFW gate: if a `.carousel-nsfw-gate` exists inside a section, the carousel only inits after the user clicks the reveal button |
| Table → accordion | `assets/js/accordion.js` | Converts tables to accordion layout on mobile via `data-accordion="table"` |
| Sidebar collapse | `assets/js/sidebar.js` | Per-group expand/collapse toggle; state persists to `localStorage["sidebar-groups"]` |
| Take-action copy | `assets/js/take-action.js` | On `/take-action/` only: adds a Copy button to every `<blockquote>` (template scripts for doctor visits, social blurbs). Clipboard API with text-selection fallback. `aria-live="polite"` on label |
| Symptom tracker | `assets/js/tracker.js` | Client-side symptom tracking on `/tracker/`. localStorage only - never transmitted |
| **Inline in `base.html`:** | | |
| Hamburger | (script block) | Opens/closes off-canvas sidebar. Moves focus into sidebar on open (mobile). Esc closes + returns focus to hamburger. Auto-closes when crossing into desktop breakpoint |
| Theme toggle | (script block) | Light/dark toggle with localStorage. First-load respects `prefers-color-scheme: light` only when no stored value |
| Back-to-top | (script block) | Window-scroll-bound (was container-scroll, since fixed). Appears after 300px |
| Bottom-nav current page | (script block) | URL path match → `aria-current="page"` on the matching tab |

The inline block exposes two globals consumed by extracted modules: `window.__searchIndexURL` and `window.__translationsURL`.

## Key File Locations

| Path | Purpose |
|---|---|
| `site.json` | Site config: `base_url`, `brand`, `nav_groups` (3 journeys), `footer_links`, legacy `colors` block, **`semantic`** block (light/dark/constant/scale), `css_files`, `js_files` |
| `build.py` | Python build script (stdlib only) |
| `templates/base.html` | Base page shell: topbar, off-canvas sidebar + backdrop, content, bottom nav (mobile), back-to-top, inline JS for shell behaviors |
| `templates/home.html` | Home page: hero + 3 journey cards + linked stats + Watch & Learn + quiz teaser + carousel + help CTA |
| `templates/page.html` | Single content page (breadcrumbs + TOC + content) |
| `templates/404.html` | 404 page content |
| `assets/css/tokens.css` | `@font-face` for self-hosted Figtree. Loaded first |
| `assets/css/reset.css` | Mobile-first CSS reset + base typography. Replaces the old `base.css` |
| `assets/css/utilities.css` | `u-stack`, `u-cluster`, `u-grid-auto`, `u-skip-link`, `u-visually-hidden`, `u-tap-target`. `:root` breakpoint markers for JS introspection |
| `assets/css/layout.css` | Topbar, off-canvas sidebar, sidebar nav groups (collapsible), shell grid, bottom nav, back-to-top. Safe-area + RTL logical properties throughout |
| `assets/css/components.css` | Cards, buttons, forms, breadcrumbs, accordion |
| `assets/css/pages.css` | Page-specific blocks: home hero/journey cards/stats/videos/quiz-teaser/help-CTA; notable-people gallery grid; take-action copyable-blocks |
| `assets/css/carousel.css` | Carousel-specific |
| `assets/css/tracker.css` | Symptom tracker page |
| `assets/js/*` | See JS systems table above |
| `static/fonts/` | Self-hosted Figtree variable WOFF2 (regular + italic), OFL 1.1 |
| `static/i18n/translations.json` | 26-language translations |
| `static/i18n/_review.json` | **Sidecar** listing keys per language that hold English placeholders pending real translation. Built during Phase 3c |
| `static/icons/`, `static/images/` | Static assets (copied verbatim to `dist/`) |
| `content/*.md` | 21 markdown pages: `_index`, about, adenomyosis, comorbidities, diagnosis, education, endometriosis, faq, fertility, graphic-images, healthcare, medications, mental-health, myths, notable-people, privacy, quiz, research, resources, take-action, tracker, treatments |
| `design/brand.md` | Brand identity v2: tokens, type scale, IA, components |
| `design/ia.md` | Information architecture spec - three primary journeys, page set, URL stability, i18n strategy, privacy |
| `design/css-architecture.md` | CSS architecture: semantic tokens, mobile-first, file structure, scroll model, safe-area, breakpoints |
| `design/accessibility-audit.md` | Phase 5 audit: contrast pairs, keyboard/SR fixes, touch targets, RTL |
| `design/perf-baseline.md` | Pre-overhaul perf baseline |
| `wrangler.toml` | Cloudflare Pages deployment config |

## Template markers

The build script replaces these placeholders:

`{{BASE_URL}}`, `{{META_TITLE}}`, `{{BRAND}}`, `{{DESCRIPTION}}`, `{{PAGE_URL}}`, `{{PAGE_CONTENT}}`, `{{CSS_VARIABLES}}`, `{{CSS_BUNDLE}}`, `{{JS_BUNDLE}}`, `{{STRUCTURED_DATA}}`, `{{SIDEBAR_NAV}}`, `{{FOOTER_LINKS}}`, `{{HOME_CONTENT}}`, `{{TOC}}`, `{{YEAR}}`, `{{OG_IMAGE}}`, `{{OG_TYPE}}`

## Conventions

- **No npm / no bundler** - Python stdlib is the only build tool. All JS is vanilla. JS modules in `assets/js/` are concatenated and minified by `build.py` in the order listed in `site.json:js_files`; only small page-shell scripts stay inline in `templates/base.html`.
- **Adding a JS or CSS module** - Drop the file in `assets/js/` or `assets/css/`, then add its path to `js_files` / `css_files` in `site.json`. Order in those arrays is the load order. `tokens.css` must remain first so `@font-face` resolves before any text renders.
- **Semantic tokens over raw colors** - Components reference `--text`, `--surface`, `--accent`, etc., NOT `--color-gold` / `--color-plum`. The semantic layer is emitted by `build_css_vars()` from `site.json:semantic` (light + dark + constant + scale). Legacy raw tokens still emit for backward compatibility but are not used by new code.
- **Mobile-first CSS** - Base styles target the smallest viewport. Larger viewports add via `@media (min-width: 48rem)` (tablet) and `@media (min-width: 64rem)` (desktop). Breakpoints in `rem` so font-size zoom shifts them proportionally. No `max-width` media queries.
- **Logical properties for RTL** - Use `inset-inline-start/end`, `margin-inline-*`, `padding-inline-*`, `text-align: start/end`. Avoid `left`/`right` for directional positioning; the sidebar uses `[dir="rtl"]` overrides where logical translates aren't enough.
- **Safe-area on mobile** - Every fixed/sticky bottom-anchored element includes `env(safe-area-inset-bottom)`. `viewport-fit=cover` is set on the `<meta name="viewport">` tag.
- **Client-side i18n** - Translations live in `/static/i18n/translations.json`; DOM elements use `data-i18n="key"` (optional `data-i18n-attr="title,aria-label"` and `data-i18n-aria="key"` for aria-label-only). New keys go to `en` first; placeholders propagate to all 26 languages and are tracked in `static/i18n/_review.json` for human translation later. i18n.js auto-falls-back to English when a key is missing.
- **`search: false` frontmatter** - Excludes a page from the search index. Used for `/take-action/`, `/privacy/`. Pages with `draft: true` are excluded from both build and index.
- **`toc: false` frontmatter** - Suppresses the auto-generated table of contents for a page. Used on `/notable-people/` (gallery layout).
- **Accessibility** - Skip-to-content, 3px focus outlines via `--focus-ring` token, 44px min touch targets (`var(--tap-min)`), `aria-current="page"` in sidebar + bottom-nav, `aria-live="polite"` on search results + copy-button label, semantic HTML (`<nav>`, `<article>`, `<main>`, breadcrumb `<ol>`). WCAG AA contrast verified on all semantic token pairs.
- **Privacy** - No third-party requests by default. Symptom data lives only in `localStorage`. Formspree submission is opt-in only and limited to the `/quiz/` result page (when built). Privacy notice at `/privacy/`.
- **Self-hosted fonts** - Figtree variable WOFF2 at `static/fonts/`, loaded via `tokens.css` `@font-face` with `../fonts/...` relative paths (works on both root and subpath deploys). No Google Fonts.
- **No `:root` in CSS** - Tokens emit on `body` (light) + `body.dark-theme` (dark). The only exception is `:root { --bp-tablet/desktop/wide }` in `utilities.css` for JS introspection.
- **No left-border accent bars** - Boxes (TOC, blockquotes, callouts) use a full `border` + `border-radius` instead of a left-only accent stripe. Do not add `border-left` as a decorative element to containers.
- **No `!important`** - CSS structured so specificity conflicts resolve without it. Only exception: `@media (prefers-reduced-motion)`.
- **Cache-busted bundles** - CSS and JS bundles are content-hashed (`bundle.<hash>.css`, `app.<hash>.js`); never reference by static name. Use `{{CSS_BUNDLE}}` / `{{JS_BUNDLE}}`.
- **`{{BASE_URL}}` for internal links** - Never use bare `/foo/` for internal navigation; always `{{BASE_URL}}foo/`. The site deploys to a subpath on GitHub Pages and root on Cloudflare; bare slashes break under subpath.
- **Three-journey navigation** - `site.json:nav_groups` has 3 groups: *Could this be me?* / *I have endo or adeno* / *Learn*. Each `nav-group` is collapsible with localStorage persistence via `sidebar.js`. Bottom nav (mobile) has 4 tabs: Home / Quiz / Learn / Help.
- **No em-dashes** - Use hyphens (`-`) instead of em-dashes (`—`) everywhere: content, comments, commit messages, documentation. Em-dashes cause rendering inconsistencies across browsers and devices.
- **Markdown content** - Custom `md_to_html()` converter with raw HTML passthrough (supports `<details>`, `<summary>`, `<main>`, blockquotes). Frontmatter (after leading `---`): `title`, `description`, `date`, `lastmod`, `draft`, `tags`, `keywords`, `search` (default true), `toc` (default true). Internal `[text](/slug/)` links are rewritten to include `base_url`.
