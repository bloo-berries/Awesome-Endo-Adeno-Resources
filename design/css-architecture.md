# 1 in 7 — CSS Architecture (mobile-first rebuild)

Status: **draft v2 — addresses adversarial review findings**. Phase 2 of the UI/UX overhaul. Pairs with `design/ia.md` (Phase 1).

Changes from v1: corrected scroll-model analysis (§3 — current site uses viewport scroll, not container scroll); added safe-area + dynamic-viewport handling (§7); self-host Figtree (§9); specified `build_css_vars()` interface (§2.6); reframed "token diet" as "semantic layer" (§2); added type-scale rationale (§2.5); prefixed utilities with `u-` (§5); added `{{BASE_URL}}` templating note (§6); sidebar floor raised to language-picker-safe (§6).

---

## 1. Problem statement

Current CSS architecture has four structural issues:

1. **Desktop-first** — base styles target desktop; `@media (max-width: 768px)` strips back for mobile. Inverts modern convention; mobile bugs are always the last fix.
2. **No semantic layer over the brand palette** — 11 brand color tokens with overlapping intent (`--color-gold` / `--color-gold-light` / `--color-gold-bright` / `--color-gold-warm` / `--color-gold-hover`), and components consume the raw tokens directly. No abstraction means a theme change requires editing every component.
3. **File overlap** — 10 CSS files; `custom.css`, `components.css`, and `layout.css` each contain partial overlapping concerns.
4. **Fixed-pixel layout constraints** — sidebar at fixed 280px, content at fixed `margin-left: 280px`, breakpoints as hard cliffs at 768/1024 px.

Plus a confirmed latent bug: `assets/js/codeblock.js`-adjacent back-to-top logic in `templates/base.html` (line 384–399) binds to `.content.container.scrollTop` on desktop, but `.content.container { overflow-y: visible }` means the container doesn't scroll — viewport does. The back-to-top button never appears on desktop. Phase 2 fixes this.

Goal: constraint-based, mobile-first system with a thin semantic layer over the brand palette, viewport-anchored layout, and explicit safe-area handling.

---

## 2. Semantic token layer

Two-layer color system. Raw brand palette stays in `site.json` for theme authoring; a new **semantic layer** is emitted by `build_css_vars()` and is what every component consumes.

### 2.1 Raw palette (unchanged authoring surface)

`site.json:colors.brand` keeps the existing structure. Phase 2 collapses redundancies:

```
gold        = #C4982A    (was: gold)
gold-warm   = #FFD166    (was: gold-warm)
plum        = #6B3A5C    (was: plum)
plum-deep   = #5A2D3E    (was: plum-deep / plum-dark / burgundy — merged)
brown       = #8B4513    (was: brown)
error       = #dc3545    (was: error)
```

Dropped from `site.json:colors.brand`: `gold-light`, `gold-bright`, `gold-hover`, `plum-dark`, `burgundy`, `plum-deep` (duplicate of plum-dark/burgundy in practice). Reason: the variants were used to express hover/active states that the semantic layer now handles via opacity/lightness modifiers.

7 raw colors instead of 11.

### 2.2 Semantic layer (new — what components consume)

Component CSS references **only** these names:

