import subprocess, sys

SQL = r"""
UPDATE product SET images = CAST('[]' AS JSON);
SELECT 'remaining_nonempty' AS metric,
       COUNT(*) AS value
FROM product WHERE JSON_LENGTH(images) > 0;
SELECT COUNT(*) AS total_products FROM product;
"""

mysql = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
args = [mysql, "-h", "127.0.0.1", "-P", "3306", "-u", "root", "-pparadox49", "vericart", "-v"]
res = subprocess.run(args, input=SQL.encode("utf-8"), capture_output=True)
sys.stdout.buffer.write(res.stdout)
sys.stderr.buffer.write(res.stderr)
print("RC=", res.returncode)
