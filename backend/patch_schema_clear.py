import subprocess

f = r"e:\CodeBuddy\VeriCart AI\backend\src\main\resources\schema.sql"
with open(f, "r", encoding="utf-8") as fh:
    text = fh.read()

repl = [
    '["/images/6-1-Apple-iPhone-15-Pro-256GB.jpg", "/images/6-1-2-Apple-iPhone-15-Pro-256GB.jpg"]',
    '["/images/6-1-2-Apple-MacBook-Pro-14-M3.jpg", "/images/8-1-Apple-MacBook-Pro-14-M3.jpg"]',
    '["/images/11-1-1-Apple-iPad-Air-11-M2.jpg", "/images/11-1-2-Apple-iPad-Air-11-M2-2.jpg"]',
    '["/images/13-2-Canon-EOS-R6-Mark-II.jpg"]',
    '["/images/14-1-Apple-Watch-Series-9-1.jpg", "/images/14-2-apple-watch-series-9-3.png"]',
    '["/images/Apple-AirPods-Pro-2.jpg", "/images/Apple-AirPods-Pro-2.webp"]',
]
for old in repl:
    if old in text:
        text = text.replace(old, "[]")
        print("REPLACED:", old[:40], "...")
    else:
        print("NOT FOUND:", old[:40])

with open(f, "w", encoding="utf-8") as fh:
    fh.write(text)
print("done")
