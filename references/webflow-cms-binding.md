# Webflow CMS Collection template binding

A Collection template page is rendered once per CMS item. Its schema must pull values from CMS fields, not hard-code them. You can't click inside the Webflow Designer, so your job is to produce a **template with placeholders** plus a **binding map** the user follows in the Designer.

## How the user wires it (context for your instructions)

1. In the Collection template page, add an **HTML Embed** element (or use Page Settings → Custom Code if the page allows it — Embed is more reliable for CMS fields).
2. Paste the `<script type="application/ld+json">` block you generated.
3. For each `{{ Field Name }}` placeholder: delete the placeholder text, keep the cursor there, click **+ Add Field**, and pick the matching CMS field. Webflow inserts a field token that renders the live value at publish.
4. Publish, then validate the live URL in the Rich Results Test.

## Your output format for a CMS page

1. The full JSON-LD block with `{{ Field Name }}` placeholders at every dynamic value.
2. A binding table:

| Placeholder | Webflow CMS field | Notes |
|---|---|---|
| `{{ Post Title }}` | Name | plain text |
| `{{ Slug }}` | Slug | builds the canonical URL |
| `{{ SEO Description }}` | Meta Description (plain text) | **not** the rich-text body |
| `{{ Published On (ISO 8601) }}` | Published On | format as ISO 8601 (see below) |
| `{{ Main Image URL }}` | Main Image | use the field's URL |
| `{{ Author Name }}` | Author → Name (referenced field) | |

## Gotchas that cause invalid schema (call these out to the user)

- **Rich-text fields break JSON.** A rich-text body outputs HTML tags and unescaped quotes/newlines that shatter the JSON string. **Never bind a description/headline to a Rich Text field.** Use a dedicated **plain-text** field (e.g. "SEO Description", "Schema Summary"). If one doesn't exist, tell the user to add it.
- **Dates must be ISO 8601.** Webflow date fields, via **+ Add Field**, let you choose a format — pick one that yields `YYYY-MM-DD` or full ISO 8601 with timezone. A display format like "June 29, 2026" is invalid for `datePublished`/`startDate`/`uploadDate`. Flag this every time a date is involved.
- **URLs must be absolute.** Build canonical/`@id`/`url` values as `https://www.goodera.com/<collection>/{{ Slug }}` — the Slug field gives the path segment. A bare slug or relative URL is invalid for `@id` and `url`.
- **Quotes inside text fields.** Even plain-text fields can contain `"` or `&`. Advise the user to avoid raw double-quotes in fields feeding JSON-LD, or to keep those values in fields they control. There's no per-field escaping in the Designer, so the safest path is clean source text.
- **Referenced fields (Author, Category).** You can pull fields from a single-reference field (e.g. Author → Name, Author → Profile URL) via + Add Field. Multi-reference fields can't be looped in a static script — don't try to enumerate them.
- **Item-specific `@id`.** Make every node's `@id` unique per item by including `{{ Slug }}`, e.g. `https://www.goodera.com/blog/{{ Slug }}/#article`. This keeps each published item's graph self-consistent.

## Collection List pages (many CMS items on ONE static page)

This is a different case from a Collection *template*. A page like `/glossary` or a blog index is a **single static page** that renders many CMS items through a **Collection List** element. Hand-listing every item in the schema means it goes stale the moment someone adds a CMS entry. The fix is to let Webflow render one schema fragment **per item, server-side**, so the markup auto-updates with the collection — no JavaScript, no DOM scraping.

**Why not client-side JavaScript?** A JS snippet that scrapes `.w-dyn-item` cards and injects JSON-LD on load is fragile (breaks when the design's classes change) and second-class for SEO: Google picks up JS-injected structured data only in its later rendering wave, and `validator.schema.org` (which fetches static HTML) can't see it at all. Server-rendered Embeds avoid all of that.

**The two-Embed pattern:**

1. **Skeleton Embed** — static, in Page Settings → Custom Code (head) or an Embed at the top of the page. Holds the `@graph` with Organization, WebSite, a `CollectionPage`, BreadcrumbList, and the **empty** `DefinedTermSet` / `ItemList` container (no items inlined). Its `@id` is what the per-item fragments link to.

2. **Per-item Embed** — placed **inside the Collection List Item** (so Webflow repeats it once per entry). It emits one *standalone* `<script type="application/ld+json">` containing a single item (e.g. a `DefinedTerm`) that links back to the container by `@id`. Bind its fields with **+ Add Field**.

```html
<!-- Embed B: inside the Collection List Item, repeats per term -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "DefinedTerm",
  "name": "{{ Term Name }}",
  "description": "{{ Definition (plain text) }}",
  "inDefinedTermSet": "https://www.goodera.com/glossary/#definedtermset"
}
</script>
```

Each item is **its own valid JSON-LD block** — so there is no array and therefore no trailing-comma problem (the classic Webflow list-schema headache). Google merges all the `DefinedTerm`s into the `DefinedTermSet` because they share its `@id` via `inDefinedTermSet`. Add a CMS term → a new server-rendered `DefinedTerm` appears automatically.

**Validate both halves:** run the skeleton through `scripts/validate.py`, and run one filled-in sample of the per-item block through it too (it accepts a single top-level node, not just a `@graph`). Use `--cms` so the `{{ }}` placeholders don't trip it.

Generalizes beyond glossaries: blog index → `CollectionPage` + per-item `BlogPosting`; resource hub → `ItemList` + per-item entries. Same skeleton-plus-repeating-Embed shape.

## What stays static even on a CMS page

The **Organization** node (`assets/organization-schema.json`) and the **WebSite** node are identical on every item — paste them as literal values, no placeholders. Only the page-specific nodes (WebPage, BreadcrumbList, the primary type, VideoObject) take CMS bindings.
