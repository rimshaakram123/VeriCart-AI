import csv, re, json, os

BASE = r"e:\CodeBuddy\VeriCart AI"
DUMP = os.path.join(BASE, "backend", "products_dump.csv")
MAP = os.path.join(BASE, "frontend", "public", "images", "IMAGE_MAPPING.csv")
OUT_SQL = os.path.join(BASE, "backend", "updates_images.sql")
OUT_PREVIEW = os.path.join(BASE, "backend", "assignments_preview.csv")

STOP = {"by","the","and","of","for","a","an","to","in","with","1st","2nd","3rd",
        "edition","new","2","3","4","5","6","7","8","9","10","11","12","13"}

def norm(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    toks = [t for t in s.split() if t not in STOP and len(t) > 1]
    return toks

def core(s):
    # strip leading numbering junk like "54.2 . " or "36"
    s = re.sub(r"^[\d\s.\-_]+", "", s.lower())
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    # drop file extension words so "book.jpeg" -> "book"
    s = re.sub(r"\b(jpg|jpeg|png|webp|gif|bmp)\b", "", s)
    return s.replace(" ", "")

# load products
products = []  # (id, name, images)
with open(DUMP, newline="", encoding="utf-16") as f:
    for row in csv.reader(f, delimiter="\t"):
        if len(row) < 3:
            continue
        pid, name, images = row[0], row[1], row[2]
        products.append((pid, name, images))

# load images
images = []  # (original, url)
with open(MAP, newline="", encoding="utf-8") as f:
    r = csv.DictReader(f)
    for row in r:
        images.append((row["original"], row["url"]))

# Pre-normalize image cores
img_cores = []
for orig, url in images:
    c = core(orig)
    if len(c) < 4:
        continue
    img_cores.append((c, url, orig))

def is_empty(im):
    return im is None or im.strip() == "" or im.strip() == "[]" or im.strip() == '""' or im.strip() == '"[]"'

def common_prefix_len(a, b):
    n = min(len(a), len(b)); i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i

assignments = {}  # normkey -> (display_name, [urls])

for pid, name, im in products:
    if not is_empty(im):
        continue
    if not name:
        continue
    pcore = core(name)
    if len(pcore) < 4:
        continue
    matches = []
    for c, url, orig in img_cores:
        if len(c) < 4:
            continue
        # Rule 1: one fully contains the other (strong, specific match)
        # Guard: when image core is contained in product, require image core
        # length >= 6 so junk like "orig" (in "original") can't match.
        if pcore in c:
            matches.append((url, orig, 1))
        elif len(c) >= 6 and c in pcore:
            matches.append((url, orig, 1))
        else:
            # Rule 2: long shared prefix (handles minor suffix diffs like "5G" vs "Pro")
            m = min(len(pcore), len(c))
            pref = common_prefix_len(pcore, c)
            if m >= 9 and pref >= 0.7 * m:
                matches.append((url, orig, 2))
    if not matches:
        continue
    matches.sort(key=lambda x: x[2])
    seen = set(); uniq = []
    for url, orig, _ in matches:
        if url not in seen:
            seen.add(url); uniq.append((url, orig))
    uniq = uniq[:2]
    nk = pcore
    if nk not in assignments:
        assignments[nk] = (name, [u for u, _ in uniq])

# Build SQL (group by exact name so all duplicate rows get images)
by_name = {}
for nk, (name, urls) in assignments.items():
    by_name.setdefault(name, []).extend(urls)

with open(OUT_SQL, "w", encoding="utf-8", newline="\n") as f:
    for name, urls in by_name.items():
        seen = set(); u2 = []
        for u in urls:
            if u not in seen:
                seen.add(u); u2.append(u)
        arr = "JSON_ARRAY(" + ", ".join("'%s'" % u.replace("'", "\\'") for u in u2) + ")"
        f.write("UPDATE product SET images = %s WHERE name = '%s' AND (images IS NULL OR JSON_LENGTH(images) = 0);\n" % (arr, name.replace("'", "\\'")))

# Preview
with open(OUT_PREVIEW, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["product_name", "image_url", "image_original"])
    for nk, (name, urls) in assignments.items():
        for url in urls:
            orig = next((o for u, _, o in img_cores if u == url), "")
            w.writerow([name, url, orig])

print("Products with empty images matched:", len(assignments))
print("Distinct product names to update:", len(by_name))
print("SQL file:", OUT_SQL)
print("Preview file:", OUT_PREVIEW)
