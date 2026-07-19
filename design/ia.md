# 1 in 7 - Information Architecture

Status: **draft v2 - addresses adversarial review findings**. Spec for the Phase 1 IA reset of the UI/UX overhaul. Read alongside `design/css-architecture.md` (Phase 2) and `design/brand.md` (legacy - will be rewritten in Phase 6).

Changes from v1: resolved all "open questions" into explicit decisions; added Privacy & data handling (§7); added URL stability table (§4); reconciled Treatments hub and comorbidities (§3, §5); rewrote i18n strategy to honor the no-English-only-ship constraint (§12); scoped action-modal port realistically (§8); scoped quiz feature realistically (§6).

---

## 1. Problem statement

Two competing nav systems and no defined user journey:

- The **sidebar** lists 18 pages grouped into 4 content-type categories.
- The **homepage filter cards** re-list the same 18 items as in-page filters that render stripped-down page excerpts inside the home page.
- The **action modal** offers a third path (Symptoms / Connect / Awareness) that overlaps with the above.

A first-time visitor lands on the homepage and sees seven competing sections with no clear first step. On mobile the entire sidebar - including search and language picker - is hidden behind a hamburger.

**Goal:** one nav, three explicit journeys, search elevated to a top-bar primary affordance, modal absorbed into a real page, mobile-first ergonomics throughout.

---

## 2. The three primary journeys

Every visitor maps to one of three intents on arrival. The IA must make each path obvious from the home page.

| # | Intent | Entry phrase | Path |
|---|---|---|---|
| 1 | "I think I might have endo / adeno" | *"Could this be me?"* | Symptom quiz → Diagnosis → Healthcare |
| 2 | "I have it, what now" | *"I'm already diagnosed"* | Treatments → Mental health → Resources/community |
| 3 | "I want to understand / support someone" | *"Learn about endo & adeno"* | Conditions → Research → Myths |

### Cross-cutting users

Real users span all three intents (newly diagnosed people are also learning while seeking care). The nav resolves this two ways:

1. **A persistent "Browse all topics" entry** at the bottom of the sidebar that opens an index of every page, grouped alphabetically. Not a journey - an escape hatch.
2. **Cross-links at the end of every page** - each content page closes with "Related" links spanning journeys, so a user reading `/diagnosis/` (Journey 1) sees curated links into `/medications/` (Journey 2) and `/research/` (Journey 3).

---

## 3. Page set decisions

Current page set: 18 pages. Every URL is preserved (see §4 for stability table).

| Slug | Decision | Where it lives in new nav |
|---|---|---|
| `_index` | Keep as homepage | - |
| `about` | Keep | Footer link |
| `endometriosis` | Keep | Learn |
| `adenomyosis` | Keep | Learn |
| `myths` | Keep | Learn |
| `notable-people` | Keep | Learn |
| `diagnosis` | Keep | Could this be me |
| `healthcare` | Keep | Could this be me |
| `comorbidities` | Keep (no demotion) | Could this be me, sub-link from `/diagnosis/` |
| `fertility` | Keep | I have endo, sub-link from `/treatments/` |
| `medications` | Keep | I have endo, sub-link from `/treatments/` |
| `mental-health` | Keep | I have endo |
| `tracker` | Keep | I have endo (also linked from quiz result) |
| `faq` | Keep | Footer link |
| `resources` | Keep | I have endo |
| `education` | Keep | Learn (now hosts featured videos) |
| `research` | Keep | Learn |
| `graphic-images` | Keep, content-warning page | Not in nav; linked from carousel CTA only |
| **`quiz`** | **New page** | Could this be me (entry point, see §6) |
| **`treatments`** | **New hub page** | I have endo (entry point, see §5) |
| **`take-action`** | **New page** (modal moves here, see §8) | Footer + mobile bottom nav |

Net: 18 → **21 pages**. Page count grows because the quiz, treatments hub, and take-action page are all promoted from inline-on-home / modal to first-class routes.

### Reversal of v1's "demote `comorbidities`" decision

Adversarial review flagged a missing redirect strategy and broken deep links. Resolution: don't demote. Keep `/comorbidities/` as a top-level URL; link it under both *Could this be me* (as a sub-link in the sidebar) and from `/diagnosis/` (as an inline link). No URL breaks; sidebar noise is addressed by grouping (see §5) not by removal.

