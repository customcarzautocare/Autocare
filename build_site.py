import json, re, html, shutil, os, zipfile
from pathlib import Path
from urllib.parse import quote

SRC = Path('.')
BUILD = Path('.site-build')
if BUILD.exists(): shutil.rmtree(BUILD)
shutil.copytree(SRC, BUILD, ignore=shutil.ignore_patterns('.git','.github','.site-build'))
OUT = BUILD

products = json.loads((SRC/'products.json').read_text(encoding='utf-8'))
site = json.loads((SRC/'site.json').read_text(encoding='utf-8'))
BASE='https://customcarzautocare.co.ke'

# Normalize/repair catalogue categories for the public site without changing the admin data schema.
def canonical_category(cat='', sub=''):
    t=(str(cat)+' '+str(sub)).lower().strip()
    if any(k in t for k in ['lighting','headlight','taillight','lens']): return 'Lighting Parts'
    if any(k in t for k in ['body part','bumper','grille','fender','mirror']): return 'Body Parts'
    if any(k in t for k in ['interior','seat cover','car mat','dashboard','steering','headrest','gear knob']): return 'Interior Accessories'
    if any(k in t for k in ['exterior','wind deflect','wheel','rim','car cover','logo']): return 'Exterior Accessories'
    if any(k in t for k in ['decor','custom','wrap','ppf','tint','styling','sticker','ambient']): return 'Decor & Customization'
    if any(k in t for k in ['electronic','infotainment','android','radio']): return 'Electronics & Infotainment'
    if any(k in t for k in ['security','safety','alarm']): return 'Safety & Security'
    if any(k in t for k in ['spare','spares']): return 'Spare Parts'
    return 'Other Accessories'

def clean(s): return re.sub(r'\s+', ' ', str(s or '')).strip()
def slugify(s):
    s=clean(s).lower()
    s=re.sub(r'[^a-z0-9]+','-',s).strip('-')
    return s[:90] or 'product'
def esc(s): return html.escape(str(s or ''), quote=True)
def text(s): return clean(re.sub(r'[#*_`]+','',str(s or '')))
def money(v):
    try: return f"KES {float(v):,.0f}"
    except: return 'Price on request'
def url_product(p): return f"{BASE}/products/{slugify(p['name'])}-{p['id']}/"
def img_abs(path):
    if not path: return f"{BASE}/assets/background-customcarz-1789665386441.jpg"
    return BASE+'/'+path.lstrip('/')

def card(p, base=''):
    url=url_product(p)
    rel='../../' if base in ('product','category') else '../' if base=='shop' else ''
    image=p.get('image','').lstrip('/')
    img=(rel+image) if rel else image
    cat=canonical_category(p.get('category',''),p.get('subcat',''))
    stock=int(p.get('stock') or 0)
    badge='In stock' if stock>0 else 'Out of stock'
    old=p.get('oldPrice')
    oldhtml=f'<span class="old">{money(old)}</span>' if old and float(old)>float(p.get('price') or 0) else ''
    return f'''<article class="product-card" data-category="{esc(cat)}" data-name="{esc(clean(p.get('name')))}" data-make="{esc(clean(p.get('make')))}" data-model="{esc(clean(p.get('model')))}">
      <a class="product-media" href="{url}"><img loading="lazy" src="{esc(img)}" alt="{esc(clean(p.get('name')))}" width="640" height="480"></a>
      <div class="product-body"><div class="eyebrow">{esc(cat)} · {esc(clean(p.get('subcat')))}</div>
      <h3><a href="{url}">{esc(clean(p.get('name')))}</a></h3>
      <div class="price">{money(p.get('price'))} {oldhtml}</div>
      <div class="stock {('out' if stock<=0 else '')}">{badge}</div>
      <a class="btn small" href="{url}">View product</a></div>
    </article>'''

