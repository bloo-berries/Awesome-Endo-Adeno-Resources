# 1 in 7 — Brand Identity (v2)

Updated 2026-05-28 after the UI/UX overhaul (Phases 1–5). Pairs with:

- `design/ia.md` — information architecture spec
- `design/css-architecture.md` — token system, mobile-first CSS, file structure
- `design/accessibility-audit.md` — WCAG AA verification, RTL coverage

---

## 1. Brand

- **Name:** 1 in 7
- **Domain:** 1in7.info
- **Mission:** A comprehensive resource hub for navigating Endometriosis and adenomyosis. The "1 in 7" framing reflects the real prevalence — not the under-counted "1 in 10" that's still commonly cited.
- **Voice:** Compassionate, evidence-based, accessible. Avoids medical jargon where possible; empowers patients with clear information and concrete next steps.
- **Privacy posture:** No third-party tracking. No analytics. No cookies. Symptom data lives only in the user's browser. Privacy notice at `/privacy/`.

---

## 2. Typography

Single family — **Figtree**, self-hosted (OFL 1.1) — used for all text. Differentiation is by weight, size, and letter-spacing.

### Loading

```css
@font-face {
  font-family: 'Figtree';
  font-style: normal;
  font-weight: 300 900;
  font-display: swap;
  src: url('../fonts/figtree.woff2') format('woff2-variations');
}
```

Variable WOFF2 (~26 KB regular, ~27 KB italic). `<link rel="preload">` on the regular file to avoid FOIT.

### Type scale (modular, ratio 1.2, fluid via `clamp()`)

| Token | Mobile floor | Desktop ceiling | Used for |
|---|---|---|---|
| `--text-xs` | 0.75rem | 0.85rem | Eyebrows, badges, captions |
| `--text-sm` | 0.875rem | 0.95rem | Secondary body, meta |
| `--text-base` | 1rem | 1.125rem | Body |
| `--text-lg` | 1.125rem | 1.25rem | Lead, top-bar brand, h4 |
| `--text-xl` | 1.25rem | 1.5rem | h3 |
| `--text-2xl` | 1.5rem | 2rem | h2, section headings |
| `--text-3xl` | 2rem | 2.75rem | h1, hero headline |

Headings differentiate by weight (h1 800 / h2 700 / h3 700 / h4 600) and letter-spacing (h1 −0.02em / h2 −0.01em). Body line-height: 1.55 on mobile, 1.6 from tablet up.

### Font stack

```
--font-primary: 'Figtree', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

---

## 3. Color system

Two-layer system: a raw brand palette plus a semantic layer that components consume. Defined in `site.json:semantic`, emitted by `build_css_vars()`.

### 3.1 Semantic tokens (what components reference)

| Token | Light | Dark | Used for |
|---|---|---|---|
| `--text` | `#2D1525` | `#F5E6D0` | Body text |
| `--text-muted` | `#7A5A3A` | `#C4A07A` | Captions, meta, dates |
| `--text-on-warm` | `#1A0A10` | `#1A0A10` | Text on `--surface-warm` (constant) |
| `--text-on-deep` | `#F5E6D0` | `#F5E6D0` | Text on `--surface-deep` (constant) |
| `--surface` | `#F5E6D0` | `#1A0E14` | Page background |
| `--surface-raised` | `#EDD8BC` | `#2D1525` | Cards, panels |
| `--surface-warm` | `#C4873A` | `#C4873A` | Sidebar, hero accent (constant) |
| `--surface-deep` | `#6B3A5C` | `#5A2D3E` | Stat tiles, primary CTA |
| `--accent` | `#8B4513` | `#E8B84A` | Links, focus, primary CTA |
| `--accent-hover` | `#6B2D3E` | `#F0D060` | Link hover |
| `--border` | `rgba(139,69,19,0.15)` | `rgba(255,255,255,0.1)` | Subtle dividers |
| `--border-strong` | `#C4982A` | `#C4982A` | Focus rings, emphasized borders (constant) |
| `--error` | `#A41A1A` | `#F87171` | Validation errors (per-theme; WCAG AA on both surfaces) |
| `--code` | `#2D1525` | `#F5E6D0` | Inline code text |
| `--code-bg` | `#F0E0C8` | `#3D1F30` | Inline code background |

