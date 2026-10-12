#!/usr/bin/env python3
"""Generate static per-product SEO pages (products/<id>.html) and sitemap.xml
from printful-products.json + custom-products.json.

Run:  python3 build_site.py
Then: git add -A && commit && push
"""
import json, os, re, html, datetime

BASE = "https://kltuf.com"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "products")
os.makedirs(OUT, exist_ok=True)

def load(name):
    try:
        with open(os.path.join(ROOT, name), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, list) else []
    except Exception:
        return []

products = load("printful-products.json") + load("custom-products.json")

def slug(s):
    return re.sub(r"[^A-Za-z0-9_-]+", "-", str(s)).strip("-") or "item"

def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — kltuf</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="product">
<meta property="og:title" content="{title} — kltuf">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{ogimage}">
<meta property="og:url" content="{canonical}">
<style>
  :root{{--cream:#FAF6E8;--snow:#FCFAF4;--ink:#1A1A1A;--charcoal:#5C5C5C;--gold-dark:#B8901E;--crimson:#B91D1D;--border:#D8D2C0;--forest:#2D5530;--serif:'Cormorant Garamond',Georgia,serif;--sans:'Inter',system-ui,sans-serif;}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:var(--sans);background:var(--cream);color:var(--ink);line-height:1.6}}
  a{{color:inherit;text-decoration:none}}
  header{{background:var(--snow);border-bottom:1px solid var(--border);padding:16px 28px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:10}}
  .logo{{font-family:var(--serif);font-size:1.7rem;font-weight:600}}
  .back{{font-size:0.78rem;letter-spacing:1.5px;text-transform:uppercase;color:var(--charcoal)}}
  .back:hover{{color:var(--gold-dark)}}
  main{{max-width:1040px;margin:0 auto;padding:36px 24px 80px;display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start}}
  @media(max-width:820px){{main{{grid-template-columns:1fr;gap:28px}}}}
  .gallery .main{{width:100%;border:1px solid var(--border);border-radius:10px;background:var(--snow);display:block}}
  .thumbs{{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}}
  .thumbs img{{width:72px;height:90px;object-fit:cover;border:1px solid var(--border);border-radius:8px;cursor:pointer}}
  .thumbs img.active{{border-color:var(--ink)}}
  .kicker{{font-size:0.72rem;letter-spacing:2px;text-transform:uppercase;color:var(--gold-dark);font-weight:600;margin-bottom:10px}}
  h1{{font-family:var(--serif);font-size:2.2rem;font-weight:600;line-height:1.15;margin-bottom:14px}}
  .price{{font-family:var(--serif);font-size:1.6rem;font-weight:600;margin-bottom:18px}}
  .desc{{color:var(--charcoal);font-size:0.95rem;margin-bottom:22px;white-space:pre-line}}
  label{{display:block;font-size:0.75rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--charcoal);margin-bottom:6px}}
  select{{width:100%;padding:13px 14px;border:1px solid var(--border);border-radius:9px;font-family:inherit;font-size:0.95rem;background:#fff;margin-bottom:16px}}
  #addBtn{{width:100%;padding:16px;background:var(--ink);color:var(--cream);border:none;border-radius:10px;font-size:0.82rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;cursor:pointer}}
  #addBtn:hover{{background:var(--forest)}}
  .ship{{font-size:0.82rem;color:var(--charcoal);margin-top:14px}}
  .backlink{{display:inline-block;margin-top:20px;font-size:0.82rem;color:var(--gold-dark)}}
</style>
<script type="application/ld+json">{ld}</script>
</head>
<body>
<header>
  <a class="logo" href="/">kltuf</a>
  <a class="back" href="/#shop">← Back to store</a>
</header>
<main>
  <div class="gallery">
    <img class="main" id="mainImg" src="{mainimage}" alt="{alt}">
    <div class="thumbs">{thumbs}</div>
  </div>
  <div class="details">
    <div class="kicker">{kicker}</div>
    <h1>{title}</h1>
    <div class="price">${price}</div>
    <p class="desc">{desc}</p>
    <label for="size">Size</label>
    <select id="size">{options}</select>
    <button id="addBtn">Add to cart</button>
    <p class="ship">🚚 Free US shipping on orders $75+ · Ships from {origin}</p>
    <a class="backlink" href="/#shop">← Continue shopping</a>
  </div>
</main>
<script type="application/json" id="pdata">{pdata}</script>
<script>
(function(){{
  var p = JSON.parse(document.getElementById('pdata').textContent);
  document.querySelectorAll('.thumbs img').forEach(function(t){{
    t.addEventListener('click', function(){{
      document.getElementById('mainImg').src = t.dataset.full;
      document.querySelectorAll('.thumbs img').forEach(function(x){{x.classList.remove('active');}});
      t.classList.add('active');
    }});
  }});
  document.getElementById('addBtn').addEventListener('click', function(){{
    var sel = document.getElementById('size');
    var vid = sel.value;
    var sizeLabel = sel.options[sel.selectedIndex].text;
    var id = p.id + '-' + vid;
    var cart = [];
    try {{ cart = JSON.parse(localStorage.getItem('kltuf_cart') || '[]'); }} catch(e) {{ cart = []; }}
    var existing = cart.find(function(i){{return i.id===id;}});
    if (existing) {{ existing.qty += 1; }}
    else cart.push({{
      id: id,
      title: p.title + (sizeLabel && sizeLabel !== 'One Size' ? ' (Size ' + sizeLabel + ')' : ''),
      price: Number(p.price) || 0,
      img: (p.images && p.images[0]) ? p.images[0] : p.image,
      qty: 1,
      pid: p.printify_id || p.id,
      vid: vid,
      source: p.source || 'custom',
      printify_shop_id: p.printify_shop_id || '',
      shipping_origin: p.shipping_origin || '',
      shipping_days: p.shipping_days || ''
    }});
    localStorage.setItem('kltuf_cart', JSON.stringify(cart));
    window.location.href = '/?cart=1';
  }});
}})();
</script>
</body>
</html>
"""

def build_page(p):
    pid = slug(p.get("id", ""))
    title = str(p.get("title", "Product")).strip()
    price = float(p.get("price") or 0)
    images = [u for u in (p.get("images") or []) if u]
    if not images and p.get("image"):
        images = [p["image"]]
    main_img = images[0] if images else ""
    desc = (p.get("description") or title).strip()
    garment = p.get("garment") or "Clothing"
    gender = (p.get("gender") or "").strip()
    kicker = garment + ((" · " + gender.capitalize()) if gender else "")
    origin = p.get("shipping_location") or p.get("shipping_origin") or "our fulfillment partner"
    variants = p.get("variants") or [{"id": "os", "title": "One Size", "price": price}]
    options = "".join(
        '<option value="%s">%s</option>' % (esc(v.get("id")), esc(v.get("title")))
        for v in variants
    )
    thumbs = "".join(
        '<img src="{u}" data-full="{u}" class="{c}" alt="{a}">'.format(
            u=esc(u), c=("active" if i == 0 else ""), a=esc(title + " view " + str(i + 1)))
        for i, u in enumerate(images)
    )
    canonical = "%s/products/%s.html" % (BASE, pid)
    ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title,
        "image": images,
        "description": desc,
        "brand": {"@type": "Brand", "name": "kltuf"},
        "offers": {
            "@type": "Offer",
            "url": canonical,
            "price": "%.2f" % price,
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "itemCondition": "https://schema.org/NewCondition",
        },
    }
    pdata = json.dumps({
        "id": p.get("id"), "title": title, "price": price, "image": p.get("image"),
        "images": images, "variants": variants,
        "printify_id": p.get("printify_id", ""), "printify_shop_id": p.get("printify_shop_id", ""),
        "source": p.get("source", "custom"),
        "shipping_origin": p.get("shipping_origin", ""), "shipping_days": p.get("shipping_days", ""),
    })
    return pid, PAGE.format(
        title=esc(title), desc=esc(desc), canonical=esc(canonical),
        ogimage=esc(main_img), mainimage=esc(main_img), alt=esc(title),
        thumbs=thumbs, kicker=esc(kicker), price=("%.2f" % price),
        options=options, origin=esc(origin),
        ld=json.dumps(ld, separators=(",", ":")), pdata=esc(pdata),
    )

written = []
for p in products:
    if not p.get("id"):
        continue
    pid, page = build_page(p)
    with open(os.path.join(OUT, pid + ".html"), "w", encoding="utf-8") as f:
        f.write(page)
    written.append(pid)

# sitemap
today = datetime.date.today().isoformat()
urls = [("%s/" % BASE, "1.0", "weekly"),
        ("%s/payment.html" % BASE, "0.4", "monthly"),
        ("%s/policies.html" % BASE, "0.4", "monthly")]
for pid in written:
    urls.append(("%s/products/%s.html" % (BASE, pid), "0.8", "weekly"))
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, prio, freq in urls:
    sm.append("  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>" % (loc, today, freq, prio))
sm.append("</urlset>\n")
with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write("\n".join(sm))

print("Generated %d product pages and sitemap.xml with %d URLs." % (len(written), len(urls)))
