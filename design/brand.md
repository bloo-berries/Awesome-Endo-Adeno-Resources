# 1 in 7 — Brand Identity

## Brand

- **Name:** 1 in 7
- **Domain:** 1in7.info
- **Mission:** A comprehensive resource hub for navigating the challenges of Endometriosis and Adenomyosis.
- **Voice:** Compassionate, evidence-based, accessible. Avoids medical jargon where possible; empowers patients with clear information.

---

## Typography

Three font families, each with a distinct role:

| Font | Variable | Usage |
|---|---|---|
| **Inter** | `--font-ui` | UI elements: sidebar, nav, buttons, inputs, tags, search, resource cards, breadcrumbs |
| **Source Serif 4** | `--font-body` | Body content: paragraphs, list items, table cells, blockquotes |
| **Monaspace Argon** | `--font-display` | Display/title elements: content headings (h2-h4), poll titles, carousel titles, action card titles |

### Font loading

- Inter and Source Serif 4: Google Fonts
- Monaspace Argon: CDN (`https://cdn.jsdelivr.net/gh/githubnext/monaspace@v1.101/`)

### Hierarchy

| Element | Font | Weight | Size |
|---|---|---|---|
| Sidebar brand title | Inter | 700-900 | 2-3rem |
| Content h1 | Inter (UI) | 700 | default |
| Content h2-h4 | Monaspace Argon (display) | 600-700 | 1.15rem+ |
| Body text | Source Serif 4 | 400 | 18px base |
| UI labels/buttons | Inter | 400-700 | varies |

---

## Color Palette

### Sidebar

| Role | Hex | Description |
|---|---|---|
| Background | `#C4873A` | Warm amber/gold |
| Heading text | `#1A0A10` | Near-black |
| Link text | `#1A0A10` | Near-black |
| Body text | `#3D1F30` | Dark plum |
| Image border | `#5A2D3E` | Deep burgundy |
| Toggle background | `#5A2D3E` | Deep burgundy |
| Toggle icon | `#F0D060` | Gold |

### Light Mode

| Role | Hex |
|---|---|
| Content background | `#F5E6D0` |
| Text | `#2D1525` |
| Links | `#8B4513` |
| Post titles | `#2D1525` |
| Dates | `#7A5A3A` |
| Table borders | `#D4B896` |
| Table stripe | `#F0DCC4` |
| Code background | `#F0E0C8` |
| Code text | `#2D1525` |

### Dark Mode

| Role | Hex |
|---|---|
| Content background | `#1A0E14` |
| Text | `#F5E6D0` |
| Links | `#E8B84A` |
| Post titles | `#F0D060` |
| Dates | `#C4A07A` |
| Table borders | `#5A2D3E` |
| Table stripe | `#2D1525` |
| Code background | `#3D1F30` |
| Code text | `#F5E6D0` |

### Accent Colors

| Role | Hex | Usage |
|---|---|---|
| Primary gold | `#FFD166` | CTAs, active states, highlights, badge backgrounds |
| Gold hover | `#FFE085` | Button hover states |
| Focus outline | `#C4982A` | Keyboard focus indicators (3px solid) |
| Content link (dark) | `#E8B84A` | In-content hyperlinks |
| Content link hover | `#F0D060` | Link hover state |
| Deep burgundy | `#5C1A3A` | Text on gold backgrounds, dark accents |
| Error/strike | `#dc3545` | Error states, strikethrough text |

### Key Gradients

| Name | CSS | Usage |
|---|---|---|
| Component gradient (dark) | `linear-gradient(160deg, #C4873A 0%, #A0694A 40%, #6B3A5C 100%)` | Poll box, carousel box |
| Component gradient (light) | `linear-gradient(160deg, #D4974A 0%, #B0795A 40%, #7D4A6C 100%)` | Poll/carousel in light mode |
| Modal gradient | `linear-gradient(180deg, #C4873A 0%, #8B2B5A 100%)` | Action modal container |
| Stat box gradient (dark) | `linear-gradient(145deg, #6B3A5C 0%, #4A1E3A 100%)` | Statistics row boxes |
| Stat box gradient (light) | `linear-gradient(145deg, #7D4A6C 0%, #5C2D4E 100%)` | Statistics row boxes in light mode |

---

## Accessibility Standards

| Standard | Implementation |
|---|---|
| Skip navigation | `.skip-link` hidden until focused, jumps to `#main-content` |
| Focus indicators | 3px solid `#C4982A` outline + 2px offset + box-shadow on all focusable elements |
| Touch targets | Minimum 44px on interactive elements (buttons, links) |
| Reduced motion | `prefers-reduced-motion: reduce` disables all animations/transitions |
| RTL support | Arabic (`ar`) triggers `dir="rtl"` on `<html>` |
| Semantic HTML | `<nav>`, `<article>`, `<main>`, breadcrumb `<ol>`, ARIA labels throughout |
| Link contrast | 2px underline with `text-underline-offset: 2px`, thickens to 3px on hover |
| Print styles | Hides interactive UI, shows link URLs, avoids page breaks inside headings/tables |

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