All semantic pairs **pass WCAG AA** (4.5:1 normal text, 3:1 large text). See `design/accessibility-audit.md` for the verified contrast table.

### 3.2 Gradients

Reduced from 5 to 2 semantic gradients:

| Token | Value | Used for |
|---|---|---|
| `--gradient-warm` | `linear-gradient(180deg, #C4873A 0%, #9B5A3A 40%, #6B3A5C 100%)` | Sidebar background, home-help CTA |
| `--gradient-deep` | `linear-gradient(145deg, #6B3A5C 0%, #5A2D3E 100%)` | Stat tiles, primary CTA, journey-card hover, back-to-top |

### 3.3 Raw palette (authoring layer, not consumed by components)

```
gold        = #C4982A    Focus, borders, emphasized accents
gold-warm   = #FFD166    Reserved (deprecated for components)
plum        = #6B3A5C    Gradient component
plum-deep   = #5A2D3E    Gradient component, deep accent
brown       = #8B4513    Light-mode link color (now: --accent)
error       = (per-theme; see semantic above)
```

Legacy tokens (`--color-gold-light`, `--color-gold-bright`, `--color-burgundy`, `--color-plum-dark`) still emit for backward compatibility but are not used by current code.

---

## 4. Design tokens (constants)

### Radius

| Token | Value | Used for |
|---|---|---|
| `--radius-sm` | `6px` | Inputs, small buttons, badges |
| `--radius-md` | `10px` | Cards, panels |
| `--radius-pill` | `9999px` | Pills, avatar masks |

### Spacing

| Token | Value | Used for |
|---|---|---|
| `--space-xs` | `0.25rem` | Inline gaps |
| `--space-sm` | `0.5rem` | Tight groups |
| `--space-md` | `1rem` | Default block spacing |
| `--space-lg` | `1.5rem` | Section spacing |
| `--space-xl` | `2.5rem` | Major section breaks |
| `--space-section` | `clamp(2rem, 5vw, 4rem)` | Fluid section gap |
| `--container-padding` | `clamp(1rem, 4vw, 2rem)` | Fluid container padding |

### Accessibility

| Token | Value | Used for |
|---|---|---|
| `--focus-ring` | `3px solid var(--border-strong)` | Focus outline |
| `--focus-offset` | `2px` | Outline offset |
| `--tap-min` | `44px` | Minimum touch target dimension |

### Breakpoints (rem-based)

| Token | Value | Equivalent | Triggers |
|---|---|---|---|
| `--bp-tablet` | `48rem` | 768px | 2-col layouts, larger touch targets |
| `--bp-desktop` | `64rem` | 1024px | Persistent sidebar, hide bottom nav |
| `--bp-wide` | `80rem` | 1280px | Max content width caps |

CSS `@media` rules hardcode values; the `--bp-*` tokens are `:root`-defined for JS introspection via `getComputedStyle()`.

---

## 5. Information architecture

### 5.1 Sidebar nav (3 journeys)

| Group | Items |
|---|---|
| **Could this be me?** | Symptom quiz / Diagnosis / Co-morbidities / Healthcare |
| **I have endo or adeno** | Treatments / Medications / Fertility / Mental health / Resources & support / Symptom tracker |
| **Learn** | Endometriosis / Adenomyosis / Myths & facts / Notable people / Research / Education |

Each group is **collapsible** with localStorage persistence (`sidebar-groups` key).

### 5.2 Footer links

About / FAQ / Take action / Privacy

### 5.3 Bottom nav (mobile only, ≤1024px)

4 thumb-zone tabs: **Home / Quiz / Learn / Help** (Help → `/take-action/`).

### 5.4 Page set (21 markdown files)

`_index`, about, adenomyosis, comorbidities, diagnosis, education, Endometriosis, faq, fertility, graphic-images (draft), healthcare, medications, mental-health, myths, notable-people, **privacy** (new), **quiz** (new), research, resources, **take-action** (new), tracker, **treatments** (new).

Pages with `search: false` frontmatter are excluded from the search index (`/take-action/`, `/privacy/`). Pages with `draft: true` are excluded from both build and index (`/graphic-images/`).

---

## 6. Layout shell

### Top bar (sticky, all viewports)

```
[≡ menu]  [brand]    [search...]    [EN ▾]  [☀ theme]
```