# Common CSS/JS
css = r'''
:root{--bg:#07090d;--panel:#10141b;--panel2:#151b24;--text:#f7f8fa;--muted:#aab3c2;--line:#252d39;--accent:#ffd21a;--accent2:#ff9d00;--ok:#58d68d;--danger:#ff6b6b;--max:1240px;--radius:18px;--shadow:0 14px 45px rgba(0,0,0,.25)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:linear-gradient(180deg,#06080c,#0b0f15 45%,#080b10);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}a{color:inherit;text-decoration:none}img{max-width:100%;display:block}button,input,select{font:inherit}.wrap{width:min(var(--max),calc(100% - 32px));margin:auto}.topbar{background:#05070a;border-bottom:1px solid var(--line);font-size:13px;color:var(--muted)}.topbar .wrap{display:flex;justify-content:space-between;gap:12px;padding:8px 0}.header{position:sticky;top:0;z-index:50;background:rgba(7,9,13,.92);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}.nav{min-height:72px;display:flex;align-items:center;gap:20px}.brand{display:flex;align-items:center;gap:10px;font-weight:900;font-size:21px;white-space:nowrap}.logo{width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#111;display:grid;place-items:center;font-weight:1000}.navlinks{display:flex;gap:18px;align-items:center;margin-left:auto}.navlinks a{color:#dce2eb;font-weight:700;font-size:14px}.navlinks a:hover{color:var(--accent)}.menu{display:none;background:none;border:1px solid var(--line);color:#fff;border-radius:10px;padding:8px}.hero{min-height:560px;display:grid;place-items:center;background:linear-gradient(90deg,rgba(3,5,8,.93),rgba(3,5,8,.62),rgba(3,5,8,.86)),url('../assets/background-customcarz-1789665386441.jpg') center/cover fixed}.hero-inner{padding:82px 0;max-width:820px}.kicker{color:var(--accent);font-weight:900;text-transform:uppercase;letter-spacing:.13em;font-size:12px}.hero h1{font-size:clamp(38px,7vw,76px);line-height:1.02;margin:14px 0}.hero p{font-size:18px;color:#d0d6df;max-width:760px}.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:12px 17px;border-radius:12px;border:1px solid var(--accent);background:var(--accent);color:#111;font-weight:900;cursor:pointer}.btn:hover{filter:brightness(1.05);transform:translateY(-1px)}.btn.secondary{background:transparent;color:#fff;border-color:var(--line)}.btn.whatsapp{background:#25d366;border-color:#25d366;color:#07130a}.btn.small{padding:9px 12px;font-size:13px}.section{padding:68px 0}.section.alt{background:#090d13}.section-head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin-bottom:25px}.section-head h2{font-size:clamp(27px,4vw,42px);margin:0}.section-head p{color:var(--muted);margin:7px 0 0;max-width:760px}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.product-card{background:linear-gradient(180deg,#121821,#0e131a);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column;min-width:0}.product-media{aspect-ratio:4/3;background:#080b10;overflow:hidden}.product-media img{width:100%;height:100%;object-fit:cover;transition:.35s}.product-card:hover .product-media img{transform:scale(1.04)}.product-body{padding:16px}.eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.product-body h3{font-size:17px;line-height:1.25;margin:7px 0 10px}.price{font-size:18px;font-weight:950;color:var(--accent)}.old{text-decoration:line-through;color:#77808e;font-size:13px;font-weight:600;margin-left:6px}.stock{font-size:12px;color:var(--ok);margin:8px 0 13px}.stock.out{color:var(--danger)}.category-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.category{min-height:180px;border:1px solid var(--line);border-radius:18px;overflow:hidden;position:relative;background:#111}.category img{width:100%;height:100%;object-fit:cover;position:absolute;inset:0;opacity:.62}.category:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent,rgba(0,0,0,.9))}.category .cat-content{position:relative;z-index:1;min-height:180px;padding:20px;display:flex;flex-direction:column;justify-content:end}.category h3{margin:0;font-size:20px}.category p{margin:5px 0 0;color:#c5ccd7;font-size:13px}.services,.reviews,.why{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.info-card{padding:22px;border:1px solid var(--line);border-radius:18px;background:var(--panel)}.info-card h3{margin:0 0 8px}.info-card p{margin:0;color:var(--muted)}.contact{display:grid;grid-template-columns:1.1fr .9fr;gap:22px}.contact-card{border:1px solid var(--line);background:var(--panel);border-radius:20px;padding:28px}.contact-list{display:grid;gap:12px}.contact-item{padding:13px 15px;border:1px solid var(--line);border-radius:12px;background:#0c1118}.footer{border-top:1px solid var(--line);padding:38px 0;color:var(--muted)}.footer-grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:30px}.footer h3{color:#fff}.muted{color:var(--muted)}.notice{padding:12px 15px;border:1px solid #3b3320;background:#17140a;border-radius:12px;color:#e8d99d}.crumbs{padding:25px 0 5px;color:var(--muted);font-size:13px}.detail{display:grid;grid-template-columns:1fr 1fr;gap:34px;padding:25px 0 70px}.detail-media{background:#0c1016;border:1px solid var(--line);border-radius:22px;overflow:hidden}.detail-media img{width:100%;aspect-ratio:1/1;object-fit:contain}.detail h1{font-size:clamp(32px,5vw,54px);line-height:1.05;margin:8px 0 15px}.detail-price{font-size:30px;font-weight:950;color:var(--accent)}.specs{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:22px 0}.spec{padding:13px;border:1px solid var(--line);border-radius:12px;background:#0d1219}.spec b{display:block;font-size:11px;text-transform:uppercase;color:var(--muted);letter-spacing:.06em}.desc{white-space:pre-line;color:#d3d8e0}.shop-tools{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:22px}.shop-tools input,.shop-tools select{background:#0d1219;color:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 13px;min-width:200px}.hidden{display:none!important}.floating{position:fixed;right:18px;bottom:18px;z-index:40;display:grid;gap:10px}.float-btn{width:50px;height:50px;border-radius:50%;display:grid;place-items:center;font-weight:1000;box-shadow:var(--shadow);border:1px solid var(--line);background:#111821}.float-btn.wa{background:#25d366;color:#07130a}.float-btn.call{background:var(--accent);color:#111}.pagination-note{margin-top:20px;color:var(--muted);font-size:13px}.notfound{text-align:center;padding:100px 0}.mobile-menu{display:none}
@media(max-width:980px){.grid{grid-template-columns:repeat(3,1fr)}.category-grid{grid-template-columns:repeat(2,1fr)}.services,.reviews,.why{grid-template-columns:1fr 1fr}.contact,.detail{grid-template-columns:1fr}.navlinks{display:none}.menu{display:block;margin-left:auto}.mobile-menu.open{display:grid;gap:10px;padding:14px 0 18px;border-top:1px solid var(--line)}.mobile-menu a{padding:8px 0}.footer-grid{grid-template-columns:1fr 1fr}}
@media(max-width:640px){.wrap{width:min(var(--max),calc(100% - 22px))}.topbar .wrap{display:block}.topbar .wrap span:last-child{display:none}.hero{min-height:520px}.hero-inner{padding:70px 0}.grid{grid-template-columns:repeat(2,1fr);gap:11px}.product-body{padding:12px}.product-body h3{font-size:15px}.price{font-size:15px}.category-grid,.services,.reviews,.why,.footer-grid{grid-template-columns:1fr}.section{padding:50px 0}.section-head{display:block}.contact{grid-template-columns:1fr}.specs{grid-template-columns:1fr 1fr}.detail{gap:18px}.nav{min-height:64px}.brand{font-size:18px}}
'''
js = r'''
document.addEventListener('DOMContentLoaded',()=>{
 const menu=document.querySelector('[data-menu]'), mobile=document.querySelector('.mobile-menu');
 if(menu&&mobile) menu.addEventListener('click',()=>mobile.classList.toggle('open'));
 const input=document.querySelector('[data-search]'), select=document.querySelector('[data-filter]'), cards=[...document.querySelectorAll('.product-card')], count=document.querySelector('[data-count]');
 function filter(){if(!cards.length)return;const q=(input?.value||'').toLowerCase().trim(), c=select?.value||'';let n=0;cards.forEach(x=>{const ok=(!q||x.dataset.name.toLowerCase().includes(q)||x.dataset.make.toLowerCase().includes(q)||x.dataset.model.toLowerCase().includes(q))&&(!c||x.dataset.category===c);x.classList.toggle('hidden',!ok);if(ok)n++});if(count)count.textContent=n+' products shown'}
 input?.addEventListener('input',filter);select?.addEventListener('change',filter);filter();
});
'''
(OUT/'assets/site.css').write_text(css,encoding='utf-8')
(OUT/'assets/site.js').write_text(js,encoding='utf-8')

