# CLAUDE.md

## Build / Serve / Deploy

```bash
# Local development
hugo server

# Production build (mirrors GitHub Actions)
hugo --gc --minify --baseURL "https://bloo-berries.github.io/Awesome-Endo-Adeno-Resources/"

# Theme is a git submodule — initialize after cloning
git submodule update --init --recursive
```

Deployed via **GitHub Pages** through `.github/workflows/hugo.yml` (push to `main` triggers build). Also configured for **Cloudflare Pages** via `wrangler.toml` (project name: `one-in-seven`, custom domain: `in7.info`).

## Architecture

**Hugo + Poison theme** with extensive custom overrides. No npm, no bundler — pure Hugo + vanilla JS.

### Inline JS systems (all in `layouts/_default/baseof.html`)

| System | What it does |
|---|---|
| Resource card filtering | Toggle-based filter cards on home page; sidebar links trigger same logic |
| Client-side search | Loads `/index.json`, debounced real-time search (200ms), max 5 results |
| Client-side i18n | Loads `/static/i18n/translations.json`, 27 languages, `data-i18n` attributes, localStorage persistence, RTL support for Arabic |
| Theme toggle | Light/dark mode with localStorage + system preference detection |
| Hamburger menu | Collapsible sidebar overlay on **all screen sizes** (not just mobile), with aria-expanded |
| Table → accordion | Converts tables to accordion layout on mobile via `data-accordion` |
| Details auto-expand | Expands all `<details>` by default (except Case Studies and table accordions) |
| Back-to-top | Smooth scroll, appears after 300px scroll |
| Resource card movement | Moves cards from main content into header bar |

### Search index

`layouts/index.json` generates `/index.json` with title, permalink, summary (200 chars), content (500 chars), and tags.

## Key File Locations

| Path | Purpose |
|---|---|
| `config.toml` | Hugo configuration, menu, theme colors, params |
| `layouts/_default/baseof.html` | Base template — contains **all** inline JS (~347 lines) |
| `layouts/index.html` | Home page with resource card filter grid |
| `layouts/_default/single.html` | Single page template |
| `layouts/partials/sidebar/` | Sidebar: menu, title, search, language picker, copyright |
| `layouts/partials/head/` | Head: fonts, meta, scripts, structured-data (JSON-LD) |
| `layouts/partials/breadcrumbs.html` | Semantic breadcrumb nav |
| `assets/css/custom.css` | All custom CSS (~1500 lines) |
| `wrangler.toml` | Cloudflare Pages deployment config |
| `static/i18n/translations.json` | 27-language translation file |
| `static/icons/`, `static/images/` | Static assets |
| `content/` | Markdown pages: about, endometriosis, adenomyosis, diagnosis, treatment, healthcare, resources |
| `content/posts/` | Blog posts |
| `themes/poison/` | Poison theme (git submodule — do not edit directly) |

## Conventions

- **No npm / no bundler** — Hugo is the only build tool. All JS is vanilla, inline in templates.
- **Client-side i18n** — NOT Hugo's built-in i18n. Translations live in `/static/i18n/translations.json`; DOM elements use `data-i18n="key"` attributes; language stored in localStorage (`site-language`).
- **Accessibility focus** — skip-to-content link, 3px focus outlines, 44px min touch targets, ARIA labels, semantic HTML (`<nav>`, `<article>`, `<main>`, breadcrumb `<ol>`).
- **Fonts** — Inter (UI/headings), Source Serif 4 (body), Monaspace Argon (titles/special). All loaded from Google Fonts / CDN.
- **Theme overrides** — Custom layouts in `/layouts/` override the Poison theme. Never edit files inside `themes/poison/` directly.
- **Markdown content** — Goldmark processor with unsafe HTML enabled (supports `<details>`, `<summary>`, `<main>`). Frontmatter: title, description, date, lastmod, draft, tags, keywords.
- **Sidebar layout** — Sidebar is always off-canvas (hamburger menu) at all screen sizes. The theme's default desktop sidebar is overridden via CSS (`position: fixed`, `transform: translateX(-100%)`). Header bar with site title is always visible.
- **Responsive breakpoint** — Mobile-first design, primary breakpoint at 768px. Resource cards use compact grid on mobile.