- Hamburger hidden on desktop (sidebar persistent).
- Brand at `--text-lg`, weight 800.
- Search input collapses to icon on mobile, expands to full top-bar width on focus.
- Language picker is a styled native `<select>` with 2-letter language codes (EN, ES, FR, 中, 日, …) so all 26 languages fit.
- Theme toggle: sun ↔ moon, syncs with `localStorage.theme` and first-load `prefers-color-scheme`.

### Sidebar (off-canvas mobile, sticky-persistent desktop)

- Mobile (`< 64rem`): off-canvas, slides in from inline-start, 70% width with 30% backdrop tap-to-close. `inset-inline-*` logical properties + `[dir="rtl"]` translate override for Arabic.
- Desktop (`≥ 64rem`): persistent left column, `grid-template-columns: minmax(17.5rem, 20rem) 1fr`.
- Collapsible nav groups via `<button class="nav-group-toggle">` with chevron + `aria-expanded`.

### Bottom nav (mobile only)

- Fixed, 4 tabs, `padding-bottom: env(safe-area-inset-bottom)` for iOS home indicator.
- Hides automatically when a `[role="dialog"][aria-modal="true"]` is open (clickjacking mitigation).
- Each item is at least 4rem tall (well above the 44px target).
- Current page is marked via `aria-current="page"` (JS path matching).

### Back-to-top

- Fixed bottom-right (`inset-inline-end`), above the bottom nav on mobile via `bottom: calc(4rem + env(safe-area-inset-bottom) + 1rem)`.
- Appears after 300px window scroll. Window-scroll (not container-scroll — see `design/css-architecture.md` §3).

---

## 7. Component patterns

### Hero (home)

- One headline at `--text-3xl`, max-width `22ch` for line-balance.
- One supporting paragraph at `--text-lg`, max-width `60ch`.
- Two CTAs side-by-side on tablet+, stacked on mobile: primary (`--gradient-deep`) and secondary (outlined, accent border).

### Journey cards (home, 3-up)

- `grid-template-columns: 1fr` mobile, `repeat(3, 1fr)` tablet+.
- Each card: eyebrow (uppercase, `--accent`), title, description, CTA chevron.
- On hover/focus the card's `::before` pseudo-element fills with `--gradient-deep` (`opacity: 0 → 1`), shifting all text to `--text-on-deep`.
- Whole card is one `<a>` — no nested interactives. `aria-current` set by browser navigation.

### Stat strip (home, 4-up)

- 2-col mobile, 4-col tablet+.
- Each stat is a `.stat-link` to a source URL. `--gradient-deep` background, `--text-on-deep` text.
- External-link icon at end, opens in new tab with `rel="noopener noreferrer"`.

### Symptom-quiz teaser (home, deferred-to-page)

- 3 sample checkboxes (no submission), CTA links to full `/quiz/` page.

### Take-action page

- Markdown content with `<blockquote>` template scripts.
- `assets/js/take-action.js` injects a Copy button on each blockquote. Clipboard API with text-selection fallback.

### Search popup (topbar)

- Focus on empty input → 6 suggestion chips from `search_suggestion_1`…`_6` i18n keys (English defaults).
- Type 2+ chars → debounced (200ms), weighted scoring, max 8 results.
- ↑/↓ navigate, Enter on suggestion runs it, Esc clears + blurs.
- `aria-live="polite"` on results panel.

### Table → accordion

- Tables with `data-accordion="table"` collapse into `<details>`/`<summary>` blocks on mobile.

### Carousel (home — dual-column "Reality of Endo")

Two carousels side-by-side (1-col mobile, 2-col at 48rem via `.home-reality-grid`):

1. **Infographic carousel** (left) — 4 endographics.org slides, `object-fit: contain`, rounded corners.
2. **Surgical photos carousel** (right) — 7 graphic images behind an NSFW gate (`.carousel-nsfw-gate`). User must click "View images" to reveal; carousel inits only after reveal.

Shared behavior:
- Multi-instance JS (`carousel.js`) — each `.carousel-section` gets independent state.
- Auto-rotates every 4s **only if** `prefers-reduced-motion: no-preference` AND `hover: hover` (not touch).
- Reacts to live changes in the motion preference.
- Per-slide `aria-hidden`, dots have `aria-label="Go to slide N"`, arrow buttons have ARIA labels.
- Controls use soft, borderless styling (`--accent-bg` / `--accent-bg-hover`) to match the site palette.

