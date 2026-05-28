# Perf baseline — pre-Phase 2

Recorded 2026-05-27 before any Phase 2 implementation.

## Bundle sizes

| Bundle | Raw | gzipped | Target (gzip) |
|---|---|---|---|
| `dist/css/bundle.*.css` | 49,292 B (48.1 KB) | 9,245 B (9.0 KB) | <15 KB ✅ |
| `dist/js/app.*.js` | 36,225 B (35.4 KB) | 8,632 B (8.4 KB) | <10 KB ✅ |

## External requests

- `https://fonts.googleapis.com/css2?family=Figtree:...` (Phase 2 step 5 will self-host and remove this)
- `https://fonts.gstatic.com/...` (eliminated by Phase 2 step 5)

## File breakdown (CSS source, pre-minify)

| File | Lines |
|---|---|
| `assets/css/base.css` | 214 |
| `assets/css/custom.css` | 194 |
| `assets/css/layout.css` | 145 |
| `assets/css/sidebar.css` | 389 |
| `assets/css/components.css` | 683 |
| `assets/css/responsive.css` | 97 |
| `assets/css/symptom-poll.css` | 161 |
| `assets/css/carousel.css` | 144 |
| `assets/css/action-modal.css` | 600 |
| `assets/css/tracker.css` | 267 |
| **Total** | **2,894** |

## File breakdown (JS source, pre-minify)

| File | Lines |
|---|---|
| `assets/js/codeblock.js` | 20 |
| `assets/js/search.js` | 116 |
| `assets/js/i18n.js` | 54 |
| `assets/js/carousel.js` | 57 |
| `assets/js/poll.js` | 31 |
| `assets/js/accordion.js` | 98 |
| `assets/js/filter.js` | 91 |
| `assets/js/action-modal.js` | 131 |
| `assets/js/tracker.js` | 243 |
| **Total** | **841** |

## Notes

- CSS bundle already comfortably under target. Phase 2 file consolidation aims for **~1,400 source lines** (down from 2,894) with similar or smaller bundle output.
- JS bundle: Phase 2 deletes `filter.js` (91 lines) and shrinks `action-modal.js` when ported to take-action page. Phase 3 adds `quiz.js` (~250 lines new). Net expected: roughly flat.
- No Lighthouse/WebPageTest run yet; deferred until network-affected changes (font self-hosting) ship.
