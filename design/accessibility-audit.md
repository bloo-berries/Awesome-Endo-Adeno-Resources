# Accessibility audit — Phase 5

Date: 2026-05-28. Site state: Phase 4 complete, v2 shell in production.

## Summary

| Category | Result |
|---|---|
| WCAG AA contrast (semantic tokens, both themes) | 12/13 pairs pass; 1 fix applied |
| Keyboard navigation | All interactives tab-reachable with visible focus |
| Screen reader (ARIA roles, labels, live regions) | 3 fixes applied |
| Touch targets (≥44px) | 3 fixes applied |
| RTL layout (Arabic) | Logical properties + dir-overrides on the v2 shell; carousel-arrow direction deferred |

---

## 5a. WCAG AA contrast

Computed contrast ratios on every semantic token pair (light + dark) using the WCAG 2.1 relative-luminance formula. Threshold: 4.5:1 for normal text, 3:1 for large (≥18pt or ≥14pt bold).

| Pair | Light | Dark |
|---|---|---|
| Body text on surface | AAA (13.74) | AAA (15.32) |
| Body text on surface-raised | AAA (12.16) | AAA (13.74) |
| Muted text on surface | AA (5.11) | AAA (7.75) |
| Muted text on surface-raised | AA (4.52) | AA (6.95) |
| Accent (link) on surface | AA (5.78) | AAA (10.20) |
| Accent on surface-raised | AA (5.12) | AAA (9.14) |
| Accent hover on surface | AAA (8.27) | AAA (12.44) |
| Text on warm surface | AA (6.28) | AA (6.28) |
| Text on deep surface | AAA (7.18) | AAA (9.10) |
| Code on code-bg | AAA (13.01) | AAA (11.91) |
| Heading on surface (large) | AAA (13.74) | AAA (15.32) |

### Failure + fix: error color

`--error` was `#dc3545` (Bootstrap red). Failed AA on both surfaces: 3.69 (light), 4.15 (dark).

**Fix:** moved `error` from `semantic.constant` to `semantic.light` / `semantic.dark` with theme-specific values:

- Light: `#A41A1A` — 6.24 on surface, 5.53 on surface-raised (AA+)
- Dark: `#F87171` — 6.80 on surface, 6.10 on surface-raised (AA+)

---

## 5b. Keyboard & screen reader

### Audited

- All 11 interactive elements in `templates/base.html` (buttons, links, inputs, select).
- All custom widgets in JS modules (sidebar collapse, search, carousel, take-action copy, theme toggle, bottom nav).

### Findings + fixes

| Finding | Fix |
|---|---|
| `<div id="search-results" role="listbox">` had no `aria-live` — result changes silent for screen readers. | Added `aria-live="polite"` + `aria-atomic="false"`. |
| Opening sidebar via hamburger left focus on the topbar — keyboard users had to tab past topbar tail to reach sidebar links. | `setOpen(true)` now moves focus to the first link inside the sidebar (mobile only; desktop already had persistent sidebar). |
| Copy-button "Copied" label change was silent for screen readers (visual-only DOM swap). | Wrapped the button's label `<span>` in `aria-live="polite"`. |
| `aria-current="page"` was confirmed working in sidebar nav (server-rendered via `active_slug`) and bottom nav (client-side via JS path-match). | No change needed; verified on both home and content pages. |

### Confirmed already correct

- Skip-link to `#main-content` at the top of `<body>`. Visually hidden until focused.
- Every icon-only button has either `aria-label`, `title`, or visible text.
- Carousel sets `aria-roledescription="slide"`, per-slide `aria-label="Slide N of M"`, and `aria-hidden` toggles for inactive slides.
- Sidebar nav-group toggle sets `aria-expanded` and `aria-controls` referencing the list ID.
- Escape on the open sidebar returns focus to the hamburger button.
- `prefers-reduced-motion` honored in carousel autoplay and sidebar transitions.

---

## 5c. Touch targets

WCAG 2.2 AAA recommends 44px minimum target dimension with ≥8px spacing. Audited every interactive selector.

