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

## What stays static even on a CMS page

The **Organization** node (`assets/organization-schema.json`) and the **WebSite** node are identical on every item — paste them as literal values, no placeholders. Only the page-specific nodes (WebPage, BreadcrumbList, the primary type, VideoObject) take CMS bindings.
