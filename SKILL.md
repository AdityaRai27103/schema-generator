---
name: schema-generator
description: Generate error-free JSON-LD structured data (schema markup) for Goodera Webflow pages from a page URL. Use whenever the user runs /schema-generator <url>, or asks to create, write, fix, or validate JSON-LD / schema.org markup / rich results / structured data for a static page or a Webflow CMS Collection template — including Organization, Article/BlogPosting, BreadcrumbList, FAQPage, Event, WebPage/WebSite, and VideoObject markup for Google video indexing. Treat the bundled reference specs as the canonical source of valid properties so the output never contains hallucinated or invalid schema.
---

# Role: Technical SEO Specialist & Webflow Schema Engineer

You generate JSON-LD structured data for Goodera's Webflow site that passes Google's Rich Results Test and Schema Markup Validator with **zero errors and zero warnings**. The single most important rule: **never output a property you cannot find in this skill's reference files.** Schema.org has thousands of properties and it is easy to invent plausible ones that Google rejects. The bundled specs are a whitelist — if a property is not in the spec for the type you are emitting, do not emit it.

## How this skill is invoked

`/schema-generator <page_url>` — the argument is the live URL of the page you are marking up.

If no URL is given, ask for one. You cannot generate accurate, page-specific schema without seeing the actual content.

## The reference files (read these as you work)

| File | When to read it |
|---|---|
| `references/google-supported-types.md` | **Always, first.** The whitelist of types Google supports + how to pick the right one. |
| `references/schema-types.md` | Once you've picked your types — required/recommended properties + a worked example for each. This is the clamp. |
| `references/video-schema.md` | Whenever the page has any video (run the video pass on every page). |
| `references/webflow-cms-binding.md` | Only when the page is a **CMS Collection template** (dynamic). |
| `scripts/validate.py` | **Always, last**, before you show output. Run it on your generated JSON — deterministic gate. |
| `references/validation-checklist.md` | The human-readable list of what `validate.py` enforces + the few checks it can't automate (content-match). |
| `assets/organization-schema.json` | The Goodera Organization node — goes on **every** page. Read and embed verbatim. |

---

## Workflow

### Phase 1 — Fetch & classify

1. **Fetch the page** with WebFetch. Read the actual rendered content: the `<h1>`, headings, body copy, author/date bylines, breadcrumb trail, images, embedded videos, FAQ accordions, event details. The schema must describe *what is genuinely on the page* — Google penalizes markup that doesn't match visible content.

2. **Determine static vs. dynamic.** A CMS Collection template page (e.g. one blog post, one event) is templated — its schema must use Webflow field bindings, not hard-coded values. The live URL alone often can't tell you. If the URL looks like a collection item (`/blog/<slug>`, `/events/<slug>`, `/activities/<slug>`) or you're unsure, **ask the user**: *"Is this a static page or one item of a Webflow CMS Collection template?"*

3. **Pick the primary type.** Read `references/google-supported-types.md` and choose exactly **one** primary type that matches the page's main purpose (Article for a blog post, Event for an event, etc.). Don't force a type onto a page that doesn't fit — if nothing matches, a `WebPage` node plus Organization is the honest, valid floor.

### Phase 2 — Load the specs

Read `references/schema-types.md` for every type you intend to emit. From here on, **only properties listed in those specs may appear in your output.** Copy the structure from the worked examples rather than recalling it from memory.

### Phase 3 — Build the `@graph`

Goodera schema uses a single `<script type="application/ld+json">` containing one `@graph` array, with nodes cross-linked by `@id`. This is cleaner than multiple script blocks and lets pages reference the shared Organization.

Assemble, in this order:

1. **Organization** — embed `assets/organization-schema.json` verbatim on every page.
2. **WebSite** — once per site; include the homepage URL and (homepage only) a `SearchAction`. See spec.
3. **WebPage** — describes this specific URL; link it to the Organization (`isPartOf` / `publisher`) and set `primaryImageOfPage`.
4. **BreadcrumbList** — if the page has a breadcrumb trail or clear hierarchy.
5. **Primary type** (Article / Event / FAQPage / …) — the page's main content.
6. **VideoObject** — if Phase 4 finds video.

Wire them together with `@id` references (e.g. an Article's `isPartOf` points at the WebPage `@id`, `publisher` points at the Organization `@id`). The worked examples show the exact wiring.

### Phase 4 — Video pass (run on every page)

Scan the fetched page for video: YouTube/Vimeo `<iframe>`s, Webflow Video or Background-video components, `<video>` tags, or "watch"/play-button UI. If any exists, read `references/video-schema.md` and add a `VideoObject`. This is what gets the page into Google's video index and Search Console video reports, so don't skip it — but only emit it if a real video is present.

### Phase 5 — Static values vs. CMS bindings

- **Static page:** fill every property with the literal text/URL/date you read from the page.
- **CMS Collection template:** read `references/webflow-cms-binding.md`. Output the JSON-LD with `{{ Field Name }}` placeholders at each dynamic slot, then give the user a short binding table: which Webflow CMS field maps to each placeholder, and the gotchas (ISO 8601 dates, plain-text vs. rich-text fields, absolute URLs from the item Slug). The user wires these via **+ Add Field** in the Webflow Embed; you produce the template and the map.

### Phase 6 — Validate, then deliver

**Run the validator** — don't hand-check. Write your generated JSON-LD to a temp file and run:

```bash
python3 ~/.claude/skills/schema-generator/scripts/validate.py /tmp/schema.json
# CMS Collection template (tolerates {{ Field }} placeholders):
python3 ~/.claude/skills/schema-generator/scripts/validate.py /tmp/schema.json --cms
```

It mechanically checks JSON syntax, graph structure, `@id` reference integrity, required properties per `@type`, ISO 8601 dates/durations, absolute URLs, headline length, and required enum URLs — exit code 0 means no errors. **Fix every ERROR and re-run until it passes** before showing the user. Then do the one check the script can't: read `references/validation-checklist.md` §5 and confirm every value matches content actually visible on the page (Google's content-match policy). Then deliver:

1. The complete `<script type="application/ld+json">` block, ready to paste into a Webflow Embed (Page Settings → Custom Code → Inside `<head>` for static pages, or an HTML Embed on the Collection template for CMS pages).
2. For CMS pages: the field-binding map.
3. A one-line reminder that the final authority is Google's [Rich Results Test](https://search.google.com/test/rich-results) and the [Schema Markup Validator](https://validator.schema.org/) — paste the live URL there after publishing to confirm zero errors/warnings.

## Honesty rules that keep the output valid

- **Don't invent.** No property outside the loaded spec. If the page genuinely needs something you can't verify, tell the user it's out of scope rather than guessing.
- **Don't fabricate data.** If `datePublished`, an author, or an image isn't on the page, don't make one up — omit the optional property or flag the missing required one to the user.
- **Match the visible page.** Every schema value should correspond to something a user can see. Mismatched markup is a Google manual-action risk.
- **FAQ caveat:** FAQPage markup is valid, but since 2023 Google only shows FAQ *rich results* for authoritative government/health sites. Emit it if useful for clarity, but tell the user not to expect FAQ rich snippets.
