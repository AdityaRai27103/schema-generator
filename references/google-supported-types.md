# Google-supported structured data types (the whitelist)

Schema.org defines thousands of types. **Google only produces rich results / search features for the list below.** Marking up a page with a type Google doesn't support is not "wrong," but it does nothing for SEO and adds risk. So: pick from this list. If a page's content doesn't map to any of these, fall back to a plain `WebPage` + `Organization` graph — that's valid and honest, never a forced fit.

## Pick the ONE primary type that matches the page's main job

| Page is mainly… | Primary type | Spec section |
|---|---|---|
| A blog post / article / news / guide | `Article` (or `BlogPosting` for blog) | schema-types.md → Article |
| An event (volunteering session, webinar, summit) | `Event` | schema-types.md → Event |
| A list of FAQs | `FAQPage` | schema-types.md → FAQPage |
| A product/offering with price or rating | `Product` | schema-types.md → Product |
| A person / team-member profile | `ProfilePage` + `Person` | schema-types.md → Person |
| A video page | `VideoObject` (as primary) | video-schema.md |
| General page (home, about, landing, services) | `WebPage` only | schema-types.md → WebPage |

## Nodes that are added in addition to the primary type (not "primary" themselves)

- **`Organization`** — on **every** page (Goodera node, from `assets/organization-schema.json`).
- **`WebSite`** — once per site; carries the optional Sitelinks `SearchAction` (homepage).
- **`WebPage`** — describes the specific URL; the structural backbone of the `@graph`.
- **`BreadcrumbList`** — any page with a breadcrumb trail or clear hierarchy.
- **`VideoObject`** — any page containing a real video, even if the primary type is Article/Event/etc.

## Types Google supports but Goodera rarely needs

Course, Dataset, JobPosting, LocalBusiness, Recipe, Review snippet, Software App, Q&A, Movie, Math solver, Vacation rental, Carousel. Use only if a page is genuinely one of these. If you reach for one, still confirm its required properties against Google's docs — don't guess.

## Caveats that prevent false expectations

- **FAQPage**: still valid markup, but since 2023 Google shows FAQ rich results **only for authoritative government and health-site pages.** Generate it for structure if helpful, but warn the user not to expect FAQ snippets on a marketing site.
- **HowTo**: Google **deprecated** HowTo rich results. Don't propose HowTo for new markup.
- **Product**: a price, `AggregateRating`, or `Review` is what unlocks the product rich result. A Product node with only a name and image earns no rich result and may warn. For Goodera "services," prefer describing them on a `WebPage` unless there's a real offer/price.
