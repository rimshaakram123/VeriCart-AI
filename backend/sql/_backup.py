import subprocess

TSV = r"e:\CodeBuddy\VeriCart AI\backend\sql\other-products-to-remove.tsv"
OUT = r"e:\CodeBuddy\VeriCart AI\backend\sql\backup-other-products-2026-09-09.sql"
MYSQL_BIN = r"C:\Program Files\MySQL\MySQL Server 8.0\bin"

# Collect the 98 "other" product ids from the TSV
ids = []
with open(TSV, encoding="utf-16") as f:
    lines = f.read().splitlines()
for line in lines[1:]:  # skip header
    parts = line.split("\t")
    if len(parts) >= 1 and parts[0].strip().isdigit():
        ids.append(int(parts[0]))

idlist = ",".join(str(i) for i in ids)
print("Collected %d product IDs to back up" % len(ids))

with open(OUT, "w", encoding="utf-8") as f:
    f.write("-- Backup of 'other' (main-category) products + their dependent rows\n")
    f.write("-- Product IDs (%d): %s\n" % (len(ids), idlist))
    f.write("-- Generated 2026-09-09. Restore with:\n")
    f.write("--   mysql -u root -pparadox49 vericart < this_file.sql\n\n")

def dump(table, where):
    with open(OUT, "a", encoding="utf-8") as f:
        r = subprocess.run(
            [MYSQL_BIN + r"\mysqldump.exe", "-u", "root", "-pparadox49",
             "--default-character-set=utf8mb4", "vericart", table, "--where", where],
            stdout=f, stderr=subprocess.DEVNULL)
    return r.returncode

for tbl, col in [("product", "id"), ("review", "product_id"),
                 ("cart_item", "product_id"), ("wishlist", "product_id"),
                 ("order_item", "product_id")]:
    rc = dump(tbl, "%s IN (%s)" % (col, idlist))
    print("dump %s -> rc=%s" % (tbl, rc))

import os
print("Backup size: %d bytes at %s" % (os.path.getsize(OUT), OUT))
