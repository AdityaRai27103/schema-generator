#!/usr/bin/env python3
"""
Deterministic validator for Goodera JSON-LD schema.

Mechanically checks the things the model would otherwise hand-walk: JSON
syntax, graph structure, @id reference integrity, required properties per
@type, ISO 8601 dates/durations, absolute URLs, headline length, and
required enum-URL values. Catches the exact errors/warnings the Google
Rich Results Test throws — but instantly and reliably.

Usage:
    python validate.py path/to/schema.json
    python validate.py path/to/page.html      # extracts the ld+json block
    cat schema.json | python validate.py -
    python validate.py schema.json --cms       # tolerate {{ Field }} placeholders

Exit code 0 = no ERRORS (warnings allowed). Non-zero = at least one ERROR.
Stdlib only, no dependencies.
"""
import argparse
import json
import re
import sys

# --- Required properties per @type (mirrors references/schema-types.md) ---
# "all": every listed prop must be present.
# "any_of": at least one of the listed props must be present.
REQUIRED = {
    "Organization": {"all": ["name", "url", "logo"]},
    "WebSite": {"all": ["url"]},
    "WebPage": {"all": ["url", "name"]},
    "BreadcrumbList": {"all": ["itemListElement"]},
    "Article": {"all": ["headline", "image", "datePublished", "author"]},
    "BlogPosting": {"all": ["headline", "image", "datePublished", "author"]},
    "NewsArticle": {"all": ["headline", "image", "datePublished", "author"]},
    "Event": {"all": ["name", "startDate", "location"]},
    "FAQPage": {"all": ["mainEntity"]},
    "Question": {"all": ["name", "acceptedAnswer"]},
    "Answer": {"all": ["text"]},
    "Person": {"all": ["name"]},
    "ProfilePage": {"all": ["mainEntity"]},
    "Product": {"all": ["name"], "any_of": ["offers", "review", "aggregateRating"]},
    "VideoObject": {
        "all": ["name", "description", "thumbnailUrl", "uploadDate"],
        "any_of": ["contentUrl", "embedUrl"],
    },
    "ImageObject": {"all": ["url"]},
    "ListItem": {"all": ["position"], "any_of": ["name", "item"]},
    "Service": {"all": ["name"]},
    "OfferCatalog": {"all": ["name", "itemListElement"]},
    "ItemList": {"all": ["itemListElement"]},
    # Offer is handled specially: a priced offer (Product/Event) needs price+priceCurrency,
    # but an Offer used as an OfferCatalog entry just wraps itemOffered and has no price.
}

DATE_PROPS = {"datePublished", "dateModified", "startDate", "endDate",
              "uploadDate", "expires", "lastReviewed"}
# Properties whose string values must be absolute URLs.
URL_PROPS = {"url", "contentUrl", "embedUrl", "item"}
# Properties that take URL value(s) but may be strings or arrays.
URL_LIST_PROPS = {"sameAs", "image", "thumbnailUrl"}
# Properties that must use a full schema.org enum URL.
ENUM_URL_PROPS = {"eventStatus", "eventAttendanceMode", "availability"}

ISO_DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}"
    r"(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})?)?$"
)
ISO_DURATION_RE = re.compile(r"^P(\d+Y)?(\d+M)?(\d+W)?(\d+D)?(T(\d+H)?(\d+M)?(\d+S)?)?$")

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def is_placeholder(v):
    return isinstance(v, str) and "{{" in v


def is_abs_url(v):
    return isinstance(v, str) and v.startswith(("https://", "http://"))


def extract_json(raw):
    """Pull JSON out of a <script type="application/ld+json"> block if present."""
    m = re.search(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        raw, re.DOTALL | re.IGNORECASE,
    )
    return m.group(1).strip() if m else raw.strip()


