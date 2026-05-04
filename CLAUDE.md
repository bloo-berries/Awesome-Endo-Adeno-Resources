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

### JS systems

Extracted JS modules live in `assets/js/` and are bundled via Hugo Pipes `resources.Concat`, then inlined in `baseof.html`. Small systems remain inline.

| System | Location | What it does |
|---|---|---|
| Client-side search | `assets/js/search.js` | Loads `/index.json`, debounced real-time search (200ms), max 5 results, synonym expansion |
| Client-side i18n | `assets/js/i18n.js` | Loads `/static/i18n/translations.json`, 27 languages, `data-i18n` attributes, localStorage persistence, RTL support for Arabic |
| Image carousel | `assets/js/carousel.js` | Auto-rotating carousel with dot indicators and arrow controls |
| Symptom poll | `assets/js/poll.js` | Checkbox-based poll submitted to Formspree |
| Action modal | `assets/js/action-modal.js` | Modal with symptoms/connect/awareness views, checklists, copy-to-clipboard |
| Resource card filtering | inline in `baseof.html` | Toggle-based filter cards on home page; sidebar links trigger same logic |
| Theme toggle | inline in `baseof.html` | Light/dark mode with localStorage + system preference detection |
| Hamburger menu | inline in `baseof.html` | Collapsible sidebar overlay on **all screen sizes**, with aria-expanded |
| Table → accordion | inline in `baseof.html` | Converts tables to accordion layout on mobile via `data-accordion` |
| Back-to-top | inline in `baseof.html` | Smooth scroll, appears after 300px scroll |
| Resource card movement | inline in `baseof.html` | Moves cards from main content into header bar |

### Search index

`layouts/index.json` generates `/index.json` with title, permalink, summary (200 chars), content (500 chars), and tags.

## Key File Locations

| Path | Purpose |
|---|---|
| `config.toml` | Hugo configuration, menu, theme colors, params |
| `layouts/_default/baseof.html` | Base template — inline JS + bundled extracted JS (~498 lines) |
| `layouts/index.html` | Home page with resource card filter grid |
| `layouts/_default/single.html` | Single page template |
| `layouts/partials/sidebar/` | Sidebar: menu, title, search, language picker, copyright |
| `layouts/partials/head/` | Head: fonts, meta, scripts, stylesheets, structured-data (JSON-LD) |
| `layouts/partials/head/stylesheets.html` | CSS bundle override (adds extracted CSS to Hugo Pipes concat) |
| `layouts/partials/breadcrumbs.html` | Semantic breadcrumb nav |
| `assets/css/custom.css` | Core custom CSS (~1,823 lines) |
| `assets/css/symptom-poll.css` | Symptom poll component styles (~203 lines) |
| `assets/css/carousel.css` | Image carousel component styles (~159 lines) |
| `assets/css/action-modal.css` | Action modal component styles (~777 lines) |
| `assets/js/search.js` | Client-side search with synonym expansion |
| `assets/js/i18n.js` | 27-language translation system with RTL |
| `assets/js/carousel.js` | Image carousel auto-rotate and controls |
| `assets/js/poll.js` | Symptom poll submission |
| `assets/js/action-modal.js` | Action modal views, checklists, copy-to-clipboard |
| `design/brand.md` | Brand identity: typography, colors, accessibility, UI patterns |
| `wrangler.toml` | Cloudflare Pages deployment config |
| `static/i18n/translations.json` | 27-language translation file |
| `static/icons/`, `static/images/` | Static assets |
| `content/` | Markdown pages: about, endometriosis, adenomyosis, diagnosis, treatment, healthcare, resources |
| `content/posts/` | Blog posts |
| `themes/poison/` | Poison theme (git submodule — do not edit directly) |

## Conventions

- **No npm / no bundler** — Hugo is the only build tool. All JS is vanilla. Larger systems are in `assets/js/` and bundled via Hugo Pipes; smaller systems remain inline in `baseof.html`.
- **Client-side i18n** — NOT Hugo's built-in i18n. Translations live in `/static/i18n/translations.json`; DOM elements use `data-i18n="key"` attributes; language stored in localStorage (`site-language`).
- **Accessibility focus** — skip-to-content link, 3px focus outlines, 44px min touch targets, ARIA labels, semantic HTML (`<nav>`, `<article>`, `<main>`, breadcrumb `<ol>`).
- **Fonts** — Inter (UI), Source Serif 4 (body), Monaspace Argon (display/title headings h2-h4). All loaded from Google Fonts / CDN. See `design/brand.md` for full typography system.
- **Theme overrides** — Custom layouts in `/layouts/` override the Poison theme. Never edit files inside `themes/poison/` directly.
- **Markdown content** — Goldmark processor with unsafe HTML enabled (supports `<details>`, `<summary>`, `<main>`). Frontmatter: title, description, date, lastmod, draft, tags, keywords.
- **Sidebar layout** — Sidebar is always off-canvas (hamburger menu) at all screen sizes. The theme's default desktop sidebar is overridden via CSS (`position: fixed`, `transform: translateX(-100%)`). Header bar with site title is always visible.
- **Responsive breakpoint** — Mobile-first design, primary breakpoint at 768px. Resource cards use compact grid on mobile.