| Token | Light value | Dark value | Used for |
|---|---|---|---|
| `--text` | `#2D1525` | `#F5E6D0` | Body text |
| `--text-muted` | `#7A5A3A` | `#C4A07A` | Captions, metadata, dates |
| `--text-on-warm` | `#1A0A10` | `#1A0A10` | Text on warm gold surfaces |
| `--text-on-deep` | `#F5E6D0` | `#F5E6D0` | Text on plum-deep surfaces |
| `--surface` | `#F5E6D0` | `#1A0E14` | Page background |
| `--surface-raised` | `#EDD8BC` | `#2D1525` | Cards, panels |
| `--surface-warm` | `#C4873A` | `#C4873A` | Sidebar, hero accent (constant across themes) |
| `--surface-deep` | `#6B3A5C` | `#5A2D3E` | Stat tiles, modal header strip |
| `--accent` | `#8B4513` | `#E8B84A` | Links, focus, primary CTA |
| `--accent-hover` | `#6B2D3E` | `#F0D060` | Link hover, CTA hover |
| `--border` | `rgba(139,69,19,0.15)` | `rgba(255,255,255,0.1)` | Subtle dividers |
| `--border-strong` | `#C4982A` | `#C4982A` | Focus rings, emphasized borders |
| `--error` | `#dc3545` | `#dc3545` | Validation errors |
| `--code` | `#2D1525` | `#F5E6D0` | Inline code text |
| `--code-bg` | `#F0E0C8` | `#3D1F30` | Inline code background |

**Naming convention** — `--text-color` (old, kept transitional) → `--text` (new). Migration: Phase 2 emits **both** name forms from `build_css_vars()` so old components keep working while we rewrite them. Phase 3 components use new names. Phase 4 deletes the transitional aliases.

### 2.3 Gradients

2 semantic gradients (down from 5):

| Token | Value | Used for |
|---|---|---|
| `--gradient-warm` | `linear-gradient(180deg, #C4873A 0%, #9B5A3A 40%, #6B3A5C 100%)` | Sidebar |
| `--gradient-deep` | `linear-gradient(145deg, #6B3A5C 0%, #5A2D3E 100%)` | Stat tiles, take-action page hero |

Dropped: `--gradient-component`, `--gradient-modal`, `--gradient-tile-light`, `--gradient-back-to-top`. Surfaces that used these become flat `--surface-raised` or `--surface-deep`. **Adversarial review note:** the warm-to-burgundy gradient on the modal was what made it feel emergency-actionable. Mitigation: the `/take-action/` page (which replaces the modal, see `ia.md` §10) gets a top hero strip using `--gradient-deep` to retain that urgency-signaling visual. Quiz result panels also use `--gradient-deep` for emphasis. So `--gradient-deep` carries the "action-required" semantic, not just decoration.

### 2.4 Radius scale

3 radii (down from 4):

| Token | Value | Used for |
|---|---|---|
| `--radius-sm` | `6px` | Inputs, small buttons, badges |
| `--radius-md` | `10px` | Cards, panels, modal content |
| `--radius-pill` | `9999px` | Pills, avatar masks |

Dropped: `--radius-lg` (12px). The 2px delta wasn't legibly different from `--radius-md` in shipped UI.

### 2.5 Spacing scale (new)

Currently no spacing tokens. Add a 5-step scale:

| Token | Value | Used for |
|---|---|---|
| `--space-xs` | `0.25rem` (4px) | Inline gaps, icon-to-text |
| `--space-sm` | `0.5rem` (8px) | Tight groups, badge padding |
| `--space-md` | `1rem` (16px) | Default block spacing, card padding |
| `--space-lg` | `1.5rem` (24px) | Section spacing, hero padding |
| `--space-xl` | `2.5rem` (40px) | Major section breaks |

Plus two fluid spacing tokens for layout breathing room:

```
--space-section: clamp(2rem, 5vw, 4rem)
--container-padding: clamp(1rem, 4vw, 2rem)
```

### 2.6 Type scale (new) — rationale included

Modular scale with ratio **1.2** ("minor third"), base size `1rem` at the 768px tablet breakpoint. Fluid `clamp()` interpolates between mobile floor and desktop ceiling.

Math per step (`base × ratio^n`):

