# CLAUDE.md

## Build / Serve / Deploy

```bash
# Build site
python3 build.py

# Serve locally
python3 -m http.server 8000 --directory dist
```

Deployed via **GitHub Pages** through `.github/workflows/deploy.yml` (push to `main` triggers build). Also configured for **Cloudflare Pages** via `wrangler.toml` (project name: `one-in-seven`, custom domain: `1in7.info`).

## Architecture

**Standalone static site** — no framework, no npm, no bundler. A Python build script (stdlib only) converts Markdown content + HTML templates into static pages. All CSS/JS is vanilla and self-contained.

### Build pipeline (`build.py`)

| Function | Purpose |
|---|---|
| `load_config()` | Read `site.json` |
| `get_card_menu(cfg)` | Flat list of nav items for cards/panels (excludes About) |
| `parse_frontmatter(text)` | Split `---` frontmatter from body, parse key-value pairs |
| `md_to_html(text)` | Markdown→HTML: headings (auto-IDs), bold/italic, links (external→`target="_blank"`), images, lists, tables, code blocks, blockquotes, hr, raw HTML passthrough |
| `build_css_vars(config)` | Generate complete `<style>` block: all design tokens for `body` (light) + `body.dark-theme` (dark) — brand colors, gradients, radius, font stack |
| `build_sidebar_nav(config)` | Generate grouped `<nav>` with `<div class="nav-group">` sections, each with `<h3 class="nav-group-label">` and item `<ul>` |
| `build_footer_links(config)` | Generate footer links (About) for sidebar bottom |
| `build_menu_cards(config)` | Generate resource card buttons for homepage |
| `build_filter_panels(pages, config)` | Render each page's content into `<article class="filter-panel">` |
| `build_search_index(pages)` | Generate `index.json` (title, permalink, summary, content, tags) |
| `build_structured_data(config)` | Generate JSON-LD structured data for SEO |
| `main()` | Clean dist/, concat CSS→`dist/css/bundle.css`, concat JS→`dist/js/app.js`, build all pages, copy static assets, write `.nojekyll` + `robots.txt` |

### JS systems

Extracted JS modules live in `assets/js/` and are concatenated into `dist/js/app.js` by the build script. Small systems remain inline in `templates/base.html`.

| System | Location | What it does |
|---|---|---|
| Client-side search | `assets/js/search.js` | Loads `/index.json`, debounced real-time search (200ms), max 5 results, synonym expansion |
| Client-side i18n | `assets/js/i18n.js` | Loads `/i18n/translations.json`, 26 languages, `data-i18n` attributes, localStorage persistence, RTL support for Arabic |
| Image carousel | `assets/js/carousel.js` | Auto-rotating carousel with dot indicators and arrow controls |
| Symptom poll | `assets/js/poll.js` | Checkbox-based poll submitted to Formspree |
| Action modal | `assets/js/action-modal.js` | Modal with symptoms/connect/awareness views, checklists, copy-to-clipboard |
| Codeblock copy | `assets/js/codeblock.js` | Copy button for code blocks (loaded separately via `<script defer>`) |
| Resource card filtering | inline in `base.html` | Toggle-based filter cards on home page; sidebar links trigger same logic |
| Theme toggle | inline in `base.html` | Light/dark mode with localStorage + system preference detection |
| Hamburger menu | inline in `base.html` | Collapsible sidebar overlay on mobile (≤1024px), persistent on desktop |
| Table → accordion | inline in `base.html` | Converts tables to accordion layout on mobile via `data-accordion` |
| Back-to-top | inline in `base.html` | Smooth scroll, appears after 300px scroll |
| Resource card movement | inline in `base.html` | Moves cards from main content into header bar |

### Search index

`build.py` generates `dist/index.json` with title, permalink, summary (200 chars), content (500 chars), and tags.

## Key File Locations

