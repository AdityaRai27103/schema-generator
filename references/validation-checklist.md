# Validation checklist — the final gate

**Don't hand-walk this.** `scripts/validate.py` automates sections 1–4 and 6 below — run it on your output and fix every ERROR first (see SKILL.md Phase 6 for the command). This list documents what the script enforces, so you understand the failures it reports.

The **one thing the script cannot check is §5 (content match)** — that needs your judgment against the fetched page. Always do §5 by hand.

This catches the errors and warnings that the Rich Results Test would otherwise throw.

## 1. JSON syntax
- [ ] Valid JSON: balanced braces/brackets, double-quoted keys and string values, **no trailing commas**, no comments, no `{{ }}` left in a *static*-page output (placeholders are only for CMS templates).
- [ ] All strings properly escaped — no raw unescaped `"` or newlines inside a value.
- [ ] Wrapped in `<script type="application/ld+json"> … </script>`.

## 2. Graph structure
- [ ] Exactly one top-level `"@context": "https://schema.org"`, then `"@graph": [ … ]`.
- [ ] Nodes inside `@graph` do **not** repeat `@context`.
- [ ] Every node has an `@type`.
- [ ] Every `@id` is a unique absolute `https://` URL with a `#fragment`.
- [ ] Every `{ "@id": "…" }` reference points at a node that actually exists in the graph.

## 3. Property validity (the anti-hallucination check)
- [ ] **Every property on every node appears in that type's spec in `schema-types.md` / `video-schema.md`.** If you can't point to where a property is listed, delete it.
- [ ] All **Required** properties for each type are present. If a required value isn't on the page, flag it to the user rather than inventing one.
- [ ] Enumerated values use full schema.org URLs where required (`eventStatus`, `eventAttendanceMode`, `availability` → `https://schema.org/…`).

## 4. Data formats
- [ ] Dates are ISO 8601 (`YYYY-MM-DD` or `YYYY-MM-DDThh:mm:ss±hh:mm`). No "June 29, 2026" style.
- [ ] Durations are ISO 8601 (`PT1H30M`), not "90 min".
- [ ] All `url` / `@id` / `image` / `logo` / `sameAs` values are absolute URLs.
- [ ] `headline` ≤ 110 characters.
- [ ] `image` / `thumbnailUrl` point at real, accessible images (ideally ≥1200px wide for Article, ≥1280×720 for video).

## 5. Content match (Google policy)
- [ ] Every value corresponds to content actually visible on the page. No marked-up data that a visitor can't see — that risks a manual action.
- [ ] `author`, `datePublished`, prices, ratings reflect the real page; nothing fabricated.

## 6. Type-specific
- [ ] **Article:** has `headline`, `image`, `datePublished`, `author` (as an object with `name`), `publisher` → Organization with a `logo`.
- [ ] **Event:** has `name`, `startDate` (ISO 8601), `location` (Place *or* VirtualLocation, correctly chosen). `offers` (if present) has `price` + `priceCurrency`.
- [ ] **BreadcrumbList:** `position` is sequential from 1; every item except the last has an `item` URL.
- [ ] **FAQPage:** each `Question` has `name` + `acceptedAnswer.text`. (Reminded user about gov/health-only rich results.)
- [ ] **VideoObject:** has `name`, `description`, `thumbnailUrl`, `uploadDate`, and at least one of `contentUrl`/`embedUrl`.
- [ ] **Product:** has `name` + at least one of `offers`/`review`/`aggregateRating`.

## 7. Delivery
- [ ] Organization node embedded (every page).
- [ ] For CMS pages: binding table included; date/rich-text/absolute-URL gotchas called out.
- [ ] Closing reminder: validate the published URL in Google's Rich Results Test + Schema Markup Validator — that's the final authority.
