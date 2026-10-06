import re, shutil

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

tuple_re = re.compile(r'^\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,')

src_lines = open(SRC, encoding="utf-8-sig").read().split("\n")
out = []
in_review = False
header = None
buf = []  # collected (kept) tuple lines for current review block

for line in src_lines:
    low = line.strip().lower()
    if low.startswith("insert into review"):
        in_review = True
        header = line
        buf = []
        continue
    if in_review:
        m = tuple_re.match(line)
        if m:
            pid = int(m.group(3))
            if pid not in removed:
                buf.append(line.rstrip())
            continue
        else:
            # closer line (ends the review block)
            if buf:
                out.append(header)
                for j, t in enumerate(buf):
                    t2 = t
                    while t2.endswith(",") or t2.endswith(";"):
                        t2 = t2[:-1]
                    out.append(t2 + ("," if j < len(buf) - 1 else ";"))
            # skip a lone ';' / ');' closer (already closed above); emit anything else
            stripped = line.strip()
            if stripped not in (";", ");"):
                out.append(line)
            in_review = False
            header = None
            buf = []
            continue
    out.append(line)

result = "\n".join(out)

# Backup original, then overwrite
shutil.copyfile(SRC, SRC + ".bak")

# Re-scan result to validate
total = 0
affected = 0
in_r = False
for line in result.split("\n"):
    if line.strip().lower().startswith("insert into review"):
        in_r = True
        continue
    if in_r:
        mm = tuple_re.match(line)
        if mm:
            total += 1
            if int(mm.group(3)) in removed:
                affected += 1
        else:
            in_r = False

open(SRC, "w", encoding="utf-8").write(result)
print("Wrote scrubbed file. Original backed up at", SRC + ".bak")
print("Review tuples after scrub:", total, "| still referencing removed products:", affected)