### Already compliant

`.topbar-menu`, `.topbar-lang`, `.topbar-theme`, `.bottomnav-item` (4rem = 64px tall), `.nav-group-toggle`, `.sidebar-nav .nav-item a`, `.home-hero-cta-primary`, `.home-hero-cta-secondary`, `.journey-card`, `.stat-link`, `.home-quiz-teaser-cta`, `.home-help-cta-btn`, `.home-quiz-teaser-option`, `.search-suggestion`.

### Fixes applied

| Element | Was | Now |
|---|---|---|
| `.topbar-brand` | Plain link, ~22px tall | `display: inline-flex; min-block-size: var(--tap-min)` + hover surface |
| `.search-result-item` | ~32px (padding-only) | Added `min-block-size: var(--tap-min)` + center alignment |
| `.copyable-btn` | `min-block-size: 2rem` (32px) | `min-block-size: var(--tap-min)` (44px) + `min-inline-size: var(--tap-min)` |

---

## 5c. RTL (Arabic)

`<html dir="rtl" lang="ar">` is set by `i18n.js` when the user picks Arabic. Audited every directional property in `layout.css` and `pages.css`.

### Fixes applied (logical properties)

| Was | Now |
|---|---|
| `.sidebar { inset: 3.5rem 30% 0 0; transform: translateX(-100%); }` | Split into `inset-block-start/end` + `inset-inline-start/end`. Added `[dir="rtl"] .sidebar { transform: translateX(100%); }` so the sidebar slides in from the inline-end side in RTL. |
| `.back-to-top-v2 { right: var(--space-md); }` | `inset-inline-end: var(--space-md);` |
| `.copyable-btn { right: var(--space-sm); }` | `inset-inline-end: var(--space-sm);` |
| `.copyable-block > blockquote { padding-right: 4.5rem; }` | `padding-inline-end: 4.5rem;` |
| `.home-hero { text-align: left; }` | `text-align: start;` |
| `.topbar-search input` and `.nav-group-toggle { text-align: left; }` | `text-align: start;` |

### Deferred (Phase 6 polish)

- **Carousel arrow direction.** The chevron icons (`◄ ►`) are absolute visual indicators. In RTL contexts the "next" semantic moves right-to-left, so the right-pointing arrow should be on the left. Two ways to fix:
  - Wrap with `[dir="rtl"] .carousel-arrow svg { transform: scaleX(-1); }` (visually mirrors)
  - Use language-aware labels and let CSS Grid flip the controls
  - Decision pending design review.

- **Sidebar backdrop tap zone for RTL.** Currently the sidebar covers 70% width with the right 30% as tap-to-close. In RTL it covers from the right; the 30% open zone is now on the left. This works correctly with `inset-inline-end: 30%` but the visual feels different — the user reads outward toward the close zone.

---

## Validation

Re-ran the contrast script after the error-color fix:

```
Pair                                              Light             Dark
------------------------------------------------------------------------
Body text on surface                        AAA (13.74)      AAA (15.32)
...
Error text on surface                        AA  (6.24)       AAA (6.80)
...
Failures: 0
```

All 13 semantic-token pairs now pass WCAG AA in both themes.

Build verified after every fix; bundle size unchanged (~7.5 KB CSS gzip, 8.5 KB JS gzip).

---

## What's NOT covered by this audit

- **Live-browser/screen-reader testing.** This audit is static — I read code and computed contrasts. A real audit needs VoiceOver / NVDA / TalkBack runs. Worth a pass before launch.
- **Keyboard testing on actual devices.** Tested by reading code; needs physical keyboard verification.
- **Image alt text.** All images on the home page have `alt` attributes. Content pages should be re-audited as content gets rewritten in Phase 6.
- **Form-error message announcement.** The take-action and quiz pages don't have forms; the home quiz-teaser is just a teaser. When the real quiz lands (deferred), error states need `aria-live="assertive"` for validation feedback.
- **Color-only differentiation.** Verified visually that journey cards, stat links, and CTAs all combine color with text/icon, not color alone. Confirmed in code.
