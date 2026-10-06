import re

TSV = r"e:\CodeBuddy\VeriCart AI\backend\sql\other-products-to-remove.tsv"
SRC = r"e:\CodeBuddy\VeriCart AI\backend\sql\seed-full-data.sql"

# Removed product ids (everything we deleted). Keep 7 & 8 (reassigned, still exist).
removed = set()
with open(TSV, encoding="utf-16") as f:
    for line in f.read().splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) >= 1 and parts[0].strip().isdigit():
            removed.add(int(parts[0]))
removed.discard(7)
removed.discard(8)
print("Removed product ids (reviews to drop):", len(removed))

text = open(SRC, encoding="utf-8-sig").read()
lines = text.split("\n")

tuple_re = re.compile(r'^\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,')

total = 0
affected = 0
affected_ids = set()
in_review = False
for line in lines:
    if line.strip().lower().startswith("insert into review"):
        in_review = True
        continue
    if in_review:
        m = tuple_re.match(line)
        if m:
            total += 1
            pid = int(m.group(3))
            if pid in removed:
                affected += 1
                affected_ids.add(pid)
        else:
            in_review = False

print("Total review tuples:", total)
print("Review tuples to drop:", affected)
print("Distinct removed product_ids that have reviews here:", len(affected_ids))