# Root index is static and self-contained for SEO.
hero=site.get('websiteSections',{}).get('hero',{})
feat=site.get('websiteSections',{}).get('featured',{})
services_text=site.get('services',[])
reviews=site.get('reviews',[])
why=site.get('whyItems',[])
links=site.get('links',{})
cat_images=site.get('categoryImages',{}) or {}
canon_cats=['Interior Accessories','Exterior Accessories','Lighting Parts','Body Parts','Decor & Customization','Electronics & Infotainment','Safety & Security','Spare Parts']
cat_counts={c:sum(canonical_category(p.get('category',''),p.get('subcat',''))==c for p in products) for c in canon_cats}
# pick existing image by filename keyword
cat_img={
'Interior Accessories': next((v for k,v in cat_images.items() if 'interior' in k.lower()), 'assets/category/interior-accessories-1789314838592.jpg'),
'Exterior Accessories': next((v for k,v in cat_images.items() if 'exterior' in k.lower()), 'assets/category/exterior-accessories-1789314898931.jpg'),
'Lighting Parts': next((v for k,v in cat_images.items() if 'lighting' in k.lower()), 'assets/category/lighting-parts-1789314933919.jpg'),
'Body Parts': next((v for k,v in cat_images.items() if 'body' in k.lower()), 'assets/category/body-parts-1789665423155.jpg'),
'Decor & Customization': next((v for k,v in cat_images.items() if 'decor' in k.lower()), 'assets/category/decor-customization-1789409959023.jpg'),
'Electronics & Infotainment': next((v for k,v in cat_images.items() if 'electronics' in k.lower()), 'assets/category/electronics-infotainment-1789410003479.jpg'),
'Safety & Security': next((v for k,v in cat_images.items() if 'safety' in k.lower()), 'assets/category/safety-emergency-1789410210062.jpg'),
'Spare Parts': 'assets/category/body-parts-1789665423155.jpg'}

