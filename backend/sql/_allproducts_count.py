import json, subprocess, shlex

json_path = r"e:\CodeBuddy\VeriCart AI\frontend\src\subcategoryProducts.json"
with open(json_path, encoding="utf-8-sig") as f:
    data = json.load(f)

total = len(data)
null_pid = [e for e in data if e.get("productId") is None]
nonnull = [e for e in data if e.get("productId") is not None]
# unique non-null productIds (preserving order, like the UI's Set)
seen = set()
unique_ids = []
for e in nonnull:
    pid = e["productId"]
    if pid not in seen:
        seen.add(pid)
        unique_ids.append(pid)

# duplicates within the JSON (same productId appears >1)
from collections import Counter
dup = {k: v for k, v in Counter(e["productId"] for e in nonnull).items() if v > 1}

print("JSON entries total           :", total)
print("entries with productId=null  :", len(null_pid), [e.get('sub') for e in null_pid])
print("entries with productId set   :", len(nonnull))
print("unique non-null productIds   :", len(unique_ids))
print("duplicate productIds in JSON :", dup)

if not unique_ids:
    raise SystemExit(0)

ids_csv = ",".join(str(i) for i in unique_ids)
sql = f"""
SELECT
  COUNT(*) AS total_in_db,
  SUM(CASE WHEN JSON_LENGTH(images) > 0 THEN 1 ELSE 0 END) AS with_image,
  SUM(CASE WHEN JSON_LENGTH(images) = 0 OR images IS NULL THEN 1 ELSE 0 END) AS without_image
FROM product
WHERE id IN ({ids_csv}) AND status = 1;
"""
mysql = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
cmd = [mysql, "-u", "root", "-pparadox49", "--default-character-set=utf8mb4", "-N", "-e", sql, "vericart"]
out = subprocess.run(cmd, capture_output=True, text=True)
print("\n--- DB check (status=1) ---")
print("raw:", repr(out.stdout), repr(out.stderr))
if out.stdout.strip():
    total_in_db, with_image, without_image = [int(x) for x in out.stdout.strip().split("\t")]
    print("matched in DB (status=1)   :", total_in_db)
    print("  with >=1 image           :", with_image)
    print("  without image            :", without_image)
    # cards shown in All Products = unique ids that exist in DB
    print("\n=> All Products cards shown :", total_in_db)
