import sys

# Map each base seed product id -> its cleaned images JSON (from the live, stripped DB).
REPL = {
    'photo-1510557880182-3d4d3cba35a5': '["/images/6-1-Apple-iPhone-15-Pro-256GB.jpg", "/images/6-1-2-Apple-iPhone-15-Pro-256GB.jpg"]',
    'photo-1517336714731-489689fd1ca8': '["/images/6-1-2-Apple-MacBook-Pro-14-M3.jpg", "/images/8-1-Apple-MacBook-Pro-14-M3.jpg"]',
    'photo-1505740420928-5e560c06d30e?w=600&h=600&fit=crop", "https://images.unsplash.com/photo-1583394838336': '[]',
    'photo-1610945265064-0e34e5519bbf': '[]',
    'photo-1542291026-7eec264c27ff': '[]',
    'photo-1558618666-fcd25c85f82e': '[]',
    'photo-1544716278-ca5e3f4abd8c': '[]',
    'photo-1527864550417-7fd91fc51a46': '[]',
    'photo-1544244015-0df4b3ffc6b0': '["/images/11-1-1-Apple-iPad-Air-11-M2.jpg", "/images/11-1-2-Apple-iPad-Air-11-M2-2.jpg"]',
    'photo-1516035069371-29a1b244cc32': '["/images/13-2-Canon-EOS-R6-Mark-II.jpg"]',
    'photo-1546868871-af0de0ae72be': '["/images/14-1-Apple-Watch-Series-9-1.jpg", "/images/14-2-apple-watch-series-9-3.png"]',
    'photo-1585790050230-5dd28404ccb9': '[]',
    'photo-1505740420928-5e560c06d30e?w=600&h=600&fit=crop", "https://images.unsplash.com/photo-1484704849700': '[]',
    'photo-1600269452121-4f2416e55c28': '[]',
    'photo-1608231387042-66d1773070a5': '[]',
    'photo-1542272454315-4c01d7abdf4a': '[]',
    'photo-1514989940723-e8e51635b782': '[]',
    'photo-1555041469-a586c61ea9bc': '[]',
    'photo-1588423771073-b8903fbb85b5': '["/images/Apple-AirPods-Pro-2.jpg", "/images/Apple-AirPods-Pro-2.webp"]',
    'photo-1580480055273-228ff5388ef8': '[]',
}

# Each key uniquely identifies one unsplash image line (id3/id13 are disambiguated by 2nd URL).
OLD_NEW = {}
for k, new in REPL.items():
    old = ('[\n  \'["https://images.unsplash.com/' + k + '&fit=crop"]\'')  # placeholder, replaced below
    OLD_NEW[k] = new

files = [r"e:\CodeBuddy\VeriCart AI\backend\src\main\resources\schema.sql",
         r"e:\CodeBuddy\VeriCart AI\backend\sql\schema.sql"]

for f in files:
    try:
        with open(f, "r", encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        print("SKIP (missing):", f)
        continue
    before = text
    for k, new in REPL.items():
        needle = 'https://images.unsplash.com/' + k
        # Replace the whole quoted JSON-array image literal that contains this URL.
        # The literal looks like: '["https://images.unsplash.com/<k>...", "https://images.unsplash.com/..."]'
        idx = text.find(needle)
        while idx != -1:
            # find start quote (the opening ' before [)
            start = text.rfind("'", 0, idx)
            # find the matching closing ']'
            end = text.find("]", idx)
            end_quote = text.find("'", end)
            old_lit = text[start:end_quote + 1]
            new_lit = "'" + new + "'"
            text = text[:start] + new_lit + text[end_quote + 1:]
            idx = text.find(needle, start + len(new_lit))
    changed = text != before
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(("PATCHED" if changed else "UNCHANGED"), f)