---

## 8. Accessibility commitments

Verified in `design/accessibility-audit.md`. Summary:

- **Skip-link** to `#main-content` at the top of every page (visually hidden until focused).
- **Focus indicator** via `--focus-ring` (3px solid `--border-strong`, 2px offset).
- **Touch targets**: every interactive `≥ 44px` block size.
- **ARIA**:
  - `aria-current="page"` on sidebar + bottom-nav for active route.
  - `aria-expanded` + `aria-controls` on sidebar group toggles.
  - `aria-live="polite"` on search results panel + take-action copy-button label.
  - `aria-hidden` on inactive carousel slides.
  - All icon-only buttons have `aria-label`.
- **Reduced motion**: `prefers-reduced-motion: reduce` disables animations, transitions, carousel autoplay, and chevron rotations.
- **RTL**: Arabic (`dir="rtl"` set by `i18n.js`) is supported via logical properties (`inset-inline-*`, `padding-inline-*`, `text-align: start`) and `[dir="rtl"]` overrides for the sidebar transform.
- **Print styles**: Hide interactive UI, show link URLs, avoid page breaks inside headings/tables.
- **Contrast**: All semantic token pairs pass WCAG AA on both light and dark surfaces.
- **Keyboard nav**: Tab reaches everything. Esc closes sidebar/search and returns focus to the trigger. Arrow keys navigate carousel and search results.
- **Sidebar focus management**: Opening the sidebar on mobile moves focus into the first nav link.

---

## 9. i18n

- 26 languages, 170+ keys.
- Translations live in `static/i18n/translations.json`, loaded async by `assets/js/i18n.js`.
- DOM uses `data-i18n="key"`, optional `data-i18n-attr="title,aria-label"` for attribute targeting, `data-i18n-aria="key"` for aria-label-only.
- Missing translations auto-fall-back to English.
- New keys land in `en` first; placeholders propagate across all 26 languages; the gap is tracked in `static/i18n/_review.json` for human translation later.
- Arabic triggers `dir="rtl"` on `<html>` and exercises the logical-property layout.

---

## 10. Performance

| Bundle | gzip |
|---|---|
| CSS | ~7.5 KB (target: <15 KB) |
| JS | ~8.5 KB (target: <10 KB) |

- Self-hosted Figtree variable WOFF2 with `preload`; no Google Fonts request.
- Cache-busted bundles (content-hashed filenames).
- Critical CSS inlined via `{{CSS_VARIABLES}}` block in `<head>`.
- Lazy-loaded images (`loading="lazy"` on all non-hero content imgs).
- No analytics, no third-party requests.

---

## 11. What changed in the v2 overhaul

For historical context, see the design docs:

- `design/ia.md` — three-journey IA design, journey definitions, page-set decisions, URL stability, privacy
- `design/css-architecture.md` — semantic token layer rationale, mobile-first inversion, file consolidation
- `design/accessibility-audit.md` — Phase 5 audit results and fixes
- `design/perf-baseline.md` — pre-overhaul perf snapshot

Key changes from v1:

| v1 | v2 |
|---|---|
| 4 nav groups by content type | 3 journeys by user intent |
| 18 pages | 21 pages (+quiz, treatments, take-action, privacy) |
| Resource filter cards on home | Removed; cards became real navigation |
| Action modal as overlay | Real page at `/take-action/` |
| Google Fonts (Figtree) | Self-hosted Figtree, OFL 1.1 |
| Sidebar persistent at 280px fixed | Sidebar `minmax(17.5rem, 20rem)` desktop, off-canvas mobile |
| No bottom nav | 4-tab thumb-zone bottom nav (mobile) |
| 5 gradients | 2 gradients (`--gradient-warm`, `--gradient-deep`) |
| 11 brand colors, no semantic layer | 7 raw + 15 semantic tokens |
| Desktop-first CSS with `@media (max-width)` | Mobile-first with `@media (min-width)` in rem |
| 10 CSS files, 9 JS files | 8 CSS files, 9 JS files |
| Container-scroll on desktop (latent bug) | Window-scroll everywhere |