def iter_nodes(graph):
    """Yield every dict in the graph (recursively) so nested types get checked too."""
    def walk(obj):
        if isinstance(obj, dict):
            yield obj
            for v in obj.values():
                yield from walk(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from walk(v)
    for node in graph:
        yield from walk(node)


def check_required(node, allow_cms):
    types = node.get("@type")
    if not types:
        # A pure {"@id": ...} reference legitimately has no @type; everything else needs one.
        if set(node.keys()) - {"@id"}:
            err(f'Node missing "@type": {json.dumps(node)[:120]}')
        return
    for t in (types if isinstance(types, list) else [types]):
        spec = REQUIRED.get(t)
        if not spec:
            continue
        for prop in spec.get("all", []):
            if prop not in node:
                err(f'{t} is missing required property "{prop}".')
        if "any_of" in spec and not any(p in node for p in spec["any_of"]):
            err(f'{t} needs at least one of: {", ".join(spec["any_of"])}.')


def check_values(node, allow_cms):
    for prop in DATE_PROPS:
        v = node.get(prop)
        if isinstance(v, str) and not (allow_cms and is_placeholder(v)):
            if not ISO_DATE_RE.match(v):
                err(f'"{prop}" is not ISO 8601: "{v}" (use YYYY-MM-DD or full ISO datetime).')
    if "duration" in node:
        v = node["duration"]
        if isinstance(v, str) and not (allow_cms and is_placeholder(v)):
            if not ISO_DURATION_RE.match(v):
                err(f'"duration" is not an ISO 8601 duration: "{v}" (e.g. PT2M30S).')
    for prop in URL_PROPS:
        v = node.get(prop)
        if isinstance(v, str) and not (allow_cms and is_placeholder(v)):
            if not is_abs_url(v):
                err(f'"{prop}" must be an absolute URL: "{v}".')
    for prop in URL_LIST_PROPS:
        if prop not in node:
            continue
        vals = node[prop] if isinstance(node[prop], list) else [node[prop]]
        for v in vals:
            if isinstance(v, str) and not (allow_cms and is_placeholder(v)):
                if not is_abs_url(v):
                    err(f'"{prop}" must be (an) absolute URL(s): "{v}".')
    for prop in ENUM_URL_PROPS:
        v = node.get(prop)
        if isinstance(v, str) and not (allow_cms and is_placeholder(v)):
            if not v.startswith("https://schema.org/"):
                err(f'"{prop}" must be a full schema.org enum URL: "{v}".')
    if "headline" in node and isinstance(node["headline"], str):
        if not is_placeholder(node["headline"]) and len(node["headline"]) > 110:
            warn(f'"headline" is {len(node["headline"])} chars; Google truncates over 110.')


def check_breadcrumb(node):
    items = node.get("itemListElement")
    if not isinstance(items, list):
        err("BreadcrumbList.itemListElement must be an array.")
        return
    positions = []
    for i, li in enumerate(items):
        if not isinstance(li, dict):
            continue
        positions.append(li.get("position"))
        last = i == len(items) - 1
        if not last and "item" not in li:
            err(f'BreadcrumbList ListItem position {li.get("position")} needs an "item" URL '
                f"(only the last item may omit it).")
    if positions and positions != list(range(1, len(positions) + 1)):
        err(f"BreadcrumbList positions must be sequential from 1; got {positions}.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="JSON/HTML file, or - for stdin")
    ap.add_argument("--cms", action="store_true",
                    help="tolerate {{ Field }} placeholders (CMS template mode)")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    text = extract_json(raw)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERROR  Invalid JSON: {e}")
        print("\n1 error, 0 warnings. NOT VALID.")
        sys.exit(1)

    # --- structure ---
    if data.get("@context") not in ("https://schema.org", "http://schema.org"):
        err('Top level must have "@context": "https://schema.org".')
    graph = data.get("@graph")
    if not isinstance(graph, list):
        err('Top level must contain a "@graph" array.')
        graph = []

    defined_ids = set()
    for node in graph:
        if isinstance(node, dict) and "@context" in node:
            warn(f'Node {node.get("@id", node.get("@type"))} repeats "@context"; '
                 f"only the top level should have it.")
        if isinstance(node, dict) and "@type" in node and "@id" in node:
            if node["@id"] in defined_ids:
                err(f'Duplicate @id defined: "{node["@id"]}".')
            defined_ids.add(node["@id"])
            if not (is_abs_url(node["@id"]) and "#" in node["@id"]):
                warn(f'@id "{node["@id"]}" should be an absolute URL with a #fragment.')

    # --- per-node checks ---
    for node in iter_nodes(graph):
        check_required(node, args.cms)
        check_values(node, args.cms)
        t = node.get("@type")
        if t == "BreadcrumbList":
            check_breadcrumb(node)
        if t == "Offer":
            # A priced offer needs both price and priceCurrency together; a catalog
            # Offer (just wrapping itemOffered) needs neither.
            has_price, has_cur = "price" in node, "priceCurrency" in node
            if has_price != has_cur:
                missing = "priceCurrency" if has_price else "price"
                err(f'Offer has one of price/priceCurrency but not the other (missing "{missing}").')
            if not has_price and "itemOffered" not in node:
                err('Offer must have either a price (with priceCurrency) or an itemOffered.')
        # @id reference integrity: a pure {"@id": x} reference must resolve.
        if set(node.keys()) == {"@id"}:
            if node["@id"] not in defined_ids:
                err(f'Reference to undefined @id "{node["@id"]}" '
                    f"(no node in the graph defines it).")

    # --- leftover placeholders on a non-CMS run ---
    if not args.cms and "{{" in text:
        err("Output still contains {{ placeholders }} — fill literal values, "
            "or run with --cms if this is a Collection template.")

    # --- report ---
    for w in warnings:
        print(f"WARN   {w}")
    for e in errors:
        print(f"ERROR  {e}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s). "
          f"{'VALID.' if not errors else 'NOT VALID.'}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
