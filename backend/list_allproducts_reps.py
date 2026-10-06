import subprocess, sys, json

MYSQL = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

def run(sql):
    p = subprocess.run([MYSQL, "-u", "root", "-pparadox49", "-N", "vericart"],
                       input=sql, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit("MySQL error:\n" + p.stderr)
    out = []
    for line in p.stdout.splitlines():
        if line.strip() == "":
            continue
        out.append(line.split("\t"))
    return out

cats = run("SELECT id, COALESCE(parent_id,0) FROM category;")
sub_ids = {int(r[0]) for r in cats if r[1] not in ("0", "", None) and int(r[1]) != 0}

# id, name, category_id, raw images
prods = run(
    "SELECT id, name, COALESCE(category_id,0), images "
    "FROM product WHERE status=1 ORDER BY created_at DESC;"
)

def first_url(raw):
    if not raw or raw == "[]":
        return ""
    try:
        arr = json.loads(raw)
        return arr[0] if isinstance(arr, list) and arr else ""
    except Exception:
        return raw

chosen = {}
for r in prods:
    pid, name, cid, raw = int(r[0]), r[1], int(r[2]), r[3]
    if cid not in sub_ids:
        continue
    has = bool(first_url(raw))
    cur = chosen.get(cid)
    if cur is None or (has and not cur[2]):
        chosen[cid] = (pid, name, has, first_url(raw))

reps = []
for cid in sorted(chosen.keys()):
    pid, name, has, url = chosen[cid]
    reps.append((pid, name.replace("SEED:", "").strip(), url))

print(f"TOTAL REP PRODUCTS: {len(reps)}\n")
for i, (pid, name, url) in enumerate(reps, 1):
    print(f"{i:2}. {name[:42]:42} | img: {url or '(none -> fallback icon)'}")

# detect duplicate image URLs among reps
from collections import defaultdict
byurl = defaultdict(list)
for pid, name, url in reps:
    if url:
        byurl[url].append(name)
print("\n=== DUPLICATE IMAGES ACROSS REPS ===")
dups = {u: ns for u, ns in byurl.items() if len(ns) > 1}
if not dups:
    print("None — every rep with an image uses a unique URL.")
else:
    for u, ns in dups.items():
        print(f"  {u}\n    used by: {', '.join(ns)}")
