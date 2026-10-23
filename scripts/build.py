from pathlib import Path
from html import escape
import json
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "src" / "pages"
ARTICLES_DIR = ROOT / "src" / "articles"
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
        "intro": (
            "Explore application areas and practical challenges "
            "involving vehicle systems, industrial equipment, "
            "and wire and cable."
        ),
    },
    "insights": {
        "heading": "Insights",
        "intro": (
            "Practical articles about product selection, installation, "
            "troubleshooting, and real-world commercial vehicle applications."
        ),
    },
    "solutions": {
        "heading": "Solutions",
        "intro": (
            "Explore application-focused approaches for commercial "
            "vehicles, industrial machinery, marine displays, "
            "and connectivity."
        ),
    },
}


def read_text(path):
    return path.read_text(encoding="utf-8")


def extract_content(source, fallback_title, fallback_description):
    title_match = re.search(
        r"<title[^>]*>(.*?)</title>",
        source,
        re.I | re.S,
    )

    description_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        source,
        re.I | re.S,
    )

    title = (
        re.sub(r"\s+", " ", title_match.group(1)).strip()
        if title_match
        else fallback_title
    )

    description = (
        description_match.group(1).strip()
        if description_match
        else fallback_description
    )

    body_match = re.search(
        r"<body\b[^>]*>(.*?)</body\s*>",
        source,
        re.I | re.S,
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
    page_class = filename.removesuffix(".html")

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
    <main id="main-content" class="page-main page-main--{escape(page_class, quote=True)}">
        {content}
    </main>
    {footer}
    <script src="assets/js/site.js" defer></script>
</body>
</html>
"""


def make_category_content(group_key, title, articles):
    group = CATEGORY_INFO[group_key]

    safe_title = escape(title)
    safe_heading = escape(group["heading"])
    safe_intro = escape(group["intro"])

    parent_page = {
        "case": "cases.html",
        "insights": "insights.html",
        "solutions": "solutions.html",
    }[group_key]

    cards = []

    # Insights pages display a separate card for each article.
    if group_key == "insights":
        for item in articles:
            article_title = escape(item["title"])
            article_filename = escape(
                item["filename"],
                quote=True,
            )
            article_description = escape(
                item.get("description", "")
            )

            cards.append(
                f"""
                <article class="category-card">
                    <p class="category-card-label">
                        {safe_title.upper()}
                    </p>
                    <h3>{article_title}</h3>
                    <p class="category-card-description">
                        {article_description}
                    </p>
                    <a class="category-card-link"
                       href="{article_filename}">
                        Read Article
                        <span aria-hidden="true">→</span>
                    </a>
                </article>
                """
            )

    if cards:
        cards_html = "\n".join(cards)

        if title.strip().casefold() == "monitors":
            section_title = "Monitor Guides"
            section_intro = (
                "Practical answers to common vehicle monitor problems."
            )
        else:
            section_title = f"{safe_title} Articles"
            section_intro = (
                "Practical information, product knowledge, "
                "and real-world applications."
            )

    else:
        section_title = f"{safe_title} Overview"
        section_intro = (
            f"Explore practical information and application "
            f"considerations related to {safe_title}."
        )

        cards_html = f"""
            <article class="category-card">
                <p class="category-card-label">
                    {safe_heading.upper()}
                </p>
                <h3>{safe_title}</h3>
                <p class="category-card-description">
                    {safe_intro}
                </p>
                <p class="category-card-description">
                    More detailed content and application examples
                    will be added to this section.
                </p>
            </article>
        """

    return f"""
        <div class="category-layout category-layout--{group_key}">
            <section class="category-hero">
                <p class="page-kicker">
                    {safe_heading.upper()} / {safe_title.upper()}
                </p>

                <h1>{safe_title}</h1>

                <p class="category-hero-intro">
                    {safe_intro}
                </p>

                <p class="category-hero-meta">
                    PRODUCT KNOWLEDGE / APPLICATIONS / PRACTICAL INSIGHTS
                </p>
            </section>

            <section class="category-content-section">
                <div class="category-section-heading">
                    <p class="page-kicker">EXPLORE</p>
                    <h2>{section_title}</h2>
                    <p>{section_intro}</p>
                </div>

                <div class="category-card-grid">
                    {cards_html}
                </div>

                <p class="category-back-link">
                    <a href="{parent_page}">
                        ← Back to {safe_heading}
                    </a>
                </p>
            </section>
        </div>
    """


def get_article_metadata(source, path):
    title_match = re.search(
        r"<h1\b[^>]*>(.*?)</h1>",
        source,
        re.I | re.S,
    )

    category_match = re.search(
        r"<strong>\s*Category:\s*</strong>\s*([^<]+)",
        source,
        re.I,
    )

    lead_match = re.search(
        r'<p class=["\']lead["\'][^>]*>(.*?)</p>',
        source,
        re.I | re.S,
    )

    if not title_match:
        raise ValueError(
            f"Article has no h1 title: {path}"
        )

    if not category_match:
        raise ValueError(
            f"Article has no Category field: {path}"
        )

    title = re.sub(
        r"<[^>]+>",
        "",
        title_match.group(1),
    ).strip()

    category = category_match.group(1).strip()

    description = (
        re.sub(
            r"<[^>]+>",
            "",
            lead_match.group(1),
        ).strip()
        if lead_match
        else title
    )

    if not title or not category:
        raise ValueError(
            f"Article title or category is empty: {path}"
        )

    return title, category, description


def main():
    if not PAGES_DIR.is_dir():
        raise FileNotFoundError(
            f"Missing pages directory: {PAGES_DIR}"
        )

    categories_path = DATA_DIR / "categories.json"

    if not categories_path.is_file():
        raise FileNotFoundError(
            f"Missing categories file: {categories_path}"
        )

    nav_path = TEMPLATES_DIR / "nav.html"
    footer_path = TEMPLATES_DIR / "footer.html"

    for required in (nav_path, footer_path):
        if not required.is_file():
            raise FileNotFoundError(
                f"Missing required template: {required}"
            )

    for required in (
        ASSETS_DIR / "css" / "site.css",
        ASSETS_DIR / "js" / "site.js",
    ):
        if not required.is_file():
            raise FileNotFoundError(
                f"Missing required asset: {required}"
            )

    categories = json.loads(read_text(categories_path))

    for group_key in CATEGORY_INFO:
        if group_key not in categories:
            raise ValueError(
                f"Missing category group: {group_key}"
            )

        for item in categories[group_key]:
            if not item.get("title") or not item.get("slug"):
                raise ValueError(
                    f"Invalid category item in group: {group_key}"
                )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    nav = read_text(nav_path)
    footer = read_text(footer_path)

    generated = []
    category_pages = {}

    # Build the six main pages.
    for filename, (
        fallback_title,
        fallback_description,
    ) in PAGE_INFO.items():
        source_path = PAGES_DIR / filename

        if not source_path.is_file():
            raise FileNotFoundError(
                f"Missing page source: {source_path}"
            )

        title, description, content = extract_content(
            read_text(source_path),
            fallback_title,
            fallback_description,
        )

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

    # Prepare category page records.
    all_category_slugs = set()

    for group_key in CATEGORY_INFO:
        category_pages[group_key] = []

        for item in categories[group_key]:
            title = item["title"].strip()
            slug = item["slug"].strip()

            if not re.fullmatch(
                r"[a-z0-9]+(?:-[a-z0-9]+)*",
                slug,
            ):
                raise ValueError(
                    f"Invalid category slug: {slug}"
                )

            filename = f"{slug}.html"

            if (
                filename in PAGE_INFO
                or filename in all_category_slugs
            ):
                raise ValueError(
                    f"Duplicate page filename: {filename}"
                )

            all_category_slugs.add(filename)

            category_pages[group_key].append({
                "title": title,
                "slug": slug,
                "filename": filename,
            })

    # Read article sources and match each article to an Insights category.
    article_records = []
    article_filenames = set()

    if ARTICLES_DIR.is_dir():
        for source_path in sorted(ARTICLES_DIR.glob("*.html")):
            title, category, description = get_article_metadata(
                read_text(source_path),
                source_path,
            )

            filename = source_path.name

            if (
                filename in PAGE_INFO
                or filename in all_category_slugs
            ):
                raise ValueError(
                    "Article filename conflicts with another page: "
                    f"{filename}"
                )

            if filename in article_filenames:
                raise ValueError(
                    f"Duplicate article filename: {filename}"
                )

            matching_categories = [
                item
                for item in category_pages["insights"]
                if item["title"].casefold() == category.casefold()
            ]

            if not matching_categories:
                raise ValueError(
                    f"Article category '{category}' does not match "
                    "an Insights category in categories.json: "
                    f"{source_path.name}"
                )

            article_records.append({
                "filename": filename,
                "title": title,
                "category": category,
                "description": description,
                "source_path": source_path,
                "category_slug": matching_categories[0]["slug"],
            })

            article_filenames.add(filename)

    # Build category pages, including article lists.
    for group_key, items in categories.items():
        if group_key not in CATEGORY_INFO:
            continue

        for item in items:
            title = item["title"].strip()
            filename = f'{item["slug"].strip()}.html'

            matching_articles = [
                article
                for article in article_records
                if (
                    group_key == "insights"
                    and article["category_slug"] == item["slug"]
                )
            ]

            content = make_category_content(
                group_key,
                title,
                matching_articles,
            )

            description = (
                f"{title}: practical information and "
                "application-focused content from Jacky Liu."
            )

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

    # Build standalone article pages.
    for article in article_records:
        content = read_text(article["source_path"])
        output_path = OUTPUT_DIR / article["filename"]

        output_path.write_text(
            make_page(
                article["title"],
                article["description"],
                content,
                nav,
                footer,
                article["filename"],
            ),
            encoding="utf-8",
        )

        generated.append(article["filename"])
        print(
            f"Built article: {output_path.relative_to(ROOT)}"
        )

    # Copy shared static assets.
    output_assets = OUTPUT_DIR / "assets"

    if output_assets.exists():
        shutil.rmtree(output_assets)

    shutil.copytree(ASSETS_DIR, output_assets)

    # Generate sitemap for main pages, category pages, and articles.
    sitemap_entries = "\n".join(
        f"  <url><loc>{escape(SITE_URL)}/{escape(filename)}</loc></url>"
        for filename in generated
    )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_entries}\n"
        "</urlset>\n"
    )

    (OUTPUT_DIR / "sitemap.xml").write_text(
        sitemap,
        encoding="utf-8",
    )

    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )

    (OUTPUT_DIR / "robots.txt").write_text(
        robots,
        encoding="utf-8",
    )

    print(
        f"\nBuild completed: {len(generated)} pages generated."
    )
    print(f"Articles built: {len(article_records)}")
    print(
        f"Output directory: {OUTPUT_DIR.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