def head(title,desc,canonical,extra=''):
    return f'''<!doctype html><html lang="en-KE"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc[:160])}"><link rel="canonical" href="{esc(canonical)}"><meta name="robots" content="index,follow,max-image-preview:large"><meta name="referrer" content="strict-origin-when-cross-origin"><meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc[:200])}"><meta property="og:url" content="{esc(canonical)}"><link rel="stylesheet" href="/assets/site.css">{extra}</head>'''

def nav(prefix=''):
    return f'''<div class="topbar"><div class="wrap"><span>{esc(site.get('location',''))}</span><span>{esc(site.get('hours',''))} · <a href="{esc(links.get('phone','tel:+254757555691'))}">{esc(site.get('phone','0757555691'))}</a></span></div></div><header class="header"><div class="wrap"><nav class="nav"><a class="brand" href="/"><span class="logo">CC</span>{esc(site.get('bizName','Customcarz Auto Care'))}</a><div class="navlinks"><a href="/shop/">Shop</a><a href="/categories/">Categories</a><a href="/#services">Services</a><a href="/#reviews">Reviews</a><a href="/#contact">Contact</a></div><button class="menu" data-menu aria-label="Open menu">☰</button></nav><div class="mobile-menu"><a href="/shop/">Shop</a><a href="/categories/">Categories</a><a href="/#services">Services</a><a href="/#reviews">Reviews</a><a href="/#contact">Contact</a></div></div></header>'''

