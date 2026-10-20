
from pathlib import Path
from html import escape
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "src" / "pages"
DATA_DIR = ROOT / "src" / "data"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
OUTPUT_DIR = ROOT / "site"

SITE_URL = "https://jackylau85.github.io/JKL85.github.io"

PAGE_INFO = {
    "index.html": (
        "Jacky Liu | Vehicle Monitor, Vehicle Safety & SVM / AVM",
        "Jacky Liu's professional website covering vehicle displays, vehicle safety, SVM, AVM, cameras, wire and cable, and international logistics.",
    ),
    "about.html": (
        "About | Jacky Liu",
        "Learn about Jacky Liu's experience in international logistics, wire and cable products, and vehicle electronics.",
    ),
    "contact.html": (
        "Contact | Jacky Liu",
        "Contact Jacky Liu to discuss vehicle displays, vehicle safety applications, and potential business cooperation.",
    ),
    "cases.html": (
        "Case Studies | Jacky Liu",
        "Application cases involving vehicle displays, wire and cable, and vehicle safety systems.",
    ),
    "insights.html": (
        "Insights | Jacky Liu",
        "Practical insights on vehicle monitors, cameras, MDVR, SVM, AVM, wire and cable, and international logistics.",
    ),
    "solutions.html": (
        "Solutions | Jacky Liu",
        "Vehicle and industrial display solutions for commercial vehicles, machinery, marine applications, and safety systems.",
    ),
}

CATEGORY_INFO = {
    "case": {
        "heading": "Case Studies",
        "intro": "Explore application areas and practical challenges involving vehicle systems, industrial equipment, and wire and cable.",
    },
    "insights": {
        "heading": "Insights",
        "intro": "Practical articles about product selection, installation, troubleshooting, and real-world commercial vehicle applications.",
    },
    "solutions": {
        "heading": "Solutions",
        "intro": "Explore application-focused approaches for commercial vehicles, industrial machinery, marine displays, and connectivity.",
    },
}


def read_text(path):
    return path.read_text(encoding="utf-8")


def extract_content(source, fallback_title, fallback_description):
    title_match = re.search(
        r"<title[^>]*>(.*?)</title>", source, re.I | re.S
    )
    description_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        source,
        re.I | re.S,
    )

    title = (
        re.sub(r"\s+", " ", title_match.group(1)).strip()
        if title_match else fallback_title
    )
    description = (
        description_match.group(1).strip()
        if description_match else fallback_description
    )

    body_match = re.search(
        r"<body\b[^>]*>(.*?)</body\s*>", source, re.I | re.S
    )
    if body_match:
        content = body_match.group(1).strip()
    else:
        content = re.sub(
            r"<!doctype[^>]*>|</?html\b[^>]*>|</?head\b[^>]*>|"
            r"<meta\b[^>]*>|<title\b[^>]*>.*?</title>|"
            r"<link\b[^>]*>|<script\b[^>]*>.*?</script>",
            "",
            source,
            flags=re.I | re.S,
        ).strip()

    return title, description, content


def make_page(title, description, content, nav, footer, filename):
    canonical_url = f"{SITE_URL}/{filename}"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="robots" content="index,follow">
  <link rel="stylesheet" href="assets/css/site.css">
  <link rel="canonical" href="{escape(canonical_url, quote=True)}">
</head>
<body>
  {nav}
  <main id="main-content">
    {content}
  </main>
  {footer}
  <script src="assets/js/site.js" defer></script>
</body>
</html>
"""


def make_category_content(group_key, title, slug):
    group = CATEGORY_INFO[group_key]
    safe_title = escape(title)
    safe_heading = escape(group["heading"])
    safe_intro = escape(group["intro"])
    parent_page = {
        "case": "cases.html",
        "insights": "insights.html",
        "solutions": "solutions.html",
    }[group_key]

    return f"""
<section class="hero category-page">
  <p class="page-kicker">{safe_heading}</p>
  <h1>{safe_title}</h1>
  <p class="lead">{safe_intro}</p>
  <div class="content-card">
    <h2>About this category</h2>
    <p>This section is being developed with practical information and application-focused content. New material will be added as it becomes available.</p>
    <p><a href="{parent_page}">Back to {safe_heading}</a></p>
  </div>
</section>
"""


def main():
    if not PAGES_DIR.is_dir():
        raise FileNotFoundError(f"Missing pages directory: {PAGES_DIR}")

    categories_path = DATA_DIR / "categories.json"
    if not categories_path.is_file():
        raise FileNotFoundError(f"Missing categories file: {categories_path}")

    nav_path = TEMPLATES_DIR / "nav.html"
    footer_path = TEMPLATES_DIR / "footer.html"

    for required in (nav_path, footer_path):
        if not required.is_file():
            raise FileNotFoundError(f"Missing required template: {required}")

    for required in (
        ASSETS_DIR / "css" / "site.css",
        ASSETS_DIR / "js" / "site.js",
    ):
        if not required.is_file():
            raise FileNotFoundError(f"Missing required asset: {required}")

    categories = json.loads(read_text(categories_path))
    for group_key in CATEGORY_INFO:
        if group_key not in categories:
            raise ValueError(f"Missing category group: {group_key}")
        for item in categories[group_key]:
            if not item.get("title") or not item.get("slug"):
                raise ValueError(f"Invalid category item in group: {group_key}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    nav = read_text(nav_path)
    footer = read_text(footer_path)

    generated = []

    # Build the six main pages.
    for filename, (fallback_title, fallback_description) in PAGE_INFO.items():
        source_path = PAGES_DIR / filename
        if not source_path.is_file():
            raise FileNotFoundError(f"Missing page source: {source_path}")

        title, description, content = extract_content(
            read_text(source_path),
            fallback_title,
            fallback_description,
        )

        output_path = OUTPUT_DIR / filename
        output_path.write_text(
            make_page(title, description, content, nav, footer, filename),
            encoding="utf-8",
        )
        generated.append(filename)
        print(f"Built: {output_path.relative_to(ROOT)}")

    # Build all category pages from categories.json.
    for group_key, items in categories.items():
        if group_key not in CATEGORY_INFO:
            print(f"Skipping unknown category group: {group_key}")
            continue

        for item in items:
            title = item["title"].strip()
            slug = item["slug"].strip()

            if (
                not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug)
                or slug in PAGE_INFO
            ):
                raise ValueError(f"Invalid category slug: {slug}")

            filename = f"{slug}.html"
            description = (
                f"{title}: practical information and application-focused "
                f"content from Jacky Liu."
            )
            content = make_category_content(group_key, title, slug)

            output_path = OUTPUT_DIR / filename
            output_path.write_text(
                make_page(
                    title,
                    description,
                    content,
                    nav,
                    footer,
                    filename,
                ),
                encoding="utf-8",
            )
            generated.append(filename)
            print(f"Built: {output_path.relative_to(ROOT)}")

    # Copy shared assets.
    output_assets = OUTPUT_DIR / "assets"
    if output_assets.exists():
        shutil.rmtree(output_assets)
    shutil.copytree(ASSETS_DIR, output_assets)

    # Generate sitemap for all generated pages.
    sitemap_entries = "\n".join(
        f"  <url><loc>{SITE_URL}/{escape(filename)}</loc></url>"
        for filename in generated
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_entries}\n"
        "</urlset>\n"
    )
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    (OUTPUT_DIR / "robots.txt").write_text(robots, encoding="utf-8")

    print(f"\nBuild completed: {len(generated)} pages generated.")
    print(f"Output directory: {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
