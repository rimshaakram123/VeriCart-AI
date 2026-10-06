import subprocess

sql = """
SELECT p.id, p.category_id, p.name
FROM product p
WHERE p.category_id IN (SELECT id FROM category WHERE parent_id IS NOT NULL)
AND (
  p.name LIKE '%iPhone%' OR p.name LIKE '%MacBook%' OR p.name LIKE '%AirPods%'
  OR p.name LIKE '%iPad%' OR p.name LIKE '%Apple Watch%' OR p.name LIKE '%Dyson%'
  OR p.name LIKE '%Kindle%' OR p.name LIKE '%Logitech%' OR p.name LIKE '%Sony%'
  OR p.name LIKE '%Canon%' OR p.name LIKE '%Huawei%' OR p.name LIKE '%Anker%'
  OR p.name LIKE '%Xiaomi%' OR p.name LIKE '%Nike%' OR p.name LIKE '%Adidas%'
  OR p.name LIKE '%LEGO%'
)
ORDER BY p.name;
"""

p = subprocess.run(
    [r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
     "-u", "root", "-pparadox49", "--default-character-set=utf8mb4", "vericart", "-e", sql],
    capture_output=True, text=True)
print(p.stdout)
if p.stderr.strip():
    print("ERR:", p.stderr)
