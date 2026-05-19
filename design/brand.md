# 1 in 7 — Brand Identity

## Brand

- **Name:** 1 in 7
- **Domain:** 1in7.info
- **Mission:** A comprehensive resource hub for navigating the challenges of Endometriosis and Adenomyosis.
- **Voice:** Compassionate, evidence-based, accessible. Avoids medical jargon where possible; empowers patients with clear information.

---

## Typography

Single font family — **Figtree** — used for all text. Differentiation via weight, size, and letter-spacing.

| Element | Weight | Size | Letter-spacing |
|---|---|---|---|
| Sidebar brand title | 800 | 2rem | -0.02em |
| Content h1 | 800 | 2rem | -0.02em |
| Content h2 | 700 | 1.5rem | -0.01em |
| Content h3 | 700 | 1.25rem | -0.01em |
| Content h4 | 600 | 1.15rem | normal |
| Body text | 400 | 18px base | normal |
| UI labels/buttons | 400-700 | varies | normal |

### Font loading

Figtree loaded from Google Fonts with variable weight range (300-900).

### CSS variable

`--font-primary: 'Figtree', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`

---

## Navigation

Sidebar nav is grouped into sections:

| Group | Items |
|---|---|
| **Conditions** | Endometriosis, Adenomyosis, Myths & Facts |
| **Getting Care** | Diagnosis, Healthcare, Co-morbidities |
| **Support** | Resources, Education |
| **Research** | Research |

About is in `footer_links` at bottom of sidebar. All groups have i18n keys (`nav_group_conditions`, `nav_group_care`, `nav_group_support`, `nav_group_research`).

---

## Color Palette

### Design Tokens (set by `build_css_vars()`)

All colors are CSS custom properties set in a `<style>` block injected by `build.py`. Light mode values are set on `body`, dark mode overrides on `body.dark-theme`.

### Brand Colors (constant across themes)

| Token | Hex | Usage |
|---|---|---|
| `--color-gold` | `#C4982A` | Focus outlines, borders, accents |
| `--color-gold-light` | `#E8B84A` | Content links (dark mode) |
| `--color-gold-bright` | `#F0D060` | Hover highlights |
| `--color-gold-warm` | `#FFD166` | CTAs, active states, badges |
| `--color-gold-hover` | `#FFE085` | Button hover states |
| `--color-plum` | `#6B3A5C` | Gradient component |
| `--color-plum-dark` | `#5C1A3A` | Text on gold backgrounds |
| `--color-plum-deep` | `#5A2D3E` | Deep accent |
| `--color-burgundy` | `#6B2D3E` | Dark accents |
| `--color-brown` | `#8B4513` | Light mode links |
| `--color-error` | `#dc3545` | Error states |

### Theme-Switching Tokens

These change value between `body` (light) and `body.dark-theme` (dark):

| Token | Light | Dark |
|---|---|---|
| `--text-color` | `#2D1525` | `#F5E6D0` |
| `--bkg-color` | `#F5E6D0` | `#1A0E14` |
| `--heading-color` | `#2D1525` | `#F0D060` |
| `--link-color` | `#8B4513` | `#E8B84A` |
| `--link-hover-color` | `#6B2D3E` | `#F0D060` |
| `--muted-color` | `#7A5A3A` | `#C4A07A` |
| `--surface-color` | `#EDD8BC` | `#2D1525` |
| `--border-color` | `rgba(139,69,19,0.15)` | `rgba(255,255,255,0.1)` |

### Sidebar Colors (constant)

| Token | Hex |
|---|---|
| `--sidebar-bg-color` | `#C4873A` |
| `--sidebar-a-color` | `#1A0A10` |
| `--sidebar-h1-color` | `#1A0A10` |
| `--sidebar-p-color` | `#3D1F30` |

### Key Gradients

| Token | CSS | Usage |
|---|---|---|
| `--gradient-sidebar` | `linear-gradient(180deg, #C4873A 0%, #9B5A3A 40%, #6B3A5C 100%)` | Sidebar background |
| `--gradient-component` | `linear-gradient(160deg, #C4873A 0%, #A0694A 40%, #6B3A5C 100%)` | Poll box, carousel box |
| `--gradient-modal` | `linear-gradient(180deg, #C4873A 0%, #8B2B5A 100%)` | Action modal |
| `--gradient-tile` | `linear-gradient(145deg, #6B3A5C 0%, #5A2D3E 100%)` | Stat boxes, resource cards |

### Design Tokens

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | `6px` | Buttons, nav items, small elements |
| `--radius-md` | `8px` | Cards, inputs, tooltips |
| `--radius-lg` | `12px` | Hero banners, modals, large cards |
| `--radius-pill` | `9999px` | Pill-shaped buttons, badges |

---

## Accessibility Standards

| Standard | Implementation |
|---|---|
| Skip navigation | `.skip-link` hidden until focused, jumps to `#main-content` |
| Focus indicators | 3px solid `var(--focus-color)` outline + 2px offset + `var(--focus-shadow)` on all focusable elements |
| Touch targets | Minimum 44px on interactive elements (buttons, links) |
| Reduced motion | `prefers-reduced-motion: reduce` disables all animations/transitions |
| RTL support | Arabic (`ar`) triggers `dir="rtl"` on `<html>` |
| Semantic HTML | `<nav>`, `<article>`, `<main>`, breadcrumb `<ol>`, ARIA labels throughout |
| Link contrast | 2px underline with `text-underline-offset: 2px`, thickens to 3px on hover |
| Print styles | Hides interactive UI, shows link URLs, avoids page breaks inside headings/tables |

---

## Layout

### Sidebar
- **Desktop (>1024px):** Persistent, fixed at left, 280px wide. Content gets `margin-left: 280px`. Hamburger hidden.
- **Mobile (<=1024px):** Off-canvas, triggered by hamburger. Overlay dims content.

### Header bar
- Sticky at top of content area with site title centered.
- Theme toggle fixed top-right.
- Resource filter cards rendered in header bar.

---

## UI Component Patterns

### Resource Cards
Toggle-based filter buttons in a sticky header bar. Click activates a filter panel; clicking again deactivates. Cards use `data-filter` attributes, sidebar links use `data-sidebar-filter`.

### Action Modal
Full-screen overlay (`z-index: 2000`) with three sub-views: Symptoms, Connect, Awareness. Uses scale+translateY entrance animation. Escape key and overlay click close.

### Symptom Poll
Checkbox-based poll submitted to Formspree. Shows suggestions list after submission. Gradient background consistent with carousel.

### Image Carousel
Auto-rotating (4s interval) with dot indicators and arrow controls. Pauses on hover. Contained in gradient box matching poll styling.

### Back-to-Top
Appears after 300px scroll. Uses `smooth` scroll behavior. Positioned fixed in bottom-right.

### Table Accordion
Tables automatically convert to `<details>`/`<summary>` accordion layout on mobile. Uses `data-accordion="table"` attribute.
