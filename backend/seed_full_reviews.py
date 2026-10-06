#!/usr/bin/env python3
"""
Generate seed data for VeriCart AI:
  • 5-6 customer reviews per product (one bad comment for ~every 3rd product)
  • Richer "Details" descriptions for every product (category-aware)

Output: backend/sql/seed-full-data.sql  (safe to re-run)
Then auto-executes it via mysql.exe.

Idempotent: deletes its own previous seed range before inserting.
"""
import subprocess, os, random, html

random.seed(42)

MYSQL = r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe'
DB    = 'vericart'
USER  = 'root'
PASS  = 'paradox49'

# Idempotency range — well clear of seed-reviews.sql (9001-9100) and any real data
REVIEW_ID_START = 10000
REVIEW_ID_END   = 50000

# Reviewer user pool — distinct fake customers so each product shows 5-6 DIFFERENT names.
# These users are created by this script (ids 1000-1023, well clear of real users: max id = 23).
FAKE_REVIEWER_IDS = list(range(1000, 1024))   # 24 ids -> 6 distinct names per product
REVIEWER_NAMES = [
    'James Carter', 'Aisha Khan', 'Marcus Lee', 'Sofia Rossi', 'Daniel Wong', 'Emily Clark',
    'Liam Murphy', 'Olivia Bennett', 'Noah Patel', 'Mia Nguyen', 'Ethan Brooks', 'Ava Thompson',
    'Lucas Silva', 'Isabella Garcia', 'Henry Wright', 'Charlotte Davis', 'Benjamin Foster',
    'Amelia Cooper', 'Samuel Kim', 'Grace Lewis', 'Jack Turner', 'Chloe Walker', 'Owen Scott',
    'Zoe Mitchell',
]
# Shared bcrypt hash (same as the seed admin) — these accounts are display-only, never logged in.
REVIEWER_HASH = '$2a$10$6Vzf8EuBVoQ4fJVFxjZ/1OwvjtMQWeMxYkw/GMU2gx9GiJNufe0Lu'


def run(sql: str) -> str:
    p = subprocess.run(
        [MYSQL, f'-u{USER}', f'-p{PASS}', DB, '-N', '-e', sql],
        capture_output=True, text=True
    )
    if p.returncode != 0:
        raise RuntimeError(f"MySQL error:\n{p.stderr}\n--- SQL ---\n{sql[:500]}")
    return p.stdout


# ---------------- category-aware content pools ----------------
# Each pool: list of (rating, content).  Reviews are picked with the matching rating.

