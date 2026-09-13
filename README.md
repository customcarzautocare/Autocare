# Customcarz Auto Care — v9

Production package for Customcarz Auto Care, Nairobi CBD.

## v9 admin improvements
- Loads the current `products.json` from GitHub so existing products can be edited.
- Product search makes existing products easy to find and edit.
- Every product field is editable: name, prices, stock, category, subcategory, make, model, year, fitment, warranty, description, image path and collection flags.
- Product photo uploads are resized in the browser, uploaded to `assets/products/`, verified on GitHub, then the product JSON is updated.
- Gallery, category and background uploads use the same safer image-upload process.
- Full classic Website Content editor for headings, subtitles and button labels.
- Service editor now includes every service title and description.
- Why Customcarz editor now includes every benefit title and description.
- Additional visible website labels can also be edited.
- Business information, social links, appearance, categories, makes, gallery, reviews and media remain editable.
- Customer site continues to load live `site.json` and `products.json` with cache-busting.

## GitHub Pages
Deploy the entire repository to the `main` branch/root (or keep the existing GitHub Actions Pages deployment). Do not upload only `index.html` or `admin.html`; the JSON files and `assets/` directory are required.

## Admin connection
Open `admin.html`, enter the repository and a GitHub fine-grained token with repository Contents read/write access, then press **CONNECT & LOAD**.
