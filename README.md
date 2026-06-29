# schema-generator

A Claude Code skill that generates **error-free JSON-LD structured data** for Goodera's Webflow site from a page URL. Built to pass Google's [Rich Results Test](https://search.google.com/test/rich-results) and the [Schema Markup Validator](https://validator.schema.org/) with zero errors and zero warnings.

## What it does

Given a page URL, the skill fetches the page, classifies its content type, and emits a single `@graph` JSON-LD block ready to paste into a Webflow Embed — handling three cases:

1. **Static pages** — literal values scraped from the live page.
2. **Webflow CMS Collection templates** — `{{ Field }}` placeholders plus a binding table mapping each slot to a CMS field via Webflow's **+ Add Field**.
3. **Video** — a `VideoObject` for Google video indexing whenever a real video is detected on the page.

The Goodera `Organization` node is embedded on every page.

## Usage

Invoke in Claude Code:

```
/schema-generator https://www.goodera.com/blog/some-post
```

## How it avoids invalid schema

Schema.org has thousands of properties and a model can easily invent plausible-but-invalid ones. This skill prevents that two ways:

- **A whitelist clamp.** The model may only emit properties listed in the bundled type specs (`references/schema-types.md`, `references/video-schema.md`) — sourced from Google's supported structured-data features, not all of Schema.org.
- **A deterministic validator.** `scripts/validate.py` mechanically checks JSON syntax, graph structure, `@id` reference integrity, required properties per type, ISO 8601 dates, absolute URLs, and enum values before any output is shown. Run it standalone:

  ```bash
  python3 scripts/validate.py path/to/schema.json          # static page
  python3 scripts/validate.py path/to/schema.json --cms     # CMS template (allows {{ }} placeholders)
  ```

## Structure

```
schema-generator/
├── SKILL.md                          # 6-phase workflow + rules
├── assets/
│   └── organization-schema.json      # Goodera Organization node (every page)
├── references/
│   ├── google-supported-types.md     # the type whitelist
│   ├── schema-types.md               # required/recommended/allowed props + examples
│   ├── video-schema.md               # VideoObject + GSC video indexing
│   ├── webflow-cms-binding.md        # CMS field binding + gotchas
│   └── validation-checklist.md       # what validate.py enforces
└── scripts/
    └── validate.py                   # deterministic JSON-LD validator
```

## Installing

Clone into your Claude Code skills directory:

```bash
git clone <repo-url> ~/.claude/skills/schema-generator
```

The skill then registers as `/schema-generator`.
