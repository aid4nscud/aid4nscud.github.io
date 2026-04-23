# WorldSchool static site

Independent static rebuild of the WorldSchool marketing site for GitHub Pages.

## Structure

- `site_src/site_data.py` — shared page content and asset sources
- `site_src/styles.css` — site styles
- `site_src/app.js` — small client-side interactions
- `scripts/build_site.py` — downloads selected public assets and regenerates the published pages

## Rebuild

Run:

`python3 scripts/build_site.py`