POOLS = {
    'Smartphones': [
        (5, "Upgraded from my old phone and the difference is night and day. The display is bright and crisp, the camera takes sharp photos even in low light, and the battery comfortably lasts a full day of heavy use."),
        (5, "Fast, smooth, and the build quality feels premium in the hand. Face unlock is instant and apps open without any lag. Delivery was quick and the packaging was secure."),
        (4, "Great phone overall — performance is snappy and the screen is gorgeous. Only minor complaint is that it gets a bit warm during long gaming sessions, but nothing concerning."),
        (4, "Camera quality is excellent, especially the night mode shots. Battery life is solid for my usage. Slightly heavier than I expected but you get used to it."),
        (5, "Best phone I have owned. The display refresh rate makes everything silky smooth and the speakers are louder than I expected. Worth every penny."),
        (4, "Solid all-rounder. Calls are clear, 5G signal is strong, and the UI is clean. Charging speed is good though I wish wireless charging were faster."),
        (2, "Disappointed with the battery — after a couple of months it drains much faster than advertised and I have to top up mid-afternoon. For this price I expected better."),
    ],
    'Laptops': [
        (5, "Incredible performance for the size and weight. The keyboard is comfortable for long typing sessions and the screen is sharp and colour accurate. Battery easily covers a full workday."),
        (5, "Handles video editing and large spreadsheets without breaking a sweat. The fanless design means it runs silently under normal use. Build quality is rock solid."),
        (4, "Great laptop for everyday productivity. Performance is snappy and the trackpad is the best I have used. The base RAM can feel limiting if you keep many tabs open."),
        (5, "Boot-up is nearly instant and the SSD is fast. Speakers are surprisingly good for such a thin machine. Very happy with the purchase."),
        (4, "Excellent display and the keyboard is a joy to type on. Performance is great for coding and office work. Could use a couple more ports but a hub solves that."),
        (5, "Lightweight, fast, and the battery life is phenomenal — I get through a full day of meetings without plugging in. Highly recommend."),
        (3, "Performance is fine but the screen hinge feels wobbly after a few weeks and the palm-rest gets noticeably warm under load."),
    ],
    'Tablets': [
        (5, "Perfect for reading, note-taking, and watching videos. The display is bright and the speakers are loud enough for a small room. Battery lasts forever."),
        (5, "Light, thin, and incredibly fast. Stylus support makes it great for sketching and marking up PDFs. Great value."),
        (4, "Good screen and the performance is smooth for streaming and light work. The app ecosystem could be better but that is the platform, not the device."),
        (4, "Comfortable to hold for long reading sessions. The display is sharp and the weight is well balanced. Charging is reasonably fast."),
        (5, "Replaced my laptop for travel and it handles everything I need. The screen is gorgeous for movies. Build quality feels premium."),
        (4, "Solid tablet with a nice display. A bit pricey for the storage you get at the base tier, but the overall experience is smooth."),
        (2, "Screen developed a bright spot within two months and customer service was slow to respond. Disappointed for the price."),
    ],
    'Headphones': [
        (5, "Noise cancelling is genuinely industry-leading. I use them on flights and the engine drone disappears completely. Battery life matches the advertised 30 hours."),
        (5, "Sound quality is rich and balanced with deep but controlled bass. Comfortable for hours of listening thanks to the soft ear cushions."),
        (4, "Great headphones with excellent sound and build. The app EQ is useful. They do get a little warm after extended wear but it is not a dealbreaker."),
        (5, "Best purchase I have made this year. Multipoint pairing works seamlessly between my laptop and phone. Mic quality on calls is clear."),
        (4, "Sound is excellent and the ANC works very well on buses and trains. Slightly expensive but the quality justifies it."),
        (5, "Comfortable for long sessions and the transparency mode sounds natural. Folding case is a nice touch for travel."),
        (2, "The headband clamp is too tight for my head — I get ear fatigue after about an hour. Returning."),
    ],
    'Cameras': [
        (5, "Image quality is stunning, especially in low light. Autofocus locks on fast and the burst rate is more than enough for sports. Build feels professional."),
        (5, "Video quality in 4K is gorgeous and the stabilisation is impressive. Menu system is intuitive once you spend a day with it."),
        (4, "Great hybrid camera for both stills and video. Battery life is solid for a day of shooting. A bit bulky with the large lens."),
        (5, "The dynamic range is incredible and the colour science is beautiful straight out of camera. Worth the investment."),
        (4, "Excellent autofocus and the eye-detection works really well for portraits. File sizes are large so bring extra memory cards."),
        (5, "Upgraded from an older DSLR and the leap in low-light performance is night and day. Highly recommend for enthusiasts."),
        (2, "Overheats during long 4K recording sessions and shuts down after about 20 minutes. Not great for event work."),
    ],
    'Smart Watches': [
        (5, "Tracks my runs, sleep, and daily activity accurately. The always-on display is bright outdoors and the battery lasts two full days."),
        (5, "Comfortable on the wrist and the health features have genuinely motivated me to move more. Notifications are clear and reliable."),
        (4, "Good smartwatch with a bright display and smooth performance. Battery is about a day and a half with always-on enabled."),
        (4, "Looks great with both casual and dressy outfits. Fitness tracking is accurate. Wish the app had better third-party support."),
        (5, "Best smartwatch I have used. Integration with my phone is seamless and the health insights are actually useful."),
        (4, "Solid build and the strap is comfortable for all-day wear. Heart-rate readings match my chest strap closely."),
        (2, "Battery barely makes it through the day with normal use. For the price, I expected much better endurance."),
    ],
    'Men\'s Clothing': [
        (5, "Fabric feels high quality and the fit is true to size. Holds up well after multiple washes with no shrinkage. Great value."),
        (5, "Comfortable enough to wear all day. The stitching and finish look premium. Will definitely buy another colour."),
        (4, "Good quality material and the cut is flattering. Slightly long in the sleeves for my frame but easy to adjust."),
        (4, "Nice weight to the fabric — not too thin, not too heavy. Colour matches the photos exactly."),
        (5, "Replaced several of my old tees with these. They wash well and keep their shape. Highly recommend."),
        (4, "Comfortable everyday piece. Fit is relaxed as described. Dries quickly which is a bonus."),
        (2, "The sizing runs small and the fabric pilled after the first wash. Returning for a larger size."),
    ],
    'Women\'s Clothing': [
        (5, "The fabric is soft and drapes beautifully. True to size and the colour is exactly as shown in the photos. Wore it to an event and got compliments."),
        (5, "Beautiful fit and very flattering. Comfortable for all-day wear. Quality of the stitching is impressive for the price."),
        (4, "Lovely dress, runs slightly small so I sized up. The material has a nice weight and the pattern is well printed."),
        (4, "Comfortable and easy to style. The lining is a nice touch. Delivery was fast and packaging was careful."),
        (5, "Fell in love with this piece the moment I tried it on. The cut is flattering and it works for both casual and dressy occasions."),
        (4, "Soft fabric and the colour is gorgeous. Slightly sheer so I wear a slip underneath — worth mentioning."),
        (2, "The colour faded after two washes and the hem came loose. Not what I expected for the price."),
    ],
    'Shoes': [
        (5, "Incredibly comfortable from day one — no break-in period needed. Cushioning feels soft but supportive. Great for long walks."),
        (5, "Stylish and well made. The fit is true to size and they look even better in person than online. Build quality is solid."),
        (4, "Nice everyday shoe with good cushioning. Took a couple of wears to break in but now they are very comfortable."),
        (4, "Quality is good and the design is classic. Grip is solid on wet pavement. A little stiff at first."),
        (5, "Replaced my old runners with these and the difference in comfort is huge. Lightweight and supportive. Highly recommend."),
        (4, "Comfortable and durable after a few months of regular use. The laces feel premium and the tongue is well padded."),
        (2, "The sole started separating from the upper after a few weeks. Disappointed with the durability for the price."),
    ],
    'Furniture': [
        (5, "Easy to assemble and the build quality is impressive. Feels sturdy and looks much more expensive than it is. Very happy."),
        (5, "Looks great in the room and is genuinely comfortable for long sitting sessions. Finish is clean and even."),
        (4, "Solid piece of furniture. Assembly took about an hour and the instructions were clear. Finish is good for the price."),
        (4, "Comfortable and well made. The cushions hold their shape well. Colour matches the photos."),
        (5, "Replaced an old shelf with this and the difference is huge. Storage is versatile and the finish looks premium."),
        (4, "Good value for the price. Feels sturdy once assembled. The included hardware could be a touch higher quality but it works."),
        (2, "Arrived with a scratch on the side and the assembly hardware was missing several pieces. Poor quality control."),
    ],
    'Kitchenware': [
        (5, "Heats evenly and the non-stick coating is excellent. Easy to clean and the weight feels balanced. A workhorse in the kitchen."),
        (5, "Beautiful enamel finish and the lid seals well for braises. Cleans up easily and looks great on the stove."),
        (4, "Solid build and heats evenly. Handles stay cool on the stovetop. A little heavier than my old pan but the heat retention is worth it."),
        (4, "Good quality and the size is perfect for family meals. Lid fits snugly. Dishwasher safe which is a plus."),
        (5, "Best pan I have owned. Eggs slide right off and the heat distribution is even. Worth the investment."),
        (4, "Nice weight and the glass lid is handy for monitoring food. Comfortable handle that does not get hot."),
        (2, "The non-stick coating started peeling after two months of normal hand-washing. Disappointed."),
    ],
    'Bedding & Towels': [
        (5, "Soft, breathable, and the stitching is impeccable. Washes beautifully and the colour has not faded after several cycles."),
        (5, "Best sheets I have owned. Cool to sleep on in summer and warm enough in winter. Deep pockets fit my mattress perfectly."),
        (4, "Nice quality cotton and the finish feels premium. Slightly wrinkled out of the dryer but irons easily."),
        (4, "Comfortable and well made. The elastic on the fitted sheet holds tight. Good value for the price."),
        (5, "Replaced an old set with these and the difference in comfort is huge. Highly recommend."),
        (4, "Soft and absorbent towels. Generous size and they dry quickly between uses."),
        (2, "Pilled heavily after the first wash and the elastic on the fitted sheet gave out within a month."),
    ],
    'Home Decor': [
        (5, "Looks beautiful in the room and the build quality is solid. The finish is even and the colour matches the photos."),
        (5, "Gorgeous piece. The light it casts is warm and inviting. Easy to set up and looks premium."),
        (4, "Nice design and good size for a side table. Assembly was simple. The finish is even and looks well made."),
        (4, "Adds a lovely ambience to the room. The mist function is quiet and the light options are versatile."),
        (5, "Exactly what I wanted for the space. Quality is impressive and it arrived well packaged."),
        (4, "Looks more expensive than it is. The materials feel substantial and the finish is clean."),
        (2, "Stopped working after two weeks. Customer service was helpful but the product itself is unreliable."),
    ],
    'Fitness Equipment': [
        (5, "Sturdy, well made, and the grip is comfortable even during long workouts. Excellent value for home use."),
        (5, "Replaces a whole rack of dumbbells and the dial system is smooth and secure. Saves a ton of space."),
        (4, "Good quality mat with nice cushioning for yoga and stretching. Slightly slippery at first but gets grippier with use."),
        (4, "Solid build and the resistance is smooth. Foam handles are comfortable. Good for both beginners and intermediate users."),
        (5, "Best addition to my home gym. Takes up minimal space and the weight changes are fast and secure."),
        (4, "Comfortable to use and the materials feel premium. Works well for stretching and core work."),
        (2, "The mat has a strong chemical smell out of the package and the surface started peeling at the edges within weeks."),
    ],
    'Accessories': [
        (5, "Beautiful craftsmanship and the leather feels premium. Hardware is sturdy and the stitching is even. Worth every penny."),
        (5, "Spacious enough for daily essentials and the design is timeless. The strap is comfortable even when fully loaded."),
        (4, "Looks great and the quality is impressive for the price. Slightly smaller than I expected but very versatile."),
        (4, "Nice hardware and the finish is clean. Comfortable to wear crossbody. Holds my phone, wallet, and keys with room to spare."),
        (5, "Compliments every time I carry it. The lining is well finished and the magnetic closure is satisfying."),
        (4, "Compact but holds a surprising amount. The leather has a lovely soft hand feel. A great everyday bag."),
        (2, "The strap stitching came loose after a month of light use. Quality control is disappointing."),
    ],
    'Electronics & Digital': [
        (5, "Plug-and-play simple and the build quality is solid. Performance is exactly what I needed for the price."),
        (5, "Reliable and well designed. Has been working flawlessly for months. Would buy again without hesitation."),
        (4, "Good value and the features match the description. Setup was straightforward."),
        (4, "Works as advertised. Comfortable to use for long sessions and the battery life is decent."),
        (5, "Great little device. Does exactly what it says on the tin and feels premium in the hand."),
        (4, "Solid everyday device. Reasonable price for the features. Packaging was nice."),
        (2, "Stopped working within the first month. Customer service was slow to respond."),
    ],
    'Stationery & Office': [
        (5, "Excellent screen, easy on the eyes, and the battery lasts weeks. Perfect for reading in any light."),
        (5, "Lightweight and the anti-glare screen is a pleasure to read on. Holds thousands of books and the store is well organised."),
        (4, "Good e-reader with a bright screen. Page turns are quick and the library syncs seamlessly across devices."),
        (4, "Comfortable to hold for long reading sessions. Waterproofing gives peace of mind at the pool or beach."),
        (5, "Replaced my paper books with this and have not looked back. Battery life is genuinely impressive."),
        (4, "Nice screen and the warm-light setting is easy on the eyes at night. Good value for the price."),
        (2, "Battery life is much shorter than advertised and the device froze twice in the first week."),
    ],
    'Home & Kitchen': [
        (5, "Powerful suction and the battery lasts through a full clean of my apartment. The laser feature is genuinely useful for spotting dust."),
        (5, "Lightweight, easy to manoeuvre, and converts to a handheld in seconds. A great all-round vacuum."),
        (4, "Strong suction and the bin is easy to empty. A bit loud on max mode but cleaning performance is excellent."),
        (4, "Great for quick clean-ups and the attachments are well thought out. Slightly heavy after long sessions."),
        (5, "Best cordless vacuum I have used. Pet hair is no longer a problem and the run time is honest."),
        (4, "Solid build and the filtration is impressive. Easy to store thanks to the wall mount."),
        (2, "Battery indicator is unreliable and the vacuum lost suction after two months. Disappointed."),
    ],
}

