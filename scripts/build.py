
from pathlib import Path
from html.parser import HTMLParser
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "src" / "pages"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"
OUTPUT_DIR = ROOT / "site"

SITE_URL = "https://jackylau85.github.io/JKL85.github.io"

PAGE_INFO = {
    "index.html": ("Jacky Liu | Vehicle Monitor, Vehicle Safety & SVM / AVM",
                   "Jacky Liu's professional website covering vehicle displays, vehicle safety, SVM, AVM, cameras, wire and cable, and international logistics."),
    "about.html": ("About | Jacky Liu",
                   "Learn about Jacky Liu's experience in international logistics, wire and cable products, and vehicle electronics."),
    "contact.html": ("Contact | Jacky Liu",
                     "Contact Jacky Liu to discuss vehicle displays, vehicle safety applications, and potential business cooperation."),
    "cases.html": ("Case Studies | Jacky Liu",
                   "Application cases involving vehicle displays, wire and cable, and vehicle safety systems."),
    "insights.html": ("Insights | Jacky Liu",
                      "Practical insights on vehicle monitors, cameras, MDVR, SVM, AVM, wire and cable, and international logistics."),
    "solutions.html": ("Solutions | Jacky Liu",
                       "Vehicle and industrial display solutions for commercial vehicles, machinery, marine applications, and safety systems."),
}


def read_text(path):
    return path.read_text(encoding="utf-8")


def extract_content(source, fallback_title, fallback_description):
    """Accept either a content fragment or a complete HTML document."""
    title_match = re.search(
        r"<title[^>]*>(.*?)</title>", source, re.I | re.S
    )
    description_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        source, re.I | re.S
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
            "", source, flags=re.I | re.S
        ).strip()

    return title, description, content


def make_page(title, description, content, nav, footer):
    # Escape metadata so special characters cannot break HTML attributes.
    from html import escape

    safe_title = escape(title, quote=False)
    safe_description = escape(description, quote=True)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title}</title>
  <meta name="description" content="{safe_description}">
  <meta name="robots" content="index,follow">
  <link rel="stylesheet" href="assets/css/site.css">
  <link rel="canonical" href="{SITE_URL}/">
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


def main():
    if not PAGES_DIR.is_dir():
        raise FileNotFoundError(f"Missing pages directory: {PAGES_DIR}")

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

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    nav = read_text(nav_path)
    footer = read_text(footer_path)

    generated = []
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
            make_page(title, description, content, nav, footer),
            encoding="utf-8",
        )
        generated.append(filename)
        print(f"Built: {output_path.relative_to(ROOT)}")

    # Copy shared static assets into the generated site.
    output_assets = OUTPUT_DIR / "assets"
    if output_assets.exists():
        shutil.rmtree(output_assets)
    shutil.copytree(ASSETS_DIR, output_assets)

    # Generate a basic sitemap for the six pages built above.
    sitemap_entries = "\n".join(
        f"  <url><loc>{SITE_URL}/{filename}</loc></url>"
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