def foot():
    return f'''<footer class="footer"><div class="wrap footer-grid"><div><h3>{esc(site.get('bizName','Customcarz Auto Care'))}</h3><p>{esc(site.get('description',''))}</p></div><div><h3>Shop</h3><p><a href="/shop/">All products</a><br><a href="/categories/">Shop by category</a></p></div><div><h3>Contact</h3><p><a href="{esc(links.get('phone','tel:+254757555691'))}">{esc(site.get('phone',''))}</a><br>{esc(site.get('location',''))}<br><a href="{esc(links.get('whatsapp','https://wa.me/254757555691'))}">WhatsApp</a></p></div></div><div class="wrap" style="margin-top:25px;border-top:1px solid var(--line);padding-top:18px">© 2026 {esc(site.get('bizName','Customcarz Auto Care'))}. All rights reserved.</div></footer><div class="floating"><a class="float-btn wa" href="{esc(links.get('whatsapp','https://wa.me/254757555691'))}" aria-label="WhatsApp">WA</a><a class="float-btn call" href="{esc(links.get('phone','tel:+254757555691'))}" aria-label="Call">☎</a></div><script src="/assets/site.js" defer></script></body></html>'''

localbusiness={"@context":"https://schema.org","@type":"AutoPartsStore","name":site.get('bizName'),'url':BASE+'/','telephone':site.get('phone'),'email':site.get('email'),'description':site.get('description'),'address":{"@type":"PostalAddress","streetAddress":"Shell, Kirinyaga Road","addressLocality":"Nairobi","addressCountry":"KE"},"openingHours":"Mo-Su 07:00-17:30","sameAs':[v for k,v in links.items() if isinstance(v,str) and v.startswith('http') and k not in ['maps','jiji']]}
extra=f'<script type="application/ld+json">{json.dumps(localbusiness,ensure_ascii=False,separators=(",",":"))}</script>'
body=f'''<body>{nav()}<main><section class="hero"><div class="wrap hero-inner"><div class="kicker">Nairobi · Kenya</div><h1>{esc(hero.get('title','Upgrade Your Drive. Define Your Car.'))}</h1><p>{esc(hero.get('subtitle',site.get('tagline','')))}</p><div class="actions"><a class="btn" href="/shop/">Browse products</a><a class="btn whatsapp" href="{esc(links.get('whatsapp','https://wa.me/254757555691'))}">WhatsApp us</a><a class="btn secondary" href="{esc(links.get('maps','#contact'))}">Find us</a></div></div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><h2>Shop by category</h2><p>Browse the catalogue by the type of accessory or service you need.</p></div><a class="btn secondary small" href="/categories/">All categories</a></div><div class="category-grid">'''
for c in canon_cats:
    if not cat_counts[c]: continue
    body+=f'<a class="category" href="/category/{slugify(c)}/"><img loading="lazy" src="/{esc(cat_img[c])}" alt="{esc(c)}"><div class="cat-content"><h3>{esc(c)}</h3><p>{cat_counts[c]} products</p></div></a>'
body+='</div></div></section>'
for key,title,subtitle,field in [('featured','Featured Products','Top featured products available now.','featured'),('bestSelling','Best Selling','Popular products customers ask for most.','bestSelling'),('mustHave','Must Have Car Accessories','Smart upgrades for your vehicle.','mustHave')]:
    arr=[p for p in products if p.get(field)]
    if arr:
        body+=f'<section class="section alt"><div class="wrap"><div class="section-head"><div><h2>{esc(site.get("websiteSections",{}).get(key,{}).get("title",title))}</h2><p>{esc(site.get("websiteSections",{}).get(key,{}).get("subtitle",subtitle))}</p></div><a class="btn secondary small" href="/shop/">View all</a></div><div class="grid">'+''.join(card(p) for p in arr[:8])+'</div></div></section>'
