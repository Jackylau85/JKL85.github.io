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
