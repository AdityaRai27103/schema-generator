# VideoObject — getting pages into Google video indexing

Run the video pass on **every** page (SKILL.md Phase 4). If a real video exists, add a `VideoObject` node to the `@graph`. This is what makes the page eligible for the video thumbnail in Search and populates the **Videos** report in Google Search Console. Without it, Google may not index the video at all.

## How to detect video on the page

Look in the fetched HTML for any of:
- A YouTube embed: `<iframe src="https://www.youtube.com/embed/VIDEO_ID">` → `embedUrl` is the iframe src; the watch URL `https://www.youtube.com/watch?v=VIDEO_ID` is a good `contentUrl`. Thumbnail: `https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg`.
- A Vimeo embed: `<iframe src="https://player.vimeo.com/video/VIDEO_ID">` → that src is `embedUrl`.
- A Webflow **Video** element (renders as a `.w-embed-youtube`/iframe) or **Background video** (`.w-background-video` with a `<video>` and `<source>` tags) → use the `<source>` URL as `contentUrl`.
- A native `<video>` / `<source src>` → `contentUrl`.

If you find none, **do not** emit a VideoObject. A VideoObject with no real video is an error.

## Properties

- **Required (Google will error without these):** `name`, `description`, `thumbnailUrl`, `uploadDate`.
  - `thumbnailUrl`: one or more URLs; image ≥ 60×30px, ideally 1280×720. For YouTube use the `i.ytimg.com/vi/.../maxresdefault.jpg` pattern.
  - `uploadDate`: ISO 8601 with a timezone if known (`2026-06-29T08:00:00+00:00`).
- **Strongly recommended (needed for indexing):** **`contentUrl` and/or `embedUrl`** — Google needs at least one to actually index the video. `contentUrl` = the raw media file or watch URL; `embedUrl` = the player URL. Provide both when available.
- **Recommended:** `duration` (ISO 8601 duration, e.g. `PT2M30S` = 2m30s), `publisher` (→ Organization `@id`).
- **Allowed:** `expires`, `hasPart` (`Clip`), `interactionStatistic` (view count), `regionsAllowed`.
- **Do not emit** properties outside this list.

## Worked example (YouTube embed found on the page)

```json
{
  "@type": "VideoObject",
  "@id": "https://www.goodera.com/blog/{{ Slug }}/#video",
  "name": "{{ Video Title }}",
  "description": "{{ Video Description }}",
  "thumbnailUrl": ["https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg"],
  "uploadDate": "{{ Upload Date (ISO 8601) }}",
  "duration": "PT2M30S",
  "contentUrl": "https://www.youtube.com/watch?v=VIDEO_ID",
  "embedUrl": "https://www.youtube.com/embed/VIDEO_ID",
  "publisher": { "@id": "https://www.goodera.com/#organization" }
}
```

## CMS note

On a CMS Collection template, a video is usually stored as a Video field or an embed/URL field. Map `{{ Video Title }}`, `{{ Video Description }}`, `{{ Upload Date }}` to CMS fields. The VIDEO_ID-derived URLs often can't be auto-built from a Webflow Video field — if the template only has a generic video field, tell the user they may need a plain-text field holding the watch/embed URL so the schema can reference it. Don't fabricate a VIDEO_ID.