body+='<section class="section" id="services"><div class="wrap"><div class="section-head"><div><h2>Professional services</h2><p>Installation and vehicle customisation from the same team.</p></div></div><div class="services">'+''.join(f'<article class="info-card"><h3>{esc(x.get("title"))}</h3><p>{esc(x.get("text"))}</p></article>' for x in services_text)+'</div></div></section>'
body+='<section class="section alt"><div class="wrap"><div class="section-head"><div><h2>Why Customcarz Auto Care</h2><p>Product matching, sourcing and installation support in Nairobi CBD.</p></div></div><div class="why">'+''.join(f'<article class="info-card"><h3>{esc(x.get("title"))}</h3><p>{esc(x.get("text"))}</p></article>' for x in why)+'</div></div></section>'
body+='<section class="section" id="reviews"><div class="wrap"><div class="section-head"><div><h2>Customer reviews</h2><p>Recent testimonials published in the business catalogue.</p></div></div><div class="reviews">'+''.join(f'<article class="info-card"><h3>★★★★★</h3><p>“{esc(x.get("text"))}”</p><div class="muted" style="margin-top:12px">{esc(x.get("name"))}</div></article>' for x in reviews[:6])+'</div></div></section>'
body+=f'<section class="section alt" id="contact"><div class="wrap contact"><div class="contact-card"><div class="kicker">Visit us</div><h2>{esc(site.get("bizName"))}</h2><p class="muted">{esc(site.get("location"))}</p><div class="actions"><a class="btn" href="{esc(links.get("maps","#"))}">Open Google Maps</a><a class="btn whatsapp" href="{esc(links.get("whatsapp","https://wa.me/254757555691"))}">WhatsApp</a></div></div><div class="contact-card"><h3>Contact</h3><div class="contact-list"><div class="contact-item"><b>Phone</b><br><a href="{esc(links.get("phone","tel:+254757555691"))}">{esc(site.get("phone"))}</a></div><div class="contact-item"><b>Email</b><br><a href="{esc(links.get("email","mailto:customcarzautocare@gmail.com"))}">{esc(site.get("email"))}</a></div><div class="contact-item"><b>Hours</b><br>{esc(site.get("hours"))}</div><div class="contact-item"><b>M-Pesa</b><br>{esc(site.get("till"))}</div></div></div></div></section></main>{foot()}'''
(OUT/'index.html').write_text(head('Customcarz Auto Care | Car Accessories & Spare Parts Nairobi',site.get('description',''),BASE+'/',extra)+body,encoding='utf-8')

# Shop
shop_cards=''.join(card(p,'shop') for p in products)
options=''.join(f'<option>{esc(c)}</option>' for c in canon_cats if cat_counts[c])
shop_body=f'''<body>{nav()}<main><section class="section"><div class="wrap"><div class="crumbs"><a href="/">Home</a> / Shop</div><div class="section-head"><div><h1>Car Accessories & Parts Shop</h1><p>Browse {len(products)} products. Use search and category filters to find the right item.</p></div></div><div class="shop-tools"><input type="search" data-search placeholder="Search products, make or model"><select data-filter><option value="">All categories</option>{options}</select><span class="notice" data-count>{len(products)} products shown</span></div><div class="grid">{shop_cards}</div></div></section></main>{foot()}'''
(OUT/'shop').mkdir(exist_ok=True)
(OUT/'shop/index.html').write_text(head('Shop | Customcarz Auto Care Nairobi','Browse car accessories, lighting parts, body parts, interior accessories and more from Customcarz Auto Care.',BASE+'/shop/')+shop_body,encoding='utf-8')

# Categories index
catbody=f'''<body>{nav()}<main><section class="section"><div class="wrap"><div class="crumbs"><a href="/">Home</a> / Categories</div><div class="section-head"><div><h1>Shop by Categories</h1><p>Browse our organized catalogue.</p></div></div><div class="category-grid">'''
for c in canon_cats:
 if not cat_counts[c]: continue
 catbody+=f'<a class="category" href="/category/{slugify(c)}/"><img loading="lazy" src="/{esc(cat_img[c])}" alt="{esc(c)}"><div class="cat-content"><h3>{esc(c)}</h3><p>{cat_counts[c]} products</p></div></a>'
catbody+='</div></div></section></main>'+foot()
(OUT/'categories').mkdir(exist_ok=True)
(OUT/'categories/index.html').write_text(head('Car Accessories Categories | Customcarz Auto Care','Shop Customcarz Auto Care by category: interior, exterior, lighting, body parts, styling, electronics and safety.',BASE+'/categories/')+catbody,encoding='utf-8')