| Step | Base × ratio | Floor (mobile) | Ceiling (desktop) | Token value | Used for |
|---|---|---|---|---|---|
| -1 | 1 × 1.2⁻¹ = 0.833 | 0.875rem | 0.95rem | `clamp(0.875rem, 0.5vw + 0.75rem, 0.95rem)` | `--text-sm` — captions |
| 0 | 1 × 1.2⁰ = 1.0 | 1rem | 1.125rem | `clamp(1rem, 0.5vw + 0.85rem, 1.125rem)` | `--text-base` — body |
| 1 | 1 × 1.2¹ = 1.2 | 1.125rem | 1.25rem | `clamp(1.125rem, 0.75vw + 0.9rem, 1.25rem)` | `--text-lg` — lead |
| 2 | 1 × 1.2² = 1.44 | 1.25rem | 1.5rem | `clamp(1.25rem, 1vw + 1rem, 1.5rem)` | `--text-xl` — h3 |
| 3 | 1 × 1.2³ = 1.73 | 1.5rem | 2rem | `clamp(1.5rem, 2vw + 1rem, 2rem)` | `--text-2xl` — h2 |
| 4 | 1 × 1.2⁴ = 2.07 | 2rem | 2.75rem | `clamp(2rem, 3vw + 1rem, 2.75rem)` | `--text-3xl` — h1, hero |
| -2 | 1 × 1.2⁻² = 0.694 | 0.75rem | 0.85rem | `clamp(0.75rem, 0.4vw + 0.65rem, 0.85rem)` | `--text-xs` — badges |

Why ratio 1.2: large enough to differentiate h1/h2/h3, small enough that body and lead don't look discontinuous. Synthwave/luxury serifs use larger ratios (1.333+); patient-facing reading-heavy interfaces benefit from tighter ratios.

### 2.7 `build_css_vars()` interface

Adversarial review correctly noted v1 didn't specify whether semantic mappings live in Python or JSON. Decision: **in `site.json`** (data, not logic).

Add to `site.json`:

```json
"semantic": {
  "light": {
    "text": "#2D1525",
    "text-muted": "#7A5A3A",
    "surface": "#F5E6D0",
    ...
  },
  "dark": {
    "text": "#F5E6D0",
    "text-muted": "#C4A07A",
    "surface": "#1A0E14",
    ...
  },
  "constant": {
    "surface-warm": "#C4873A",
    "border-strong": "#C4982A",
    "error": "#dc3545",
    ...
  }
}
```

`build_css_vars()` emits three CSS blocks:
1. `body { --text: ...; --surface: ...; ... }` from `semantic.light` + `semantic.constant`
2. `body.dark-theme { --text: ...; --surface: ...; ... }` from `semantic.dark` + `semantic.constant`
3. Transitional aliases (e.g., `--text-color: var(--text);`) emitted under both `body` and `body.dark-theme` until Phase 4 cleanup removes them.

Spacing, radius, type-scale tokens are constants (not theme-switching) and are emitted once outside the theme blocks. Add to `site.json:semantic.scale`:

```json
"scale": {
  "radius-sm": "6px",
  "radius-md": "10px",
  "space-md": "1rem",
  ...
}
```

This keeps `build_css_vars()` to a small Python loop over JSON keys, no hardcoded color logic in the build script.

---

## 3. Scroll model (corrected from v1)

Adversarial review's v1 assertion that the site uses container-scroll on desktop was based on the back-to-top JS. Verified: `.content.container` has `overflow-y: visible` (`assets/css/layout.css:34`), so the container doesn't actually scroll. The site uses **viewport-level scroll** (body content grows past viewport height; root scroller is `html`/`body`).

The back-to-top JS that binds `container.addEventListener('scroll', ...)` on desktop is **latent dead code** — the listener never fires because the container has no scroll. Visible-on-mobile only.

### Phase 2 changes

