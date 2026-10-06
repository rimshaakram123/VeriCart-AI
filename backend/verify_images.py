import subprocess, sys
sql = (
    "SELECT "
    "(SELECT COUNT(*) FROM product WHERE JSON_SEARCH(images,'one','http%') IS NOT NULL) AS http_imgs, "
    "(SELECT COUNT(*) FROM product WHERE JSON_LENGTH(images) > 0) AS with_local, "
    "(SELECT COUNT(*) FROM product) AS total;"
)
r = subprocess.run(
    [r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
     "-h", "127.0.0.1", "-P", "3306", "-u", "root", "-pparadox49", "vericart", "-e", sql],
    capture_output=True)
sys.stdout.buffer.write(r.stdout)
sys.stderr.buffer.write(r.stderr)
