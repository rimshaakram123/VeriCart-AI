import subprocess

MYSQL = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

sql = """
SELECT 'subcats_exist' k, COUNT(*) v FROM category WHERE parent_id IS NOT NULL
UNION ALL SELECT 'mains_exist', COUNT(*) FROM category WHERE parent_id IS NULL
UNION ALL SELECT 'products_total', COUNT(*) FROM product
UNION ALL SELECT 'products_in_subcat', COUNT(*) FROM product WHERE category_id IN (SELECT id FROM category WHERE parent_id IS NOT NULL)
UNION ALL SELECT 'products_in_main', COUNT(*) FROM product WHERE category_id IN (SELECT id FROM category WHERE parent_id IS NULL)
UNION ALL SELECT 'products_orphan_cat', COUNT(*) FROM product p WHERE NOT EXISTS (SELECT 1 FROM category c WHERE c.id=p.category_id);
"""

p = subprocess.run([MYSQL, "-u", "root", "-pparadox49", "--default-character-set=utf8mb4", "vericart", "-e", sql],
                   capture_output=True, text=True)
print(p.stdout)
if p.stderr.strip():
    print("ERR:", p.stderr)
