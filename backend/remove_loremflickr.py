import subprocess, sys, json

MYSQL = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

def run(sql, as_str=False):
    p = subprocess.run([MYSQL, "-u", "root", "-pparadox49", "-N", "vericart"],
                       input=sql, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit("MySQL error:\n" + p.stderr)
    return p.stdout

# 1) How many products reference loremflickr?
cnt = run("SELECT COUNT(*) FROM product WHERE images LIKE '%loremflickr%';").strip().splitlines()
print("Products with loremflickr in images:", cnt[0] if cnt else "0")

# 2) Also check category.images just in case
ccnt = run("SELECT COUNT(*) FROM category WHERE images LIKE '%loremflickr%';").strip().splitlines()
print("Categories with loremflickr in images:", ccnt[0] if ccnt else "0")

# 3) Pull affected products: id, name, current images
rows = run("SELECT id, name, images FROM product WHERE images LIKE '%loremflickr%';").splitlines()
data = []
for line in rows:
    if not line.strip():
        continue
    parts = line.split("\t")
    data.append((int(parts[0]), parts[1], parts[2]))

emptied = 0
kept_other = 0
for pid, name, raw in data:
    try:
        arr = json.loads(raw) if raw else []
    except Exception:
        arr = [raw] if raw else []
    if not isinstance(arr, list):
        arr = [arr]
    filtered = [u for u in arr if "loremflickr" not in str(u)]
    if len(filtered) == 0:
        new_raw = "[]"
        emptied += 1
    else:
        new_raw = json.dumps(filtered, ensure_ascii=False)
        kept_other += 1
    upd = f"UPDATE product SET images = '{new_raw.replace(chr(39), chr(39)+chr(39))}' WHERE id = {pid};"
    subprocess.run([MYSQL, "-u", "root", "-pparadox49", "-N", "vericart"],
                   input=upd, capture_output=True, text=True)

print(f"Updated {len(data)} products: {emptied} now have NO image, {kept_other} kept a non-loremflickr image.")

# 4) Verify
after = run("SELECT COUNT(*) FROM product WHERE images LIKE '%loremflickr%';").strip().splitlines()
print("Products still referencing loremflickr after update:", after[0] if after else "?")
