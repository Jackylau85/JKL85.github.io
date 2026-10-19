# JKL85 Website Skeleton

This package adds the initial source structure for the new Jacky Liu website.
It does not replace the current root `index.html`, change GitHub Pages settings,
or add a publishing workflow.

## Folder responsibilities

- `src/pages/`: editable page content fragments (not complete published pages).
- `src/data/categories.json`: one source of truth for the CASE, INSIGHTS and SOLUTIONS menus.
- `templates/nav.html`: shared navigation source.
- `templates/footer.html`: shared footer source.
- `assets/css/site.css`: shared styles.
- `assets/js/site.js`: shared navigation interactions.

## Important

Do not edit files in a generated `site/` folder. The build process will be added
in the next stage. The existing published homepage remains untouched during this
stage. Contact details are intentionally not included.
