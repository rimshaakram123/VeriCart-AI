import re

SRC = r"e:\CodeBuddy\VeriCart AI\backend\sql\seed-full-data.sql"
lines = open(SRC, encoding="utf-8-sig").read().split("\n")
tuple_re = re.compile(r'^\s*\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,')

errors = 0
in_r = False
header = None
count = 0
for idx, line in enumerate(lines):
    low = line.strip().lower()
    if low.startswith("insert into review"):
        in_r = True
        header = idx
        count += 1
        continue
    if in_r:
        if tuple_re.match(line):
            continue
        else:
            # block ended; verify the previous emitted tuple ended with ';'
            # find last tuple line before this closer
            last = None
            for k in range(idx - 1, header, -1):
                if tuple_re.match(lines[k]):
                    last = lines[k].rstrip()
                    break
            if last is None:
                print("EMPTY review block at line", header + 1)
                errors += 1
            elif not last.endswith(";"):
                print("Block not closed with ';' near line", idx + 1, "->", last[-30:])
                errors += 1
            in_r = False

print("Review INSERT blocks:", count, "| structural errors:", errors)
