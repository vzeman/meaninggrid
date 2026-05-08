# Site Audit Fixture

This fixture is a tiny static website for MeaningGrid v0 crawler and analysis
tests.

Expected signals:

- `pricing.html` and `duplicate-pricing.html` should be near duplicates.
- `weird-recipes.html` should be a semantic outlier.
- `missing-meta.html` is missing title and meta description.
- `index.html` links to `/missing-page.html`, which should become a broken link.

Serve locally with:

```bash
python -m http.server 8088 --directory examples/site-audit/fixture-site
```

Then crawl:

```text
http://localhost:8088/index.html
```