---

## 4. URL stability table

Explicit policy: **zero URL breakage in this overhaul.** Every existing URL continues to resolve. New URLs are additive only.

| URL | Status | Notes |
|---|---|---|
| `/` | Unchanged | Rewritten content per §9, same URL |
| `/about/` | Unchanged | |
| `/endometriosis/` | Unchanged | |
| `/adenomyosis/` | Unchanged | |
| `/diagnosis/` | Unchanged | Inline `#comorbidities` anchor added |
| `/healthcare/` | Unchanged | |
| `/comorbidities/` | Unchanged | Reversed v1 demotion |
| `/myths/` | Unchanged | |
| `/notable-people/` | Unchanged | |
| `/fertility/` | Unchanged | Reparented under treatments in nav |
| `/medications/` | Unchanged | Reparented under treatments in nav |
| `/mental-health/` | Unchanged | |
| `/tracker/` | Unchanged | |
| `/resources/` | Unchanged | |
| `/education/` | Unchanged | Featured videos block migrates here from home |
| `/research/` | Unchanged | |
| `/faq/` | Unchanged | Footer link |
| `/graphic-images/` | Unchanged | Excluded from search index (§10) |
| `/quiz/` | **New** | Symptom quiz, formerly inline poll |
| `/treatments/` | **New** | Treatment hub page summarizing options + sub-link grid |
| `/take-action/` | **New** | Modal content as page |

Anchor links inside existing pages (e.g., `#comorbidities` in `/diagnosis/`) are additive - no existing anchors are renamed.

---

## 5. New nav structure

Sidebar reorganized around the three journeys (was: Conditions / Getting Care / Support / Research):

```
Could this be me?
  Symptom quiz          /quiz/
  Diagnosis             /diagnosis/
  Co-morbidities        /comorbidities/
  Healthcare            /healthcare/

I have endo / adeno
  Treatments            /treatments/      (hub page)
    Medications         /medications/
    Fertility           /fertility/
  Mental health         /mental-health/
  Resources & support   /resources/
  Symptom tracker       /tracker/

Learn
  Endometriosis         /endometriosis/
  Adenomyosis           /adenomyosis/
  Myths & facts         /myths/
  Notable people        /notable-people/
  Research              /research/
  Education             /education/

[Footer]
  About                 /about/
  FAQ                   /faq/
  Take action           /take-action/
  Browse all topics     (in-page index modal)
```

### Treatments hub - decision: real page, not nav-only

`/treatments/` is a **real markdown page** at `content/treatments.md` that:

- Introduces the categories (surgical, hormonal, non-hormonal, alternative)
- Links to each sub-page (`/medications/`, `/fertility/`, etc.) with a one-sentence description
- Hosts content currently buried in `/endometriosis/` and `/adenomyosis/` about treatment options

Why a real page, not a nav-only grouping: the hub gets indexed by search, gets a real URL for linking from external sites, and gives users a content-rich landing if they don't yet know which sub-topic they need.

### Sidebar links *navigate*, not *filter*

The current sidebar-link-activates-home-filter-panel behavior is removed. Clicking a sidebar link routes to the page. `assets/js/filter.js`, `data-sidebar-filter` attributes, and `build_filter_panels()` in `build.py` are deleted in Phase 3 (see §11).

### Why this structure beats the four-bucket version

- The current four groups are organized by *content type*, not *user intent*. Users don't think "I need a Support resource" - they think "I'm scared and need to find a doctor."
- Journey labels phrased as the visitor's own thought lower cognitive load.
- "Could this be me?" first acknowledges the 10-year diagnostic delay - the #1 problem this site addresses.

---

## 6. The quiz - scope clarification (was under-specified in v1)

Adversarial review correctly flagged that the v1 phrasing ("symptom quiz becomes a journey entry") understated the work. Explicit scope:

### What exists today

`templates/home.html` lines 61–135: 8 symptom checkboxes inline on the homepage. Submission goes to Formspree (a third-party form host). `assets/js/poll.js` (31 lines) handles validation and POST. A "thanks" panel appears with 3 hardcoded suggestion links.

### What the new quiz is

A **new client-side decision tool**, not a relocation:

