import subprocess

MYSQL = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

sql = """
-- 1) Reassign the 2 base heroes that have NO sub-category twin, so they are
--    preserved and appear in the per-sub-category browse view (not deleted).
UPDATE product SET category_id = 23 WHERE id = 7;   -- Kindle Paperwhite -> Books (sub 23)
UPDATE product SET category_id = 54 WHERE id = 8;   -- Logitech MX Master 3S -> Computer Accessories (sub 54)

-- 2) Delete the remaining 'other' products (those still assigned to a MAIN category).
--    Their reviews/order-items cascade (CASCADE); cart_item/wishlist use NO ACTION so
--    we delete them explicitly first. FK checks disabled for a clean, ordered delete.
SET FOREIGN_KEY_CHECKS=0;
DELETE FROM review     WHERE product_id IN (SELECT id FROM product WHERE category_id IN (SELECT id FROM category WHERE parent_id IS NULL));
DELETE FROM order_item WHERE product_id IN (SELECT id FROM product WHERE category_id IN (SELECT id FROM category WHERE parent_id IS NULL));
DELETE FROM cart_item  WHERE product_id IN (SELECT id FROM product WHERE category_id IN (SELECT id FROM category WHERE parent_id IS NULL));
DELETE FROM wishlist   WHERE product_id IN (SELECT id FROM product WHERE category_id IN (SELECT id FROM category WHERE parent_id IS NULL));
DELETE FROM product    WHERE category_id IN (SELECT id FROM category WHERE parent_id IS NULL);
SET FOREIGN_KEY_CHECKS=1;

-- 3) Report
SELECT 'total_products' k, COUNT(*) v FROM product
UNION ALL SELECT 'subcat_products', COUNT(*) FROM product WHERE category_id IN (SELECT id FROM category WHERE parent_id IS NULL)
UNION ALL SELECT 'maincat_products', COUNT(*) FROM product WHERE category_id IN (SELECT id FROM category WHERE parent_id IS NULL);
"""

p = subprocess.run(
    [MYSQL, "-u", "root", "-pparadox49", "--default-character-set=utf8mb4", "vericart", "-e", sql],
    capture_output=True, text=True)
print(p.stdout)
if p.stderr.strip():
    print("ERR:", p.stderr)