# Fallback pool for any unexpected category
DEFAULT_POOL = POOLS['Electronics & Digital']

# Detailed description templates — appended/replacing product.description
DESC_TEMPLATES = {
    'Smartphones': (
        "{name} combines premium build quality with flagship performance. Powered by a top-tier mobile chipset, "
        "it delivers smooth multitasking, console-quality gaming, and efficient battery use. The high-refresh display "
        "produces vibrant, accurate colours and remains readable even in direct sunlight. The multi-lens camera system "
        "captures sharp detail in daylight and clean, low-noise shots at night, with AI scene optimisation and 4K video recording. "
        "Fast wired and wireless charging, IP-rated water resistance, and the latest connectivity standards (5G, Wi-Fi 6/6E, Bluetooth 5+) "
        "round out a complete package. Every unit sold on VeriCart is verified authentic and ships with full warranty and a tamper-evident seal."
    ),
    'Laptops': (
        "{name} is built for productivity and creativity on the go. The latest-generation processor and fast SSD deliver "
        "instant boot times and smooth performance for office work, programming, photo/video editing, and casual gaming. "
        "The high-resolution display is colour-calibrated out of the box, and the backlit keyboard is comfortable for long typing sessions. "
        "All-day battery life, a lightweight aluminium chassis, and a full set of ports (USB-C, USB-A, HDMI, headphone jack) "
        "make it ideal for both desk and travel use. VeriCart authentication guarantees a brand-new, factory-sealed unit with full manufacturer warranty."
    ),
    'Tablets': (
        "{name} strikes the ideal balance between portability and capability. The vibrant display is perfect for reading, "
        "streaming, sketching, and note-taking, with stylus support and low-latency input for creative workflows. "
        "The chipset handles multitasking, light editing, and modern games without breaking a sweat, while the battery "
        "delivers all-day endurance. Lightweight and thin, it slips easily into a bag and pairs seamlessly with "
        "wireless keyboards and styluses for laptop-style productivity. VeriCart AI verifies authenticity and ships every unit "
        "with tamper-evident packaging and full warranty."
    ),
    'Headphones': (
        "{name} delivers studio-quality sound with deep, controlled bass, clear mids, and detailed highs. "
        "Industry-leading active noise cancellation adapts to your environment, while transparency mode lets in "
        "natural sound when you need to stay aware. Multipoint Bluetooth lets you stay connected to two devices at once, "
        "and the battery delivers up to 30 hours of playback per charge. Plush memory-foam ear cushions and an "
        "adjustable headband keep them comfortable for hours. Every pair sold on VeriCart is verified authentic and ships in "
        "factory-sealed packaging with full manufacturer warranty."
    ),
    'Cameras': (
        "{name} is a professional-grade imaging tool for stills and video. The high-resolution back-illuminated sensor captures "
        "excellent detail with wide dynamic range, while AI-assisted autofocus locks on quickly and tracks subjects reliably "
        "for sports, wildlife, and events. In-body stabilisation keeps handheld shots sharp and video footage smooth. "
        "4K (and in some models 6K/8K) video, 10-bit colour, and dual card slots make it ready for serious production work. "
        "VeriCart AI authenticates every unit and ships with full manufacturer warranty, ensuring you receive a brand-new, factory-sealed body."
    ),
    'Smart Watches': (
        "{name} combines premium materials with comprehensive health and fitness tracking. Continuous heart-rate and SpO2 monitoring, "
        "advanced sleep analysis, ECG, and stress tracking give you a clear picture of your wellbeing. Built-in GPS accurately "
        "tracks runs, rides, and swims without your phone, while the always-on AMOLED display is bright outdoors and easy to read at a glance. "
        "Notifications, music control, contactless payments, and a robust app ecosystem keep you connected on the go. "
        "VeriCart AI authenticates every unit and ships with full manufacturer warranty."
    ),
    'Men\'s Clothing': (
        "{name} is crafted from premium-quality fabric with a tailored fit and clean finish. Reinforced stitching at stress points "
        "and pre-shrunk material ensure the piece holds its shape wash after wash. Breathable and comfortable for all-day wear, "
        "it transitions easily from casual to smart-casual settings. Each item is inspected and shipped in protective packaging by VeriCart AI, "
        "guaranteed authentic with a 30-day fit and quality guarantee."
    ),
    'Women\'s Clothing': (
        "{name} features a flattering silhouette and is made from soft, breathable fabric that drapes beautifully. "
        "Attention to detail — from lined bodices to reinforced hems and quality stitching — ensures it holds up to regular wear. "
        "Versatile enough to dress up or down, it pairs easily with pieces already in your wardrobe. "
        "VeriCart AI inspects and authenticates every piece and ships with a 30-day fit and quality guarantee."
    ),
    'Shoes': (
        "{name} delivers responsive cushioning and reliable support for everyday wear. A breathable upper keeps feet cool, "
        "while a durable rubber outsole provides confident grip on a variety of surfaces. Reinforced stitching and quality "
        "materials ensure long-lasting wear, and the design transitions easily from casual to active use. "
        "Each pair sold on VeriCart is verified authentic and ships with the original box and full manufacturer warranty."
    ),
    'Furniture': (
        "{name} is built with a solid frame and premium finishes for everyday use. Easy-to-follow assembly instructions "
        "and all hardware are included, and the materials are selected for durability and clean aesthetics. "
        "Thoughtful proportions and a versatile design let it blend into a wide range of interiors. "
        "VeriCart AI inspects and ships each piece with protective packaging and a 30-day quality guarantee."
    ),
    'Kitchenware': (
        "{name} is designed for serious home cooking. Heavy-gauge construction and an even-heating base eliminate hot spots, "
        "while the premium non-stick (or enamel) coating makes cooking and cleaning effortless. The ergonomic handle stays "
        "cool on the stovetop and the tight-fitting lid locks in moisture. Oven- and dishwasher-safe, it is built to become "
        "a daily workhorse in your kitchen. VeriCart AI authenticates every piece and ships in tamper-evident packaging with full warranty."
    ),
    'Bedding & Towels': (
        "{name} is woven from long-staple cotton for a soft, breathable feel that gets better with every wash. "
        "Deep pockets and elasticised edges keep the fitted sheet securely in place, while reinforced hems resist fraying. "
        "Quick-drying, low-lint, and certified free of harmful substances for restful sleep. "
        "VeriCart AI inspects and ships each set with protective packaging and a quality guarantee."
    ),
    'Home Decor': (
        "{name} brings warmth and personality to any room. Thoughtful proportions and quality materials give it a premium look and feel, "
        "and the versatile design complements a wide range of interiors. Easy to set up and built to last, it is a simple way to refresh your space. "
        "VeriCart AI inspects and authenticates every piece and ships with protective packaging and a quality guarantee."
    ),
    'Fitness Equipment': (
        "{name} is built for reliable performance in a home-gym setting. Quality steel or high-density foam construction ensures stability, "
        "and the ergonomic grip or surface stays comfortable through long workouts. Space-saving design and quiet operation make it "
        "ideal for apartments. VeriCart AI authenticates every piece of equipment and ships with full warranty and easy assembly instructions."
    ),
    'Accessories': (
        "{name} is crafted from premium leather (or material) with even stitching, sturdy hardware, and a clean finish. "
        "Generously sized for daily essentials yet compact enough to wear comfortably, it transitions easily from day to evening. "
        "A secure closure and well-organised interior keep your belongings safe and easy to reach. "
        "VeriCart AI authenticates every piece and ships in protective packaging with a quality guarantee."
    ),
    'Electronics & Digital': (
        "{name} combines reliable performance with thoughtful design. Plug-and-play simple to set up, it delivers the features "
        "described and is built with quality components for long service life. Backed by manufacturer warranty and VeriCart AI "
        "authentication, so you can shop with complete confidence."
    ),
    'Stationery & Office': (
        "{name} makes reading and note-taking a pleasure. The high-resolution, anti-glare display is easy on the eyes even in "
        "direct sunlight, and adjustable warm light helps you read comfortably at night. Waterproofing (where applicable), "
        "weeks-long battery life, and seamless library syncing across devices make it the perfect everyday companion. "
        "VeriCart AI authenticates every unit and ships with full manufacturer warranty."
    ),
    'Home & Kitchen': (
        "{name} brings professional-grade cleaning (or cooking) performance into the home. Powerful suction (or even heat distribution), "
        "intuitive controls, and a versatile set of attachments make quick work of everyday tasks. Lightweight, well balanced, and "
        "easy to store. VeriCart AI authenticates every unit and ships in tamper-evident packaging with full manufacturer warranty."
    ),
}