- New page `content/quiz.md` + `templates/quiz.html` partial.
- Expanded question set (10–15 checkboxes covering both endo and adeno symptom patterns) with optional severity scoring.
- **Client-side recommendation engine** in `assets/js/quiz.js` that maps answers to a personalized result panel ("Based on your answers, your next steps are…"). Recommendations are deterministic and rule-based, not ML - a small set of if/then rules per symptom cluster.
- **No third-party submission by default.** Formspree integration becomes opt-in via a separate "help us improve" checkbox at the bottom of the result panel, with an explicit consent label. See §7 (Privacy).
- The inline poll on the homepage is replaced by a 3-question teaser that links to the full quiz at `/quiz/`. Keeps the high-intent funnel visible without duplicating logic.

### Implementation scope estimate

| Item | LoC |
|---|---|
| `content/quiz.md` (copy) | 200 |
| `templates/quiz.html` (partial) | 80 |
| `assets/js/quiz.js` (recommendation engine + UI state) | 250 |
| Updated `assets/js/poll.js` (homepage teaser, retired) | -31 |
| New i18n keys (quiz Q&A, results) | ~50 keys |

This is **net-new feature work** of ~500 lines + i18n. The plan owner should treat it as a feature, not as part of "moving things around."

---

## 7. Privacy & data handling

Symptom data is special-category personal data under GDPR Article 9. The site serves a global audience including the EU; this section is binding.

### Principles

1. **Client-side by default.** Quiz answers, tracker entries, sidebar group state, language preference, and theme preference live in `localStorage` only and never leave the device unless the user explicitly opts in.
2. **No analytics on health data.** Page analytics may exist (basic page views), but symptom answers, tracker entries, and quiz inputs are never sent to any analytics provider.
3. **Third-party submission is opt-in.** The existing Formspree integration is reframed: it appears only at the bottom of the `/quiz/` result panel as a checkbox + explicit-consent label ("Send anonymized answers to help improve this resource - optional"), defaulting to unchecked. No submission without affirmative consent.
4. **Self-host fonts.** Google Fonts is removed in Phase 2 (Figtree variable font is self-hosted under `/fonts/`) so that page loads don't leak user IP to Google. See `design/css-architecture.md` §9.
5. **Privacy notice on every page.** A footer link to `/privacy/` (new page) appears on every page. Notice covers what's stored, where, retention, opt-in submission, third-party fonts/services (post-Phase-2: none).
6. **Privacy notice is localized.** Translation of the privacy notice into all 26 supported languages is a Phase 5 blocker (not Phase 6). EU users in any of the 13 EU languages we support must see the notice in their language.

### What we collect, where it lives, when it's deleted

| Data | Storage | Retention | User control |
|---|---|---|---|
| Quiz answers (current session) | In-memory only | Cleared on navigation | Auto |
| Quiz "save my result" (opt-in) | `localStorage` key `quiz-result` | Until user clears | "Clear my data" button in `/privacy/` |
| Tracker entries | `localStorage` key `tracker-entries` | Until user clears | "Clear my data" button in `/privacy/` |
| Theme preference | `localStorage` key `theme` | Until user clears | UI toggle |
| Language preference | `localStorage` key `site-language` | Until user clears | UI picker |
| Sidebar group expanded/collapsed state | `localStorage` key `sidebar-groups` | Until user clears | Auto on toggle |
| Opt-in submission to Formspree | Formspree's servers | Per their TOS | One-time consent at point of submission |

### Pages affected

- New: `content/privacy.md`, route `/privacy/`. Linked from every page footer.
- Updated: every page's footer block gets the privacy link.
- Updated: `/take-action/` page and `/quiz/` page reference the privacy notice when they ask for any input.

### Cookie banner

**Not needed** while we have zero non-essential cookies/third-party calls (post-Phase-2). If we re-add analytics or any third-party service later, a banner becomes mandatory.

---

## 8. Top bar (mobile + desktop)

Persistent thin bar at the top of the content area, visible on all viewports.

```
[≡]  [brand]    [search...]    [EN ▾]  [☀]
```

