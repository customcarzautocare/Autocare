# Customcarz Auto Care — rebuilt storefront

This rebuild keeps the existing `products.json`, `site.json`, product images and GitHub-backed admin workflow, but changes the public storefront to a static, crawlable architecture.

## Public architecture
- `/` — SEO-ready homepage
- `/shop/` — full catalogue
- `/categories/` — category hub
- `/category/<slug>/` — crawlable category pages
- `/products/<slug>-<id>/` — one URL per product with initial-HTML Product JSON-LD
- `/sitemap.xml` — generated from the real catalogue
- `/robots.txt` — public crawl allowed, admin excluded
- `/.well-known/security.txt` — security contact
- `/404.html` — custom 404

## Automatic publishing
`.github/workflows/pages.yml` rebuilds the public pages when `products.json` or `site.json` changes. This means the existing admin can continue editing those files without manually regenerating product pages.

## Security model
The public site contains no GitHub token and no server-side credentials. The admin uses a token entered by the administrator in the browser to call GitHub. Do not put tokens in `products.json`, HTML, JavaScript, or repository files.

HTTPS must be enabled in GitHub Pages Settings. GitHub Pages provisions the TLS certificate for a correctly configured custom domain.

## Catalogue
Generated from 85 current product records. Public category names are normalized for display; the original product fields remain in `products.json` for admin compatibility.

Generated URLs: 94.