def pick_pool(category: str):
    return POOLS.get(category, DEFAULT_POOL)


def rating_comment(rating: int) -> str:
    return {5: 'Excellent', 4: 'Great', 3: 'Okay', 2: 'Poor', 1: 'Terrible'}[rating]


# ---------------- generate ----------------
print("Querying products...")
out = run("SELECT id, name, category_id, IFNULL((SELECT c.name FROM category c WHERE c.id=p.category_id LIMIT 1),'') FROM product p ORDER BY id;")
products = []
for line in out.strip().splitlines():
    parts = line.split('\t')
    if len(parts) >= 4:
        pid, name, cid, cat = parts[0], parts[1], parts[2], parts[3]
        products.append((int(pid), name, cat))

print(f"Found {len(products)} products.")

next_review_id = REVIEW_ID_START
lines_sql = []
lines_sql.append("USE vericart;")
lines_sql.append(f"-- Auto-generated by backend/seed_full_reviews.py")
lines_sql.append(f"-- Reviews per product: 5-6  |  ~1/3 of products include a bad (rating<=2) comment")
lines_sql.append(f"-- Description: richer, category-aware 'Details' content for every product")
lines_sql.append("")
lines_sql.append("SET NAMES utf8mb4;")
lines_sql.append("")
lines_sql.append(f"DELETE FROM review WHERE id BETWEEN {REVIEW_ID_START} AND {REVIEW_ID_END};")
lines_sql.append("")

