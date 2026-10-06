import subprocess, re, sys, os

MYSQL = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

sql = r"""
SET SESSION group_concat_max_len = 100000;

SELECT
  m.name AS main_name,
  c.name AS sub_name,
  (
    SELECT p.name
    FROM product p
    WHERE p.category_id = c.id
    ORDER BY p.id
    LIMIT 1
  ) AS sample_product
FROM category c
JOIN category m ON m.id = c.parent_id
WHERE c.parent_id IS NOT NULL
ORDER BY m.name, c.name;
"""

proc = subprocess.run(
    [MYSQL, "-u", "root", "-pparadox49", "--default-character-set=utf8mb4", "vericart"],
    input=sql.encode("utf-8"),
    capture_output=True,
)
out = proc.stdout.decode("utf-8", "replace")
err = proc.stderr.decode("utf-8", "replace")
if proc.returncode != 0:
    print("ERROR:", err)
    sys.exit(1)

lines = out.strip().split("\n")
# skip header row (first line) if present
rows = []
for line in lines[1:]:
    if not line.strip():
        continue
    # mysql tab-separated output
    parts = line.split("\t")
    if len(parts) >= 3:
        rows.append((parts[0], parts[1], parts[2]))

def strip_seed(n):
    return re.sub(r"^SEED:\s*", "", n).strip()

cur_main = None
for main, sub, prod in rows:
    if main != cur_main:
        print(f"\n## {main}")
        cur_main = main
    sample = strip_seed(prod) if prod else "(no products)"
    print(f"  - {sub}: {sample}")

print(f"\nTotal subcategories: {len(rows)}")