- **Hamburger (mobile only)** - opens off-canvas sidebar. Hidden on desktop (sidebar persistent).
- **Brand** - text "1 in 7", links to `{{BASE_URL}}` (templating note: never `/` alone; all internal links use `{{BASE_URL}}` to honor the GitHub Pages `/Awesome-Endo-Adeno-Resources/` subpath and the Cloudflare Pages `/` root identically).
- **Search** - input expands inline. Mobile: input collapses to icon, expands to full top-bar width on focus (animated via `transition: width 200ms`).
- **Language picker** - collapsed to language code (`EN`, `ES`, etc.) with a dropdown chevron. Click opens a popup list of 26 languages. Replaces the sidebar `<select>`. Width budget: the popup is positioned with `right: 0` and the trigger is icon+code only, so the picker never has to fit 26 long-name labels in-line.
- **Theme** - sun/moon toggle, joins the top bar (was: floating top-right `position: fixed`).

Scroll behavior: `position: sticky; top: 0` on the body's natural scroll. Verified safe - the current site uses viewport-level scrolling (body `overflow-y: auto` with content sized larger than viewport, root scroller is `html`).

i18n keys: all exist (`search_placeholder`, `language_picker_label`, `toggle_theme`, `toggle_menu`) - no new keys.

---

## 9. Bottom nav (mobile only, ≤768px)

A fixed-position 4-tab bar at the bottom of the viewport, in the thumb zone.

```
[Home]  [Quiz]  [Learn]  [Help]
```

| Tab | Icon | Route | i18n key |
|---|---|---|---|
| Home | house | `{{BASE_URL}}` | `nav_home` |
| Quiz | clipboard-check | `{{BASE_URL}}quiz/` | `nav_quiz` |
| Learn | book-open | `{{BASE_URL}}endometriosis/` | `nav_learn` |
| Help | life-buoy | `{{BASE_URL}}take-action/` | `nav_help` |

### iOS / Android safe-area handling

- Container uses `padding-bottom: env(safe-area-inset-bottom)` so the nav clears iOS home indicator + Android gesture bar.
- Content shell adds `padding-bottom: calc(4rem + env(safe-area-inset-bottom))` to prevent the last bit of content being covered.
- Use `dvh` (dynamic viewport height) units, not `vh`, so the layout responds correctly to iOS Safari's URL bar slide-up/down.

### Back-to-top collision

The current back-to-top button sits at `bottom: 1rem; right: 1rem`. With the bottom nav at `bottom: 0`, they collide. Resolution:

