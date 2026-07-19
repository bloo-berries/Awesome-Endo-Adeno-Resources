# 1 in 7 - Brand Guidelines

## Brand Identity

**Name:** 1 in 7
**Domain:** 1in7.info
**Tagline:** Endometriosis & Adenomyosis Resources
**Mission:** Provide accessible, evidence-based information for people navigating endometriosis and adenomyosis.

The name references the approximately 1 in 7 people affected by endometriosis worldwide.

---

## Logo

### Variants

| File | Use case |
|------|----------|
| `logo-full.svg` | Primary logo - heart icon + "1 in 7" wordmark (horizontal) |
| `logo-icon.svg` | Square icon - favicons, app icons, small spaces |
| `logo-wordmark.svg` | Text-only - when the icon is already present nearby |

### Usage Rules

- **Clear space:** Maintain padding equal to the heart icon's width on all sides.
- **Minimum size:** Icon alone: 24px. Full logo: 120px wide.
- **Backgrounds:** Use on light (#F5E6D0) or dark (#2A1A24) surfaces only. Never place on busy images without a scrim.
- **Do not:** Rotate, stretch, recolor the gradient, add drop shadows, or outline the heart.

---

## Color Palette

### Heart Gradient (Primary Mark)

| Stop | Hex | Usage |
|------|-----|-------|
| 0% | `#D4A830` | Gold (top) |
| 40% | `#C4982A` | Warm gold |
| 70% | `#8B3A4A` | Burgundy |
| 100% | `#4A0E1B` | Deep wine (bottom) |

### Light Theme

| Token | Hex | Usage |
|-------|-----|-------|
| `--text` | `#3D2435` | Body text |
| `--text-muted` | `#7A5A3A` | Secondary text |
| `--heading` | `#3D2435` | Headings |
| `--surface` | `#F5E6D0` | Page background |
| `--surface-raised` | `#EDD8BC` | Cards, elevated elements |
| `--accent` | `#8B4513` | Links, interactive elements |
| `--accent-hover` | `#7D4060` | Hover state |
| `--border` | `rgba(139, 69, 19, 0.15)` | Subtle borders |

### Dark Theme

| Token | Hex | Usage |
|-------|-----|-------|
| `--text` | `#F5E6D0` | Body text |
| `--text-muted` | `#C4A07A` | Secondary text |
| `--heading` | `#F0D060` | Headings |
| `--surface` | `#2A1A24` | Page background |
| `--surface-raised` | `#3D2435` | Cards, elevated elements |
| `--accent` | `#E8B84A` | Links, interactive elements |
| `--accent-hover` | `#F0D060` | Hover state |
| `--border` | `rgba(255, 255, 255, 0.12)` | Subtle borders |

### Constants (Theme-independent)

| Token | Hex | Usage |
|-------|-----|-------|
| `--surface-warm` | `#7D4E6E` | Hero backgrounds, CTAs |
| `--accent-warm` | `#FFD166` | Highlights on warm surfaces |
| `--border-strong` | `#C4982A` | Focus rings, emphasis borders |
| `--text-on-warm` | `#F5E6D0` | Text on warm surfaces |

---

## Typography

**Font:** Figtree (variable, self-hosted, OFL 1.1 license)
**Weights:** 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
**Style:** Regular + Italic

### Type Scale

| Token | Size | Usage |
|-------|------|-------|
| `--text-3xl` | 2rem–2.75rem | Page titles |
| `--text-2xl` | 1.5rem–2rem | Section headings |
| `--text-xl` | 1.25rem–1.5rem | Subheadings |
| `--text-lg` | 1.125rem–1.25rem | Lead paragraphs |
| `--text-base` | 1rem–1.125rem | Body text |
| `--text-sm` | 0.875rem–0.95rem | Captions, metadata |
| `--text-xs` | 0.75rem–0.85rem | Fine print |

All sizes use `clamp()` for fluid scaling between mobile and desktop.

---

## Social Media Assets

| File | Dimensions | Purpose |
|------|-----------|---------|
| `social-banner-light.svg` | 1500x500 | Twitter/X header (light) |
| `social-banner-dark.svg` | 1500x500 | Twitter/X header (dark) |
| `og-template.svg` | 1200x630 | Open Graph / social preview template |
| `apple-touch-icon.png` | 180x180 | iOS home screen icon |

---

## Asset Inventory

```
static/brand/
├── BRAND-GUIDELINES.md    ← This file
├── logo-full.svg          ← Heart + wordmark (horizontal)
├── logo-icon.svg          ← Heart icon only (square)
├── logo-wordmark.svg      ← "1 in 7" text only
├── social-banner-light.svg
├── social-banner-dark.svg
├── og-template.svg
└── apple-touch-icon.png

static/
├── favicon.svg            ← Browser favicon (heart, 64x64 viewBox)
├── social-preview.png     ← Default OG image (1200x630)
└── manifest.json          ← Web app manifest
```

---

## Attribution

The Figtree typeface is licensed under the SIL Open Font License 1.1. The brand heart icon is original work. All brand assets in this directory are provided for use in promoting or referencing the 1 in 7 project.