# Category pages
for c in canon_cats:
 arr=[p for p in products if canonical_category(p.get('category',''),p.get('subcat',''))==c]
 if not arr: continue
 d=f'Shop {c.lower()} in Nairobi from Customcarz Auto Care. Browse prices, fitment details and product information.'
 b=f'''<body>{nav()}<main><section class="section"><div class="wrap"><div class="crumbs"><a href="/">Home</a> / <a href="/categories/">Categories</a> / {esc(c)}</div><div class="section-head"><div><h1>{esc(c)}</h1><p>{esc(d)}</p></div></div><div class="grid">{''.join(card(p,'category') for p in arr)}</div></div></section></main>{foot()}'''
 pdir=OUT/'category'/slugify(c); pdir.mkdir(parents=True,exist_ok=True)
 (pdir/'index.html').write_text(head(f'{c} | Customcarz Auto Care Nairobi',d,BASE+'/category/'+slugify(c)+'/')+b,encoding='utf-8')

# Product pages
product_urls=[]
for p in products:
 slug=slugify(p.get('name'))+'-'+str(p.get('id'))
 pdir=OUT/'products'/slug; pdir.mkdir(parents=True,exist_ok=True)
 url=url_product(p); product_urls.append(url)
 name=clean(p.get('name')) or 'Car accessory'
 desc=text(p.get('description')) or f'{name} available from Customcarz Auto Care in Nairobi, Kenya.'
 cat=canonical_category(p.get('category',''),p.get('subcat',''))
 stock=int(p.get('stock') or 0)
 offer={'@type':'Offer','url':url,'priceCurrency':'KES','price':str(p.get('price') or 0),'availability':'https://schema.org/'+('InStock' if stock>0 else 'OutOfStock'),'seller':{'@type':'Organization','name':site.get('bizName')}}
 schema={'@context':'https://schema.org','@type':'Product','name':name,'description':desc,'image':[img_abs(p.get('image'))],'category':cat,'brand':{'@type':'Brand','name':clean(p.get('make')) or 'Customcarz Auto Care'},'offers':offer}
 extra=f'<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(",",":"))}</script>'
 image='../../'+p.get('image','')
 oldhtml=f'<span class="old">{money(p.get("oldPrice"))}</span>' if p.get('oldPrice') and float(p.get('oldPrice'))>float(p.get('price') or 0) else ''
 wa=links.get('whatsapp','https://wa.me/254757555691')+'?text='+quote(f'Hello Customcarz, I am interested in {name} - {money(p.get("price"))}')
 b=f'''<body>{nav()}<main><div class="wrap"><div class="crumbs"><a href="/">Home</a> / <a href="/shop/">Shop</a> / {esc(cat)} / {esc(name)}</div><section class="detail"><div class="detail-media"><img src="{esc(image)}" alt="{esc(name)}" width="900" height="900"></div><div><div class="kicker">{esc(cat)}</div><h1>{esc(name)}</h1><div class="detail-price">{money(p.get('price'))} {oldhtml}</div><p class="desc">{esc(desc)}</p><div class="specs"><div class="spec"><b>Availability</b>{'In stock' if stock>0 else 'Out of stock'}</div><div class="spec"><b>Stock</b>{stock}</div><div class="spec"><b>Make</b>{esc(clean(p.get('make')) or '—')}</div><div class="spec"><b>Model</b>{esc(clean(p.get('model')) or '—')}</div><div class="spec"><b>Year</b>{esc(clean(p.get('year')) or '—')}</div><div class="spec"><b>Subcategory</b>{esc(clean(p.get('subcat')) or '—')}</div></div><div class="actions"><a class="btn whatsapp" href="{esc(wa)}">Ask on WhatsApp</a><a class="btn secondary" href="{esc(links.get('phone','tel:+254757555691'))}">Call {esc(site.get('phone'))}</a></div><p class="muted" style="margin-top:20px">📍 {esc(site.get('location'))}</p></div></section></div></main>{foot()}'''
 (pdir/'index.html').write_text(head(f'{name} | Customcarz Auto Care',desc,url,extra)+b,encoding='utf-8')

# 404
(OUT/'404.html').write_text(head('Page not found | Customcarz Auto Care','The page you requested was not found.',BASE+'/404.html')+f'''<body>{nav()}<main><section class="section"><div class="wrap notfound"><div class="kicker">404</div><h1>Page not found</h1><p class="muted">The page may have moved. Browse the current catalogue instead.</p><a class="btn" href="/shop/">Open shop</a></div></section></main>{foot()}''',encoding='utf-8')

