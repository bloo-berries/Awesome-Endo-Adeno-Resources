# TODO

## i18n - Full Internationalization

### Missing translation keys (not yet in translations.json)
- [x] `home_hero_cta_surgery` - "Surgical Costs" CTA on home page
- [x] `home_people_heading` - "Notable people with Endometriosis" heading
- [x] `home_urgent_btn` - Help/warning button in topbar
- [x] `stats_context` - Mortality stat tooltip disclaimer
- [x] `home_memorial_heading` - "In memory" heading
- [x] `home_memorial_see_all` - "View all" link for memorial section

### Hardcoded English text needing `data-i18n` attributes
- [x] `base.html`: Settings button - `aria-label="Settings"` and `title="Settings"` need i18n keys
- [x] `base.html`: "Language" label in settings panel - removed (no longer shown)
- [x] `base.html`: "Theme" label in settings panel - removed (no longer shown)
- [x] `base.html`: "Light / Dark" theme toggle label - removed (icon-only button now)
- [x] `home.html`: "Here's where to start." subheading - not wrapped in i18n
- [x] `home.html`: "See all" link (notable-people section) - no `data-i18n`
- [x] `home.html`: "Graphics via" carousel credit - hardcoded

### Translation backlog (~95 keys pending across 26 languages)
- [ ] Prioritize Spanish, French, German, Arabic (highest traffic)
- [ ] Navigation group labels (`nav_group_could_this_be_me`, etc.)
- [ ] Home page journey cards (eyebrow/title/desc/cta - 9 keys)
- [ ] Quiz teaser section (title/desc/cta + options - 5 keys)
- [ ] Video captions + section headings
- [ ] Stats tooltips
- [ ] Search suggestions
- [ ] Memorial section keys (person bios, roles, conditions)
- [ ] All keys tracked in `static/i18n/_review.json`

---

## Accessibility

- [x] RTL carousel arrows - flip chevrons for Arabic (`[dir="rtl"] .carousel-arrow svg { transform: scaleX(-1); }`)
- [ ] Live browser + screen-reader testing (VoiceOver, NVDA, TalkBack)
- [ ] Physical keyboard testing on actual devices
- [ ] Content page image alt text audit (home page done; content pages pending)
- [ ] Form validation announcements (`aria-live="assertive"`) when quiz form lands
- [ ] Sidebar backdrop RTL tap zone UX review

---

## Performance

- [ ] Measure Lighthouse scores post-CSS refactor (ambient.css, home.css, etc.)
- [x] `loading="lazy"` on below-fold images (101 instances across templates + content)
- [ ] Preconnect hint if any external resources are added
- [ ] Evaluate critical CSS inlining for above-fold content

---

## Content

- [x] Finalize surgery-costs page content + data
- [ ] Review all markdown files for stale links or outdated stats
- [x] Add `lastmod` frontmatter to pages that have been updated (all 22 pages have `lastmod`)
- [x] FAQ schema markup (JSON-LD) - already in build.py
- [x] In Memory page with memorial cards
- [x] Add Wikipedia / reference links to all notable people and memorial cards

---

## Features

- [x] Multi-instance carousel JS (supports multiple carousels per page)
- [x] Dual-column "Reality of Endo" section: infographic carousel + NSFW-gated surgical photos carousel
- [x] NSFW gate on surgical carousel (click-to-reveal, carousel inits only after reveal)
- [x] Face centering on notable people cards (`object-position: center 20%`)
- [x] Surgical images moved to `static/images/graphic-images/` (survive rebuilds)
- [x] Organic blob avatar shapes on people cards
- [x] Ambient background orbs (7 orbs, light + dark modes, respects reduced motion)
- [x] Topbar gradient blending with ambient background
- [x] Person modal with Wikipedia + general reference links (`data-wiki`, `data-link`)
- [ ] PWA offline support (service worker + cache strategy)
- [ ] Share button on content pages (Web Share API with fallback)
- [x] Print stylesheet for content pages
- [ ] RSS/Atom feed generation in build.py
- [x] Sitemap `<lastmod>` dates from frontmatter - already in build.py
- [ ] 404 page search suggestions (reuse search index)

---

## Brand & Marketing

- [x] OG image updated with "1 in 7" branding (1200x630, warm cream gradient, Figtree font)
- [x] Brand doc updated to v2.1 (`design/brand.md`)
- [ ] Create favicon.ico fallback for legacy browsers (currently SVG only)
- [ ] Social media profile links in manifest.json

---

## Infrastructure

- [ ] CI: Add build verification to GitHub Actions (already deploys, add lint/check step)
- [ ] CI: HTML validation (Nu HTML Checker) on built output
- [ ] CI: Lighthouse CI for performance regression detection
- [x] CDN cache headers in Cloudflare Pages `_headers` file