| Path | Purpose |
|---|---|
| `site.json` | Site config: base URL, brand, `nav_groups` (grouped nav), `footer_links`, `colors` (brand + light/dark + gradients), CSS/JS file lists |
| `build.py` | Python build script (stdlib only) |
| `templates/base.html` | Base template — full page shell with sidebar, modal, inline JS |
| `templates/home.html` | Homepage content (cards, videos, poll, carousel, stats) |
| `templates/page.html` | Single page wrapper (breadcrumbs + content) |
| `templates/404.html` | 404 page content |
| `assets/css/base.css` | Clean CSS reset + semantic defaults (~130 lines, all colors via variables) |
| `assets/css/codeblock.css` | Code block styling + syntax highlighting |
| `assets/css/custom.css` | Core site styles — layout, sidebar, components, responsive, print |
| `assets/css/symptom-poll.css` | Symptom poll component styles |
| `assets/css/carousel.css` | Image carousel component styles |
| `assets/css/action-modal.css` | Action modal component styles |
| `assets/js/search.js` | Client-side search with synonym expansion |
| `assets/js/i18n.js` | 26-language translation system with RTL |
| `assets/js/carousel.js` | Image carousel auto-rotate and controls |
| `assets/js/poll.js` | Symptom poll submission |
| `assets/js/action-modal.js` | Action modal views, checklists, copy-to-clipboard |
| `assets/js/codeblock.js` | Code block copy button |
| `design/brand.md` | Brand identity: Figtree font, color tokens, grouped nav, radius/gradient tokens, accessibility |
| `wrangler.toml` | Cloudflare Pages deployment config |
| `static/i18n/translations.json` | 26-language translation file |
| `static/icons/`, `static/images/` | Static assets |
| `content/` | Markdown pages: about, endometriosis, adenomyosis, diagnosis, comorbidities, healthcare, resources, education, myths, research |

## Template markers

The build script replaces these placeholders in templates:

`{{BASE_URL}}`, `{{META_TITLE}}`, `{{BRAND}}`, `{{DESCRIPTION}}`, `{{PAGE_URL}}`, `{{PAGE_CONTENT}}`, `{{CSS_VARIABLES}}`, `{{STRUCTURED_DATA}}`, `{{SIDEBAR_NAV}}`, `{{FOOTER_LINKS}}`, `{{SOCIALS}}`, `{{MENU_CARDS}}`, `{{FILTER_PANELS}}`, `{{HOME_CONTENT}}`, `{{BREADCRUMBS}}`, `{{YEAR}}`

## Conventions

- **No npm / no bundler** — Python stdlib is the only build tool. All JS is vanilla. JS modules in `assets/js/` are concatenated by the build script; inline JS stays in `templates/base.html`.
- **Client-side i18n** — Translations live in `/static/i18n/translations.json`; DOM elements use `data-i18n="key"` attributes; language stored in localStorage (`site-language`).
- **Accessibility focus** — skip-to-content link, 3px focus outlines, 44px min touch targets, ARIA labels, semantic HTML (`<nav>`, `<article>`, `<main>`, breadcrumb `<ol>`).
- **Font** — Figtree (single family for all text). Loaded from Google Fonts. Headings differentiate by weight/size/letter-spacing. See `design/brand.md` for hierarchy.
- **Design tokens** — All colors, gradients, radii, and font stack set by `build_css_vars()` in `build.py` as an injected `<style>` block. Light values on `body`, dark overrides on `body.dark-theme`. No `:root` in CSS, no `body:not(.dark-theme)` selectors.
- **No `!important`** — CSS is structured so specificity conflicts are resolved without `!important`. Only exception: `@media (prefers-reduced-motion)`.
- **Grouped navigation** — `site.json` has `nav_groups` array with 4 groups (Conditions, Getting Care, Support, Research). `build_sidebar_nav()` emits `<div class="nav-group">` with `<h3 class="nav-group-label">`. Flat `menu` array kept for backward compat.
- **Standalone design** — No external dependencies. `assets/css/base.css` provides the CSS reset with variable-based colors. CSS custom properties from `site.json` config.
- **Markdown content** — Custom `md_to_html()` converter with raw HTML passthrough (supports `<details>`, `<summary>`, `<main>`). Frontmatter: title, description, date, lastmod, draft, tags, keywords.
- **Sidebar layout** — Persistent on desktop (>1024px) with content margin-left. Off-canvas on mobile (≤1024px) with hamburger toggle and overlay.
- **Responsive breakpoints** — Mobile-first design. Primary: 768px (layout). Secondary: 1024px (sidebar persistent). Resource cards use compact grid on mobile.
