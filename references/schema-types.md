# Schema type specs (the property whitelist + worked examples)

For each type: **Required** = Google errors without it. **Recommended** = Google warns / you lose features without it. **Allowed** = valid extras you may use if the page supports them. **Do not emit anything outside these lists.** Copy structure from the worked examples; all examples use the shared `@graph` + `@id` pattern.

All values shown as `{{ Field Name }}` are CMS-binding placeholders (see webflow-cms-binding.md). On a static page, replace them with literal values.

## Table of contents
1. [WebSite](#website)
2. [WebPage](#webpage)
3. [BreadcrumbList](#breadcrumblist)
4. [Article / BlogPosting](#article--blogposting)
5. [Event](#event)
6. [FAQPage](#faqpage)
7. [Person / ProfilePage](#person--profilepage)
8. [Product](#product)
9. [Service + OfferCatalog](#service--offercatalog)
10. [ItemList](#itemlist)
11. [CollectionPage](#collectionpage)
12. [DefinedTermSet / DefinedTerm (glossaries)](#definedtermset--definedterm)
13. [The full graph: how nodes wire together](#the-full-graph)

---

## WebSite
Use once per site. The `SearchAction` (Sitelinks Search Box) belongs on the **homepage only** and only if the site has a working `/search?q=` endpoint — otherwise omit it.

- **Required (for SearchAction):** `url`, `potentialAction`
- **Recommended:** `name`, `publisher` (→ Organization `@id`)
- **Allowed:** `inLanguage`, `description`

```json
{
  "@type": "WebSite",
  "@id": "https://www.goodera.com/#website",
  "url": "https://www.goodera.com",
  "name": "Goodera",
  "publisher": { "@id": "https://www.goodera.com/#organization" },
  "inLanguage": "en-US"
}
```

---

## WebPage
The backbone node describing one URL. Not a rich result by itself, but it anchors the graph and is good practice.

- **Required:** `@id`, `url`, `name`
- **Recommended:** `isPartOf` (→ WebSite), `about`/`publisher` (→ Organization), `primaryImageOfPage`, `datePublished`, `dateModified`, `breadcrumb` (→ BreadcrumbList)
- **Allowed:** `description`, `inLanguage`, `lastReviewed`

```json
{
  "@type": "WebPage",
  "@id": "https://www.goodera.com/about/#webpage",
  "url": "https://www.goodera.com/about",
  "name": "About Goodera",
  "isPartOf": { "@id": "https://www.goodera.com/#website" },
  "about": { "@id": "https://www.goodera.com/#organization" },
  "primaryImageOfPage": { "@type": "ImageObject", "url": "https://.../hero.jpg" },
  "breadcrumb": { "@id": "https://www.goodera.com/about/#breadcrumb" },
  "inLanguage": "en-US"
}
```

---

## BreadcrumbList
Mirror the page's actual breadcrumb trail / URL hierarchy. `position` is 1-based. The final item is the current page; its `item` may be omitted or self-referential.

- **Required:** `itemListElement` (array of `ListItem`); each `ListItem` needs `position` and `name`; `item` (a URL) is required for every item **except** the last.
- **Allowed:** nothing else.

```json
{
  "@type": "BreadcrumbList",
  "@id": "https://www.goodera.com/blog/post-slug/#breadcrumb",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.goodera.com" },
    { "@type": "ListItem", "position": 2, "name": "Blog", "item": "https://www.goodera.com/blog" },
    { "@type": "ListItem", "position": 3, "name": "{{ Post Title }}" }
  ]
}
```

---

## Article / BlogPosting
Use `BlogPosting` for blog content, `Article` for general, `NewsArticle` for news. Same property set.

- **Required:** none are hard-fail for Google, but treat **`headline`, `image`, `datePublished`, `author`** as required — without them you get warnings and no rich result.
- **`headline`:** ≤ 110 characters (Google truncates longer).
- **`author`:** must be a `Person` or `Organization` object with a `name`; add `url` if there's an author page. Never a bare string.
- **`image`:** one or more high-res URLs (≥ 1200px wide ideal); use `ImageObject` or a URL array.
- **`datePublished` / `dateModified`:** ISO 8601 (`2026-06-29` or `2026-06-29T10:00:00+05:30`).
- **Recommended:** `dateModified`, `publisher` (→ Organization, must have a `logo`), `mainEntityOfPage`/`isPartOf`, `description`.
- **Allowed:** `articleSection`, `keywords`, `wordCount`, `inLanguage`, `articleBody`.

```json
{
  "@type": "BlogPosting",
  "@id": "https://www.goodera.com/blog/{{ Slug }}/#article",
  "isPartOf": { "@id": "https://www.goodera.com/blog/{{ Slug }}/#webpage" },
  "mainEntityOfPage": { "@id": "https://www.goodera.com/blog/{{ Slug }}/#webpage" },
  "headline": "{{ Post Title }}",
  "description": "{{ SEO Description }}",
  "image": ["{{ Main Image URL }}"],
  "datePublished": "{{ Published On (ISO 8601) }}",
  "dateModified": "{{ Updated On (ISO 8601) }}",
  "author": {
    "@type": "Person",
    "name": "{{ Author Name }}",
    "url": "{{ Author Profile URL }}"
  },
  "publisher": { "@id": "https://www.goodera.com/#organization" },
  "inLanguage": "en-US"
}
```

---

## Event
For volunteering sessions, webinars, summits.

- **Required:** `name`, `startDate` (ISO 8601), `location`.
  - `location` is a `Place` (with `address` `PostalAddress`) for in-person, or a `VirtualLocation` (with `url`) for online. For hybrid, provide an array of both.
- **Recommended:** `endDate`, `eventStatus` (`https://schema.org/EventScheduled` | `EventCancelled` | `EventPostponed` | `EventMovedOnline`), `eventAttendanceMode` (`OfflineEventAttendanceMode` | `OnlineEventAttendanceMode` | `MixedEventAttendanceMode`), `image`, `description`, `organizer` (→ Organization), `offers`.
- **`offers`:** if present, needs `price`, `priceCurrency`, `availability`, `url`. For free events use `"price": "0"`.
- **Allowed:** `performer`, `eventSchedule`, `maximumAttendeeCapacity`.

```json
{
  "@type": "Event",
  "@id": "https://www.goodera.com/events/{{ Slug }}/#event",
  "name": "{{ Event Name }}",
  "description": "{{ Event Description }}",
  "startDate": "{{ Start Date (ISO 8601) }}",
  "endDate": "{{ End Date (ISO 8601) }}",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode",
  "location": {
    "@type": "VirtualLocation",
    "url": "{{ Event URL }}"
  },
  "image": ["{{ Event Image URL }}"],
  "organizer": { "@id": "https://www.goodera.com/#organization" }
}
```

---

## FAQPage
Only for pages whose main purpose is a Q&A list. One `FAQPage` per page. Each answer's `text` may contain limited HTML; strip anything that isn't an answer.

- **Required:** `mainEntity` (array of `Question`); each `Question` needs `name` (the question) and `acceptedAnswer` (an `Answer` with `text`).
- **Allowed:** nothing else on the Question/Answer beyond `name` / `text`.
- **Caveat:** see google-supported-types.md — FAQ rich results now only render for gov/health sites. Tell the user.

```json
{
  "@type": "FAQPage",
  "@id": "https://www.goodera.com/faq/#faqpage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{{ Question 1 }}",
      "acceptedAnswer": { "@type": "Answer", "text": "{{ Answer 1 }}" }
    }
  ]
}
```

---

## Person / ProfilePage
For team / author profile pages.

- **Person required:** `name`. **Recommended:** `jobTitle`, `image`, `url`, `worksFor` (→ Organization), `sameAs` (social profiles).
- Wrap in a `ProfilePage` whose `mainEntity` → the Person.

```json
{
  "@type": "ProfilePage",
  "@id": "https://www.goodera.com/team/{{ Slug }}/#profilepage",
  "mainEntity": {
    "@type": "Person",
    "name": "{{ Full Name }}",
    "jobTitle": "{{ Job Title }}",
    "image": "{{ Headshot URL }}",
    "worksFor": { "@id": "https://www.goodera.com/#organization" },
    "sameAs": ["{{ LinkedIn URL }}"]
  }
}
```

---

## Product
Only when there's a real price, rating, or review — otherwise it warns and earns no rich result (see google-supported-types.md).

- **Required:** `name`, plus **at least one** of `review`, `aggregateRating`, or `offers`.
- **`offers`:** `price`, `priceCurrency`, `availability`, `url`.
- **`aggregateRating`:** `ratingValue`, `reviewCount` (or `ratingCount`).
- **Recommended:** `image`, `description`, `brand` (→ Organization).

```json
{
  "@type": "Product",
  "@id": "https://www.goodera.com/solutions/{{ Slug }}/#product",
  "name": "{{ Product Name }}",
  "image": ["{{ Image URL }}"],
  "description": "{{ Description }}",
  "brand": { "@id": "https://www.goodera.com/#organization" },
  "offers": {
    "@type": "Offer",
    "price": "{{ Price }}",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://www.goodera.com/solutions/{{ Slug }}"
  }
}
```

---

## Service + OfferCatalog
This is the high-value pattern for Goodera's offering / solution / "what we do" pages (e.g. the Help Center, solutions pages). It models *what Goodera provides* and *the menu of options* — capturing the real depth of the page instead of stopping at a bare WebPage.

**Important:** `Service` and `OfferCatalog` are **not** Google rich-result types — they won't draw a SERP visual. But they are valid schema.org, they consolidate Goodera's entity, and they feed Google's Knowledge Graph and AI Overviews / LLM answers, which increasingly drive discovery. Emit them whenever the page genuinely describes a service and its options. Every value must be backed by visible page content — don't invent service types, prices, or regions.

`Service`
- **Required:** `name`
- **Recommended:** `provider` (→ Organization `@id`, never a duplicated Organization), `serviceType`, `description`, `areaServed`, `hasOfferCatalog`
- **`areaServed`:** an array of `Country`/`Place` objects — only the regions explicitly stated on the page.
- **`hasOfferCatalog`:** an `OfferCatalog` listing the distinct options.

`OfferCatalog`
- **Required:** `name`, `itemListElement` (array of `Offer`)
- Each `Offer` wraps an `itemOffered` (a `Service` with `name` + `description`).

```json
{
  "@type": "Service",
  "@id": "https://www.goodera.com/help-center/#service",
  "name": "Goodera Corporate Volunteering Experiences",
  "serviceType": "Corporate volunteering programs",
  "description": "{{ short page summary }}",
  "provider": { "@id": "https://www.goodera.com/#organization" },
  "areaServed": [
    { "@type": "Country", "name": "United States" },
    { "@type": "Country", "name": "India" }
  ],
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Volunteering experience formats",
    "itemListElement": [
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "In-person volunteering",
          "description": "Hands-on impact at nonprofit locations, schools, shelters, or community sites."
        }
      }
    ]
  }
}
```

Wire the page's `WebPage.about` to this Service's `@id`, and the Service's `provider` back to the Organization `@id`. One canonical Organization, referenced everywhere.

---

## ItemList
Use for an ordered/unordered set the page presents as a list — e.g. a category index, a "use cases" grid, a directory of links. Not a rich result on its own (except the Carousel pattern for specific types), but valid and useful for structure.

- **Required:** `itemListElement` (array of `ListItem`); each `ListItem` needs `position` and either `name` or `item`.
- **Allowed:** `name`, `numberOfItems`, `itemListOrder`.

```json
{
  "@type": "ItemList",
  "@id": "https://www.goodera.com/help-center/#usecases",
  "name": "Volunteering use cases",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Volunteering with children & family" },
    { "@type": "ListItem", "position": 2, "name": "Team meetings & offsites" }
  ]
}
```

---

## CollectionPage
Use **instead of `WebPage`** when the page's main job is to present a *collection/list* of things — a glossary, a blog index, a directory, a resource hub. Same properties as WebPage, plus `mainEntity` pointing at the list/set the page is built around.

- **Required:** `@id`, `url`, `name`
- **Recommended:** `isPartOf` (→ WebSite), `about` (→ Organization), `mainEntity` (→ the ItemList / DefinedTermSet `@id`), `breadcrumb`, `description`
- Everything valid on WebPage is valid here.

---

## DefinedTermSet / DefinedTerm
The correct modeling for a **glossary / terminology page** — far better than a bare `ItemList` of names, because it captures that each entry is a *defined term with a definition*. Neither is a Google rich-result type (no SERP visual), but they're the right schema.org types and feed Knowledge Graph / AI answers, where glossaries get surfaced.

`DefinedTermSet` — the glossary as a whole.
- **Required:** `name`
- **Recommended:** `description`, `@id`. The member terms usually link *up* to the set via `inDefinedTermSet` (see below) rather than being inlined in a `hasDefinedTerm` array — this is what makes the per-item CMS pattern work.

`DefinedTerm` — one entry.
- **Required:** `name`, `inDefinedTermSet` (the set's `@id` URL, as a string or `{ "@id": … }`)
- **Recommended:** `description` (the definition — plain text, never rich-text HTML), `url` (if the term has its own page), `termCode`

```json
{
  "@type": "DefinedTermSet",
  "@id": "https://www.goodera.com/glossary/#definedtermset",
  "name": "Goodera Social Impact & CSR Glossary",
  "description": "Plain-language definitions for the CSR, ESG, sustainability, social impact, and AI terms used across Goodera."
}
```

```json
{
  "@type": "DefinedTerm",
  "name": "Carbon Neutrality",
  "description": "A state in which net carbon dioxide emissions are zero, achieved by balancing emissions with removal or offsetting.",
  "inDefinedTermSet": "https://www.goodera.com/glossary/#definedtermset"
}
```

**Static list vs. auto-updating CMS list:** if the page is a Webflow Collection List (one static page rendering many CMS items, like /glossary), don't hand-list the terms — they go stale. Use the per-item Embed pattern in webflow-cms-binding.md → "Collection List pages" so each published term renders its own server-side `DefinedTerm` automatically.

---

## The full graph
A blog post page assembles like this — note how `@id` references (not duplicated objects) wire the nodes together:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    { ...Organization (from assets/organization-schema.json)... },
    {
      "@type": "WebSite",
      "@id": "https://www.goodera.com/#website",
      "url": "https://www.goodera.com",
      "name": "Goodera",
      "publisher": { "@id": "https://www.goodera.com/#organization" }
    },
    {
      "@type": "WebPage",
      "@id": "https://www.goodera.com/blog/{{ Slug }}/#webpage",
      "url": "https://www.goodera.com/blog/{{ Slug }}",
      "name": "{{ Post Title }}",
      "isPartOf": { "@id": "https://www.goodera.com/#website" },
      "primaryImageOfPage": { "@type": "ImageObject", "url": "{{ Main Image URL }}" },
      "breadcrumb": { "@id": "https://www.goodera.com/blog/{{ Slug }}/#breadcrumb" }
    },
    { ...BreadcrumbList with @id .../#breadcrumb... },
    { ...BlogPosting with @id .../#article, publisher → #organization... },
    { ...VideoObject if a video is present (see video-schema.md)... }
  ]
}
</script>
```

Rules for the graph:
- Exactly one `"@context": "https://schema.org"` at the top level, then the `@graph` array. Individual nodes inside `@graph` do **not** repeat `@context`.
- Every `@id` is a unique absolute URL with a `#fragment`. Reference a node elsewhere with `{ "@id": "<that id>" }` — never paste the whole object twice.
- A node you reference by `@id` must actually exist in the graph.