# --- reviewer users (distinct names per product) ---
print("Generating fake reviewer users...")
user_rows = []
for uid, name in zip(FAKE_REVIEWER_IDS, REVIEWER_NAMES):
    uname = name.replace(' ', '.').lower()
    email = f"reviewer{uid}@vericart.reviews"
    user_rows.append(f"({uid}, '{uname}', '{email}', '{REVIEWER_HASH}', 'CUSTOMER', 1)")
lines_sql.append(f"DELETE FROM user WHERE id BETWEEN {FAKE_REVIEWER_IDS[0]} AND {FAKE_REVIEWER_IDS[-1] + 100};")
lines_sql.append("INSERT INTO user (id, username, email, password, role, status) VALUES")
lines_sql.append(",\n".join(user_rows) + ";")
lines_sql.append("")

# --- reviews ---
print("Generating reviews...")
review_rows = []
n_with_bad = 0
for (pid, pname, cat) in products:
    pool = pick_pool(cat)
    # Pick 6 reviews. If product id is in "bad" set, force one bad review.
    is_bad_product = (pid % 3 == 0)
    if is_bad_product:
        n_with_bad += 1
        bad_pool = [r for r in pool if r[0] <= 2] or [r for r in pool if r[0] <= 3]
        good_pool = [r for r in pool if r[0] >= 4]
        # 5 good + 1 bad, shuffled
        chosen = random.sample(good_pool, k=min(5, len(good_pool)))
        bad = random.choice(bad_pool) if bad_pool else (2, "Disappointed with the product for the price.")
        chosen.append(bad)
        random.shuffle(chosen)
    else:
        # All positive — pick 6 reviews (with replacement if needed)
        good_pool = [r for r in pool if r[0] >= 4]
        chosen = random.choices(good_pool, k=6)
        # Occasionally drop a 5 to a 4 for realism
        chosen = [(5 if r[0] == 5 and random.random() < 0.4 else r[0], r[1]) for r in chosen]

    base_time = 1700000000  # ~Nov 2023 — converted by MySQL via FROM_UNIXTIME
    for i, (rating, content) in enumerate(chosen[:6]):
        rid = next_review_id
        next_review_id += 1
        user_id = FAKE_REVIEWER_IDS[i % len(FAKE_REVIEWER_IDS)]
        # Stagger createdAt over ~120 days
        offset_days = random.randint(0, 120) + i * 7
        offset_secs = offset_days * 86400 + random.randint(0, 86400)
        ts = base_time + offset_secs
        content_safe = content.replace("'", "''")
        review_rows.append(
            f"({rid},{user_id},{pid},NULL,{rating},'{content_safe}',FROM_UNIXTIME({ts}))"
        )

