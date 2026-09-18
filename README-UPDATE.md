CUSTOMCARZ AUTOCARZ SITE REBUILD
================================

Replace these repository files:
- index.html
- admin.html
- site.json
- robots.txt
- sitemap.xml

Keep your existing:
- products.json
- assets/
- CNAME

IMPORTANT
1. The old index.html fetched live data from a different repository name. This rebuild reads products.json and site.json from the same repository.
2. site.json category data is cleaned into a real array; the corrupt single-string category list and broken category-image keys are removed.
3. The customer site displays all saved reviews instead of only the first review.
4. Admin sorting is drag-and-drop; displayOrder is rebuilt automatically.
5. Product/category/background/gallery image uploads are stored as relative paths under assets/.
6. Use a fine-grained GitHub token with Contents: Read and write permission for customcarzautocare/Autocare.

GOOGLE SEARCH CONSOLE
After deploying:
- Open URL Inspection for https://customcarzautocare.co.ke/
- Test Live URL
- Confirm robots.txt is no longer reported as blocking
- Request indexing after the live test succeeds