- On mobile, back-to-top moves to `bottom: calc(4rem + env(safe-area-inset-bottom) + 1rem)` - above the bottom nav.
- On desktop, back-to-top stays at `bottom: 1rem; right: 1rem` (bottom nav is hidden).
- Also fix the current latent bug in back-to-top JS (binds to `container.scrollTop` on desktop, but container doesn't scroll). Phase 2 standardizes on `window.pageYOffset`.

### Clickjacking-adjacent concern

Bottom nav at fixed position can intercept taps intended for dialog/sheet actions. Mitigation:

- Any dialog or full-screen sheet (e.g., the share-result panel from quiz) hides the bottom nav (`.bottomnav { display: none }` when a `[role="dialog"]` is open in the body).
- Confirm-action buttons inside any sheet are placed in the *top* of the sheet, not the bottom, so they never share thumb territory with the nav.

### Why these four tabs

- **Home** for resetting.
- **Quiz** as the highest-traffic entry to Journey 1 (the diagnostic-delay primary problem).
- **Learn** points at the most-read content page (`/endometriosis/`).
- **Help** opens the take-action page; replaces the current floating "Take Action Now" modal CTA.

Hidden on desktop (≥1024px) where the persistent sidebar serves the same role.

i18n: 4 new keys (`nav_home`, `nav_quiz`, `nav_learn`, `nav_help`).

---

## 10. Action modal - port to /take-action/

The action modal (Symptoms / Connect / Awareness) becomes a route at `/take-action/`.

### Honest scope (was understated in v1)

The current modal is a **mini-app**, not markdown content. It has:

- 3 cards entry view
- 3 sub-views (one per card), each with:
  - Checklist (Symptoms view)
  - Templated copy-to-clipboard messages (Connect, Awareness views)
- Back-navigation between sub-views
- Focus management, scale-in animation, overlay close-on-click

Porting it means:

1. New `content/take-action.md` with the three card titles and intro copy (~50 lines).
2. New `templates/take-action.html` partial holding the three-card grid + the three sub-view panels (~150 lines, all the rich UI markup that doesn't fit in markdown).
3. Rewrite `assets/js/action-modal.js` (131 lines today) as `assets/js/take-action.js` driving in-page view switching instead of overlay open/close. About 90% of logic reuses.
4. Remove modal overlay markup from `templates/base.html` (lines 146 onward in base.html).
5. Remove `assets/css/action-modal.css` (600 lines); the small subset for the three sub-views moves into `assets/css/pages.css`.

Total: roughly **8 hours of focused work**. Not the 30 minutes that "modal → markdown page" implies.

### Privacy property loss - acknowledged trade-off

The current modal doesn't change the URL. Visiting `/take-action/` does put it in browser history and the URL bar - a small privacy regression for users on shared devices. We accept this trade-off in exchange for:

- Linkability (someone can share `/take-action/` to a friend without explaining "go to the home page and click the floating button")
- Search-indexability (modal content currently invisible to search)
- Bottom-nav target (the Help tab needs a real route)
- Bookmarkability

The privacy notice on the take-action page will note: *"Visiting this page is logged in your browser history like any other page. If you're using a shared device, you may want to clear history afterward."*

### URL strategy

- The CTA buttons on home (`#cta-take-action`, `#poll-take-action`) navigate to `{{BASE_URL}}take-action/` instead of opening the modal.
- The Help tab in bottom nav points to the same.
- The take-action page is **excluded from the search index** (see §11) - searching for "endometriosis" shouldn't surface a UI-tooling page.

i18n: all existing card title/body keys reused (`actions_symptoms_title`, `actions_connect_title`, etc.). One new key: `take_action_title`.

---

## 11. Search index inclusion/exclusion rules

`build_search_index()` currently indexes every `content/*.md` page. New explicit policy:

| Slug | Indexed? | Why |
|---|---|---|
| All journey content pages | Yes | Default |
| `/graphic-images/` | **No** | Content-warning page; surfacing it via search defeats the warning |
| `/take-action/` | **No** | UI/tooling page, not informational content |
| `/privacy/` | **No** | Legal/utility page; surface from footer only |
| `/about/`, `/faq/` | Yes | Informational |
| `/quiz/` | Yes | Lands users into Journey 1 |
| `/tracker/` | Yes | Surfaces the tool when searched |

Implementation: add a `search: false` frontmatter key to the markdown of excluded pages; `build_search_index()` honors it.

The tracker page's *content* (description of the tool) is indexed; **the user's tracker data is never indexed** - it lives only in their `localStorage` and is never read at build time.

---

## 12. i18n strategy - honors the no-English-only-ship constraint

User constraint: *"Every new copy string and every nav item must have a data-i18n key from day one. No English-only ship."*

Two-part compliance:

### Part A - every new string is wired

Every new copy element in HTML/templates has a `data-i18n="key"` attribute from the moment it's written. No exceptions, no `TODO:i18n` placeholders. `i18n.js` already falls back to the English value automatically when a target-language string is missing - so wiring is what unlocks all 26 languages with English as fallback.

### Part B - every new key has all 26 translations before Phase 3 ships

Adversarial review correctly noted v1 violated this by saying "ships English-only with a translation pass before launch." Revised: **translation completion is a Phase 3 ship blocker, not a pre-launch task.**

Process:

1. Phase 1 closes by listing every new i18n key with its English source value in a single file: `static/i18n/_new_keys_phase1.json`.
2. Phase 2 expands the list as the CSS rebuild introduces new UI strings.
3. Before Phase 3 implementation, all new keys are machine-translated (DeepL or equivalent) into the 25 non-English languages and merged into `static/i18n/translations.json`. Auto-translated entries are flagged with a sibling `static/i18n/_review.json` listing which keys need human review.
4. Phase 3 ships with **complete** translations (auto-translated where human review hasn't completed yet, but never missing). User-visible UI is never English-only in any language.
5. Human translator review is an ongoing Phase 5/6 task that *improves* the auto-translations but isn't a launch gate.

### Concrete new-key inventory

| Source | Keys | Count |
|---|---|---|
| Nav groups (§5) | `nav_group_could_this_be_me`, `nav_group_already_diagnosed`, `nav_group_learn`, `nav_group_browse_all` | 4 |
| Sidebar items (§5) | `nav_quiz`, `nav_treatments`, `nav_take_action`, `nav_browse_all` | 4 |
| Bottom nav (§9) | `nav_home`, `nav_learn`, `nav_help` *(plus `nav_quiz` already counted)* | 3 |
| Home hero (§13) | `home_hero_headline`, `home_hero_cta_primary`, `home_hero_cta_secondary` | 3 |
| Journey cards (§13) | `journey_1_title`, `journey_1_desc`, `journey_1_cta`, `journey_2_title`, `journey_2_desc`, `journey_2_cta`, `journey_3_title`, `journey_3_desc`, `journey_3_cta` | 9 |
| Search (§8) | `search_suggestion_1` through `search_suggestion_6` | 6 |
| Treatments hub (§5) | `treatments_title`, `treatments_intro`, sub-link descriptions | 6 |
| Quiz content (§6) | quiz Q&A, result panels, opt-in copy | ~50 |
| Take-action page (§10) | `take_action_title`, plus reusing existing modal keys | 1 |
| Privacy notice (§7) | `privacy_title`, body sections | ~12 |

**Total new keys: ~98.** Each gets 26 translations = **~2,548 translation entries**. Machine translation handles the first pass; human review polishes incrementally.

---

## 13. Home page block plan

Detailed in Phase 3 (`templates/home.html` rewrite). For IA purposes, five blocks in order:

1. **Hero** - one sentence problem statement, one primary CTA ("Take the symptom quiz" → `/quiz/`), one secondary link ("I'm already diagnosed" → `/treatments/`).
2. **Three journey cards** - large tap targets, one per journey, with the entry phrase + first concrete next step.
3. **Linked stats strip** - the four existing stats become buttons routing to source/topic.
4. **Featured videos** - kept on home as the BAFTA documentary block. Demoted in vertical priority (after journey cards + stats) but not removed. Reframed as a "Watch & learn" module so it feels like content not a competing CTA. (v1 wanted to remove these; adversarial review correctly identified that as an SEO/visibility regression. Reversed.)
5. **Below the fold** - 3-question quiz teaser (full quiz lives at `/quiz/`), carousel, "Get help now" CTA → `/take-action/`.

---

## 14. What gets deleted

- `assets/js/filter.js` - filter-panel system no longer needed.
- `build_filter_panels()` function in `build.py` and `{{FILTER_PANELS}}` template marker.
- Sidebar `data-sidebar-filter` attributes and the inline JS in `base.html` that wires them up.
- `<section class="resource-cards">` and the homepage filter panel block.
- Modal overlay markup in `templates/base.html` (modal becomes `/take-action/` page).

### What stays (and is migrated)

- All content under `content/` (no content deletion; reorganized in §3).
- Sidebar nav, reorganized around journeys and rewired to real navigation.
- Search, language picker, theme toggle - moved to top bar.
- Carousel, poll (de-emphasized, kept on home).
- Symptom tracker on its own page.
- Featured videos on home (demoted in priority but kept).
- Action modal mini-app, ported to `/take-action/`.

---

## 15. Resolved questions (v1 had these as "open")

1. ~~Quiz as a standalone page?~~ **Yes** (§6) - new page, new feature, scope acknowledged.
2. ~~Comorbidities demoted?~~ **No** (§3, §5) - kept at top-level URL, regrouped in nav under Journey 1.
3. ~~FAQ merged into About?~~ **No** - kept as footer link (§3).
4. ~~Bottom nav tab choices?~~ Home / Quiz / Learn / Help (§9).
5. ~~Action modal stays as overlay or becomes route?~~ **Becomes route** on all viewports (§10).
6. ~~Featured videos moving from home to /education/?~~ **No, kept on home** (§13) - both places now host video content.

### Remaining decisions that need explicit owner sign-off

These are not blocking the Phase 2 CSS rebuild (which can proceed in parallel), but they block Phase 3 implementation:

a. **Quiz recommendation rules.** §6 commits to client-side rule-based recommendations. Who authors the rules (which symptom cluster → which next page)? Likely needs medical-input review; not just an engineering call.
b. **Privacy notice authoring.** §7 mandates `/privacy/`. Owner needs to draft the legal text (or approve a template). Translation pass is automatable; the source text is not.
c. **Treatments hub copy.** §5 commits to a real page. Who writes it?

If any of these don't have an owner, surface that risk before Phase 3 begins.