1. **Standardize on `window.pageYOffset`** in back-to-top JS for both mobile and desktop. Remove the `isMobile`-branched scroll source.
2. **Top bar uses `position: sticky; top: 0`** on its place in the body's natural flow. Works because we're already viewport-scrolling.
3. **Drop the dual scrollbar styling** in `assets/css/layout.css:5–22` that targets both `.container.content` and the body scrollbar — only the body's scrollbar exists in practice.
4. **Sidebar gets its own scroll** (it's tall and may overflow when collapsed groups are expanded). `aside.sidebar { overflow-y: auto; }` — verified safe with `position: fixed` (or `position: sticky; top: 0; height: 100dvh`).

### Tested before commit

Browser matrix: Safari 16+, Chrome 110+, Firefox 110+, mobile Safari iOS 16+, Chrome Android. The `position: sticky` + `dvh` combo is safe in this matrix.

---

## 4. Breakpoint inversion (mobile-first)

### 4.1 Convention

Base styles target mobile (320px–767px viewport). All `@media` queries are `min-width`, layered in ascending order. Breakpoints in `rem` so a user's font-size zoom shifts breakpoints proportionally — accessibility win.

```css
/* Base: mobile (no media query) */
.card { padding: var(--space-md); }

@media (min-width: 48rem) { /* tablet */
  .card { padding: var(--space-lg); }
}

@media (min-width: 64rem) { /* desktop */
  .card { padding: var(--space-xl); }
}
```

### 4.2 Breakpoint values

| Token (doc-only) | Value | Equivalent | Triggers |
|---|---|---|---|
| `--bp-tablet` | `48rem` | 768px | 2-col layouts, larger touch targets |
| `--bp-desktop` | `64rem` | 1024px | Persistent sidebar, multi-column grids |
| `--bp-wide` | `80rem` | 1280px | Max content width caps |

Note: CSS custom properties can't be referenced in `@media` declarations. The tokens above are documentation only; actual `@media` rules hardcode the values. A `:root { --bp-tablet: 48rem; }` declaration is emitted for JS to read via `getComputedStyle()`.

### 4.3 Removal of `max-width` media queries

Every current `@media (max-width: ...)` rule in `responsive.css` and inline elsewhere gets rewritten as a `min-width` delta from mobile base.

---

## 5. File consolidation

### Current (10 files, ~2,094 lines)

```
base.css            214   reset + typography + tables + code
custom.css          194   site-wide overrides
layout.css          145   container, grid, content flow
sidebar.css         389   sidebar nav + mobile overlay
components.css      683   cards, buttons, breadcrumbs, all components
responsive.css       97   @media max-width overrides
symptom-poll.css    161   poll-specific
carousel.css        144   carousel-specific
action-modal.css    600   modal + 3 sub-views
tracker.css         267   tracker page
```

### Target (6 files, ~1,400 lines expected)

```
tokens.css       Semantic tokens, theme switches, spacing, type, breakpoints
reset.css        Reset, base typography, tables, code, blockquotes, links
layout.css       Top bar, sidebar, bottom nav, container, content shell, safe-area
components.css   Cards, buttons, forms, breadcrumbs, accordion, search, take-action sub-views
pages.css        Page-specific blocks: home journey cards, hero, stats, poll, carousel, tracker
utilities.css    .u-stack, .u-cluster, .u-grid-auto, .u-visually-hidden, .u-skip-link
```

### Migration tactic (revised from v1)

v1 promised "stays buildable at every commit" without explaining how. Concrete sequence:

1. **Land `tokens.css` as pure addition** (semantic + scale tokens, transitional aliases for old names). Existing components keep using old names; new tokens are dormant until referenced. ✅ Buildable.
2. **Land `utilities.css` as pure addition** (u-prefixed classes). Not yet used anywhere. ✅ Buildable.
3. **Land `reset.css` next to `base.css`** (mobile-first, no overlapping selectors). Don't delete `base.css` yet — both ship. Test for selector conflicts. ✅ Buildable.
4. **Rewrite layout shell in `layout.css`** (new top bar, off-canvas sidebar, bottom nav). Old shell coexists; the new template references new layout, old templates reference old. ✅ Buildable.
5. **Migrate `components.css` selector-by-selector** to consume semantic tokens. Each commit changes one component, drops corresponding rules from `custom.css`. ✅ Buildable.
6. **Move home-page styles to `pages.css`** in one commit (`symptom-poll.css` + `carousel.css` content + home blocks from `components.css`). Delete the source files. ✅ Buildable.
7. **Migrate `action-modal.css`** → small subset of take-action sub-view CSS into `components.css`. Delete `action-modal.css`. ✅ Buildable.
8. **Migrate `tracker.css`** → tracker-specific block at end of `pages.css`. Delete `tracker.css`. ✅ Buildable.
9. **Delete `responsive.css`** once every `max-width` rule has been inverted. ✅ Buildable.
10. **Delete `base.css`** and **`custom.css`** when all rules have moved. ✅ Buildable.
11. **Update `site.json:css_files`** at each step to add new files and remove deleted ones in the bundle.
12. **Remove transitional aliases from `tokens.css`** once no component references old names. ✅ Buildable.

Each step ships green. The site is deployable after every commit. Phase 2 is roughly 12 commits.

---

## 6. Layout shell rewrite

### 6.1 Markup

```html
<body class="dark-theme">
  <a class="u-skip-link" href="#main-content">Skip to content</a>

  <header class="topbar">
    <button class="topbar-menu" aria-label="Menu">≡</button>
    <a class="topbar-brand" href="{{BASE_URL}}">1 in 7</a>
    <div class="topbar-search">
      <input type="search" id="search-input" />
      <div class="search-results" id="search-results"></div>
    </div>
    <div class="topbar-actions u-cluster">
      <button class="topbar-lang" aria-haspopup="listbox" aria-expanded="false">EN ▾</button>
      <button class="topbar-theme" aria-label="Toggle theme">☀</button>
    </div>
  </header>

  <div class="shell">
    <aside class="sidebar" id="sidebar" data-open="false">…</aside>
    <main class="content" id="main-content">
      {{PAGE_CONTENT}}
    </main>
  </div>

  <nav class="bottomnav" aria-label="Primary">
    <a href="{{BASE_URL}}" class="bottomnav-item">Home</a>
    <a href="{{BASE_URL}}quiz/" class="bottomnav-item">Quiz</a>
    <a href="{{BASE_URL}}endometriosis/" class="bottomnav-item">Learn</a>
    <a href="{{BASE_URL}}take-action/" class="bottomnav-item">Help</a>
  </nav>
</body>
```

**`{{BASE_URL}}` templating** — every internal link uses `{{BASE_URL}}` (already replaced by `build.py`). Never use bare `/` for internal links; the site deploys to both a root (Cloudflare Pages) and a subpath (GitHub Pages: `/Awesome-Endo-Adeno-Resources/`). Bare-slash links break under the subpath deployment.

### 6.2 Shell layout

```css
.shell {
  display: grid;
  grid-template-columns: 1fr; /* mobile: single column */
}

@media (min-width: 64rem) {
  .shell {
    grid-template-columns: minmax(17.5rem, 20rem) 1fr; /* sidebar + content */
  }
  .bottomnav { display: none; }
}
```

**Sidebar width floor raised to 17.5rem (280px)** — adversarial review flagged that 16rem (256px) wouldn't fit the 26-language picker. With the language picker moved to the top bar (per `ia.md` §8), the floor could theoretically come down, but 17.5rem also accommodates long sidebar group labels in German/Russian/Polish without wrap. Keep the existing 280px floor.

### 6.3 Topbar

```css
.topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: var(--space-sm) var(--container-padding);
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--space-sm);
  align-items: center;
  min-block-size: var(--tap-min);
}

@media (min-width: 64rem) {
  .topbar-menu { display: none; }
}
```

Search input collapses to icon on mobile, expands on focus via grid-template-columns transition.

### 6.4 Off-canvas sidebar (mobile)

```css
.sidebar {
  position: fixed;
  inset: 0 30% 0 0; /* leave 30% on right for backdrop tap-to-close */
  background: var(--surface-warm);
  transform: translateX(-100%);
  transition: transform 200ms ease-out;
  z-index: 40;
  overflow-y: auto;
  padding-bottom: env(safe-area-inset-bottom);
}

.sidebar[data-open="true"] {
  transform: translateX(0);
}

@media (min-width: 64rem) {
  .sidebar {
    position: sticky;
    top: 0;
    inset: auto;
    transform: none;
    height: 100dvh;
  }
}
```

Backdrop is a sibling `.sidebar-backdrop` with `position: fixed; inset: 0; z-index: 39` that becomes interactive when sidebar opens. Tap closes the sidebar.

### 6.5 Bottom nav (mobile only)

```css
.bottomnav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 30;
  background: var(--surface);
  border-top: 1px solid var(--border);
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  padding-bottom: env(safe-area-inset-bottom);
}

.bottomnav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-block-size: 4rem;
  color: var(--text-muted);
  font-size: var(--text-xs);
  gap: 2px;
}

.bottomnav-item[aria-current="page"] {
  color: var(--accent);
}

/* Hide when a dialog is open — prevents clickjacking-adjacent intercepts */
body:has([role="dialog"][aria-modal="true"]) .bottomnav { display: none; }

@media (min-width: 64rem) {
  .bottomnav { display: none; }
}
```

**Content offset** for the bottom nav:

```css
.content {
  padding-bottom: calc(4rem + env(safe-area-inset-bottom) + var(--space-md));
}

@media (min-width: 64rem) {
  .content { padding-bottom: var(--space-xl); }
}
```

**Back-to-top relocates above the bottom nav on mobile:**

```css
.back-to-top {
  position: fixed;
  bottom: calc(4rem + env(safe-area-inset-bottom) + 1rem);
  right: 1rem;
}

@media (min-width: 64rem) {
  .back-to-top {
    bottom: 1rem; /* no bottom nav on desktop */
  }
}
```

### 6.6 Dynamic viewport handling

Use `dvh` (dynamic viewport height) for any full-height container so layout doesn't jump when iOS Safari's URL bar slides up/down:

```css
.sidebar { height: 100dvh; }  /* not 100vh */
[role="dialog"].modal-overlay { height: 100dvh; }
```

`dvh` support: Safari 15.4+, Chrome 108+, Firefox 101+. Fallback `vh` for older browsers if needed (`height: 100vh; height: 100dvh;`).

---

## 7. Safe-area + dynamic-viewport handling (consolidated)

All fixed/sticky bottom-anchored elements **must** include `env(safe-area-inset-bottom)`. The audit list:

- `.bottomnav` — bottom: 0 with `padding-bottom: env(safe-area-inset-bottom)`
- `.back-to-top` — bottom calc includes `env(safe-area-inset-bottom)` on mobile
- `.content` — padding-bottom on mobile clears the nav and includes safe-area

For top-anchored elements:

- `.topbar` — sticky; the system top-bar (notch area) is handled by the browser, no manual inset needed
- `.sidebar` (desktop) — `height: 100dvh` ensures it doesn't extend past visible viewport when URL bar is visible

Required `<meta>` viewport tag (verified present in `templates/base.html:8`): `<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">`. **The current site is missing `viewport-fit=cover`** — without it, `env(safe-area-inset-*)` returns 0 on iOS even with notch devices. Phase 2 adds this to the meta tag.

---

## 8. Layout primitives (new utilities, `u-` prefixed)

Three core classes solve 90% of layouts. Defined in `utilities.css`, all prefixed `u-` to prevent collision with author-written Markdown content classes.

### `.u-stack` — vertical rhythm

```css
.u-stack > * + * {
  margin-top: var(--stack-space, var(--space-md));
}
```

### `.u-cluster` — horizontal wrap

```css
.u-cluster {
  display: flex;
  flex-wrap: wrap;
  gap: var(--cluster-gap, var(--space-sm));
  align-items: center;
}
```

### `.u-grid-auto` — responsive auto-grid

```css
.u-grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, var(--grid-min, 16rem)), 1fr));
  gap: var(--grid-gap, var(--space-md));
}
```

Items wrap when they hit `--grid-min`, no breakpoint queries needed. **Browser support note:** the nested `min()` inside `minmax()` inside `repeat(auto-fit, ...)` is supported in Safari 14+, Chrome 88+, Firefox 79+. Older Safari (≤13) renders as a single column instead of broken grid — acceptable graceful degradation.

### Other utilities

- `.u-skip-link` — visually-hidden skip nav, becomes visible on focus
- `.u-visually-hidden` — for screen-reader-only content
- `.u-sr-text` — alias for visually-hidden (semantic name)
- `.u-tap-target` — `min-block-size: var(--tap-min); min-inline-size: var(--tap-min);` for touch ergonomics

---

## 9. Self-host Figtree (privacy, performance)

Current site loads Figtree from Google Fonts (`templates/base.html:17`). Per German court ruling on Google Fonts (2022) and GDPR Article 6, dynamically loading Google Fonts leaks the user's IP to Google without consent. Phase 2 self-hosts.

### Implementation

1. Download Figtree variable font (weight range 300–900, normal + italic) from Google Fonts archives or the font's GitHub repository.
2. Place WOFF2 files at `static/fonts/figtree.woff2` (regular) and `static/fonts/figtree-italic.woff2` (italic).
3. Replace `<link rel="stylesheet" href="https://fonts.googleapis.com/...">` in `templates/base.html` with a self-hosted `@font-face` block in `tokens.css`:

```css
@font-face {
  font-family: 'Figtree';
  font-style: normal;
  font-weight: 300 900;
  font-display: swap;
  src: url('/fonts/figtree.woff2') format('woff2-variations');
}
@font-face {
  font-family: 'Figtree';
  font-style: italic;
  font-weight: 300 900;
  font-display: swap;
  src: url('/fonts/figtree-italic.woff2') format('woff2-variations');
}
```

4. Add `<link rel="preload" as="font" href="{{BASE_URL}}fonts/figtree.woff2" type="font/woff2" crossorigin>` to base.html to avoid FOIT.
5. Remove `<link rel="preconnect" href="https://fonts.googleapis.com">` and the Google Fonts stylesheet link.
6. `build.py` already copies `static/*` into `dist/` verbatim, so `static/fonts/` flows through automatically.

### License check

Figtree is licensed under the Open Font License (OFL 1.1) — self-hosting is permitted.

---

## 10. Accessibility constants

| Token | Value | Used for |
|---|---|---|
| `--focus-ring` | `3px solid var(--border-strong)` | Outline on focusable elements |
| `--focus-offset` | `2px` | `outline-offset` |
| `--tap-min` | `44px` | Minimum touch target dimension |

Touch-target audit (Phase 5): every interactive must have `min-block-size: var(--tap-min)` AND `min-inline-size: var(--tap-min)`, with ≥8px gap between adjacent targets.

---

## 11. Dark mode default — preserved

Current site ships `<body class="dark-theme">` from the server. Phase 2 preserves this.

Refinement: respect user preference on **first load only** when no localStorage value exists:

```js
const stored = localStorage.getItem('theme');
if (!stored && window.matchMedia('(prefers-color-scheme: light)').matches) {
  document.body.classList.remove('dark-theme');
}
```

Returning users always get their stored choice. First-time light-OS users get light by default; first-time dark-OS users (and users with no OS preference) keep the served dark. Small a11y win without violating the "dark default" non-negotiable.

---

## 12. Performance budget

Baseline (current site, no measurement done yet — Phase 2 step 0 is to measure):

- CSS bundle uncompressed: 2,094 lines (~52 KB estimated)
- JS bundle uncompressed: 9 files totaling ~1,041 lines (~28 KB estimated)
- Google Fonts: external request

Phase 2 targets:

- CSS bundle minified + gzipped: under **15 KB**
- JS bundle minified + gzipped: under **10 KB**
- Critical CSS: continue inlining via `{{CSS_VARIABLES}}`
- Web fonts: self-hosted with `preload` (one request, no DNS lookup for fonts.googleapis.com)
- First Contentful Paint target: <1s on 3G Fast (Chrome DevTools throttle)

Measurement: WebPageTest or Chrome DevTools Lighthouse run on `https://1in7.info` before and after each phase. Recorded in `design/perf-baseline.md` (created in Phase 2 step 0).

---

## 13. What gets deleted in Phase 2

Files removed once consolidation lands:
- `assets/css/custom.css` (folded into `pages.css` + `components.css`)
- `assets/css/responsive.css` (eliminated; mobile-first base means no top-level `@media` file)
- `assets/css/symptom-poll.css`, `assets/css/carousel.css` (folded into `pages.css` — home-page-only)
- `assets/css/action-modal.css` (mostly deleted; small subset moves to `components.css`)
- `assets/css/base.css` (replaced by `reset.css` + `tokens.css`)

Net file count: 10 → 6.

External resource removed:
- Google Fonts (preconnect + stylesheet) — self-hosted instead.

---

## 14. Order of operations

Phase 2 can run in parallel with Phase 1 (IA). They sync at Phase 3 (home rebuild). Order within Phase 2:

0. **Measure baseline perf** (Lighthouse run, record in `design/perf-baseline.md`).
1. Add `assets/css/tokens.css` with the new semantic + spacing + type tokens, plus transitional aliases for old names.
2. Update `build_css_vars()` to emit from `site.json:semantic` block. Update `site.json` with new `semantic` structure.
3. Add `assets/css/utilities.css` with `u-`prefixed primitives.
4. Add `viewport-fit=cover` to the `<meta>` viewport tag.
5. Self-host Figtree (download font, add `@font-face`, remove Google Fonts links, add preload).
6. Rewrite `base.css` → `reset.css` as mobile-first.
7. Build the new shell (top bar, off-canvas sidebar, bottom nav) in a new `layout.css`. New shell ships behind a template toggle until Phase 3.
8. Fix back-to-top JS to use `window.pageYOffset` unconditionally.
9. Consolidate `components.css`, dropping overlap with `custom.css`.
10. Move home-page styles to `pages.css`, delete `symptom-poll.css` and `carousel.css`.
11. Migrate `action-modal.css` to take-action sub-view styles in `components.css`. Delete `action-modal.css`.
12. Migrate `tracker.css` into `pages.css`. Delete `tracker.css`.
13. Delete `responsive.css` once all `max-width` rules have been inverted.
14. Delete `base.css` and `custom.css`.
15. Update `site.json:css_files` to reflect final 6-file order.
16. Remove transitional token aliases.

Each step is a self-contained commit; site stays deployable throughout.

---

## 15. Decisions made (v1 had these as "open")

1. ~~Bottom-nav scroll-hide?~~ **No** — static, simpler, no scroll-direction state to manage (§6.5).
2. ~~Sidebar minmax?~~ **`minmax(17.5rem, 20rem)`** — keeps current floor; allows wider sidebars on large screens (§6.2).
3. ~~Gradient cut visual review?~~ **Cut to 2** — `--gradient-deep` carries the urgency signal previously held by `--gradient-modal` (§2.3).
4. ~~Radius drop to 3?~~ **Yes** — 12px vs 10px wasn't legibly different (§2.4).
5. ~~rem-based breakpoints?~~ **Yes** — accessibility win for zoom users (§4.1).

### Remaining open items

None blocking. The CSS rebuild can begin immediately on tokens, utilities, fonts, and meta-tag updates while Phase 1 IA decisions about quiz content and treatments-hub copy proceed in parallel.
