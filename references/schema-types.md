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
9. [The full graph: how nodes wire together](#the-full-graph)

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
