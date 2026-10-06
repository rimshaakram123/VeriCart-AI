import subprocess, sys

SQL = r"""
-- Case 1: products that have BOTH local and http images -> keep only the local ones
UPDATE product p
JOIN (
  SELECT p2.id, JSON_ARRAYAGG(t.val) AS kept
  FROM product p2
  JOIN JSON_TABLE(p2.images, '$[*]' COLUMNS (val VARCHAR(1000) PATH '$')) t
  WHERE t.val NOT LIKE 'http%'
  GROUP BY p2.id
) x ON x.id = p.id
SET p.images = x.kept
WHERE JSON_SEARCH(p.images,'one','http%') IS NOT NULL;

-- Case 2: products that have ONLY http images (no local) -> set to []
UPDATE product
SET images = CAST('[]' AS JSON)
WHERE JSON_SEARCH(images,'one','http%') IS NOT NULL
  AND JSON_SEARCH(images,'one','/images%') IS NULL
  AND JSON_SEARCH(images,'one','images/%') IS NULL;

-- Report: how many products still reference any http image
SELECT 'remaining_http_products' AS metric, COUNT(*) AS value
FROM product WHERE JSON_SEARCH(images,'one','http%') IS NOT NULL;

-- Show the cleaned images for the 20 base seed products (so schema.sql can be aligned)
SELECT id, name, images FROM product WHERE id BETWEEN 1 AND 20 ORDER BY id;
"""

mysql = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
args = [mysql, "-h", "127.0.0.1", "-P", "3306", "-u", "root", "-pparadox49", "vericart", "-v"]
res = subprocess.run(args, input=SQL.encode("utf-8"), capture_output=True)
sys.stdout.buffer.write(res.stdout)
sys.stderr.buffer.write(res.stderr)
print("RC=", res.returncode)