# Sitemap
urls=[BASE+'/',BASE+'/shop/',BASE+'/categories/']+[BASE+'/category/'+slugify(c)+'/' for c in canon_cats if cat_counts[c]]+product_urls
xml=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
for u in urls:
 xml.append('  <url><loc>'+esc(u)+'</loc></url>')
xml.append('</urlset>')
(OUT/'sitemap.xml').write_text('\n'.join(xml),encoding='utf-8')
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /admin.html\n\nSitemap: https://customcarzautocare.co.ke/sitemap.xml\n',encoding='utf-8')

# Security and browser files
(OUT/'.nojekyll').write_text('',encoding='utf-8')
(OUT/'.well-known').mkdir(exist_ok=True)
(OUT/'.well-known/security.txt').write_text('Contact: mailto:customcarzautocare@gmail.com\nExpires: 2027-09-25T00:00:00.000Z\nPreferred-Languages: en\nCanonical: https://customcarzautocare.co.ke/.well-known/security.txt\n',encoding='utf-8')
(OUT/'site.webmanifest').write_text(json.dumps({'name':'Customcarz Auto Care','short_name':'Customcarz','start_url':'/','display':'standalone','background_color':'#07090d','theme_color':'#ffd21a'},indent=2),encoding='utf-8')
# CNAME correct
(OUT/'CNAME').write_text('customcarzautocare.co.ke\n',encoding='utf-8')

# Replace admin defaults and obsolete SEO snapshot button behavior.
admin=(OUT/'admin.html').read_text(encoding='utf-8',errors='ignore')
admin=admin.replace('value="Customcarzautocare.co.ke-"','value="Autocare"')
admin=admin.replace('PUBLISH SEO SNAPSHOT','REBUILD SEO PAGES')
old="$('publishSeo').onclick=async()=>{try{const path='index.html';const r=await gh(path+'?ref='+encodeURIComponent($('branch').value));let text=ub64(r.content);const graph={'@context':'https://schema.org','@graph':products.map(p=>({'@type':'Product',name:p.name,description:p.description||p.name,image:p.image?['https://customcarzautocare.co.ke/'+p.image.replace(/^\\//,'')]:[],offers:{'@type':'Offer',url:'https://customcarzautocare.co.ke/#product-'+p.id,priceCurrency:'KES',price:String(p.price||0),availability:'https://schema.org/'+(Number(p.stock||0)>0?'InStock':'OutOfStock')}}))};const tagStart='<script id=\"product-schema\" type=\"application/ld+json\">';const tagEnd='<\\/script>';const re=new RegExp(tagStart.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+'[\\s\\S]*?'+tagEnd);const newTag=tagStart+JSON.stringify(graph)+tagEnd;if(re.test(text))text=text.replace(re,newTag);else{const headClose='</head>';text=text.replace(headClose,newTag+headClose)}await gh(path,{method:'PUT',body:JSON.stringify({message:'Publish product SEO snapshot',content:b64(text),branch:$('branch').value,sha:r.sha})});message('SEO snapshot published.',true)}catch(e){message('ERROR: '+e.message)}};"
# Simpler regex remove actual line and replace.
admin=re.sub(r"\$\('publishSeo'\)\.onclick=async\(\)=>\{.*?\};\n", "$('publishSeo').onclick=async()=>{message('SEO rebuild is automatic: saving products.json or site.json triggers the GitHub Pages rebuild workflow.',true)};\n", admin, flags=re.S)
# Make repo note explicit
admin=admin.replace('Connect to your website files</h2>','Connect to your website files</h2>')
(OUT/'admin.html').write_text(admin,encoding='utf-8')
# remove confusing duplicate admin entry points from root but keep copies in docs/legacy-admin
legacy=OUT/'docs/legacy-admin'; legacy.mkdir(parents=True,exist_ok=True)
for f in ['admin-1.html','admin_fixed.html']:
    if (OUT/f).exists():
        shutil.move(str(OUT/f),str(legacy/f))

