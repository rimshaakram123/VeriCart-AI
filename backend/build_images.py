import subprocess, os, re, json, sys, unicodedata

sys.stdout.reconfigure(encoding="utf-8")

MYSQL = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
SRC = r"e:\CodeBuddy\VeriCart AI\frontend\src\image"
PUB = r"e:\CodeBuddy\VeriCart AI\frontend\public\images"
JSON_OUT = r"e:\CodeBuddy\VeriCart AI\frontend\src\subcategoryProducts.json"

# ---------- 1) list + parse image files ----------
files = [f for f in os.listdir(SRC) if os.path.isfile(os.path.join(SRC, f))]

def parse(fn):
    base, ext = os.path.splitext(fn)
    if "\u2192" in base:
        sub, prod = base.split("\u2192", 1)
        return sub.strip(), prod.strip(), ext
    return None, base.strip(), ext

def prod_key(name):
    # neutralise trailing (2), (copy), etc. and normalise
    return re.sub(r"\s*\(.*?\)\s*$", "", name).strip().lower()

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "img"

def strip_seed(n):
    return re.sub(r"^SEED:\s*", "", n).strip()

# group files by subcategory
subs = {}  # sub -> list of (file, prod, ext)
for fn in files:
    sub, prod, ext = parse(fn)
    if sub is None:
        continue
    subs.setdefault(sub, []).append((fn, prod, ext))

# pick best file per sub (prefer no "(2)" and png)
def rank(t):
    fn, prod, ext = t
    return (0 if "(2)" not in fn and "(copy" not in fn.lower() else 1,
            0 if ext.lower() == ".png" else 1)

chosen = {}  # sub -> (file, prod, ext, slug, dest)
used_slugs = set()
for sub, lst in subs.items():
    lst.sort(key=rank)
    fn, prod, ext = lst[0]
    slug = slugify(prod)
    base_slug = slug
    i = 2
    while slug in used_slugs:
        slug = f"{base_slug}-{i}"
        i += 1
    used_slugs.add(slug)
    dest = f"{slug}{ext.lower()}"
    chosen[sub] = (fn, prod, ext, slug, dest)

# copy
os.makedirs(PUB, exist_ok=True)
for sub, (fn, prod, ext, slug, dest) in chosen.items():
    srcp = os.path.join(SRC, fn)
    dstp = os.path.join(PUB, dest)
    with open(srcp, "rb") as f:
        data = f.read()
    with open(dstp, "wb") as f:
        f.write(data)
print(f"Copied {len(chosen)} images to public/images/")

# ---------- 2) fetch DB products + categories ----------
def q(sql):
    p = subprocess.run([MYSQL, "-u", "root", "-pparadox49", "--default-character-set=utf8mb4", "vericart"],
                       input=sql.encode("utf-8"), capture_output=True)
    if p.returncode != 0:
        print("SQL ERR:", p.stderr.decode("utf-8", "replace")); sys.exit(1)
    return p.stdout.decode("utf-8", "replace")

cats = q("SELECT id,name,parent_id FROM category;")
prods = q("SELECT id,name,price,category_id FROM product;")
cat_rows = [l.split("\t") for l in cats.strip().split("\n")[1:] if l.strip()]
prod_rows = [l.split("\t") for l in prods.strip().split("\n")[1:] if l.strip()]

cat_name_to_id = {r[1].strip(): r[0] for r in cat_rows if len(r) >= 2}
# product name (lower) -> list of ids
prod_by_name = {}
prod_by_id = {}
for r in prod_rows:
    if len(r) < 4: continue
    pid, name, price, cid = r[0], r[1], r[2], r[3]
    prod_by_id[pid] = {"id": pid, "name": name, "price": price, "category_id": cid}
    prod_by_name.setdefault(strip_seed(name).lower(), []).append(pid)

# subcategory name -> first product id (fallback)
sub_first_pid = {}
for r in prod_rows:
    if len(r) < 4: continue
    pid, cid = r[0], r[3]
    # find category name for cid
    cname = None
    for cr in cat_rows:
        if len(cr) >= 2 and cr[0] == cid:
            cname = cr[1].strip(); break
    if cname and cname not in sub_first_pid:
        sub_first_pid[cname] = pid

# ---------- 3) build JSON + collect DB updates ----------
entries = []
db_updates = {}  # url -> set(ids)
for sub, (fn, prod, ext, slug, dest) in chosen.items():
    url = f"/images/{dest}"
    key = prod_key(prod)
    ids = prod_by_name.get(key)
    pid = None
    price = None
    display = prod
    if ids:
        pid = ids[0]
        price = prod_by_id[pid]["price"]
        display = strip_seed(prod_by_id[pid]["name"])
        for i in ids:
            db_updates.setdefault(url, set()).add(i)
    else:
        # fallback: subcategory first product
        fid = sub_first_pid.get(sub)
        if fid:
            pid = fid
            price = prod_by_id[fid]["price"]
            display = strip_seed(prod_by_id[fid]["name"])
            db_updates.setdefault(url, set()).add(fid)
        else:
            display = prod  # no product at all -> show image with filename label
    entries.append({
        "sub": sub,
        "productName": display,
        "image": url,
        "productId": (int(pid) if pid else None),
        "price": (float(price) if price not in (None, "") else None)
    })

entries.sort(key=lambda e: (e["sub"] or ""))
with open(JSON_OUT, "w", encoding="utf-8") as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)
print(f"Wrote {len(entries)} entries to subcategoryProducts.json")

# ---------- 4) update live DB ----------
sql_lines = []
for url, idset in db_updates.items():
    ids = ",".join(sorted(idset, key=lambda x: int(x)))
    sql_lines.append(f"UPDATE product SET images = JSON_ARRAY('{url}') WHERE id IN ({ids});")
sql = "\n".join(sql_lines) + "\n"
p = subprocess.run([MYSQL, "-u", "root", "-pparadox49", "--default-character-set=utf8mb4", "vericart"],
                   input=sql.encode("utf-8"), capture_output=True)
if p.returncode != 0:
    print("DB UPDATE ERR:", p.stderr.decode("utf-8", "replace"))
else:
    print(f"Updated images for {len(db_updates)} distinct products (rows: {sum(len(v) for v in db_updates.values())}).")

# verification
chk = q("SELECT COUNT(*) FROM product WHERE JSON_LENGTH(images) > 0;")
print("Products with >=1 image now:", chk.strip().split("\n")[-1])