# Emit in chunks of 1000 rows per INSERT
CHUNK = 500
for i in range(0, len(review_rows), CHUNK):
    chunk = review_rows[i:i+CHUNK]
    lines_sql.append("INSERT INTO review (id, user_id, product_id, order_id, rating, content, created_at) VALUES")
    lines_sql.append(",\n".join(chunk) + ";")
    lines_sql.append("")

print(f"  -> {len(review_rows)} reviews across {len(products)} products ({n_with_bad} with a bad review).")

# --- descriptions ---
print("Generating detailed descriptions...")
desc_updates = []
for (pid, pname, cat) in products:
    tmpl = DESC_TEMPLATES.get(cat, DESC_TEMPLATES['Electronics & Digital'])
    desc = tmpl.format(name=pname)
    # Escape for SQL
    desc_safe = desc.replace("'", "''")
    desc_updates.append(f"UPDATE product SET description = '{desc_safe}' WHERE id = {pid};")

lines_sql.append("-- Update descriptions with richer, category-aware content")
lines_sql.extend(desc_updates)
lines_sql.append("")

# Write file
out_path = os.path.join(os.path.dirname(__file__), 'sql', 'seed-full-data.sql')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines_sql))

print(f"Wrote SQL to {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")
print("Executing SQL against MySQL...")

# Execute via stdin to avoid arg-length limits
with open(out_path, 'rb') as f:
    p = subprocess.run(
        [MYSQL, f'-u{USER}', f'-p{PASS}', DB],
        input=f.read(),
        capture_output=True
    )
    if p.returncode != 0:
        print("STDERR:", p.stderr.decode('utf-8', errors='replace'))
        raise SystemExit(1)
    if p.stderr:
        # warnings are OK
        msg = p.stderr.decode('utf-8', errors='replace').strip()
        if 'Warning' in msg and 'password' in msg.lower():
            pass
        else:
            print("MySQL stderr:", msg)

print("Done.")
print(f"  reviews inserted:        {len(review_rows)}")
print(f"  products with bad review:{n_with_bad}")
print(f"  descriptions updated:    {len(desc_updates)}")