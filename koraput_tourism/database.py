"""
database.py - Database manager and pre-seeded dataset for Koraput Tourism.
Supports multiple image galleries, rich Koraput heritage lore, hotels, and full Admin CRUD.
"""

import sqlite3
import json
import os
from datetime import datetime

try:
    from refiner import TourismContentRefiner
except ImportError:
    from koraput_tourism.refiner import TourismContentRefiner

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "koraput_tourism.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Places table (with image_urls JSON column)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        location TEXT NOT NULL,
        distance_koraput TEXT,
        image_url TEXT,
        image_urls TEXT,
        raw_content TEXT,
        refined_title TEXT,
        tagline TEXT,
        refined_story TEXT,
        highlights TEXT,
        travel_tips TEXT,
        best_season TEXT,
        ideal_duration TEXT,
        entry_fee TEXT,
        timing TEXT,
        rating REAL DEFAULT 4.8,
        featured INTEGER DEFAULT 1,
        created_at TEXT
    )
    """)

    # 2. Hotels & Eco-Stays table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        location TEXT NOT NULL,
        distance_koraput TEXT,
        image_url TEXT,
        image_urls TEXT,
        price_range TEXT,
        raw_content TEXT,
        refined_title TEXT,
        tagline TEXT,
        refined_story TEXT,
        amenities TEXT,
        contact TEXT,
        rating REAL DEFAULT 4.7,
        booking_url TEXT,
        created_at TEXT
    )
    """)

    # 3. Itineraries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itineraries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subtitle TEXT,
        duration TEXT NOT NULL,
        theme TEXT,
        raw_content TEXT,
        refined_story TEXT,
        days TEXT,
        budget TEXT,
        difficulty TEXT,
        featured INTEGER DEFAULT 1,
        created_at TEXT
    )
    """)

    # 4. Culture, Coffee & Famous Things table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS culture (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        raw_notes TEXT,
        refined_article TEXT,
        highlights TEXT,
        image_url TEXT,
        image_urls TEXT,
        created_at TEXT
    )
    """)

    # 5. Reviews table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        place_id INTEGER,
        user_name TEXT,
        rating INTEGER,
        comment TEXT,
        date TEXT
    )
    """)

    # Migrate columns if they don't exist yet
    for table in ["places", "hotels", "culture"]:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [col[1] for col in cursor.fetchall()]
        if "image_urls" not in cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN image_urls TEXT")

    conn.commit()

    # Re-seed if tables empty or migrate missing image_urls
    cursor.execute("SELECT COUNT(*) FROM places")
    if cursor.fetchone()[0] == 0:
        seed_comprehensive_data(conn)
    else:
        # Check if places need image_urls backfilled
        cursor.execute("SELECT id, image_url, image_urls FROM places WHERE image_urls IS NULL OR image_urls = ''")
        rows = cursor.fetchall()
        if rows:
            seed_comprehensive_data(conn, overwrite=True)

    conn.close()

def seed_comprehensive_data(conn, overwrite=False):
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if overwrite:
        cursor.execute("DELETE FROM places")
        cursor.execute("DELETE FROM hotels")
        cursor.execute("DELETE FROM itineraries")
        cursor.execute("DELETE FROM culture")
        conn.commit()

    # 1. SEED PLACES WITH MULTIPLE IMAGES FOR SCROLLING
    places_data = [
        {
            "name": "Deomali Peak",
            "category": "peak",
            "location": "Pottangi Block, Koraput District",
            "distance_koraput": "65 km (approx. 1.5 hrs)",
            "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_content": (
                "deomali highest peak of odisha 1672m elevation near pottangi block. "
                "lush green hills very windy road goes almost till hilltop last 200m walking steps. "
                "best time sunrise sunset rolling clouds feel like heaven. "
                "entry fee 20 rs per person parking available carry jackets cold winds. "
                "tea stalls available at base eco cottages opened recently."
            ),
            "entry_fee": "₹20 per person | ₹50 per vehicle",
            "timing": "05:30 AM - 06:30 PM (Daily)",
            "rating": 4.9,
            "featured": 1
        },
        {
            "name": "Duduma Waterfalls",
            "category": "waterfall",
            "location": "Badigada, Machkund, Koraput",
            "distance_koraput": "70 km (approx. 2 hrs)",
            "image_url": "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1546587348-d12660c30c50?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_content": (
                "duduma waterfall on machkund river boundary of odisha and andhra pradesh. "
                "175 meters 574 feet drop horse tail waterfall very deep canyon gorge. "
                "hydro power plant machkund dam upstream. "
                "around 1000 steep steps down to bottom viewpoint very slippery beware monkeys. "
                "best in monsoon and winter post monsoon rainbow seen in morning mist. "
                "entry fee 20 rs food stalls near parking."
            ),
            "entry_fee": "₹20 per person",
            "timing": "07:00 AM - 05:00 PM (Daily)",
            "rating": 4.8,
            "featured": 1
        },
        {
            "name": "Gupteswar Cave Temple",
            "category": "temple",
            "location": "Jeypore Sub-division, Koraput",
            "distance_koraput": "75 km from Koraput (55 km from Jeypore)",
            "image_url": "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1609766857041-ed402ea8069a?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_content": (
                "gupteswar limestone cave shrine dedicated to lord shiva lingam naturally formed. "
                "surrounded by dense sal forest on the banks of kolab river sabari tributary. "
                "lord rama believed to have worshipped here during exile ramayana connection. "
                "shravan month thousands of bol bam pilgrims visit carrying holy water. "
                "cave is cool inside limestone formations steps lead into inner sanctum. "
                "small shops for prasad pooja items beware of deep river currents."
            ),
            "entry_fee": "Free Entry | ₹50 VIP Darshan during festivals",
            "timing": "06:00 AM - 08:00 PM (Daily)",
            "rating": 4.8,
            "featured": 1
        },
        {
            "name": "Kolab Dam & Reservoir",
            "category": "waterbody",
            "location": "Kolab, Koraput Town Periphery",
            "distance_koraput": "15 km (approx. 25 mins)",
            "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_content": (
                "kolab reservoir hydro electric project on kolab river. "
                "huge blue water lake surrounded by hills botanical garden kolab park. "
                "boating facility available speed boat paddle boat sunset is amazing. "
                "island hillocks inside lake photography favorite spot. "
                "entry 20 rs boating 100-250 rs cafeteria inside garden."
            ),
            "entry_fee": "₹20 entry to Kolab Park | Boating ₹100 - ₹250",
            "timing": "08:00 AM - 06:30 PM (Daily)",
            "rating": 4.7,
            "featured": 1
        },
        {
            "name": "Sabara Srikhetra (Jagannath Temple)",
            "category": "temple",
            "location": "Town Center Hilltop, Koraput",
            "distance_koraput": "2 km (Within town center)",
            "image_url": "https://images.unsplash.com/photo-1609766857041-ed402ea8069a?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1609766857041-ed402ea8069a?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_content": (
                "sabara srikhetra hilltop jagannath temple built in 1972. "
                "highlights tribal sabara origin of lord jagannath equality for all castes tribes. "
                "temple complex has tribal museum displaying ornaments weapons dress of 62 odisha tribes. "
                "peaceful garden view of entire koraput valley rath yatra celebrated grandly. "
                "prasad abadha available noon clean campus no entry fee."
            ),
            "entry_fee": "Free Entry | Tribal Museum: ₹10",
            "timing": "05:00 AM - 12:30 PM & 04:00 PM - 09:00 PM",
            "rating": 4.9,
            "featured": 1
        },
        {
            "name": "Koraput Coffee Research & Plantations",
            "category": "coffee",
            "location": "Landiguda & Machkund Road, Koraput",
            "distance_koraput": "5 km to 20 km",
            "image_url": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1447933601403-0c6688de566e?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_content": (
                "koraput arabica coffee plantations high altitude shade grown under silver oak. "
                "got gi tag geographic indication purely organic tribal farmer cooperatives. "
                "coffee board research center coffee nursery tasting centers in town. "
                "beans harvested dec to feb flowering in march aroma is pleasant. "
                "visit coffee cafes try koraput roasted coffee purchase gift packs."
            ),
            "entry_fee": "Free Visit | Coffee Tour Tasting ₹150",
            "timing": "09:00 AM - 05:30 PM (Closed Sundays)",
            "rating": 4.9,
            "featured": 1
        },
        {
            "name": "Putsil Valley & Doliamba Tableland",
            "category": "peak",
            "location": "Near Semiliguda & Pottangi, Koraput",
            "distance_koraput": "42 km (approx. 1 hr)",
            "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_content": (
                "putsil tableland flat top hill plateau called switzerland of odisha. "
                "meadows grass carpet pine trees clouds float below hill top during morning. "
                "paragliding trials happen here road is newly made good for bikes cars. "
                "best for picnic camping bonfire photography carry snacks no shops on top."
            ),
            "entry_fee": "Free Access",
            "timing": "Open all day | Best 05:30 AM - 05:00 PM",
            "rating": 4.8,
            "featured": 1
        },
        {
            "name": "Rani Duduma Waterfall (Bhatrajora)",
            "category": "waterfall",
            "location": "Nandapur Block, Koraput",
            "distance_koraput": "52 km from Koraput",
            "image_url": "https://images.unsplash.com/photo-1546587348-d12660c30c50?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1546587348-d12660c30c50?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_content": (
                "rani duduma smaller serene sister of duduma waterfall at bhatrajora nandapur. "
                "cascading tier stream clear water forest surroundings peaceful picnic spot. "
                "less crowded than main duduma shallow pools safe for dipping feet. "
                "road passes through tribal villages scenic landscapes carry own food."
            ),
            "entry_fee": "Free Entry",
            "timing": "07:00 AM - 05:30 PM (Daily)",
            "rating": 4.6,
            "featured": 0
        },
        {
            "name": "Kunduli Weekly Tribal Haat",
            "category": "culture",
            "location": "Kunduli, Similiguda Tehsil, NH-26",
            "distance_koraput": "32 km (approx. 45 mins)",
            "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_content": (
                "kunduli friday tribal market biggest weekly haat in south odisha. "
                "paroja gadaba mali tribes gather in colorful traditional dress bead necklaces. "
                "organic hill produce sold vegetables handmade bamboo baskets terracotta pots. "
                "photographers paradise authentic barter culture respect tribal sentiments. "
                "starts early morning 7am winds down by 2pm only on fridays."
            ),
            "entry_fee": "Free Access",
            "timing": "Every Friday: 07:00 AM - 02:00 PM",
            "rating": 4.9,
            "featured": 1
        },
        {
            "name": "Jagannath Sagar Pond",
            "category": "waterbody",
            "location": "Jeypore Town (Historic Koraput)",
            "distance_koraput": "22 km from Koraput",
            "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_content": (
                "huge 25 acre historic pond built by kings of jeypore royal family. "
                "promenade walkway newly beautified musical fountain children play park. "
                "lotus flowers morning walkers sunset reflection of palace ruins. "
                "street food stalls near lake chaat coffee ice cream."
            ),
            "entry_fee": "Free Access",
            "timing": "Open 24 hours | Best during evening strolls",
            "rating": 4.5,
            "featured": 0
        }
    ]

    for p in places_data:
        refined = TourismContentRefiner.refine_content(
            raw_text=p["raw_content"],
            category=p["category"],
            title=p["name"],
            location=p["location"]
        )

        cursor.execute("""
        INSERT INTO places (
            name, category, location, distance_koraput, image_url, image_urls,
            raw_content, refined_title, tagline, refined_story,
            highlights, travel_tips, best_season, ideal_duration,
            entry_fee, timing, rating, featured, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["name"], p["category"], p["location"], p["distance_koraput"], p["image_url"],
            json.dumps(p["image_urls"]), p["raw_content"], refined["refined_title"], refined["tagline"],
            refined["refined_story"], json.dumps(refined["highlights"]), json.dumps(refined["travel_tips"]),
            refined["best_season"], refined["ideal_duration"],
            p["entry_fee"], p["timing"], p["rating"], p["featured"], now
        ))

    # 2. SEED HOTELS & ECO-COTTAGES WITH MULTIPLE IMAGES
    hotels_data = [
        {
            "name": "Deomali Eco Tourism Nature Camp",
            "category": "eco_resort",
            "location": "Foothills of Deomali, Pottangi",
            "distance_koraput": "62 km from Koraput Town",
            "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&q=80"
            ],
            "price_range": "₹2,500 - ₹4,500 / night (Incl. Meals)",
            "contact": "+91 94370 12345 | eco-odisha.gov.in",
            "booking_url": "https://www.ecotourodisha.com",
            "rating": 4.9,
            "raw_content": (
                "odisha tourism eco cottages right under deomali summit. "
                "tented cottages and wooden suites mountain sunrise view directly from bed. "
                "tribal village style food complimentary dinner breakfast bonfires arranged. "
                "stargazing at night crisp chill weather advance booking required online."
            ),
            "amenities": ["Mountain View Balcony", "Complimentary Tribal Meals", "Bonfire Nights", "Stargazing Deck", "Local Guided Treks", "Free Parking"]
        },
        {
            "name": "Kolab Nature Camp & Lakeside Cottages",
            "category": "nature_camp",
            "location": "Kolab Dam Lakeside Promenade",
            "distance_koraput": "16 km from Koraput Town",
            "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80"
            ],
            "price_range": "₹2,000 - ₹3,500 / night",
            "contact": "+91 6852 250100 | kolabtourism@odisha.gov.in",
            "booking_url": "https://www.ecotourodisha.com",
            "rating": 4.7,
            "raw_content": (
                "cottages on the water edge of kolab reservoir lake. "
                "lush botanical gardens birds singing boating dock right outside. "
                "spacious air conditioned rooms delicious fresh river fish and odia thalis. "
                "peaceful family getaway great sunset over water."
            ),
            "amenities": ["Lake View Rooms", "Private Boating Jetty", "Botanical Garden Access", "Multi-cuisine Restaurant", "Kids Play Area", "Wi-Fi"]
        },
        {
            "name": "Chandoori Sai Guest House",
            "category": "homestay",
            "location": "Ghatgaon Village, Koraput District",
            "distance_koraput": "48 km from Koraput",
            "image_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80"
            ],
            "price_range": "₹5,000 - ₹8,000 / night (Boutique Heritage)",
            "contact": "+91 94371 88990 | chandoorisai.com",
            "booking_url": "http://chandoorisai.com",
            "rating": 4.9,
            "raw_content": (
                "unique architectural mud and terracotta eco luxury guest house by mark herten. "
                "located inside peaceful tribal pottery village. "
                "terracotta floor tiles hand woven fabrics gourmet organic dining experience. "
                "guided tribal walks to nearby bantalbiri and weekly haats. cultural delight."
            ),
            "amenities": ["Artisan Architecture", "Gourmet Organic Dining", "Cultural Excursions", "Pottery Workshops", "Library Lounge", "Bespoke Hospitality"]
        },
        {
            "name": "Hotel Lemon Castle",
            "category": "luxury",
            "location": "Main Road, Koraput Town",
            "distance_koraput": "0.5 km (Town Center)",
            "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80"
            ],
            "price_range": "₹2,200 - ₹4,000 / night",
            "contact": "+91 6852 251500 | reservations@lemoncastle.in",
            "booking_url": "https://lemoncastle.in",
            "rating": 4.6,
            "raw_content": (
                "modern town hotel with conference halls banquet and multi cuisine restaurant. "
                "very close to bus stand and sabara srikhetra temple. "
                "clean rooms high speed wifi 24x7 hot water taxi tour desk available. "
                "convenient central base for visiting waterfalls and peaks."
            ),
            "amenities": ["High-Speed Wi-Fi", "In-house Multi-Cuisine Restaurant", "Tour Desk & Car Rental", "24x7 Room Service", "Conference Hall", "Elevator Access"]
        }
    ]

    for h in hotels_data:
        refined = TourismContentRefiner.refine_content(
            raw_text=h["raw_content"],
            category="hotel",
            title=h["name"],
            location=h["location"]
        )

        cursor.execute("""
        INSERT INTO hotels (
            name, category, location, distance_koraput, image_url, image_urls,
            price_range, raw_content, refined_title, tagline,
            refined_story, amenities, contact, rating, booking_url, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            h["name"], h["category"], h["location"], h["distance_koraput"], h["image_url"],
            json.dumps(h["image_urls"]), h["price_range"], h["raw_content"], refined["refined_title"],
            refined["tagline"], refined["refined_story"], json.dumps(h["amenities"]),
            h["contact"], h["rating"], h["booking_url"], now
        ))

    # 3. SEED ITINERARIES
    itineraries_data = [
        {
            "title": "Weekend Misty Hills & Coffee Trail",
            "subtitle": "The quintessential Koraput immersion for short getaways",
            "duration": "2 Days / 1 Night",
            "theme": "Highland Peaks, Coffee Aromas & Serene Lakes",
            "budget": "₹3,500 - ₹6,000 per person",
            "difficulty": "Easy to Moderate",
            "raw_content": (
                "day 1 morning reach koraput town visit sabara srikhetra temple then visit coffee plantations. "
                "afternoon lunch try local thali head to kolab dam for sunset and boating stay overnight at kolab nature camp. "
                "day 2 early morning 5am drive to deomali peak for sunrise clouds. visit putsil valley lunch on way return."
            ),
            "days": [
                {
                    "day": 1,
                    "title": "Spiritual Roots, Coffee Aromas & Lakeside Sunset",
                    "schedule": [
                        {"time": "08:30 AM", "activity": "Arrive in Koraput, check-in, and savor fresh Koraput Arabica Coffee at a town cafe"},
                        {"time": "10:00 AM", "activity": "Seek blessings at Sabara Srikhetra (Hilltop Jagannath Temple) and explore the Tribal Museum"},
                        {"time": "12:30 PM", "activity": "Tour the shade-grown Koraput Coffee plantations along Machkund Road"},
                        {"time": "02:00 PM", "activity": "Traditional Odia tribal lunch featuring Mandia Pej and regional curries"},
                        {"time": "04:00 PM", "activity": "Leisurely speed boating and sunset photography at Kolab Reservoir & Botanical Garden"},
                        {"time": "08:00 PM", "activity": "Lakeside bonfire and overnight stay at Kolab Nature Camp"}
                    ]
                },
                {
                    "day": 2,
                    "title": "Conquering Deomali & Swiss-like Valley Meadows",
                    "schedule": [
                        {"time": "05:00 AM", "activity": "Dawn departure toward Deomali Peak (Odisha's highest point at 1,672m)"},
                        {"time": "06:30 AM", "activity": "Witness ethereal sea-of-clouds sunrise from the summit ridge"},
                        {"time": "09:30 AM", "activity": "Warm country breakfast at Pottangi foothill cafe"},
                        {"time": "11:30 AM", "activity": "Explore Putsil Tableland meadows, breezy cliffs, and pine groves"},
                        {"time": "02:30 PM", "activity": "Scenic drive back to Koraput with mementos of organic coffee and tribal handicrafts"}
                    ]
                }
            ]
        },
        {
            "title": "Grand Koraput Odyssey: Peaks, Waterfalls & Tribal Heartlands",
            "subtitle": "A deep 3-day expedition into nature, folklore, and tribal life",
            "duration": "3 Days / 2 Nights",
            "theme": "Comprehensive Explorer: Waterfalls, Caves, Weekly Haat & Peaks",
            "budget": "₹6,500 - ₹11,000 per person",
            "difficulty": "Moderate Trekking",
            "raw_content": (
                "day 1 arrival koraput visit jagannath temple drive to deomali sunset stay at deomali eco cottages. "
                "day 2 morning putsil valley then proceed to roaring duduma waterfall machkund canyon gorge. "
                "day 3 gupteswar cave temple on kolab river banks kunduli tribal market friday evening departure."
            ),
            "days": [
                {
                    "day": 1,
                    "title": "Town Heritage & Sunset on Odisha's Roof",
                    "schedule": [
                        {"time": "09:00 AM", "activity": "Arrival, briefing, and pilgrimage to Sabara Srikhetra"},
                        {"time": "11:30 AM", "activity": "Koraput Coffee Board tasting session and processing insight"},
                        {"time": "03:00 PM", "activity": "Ascend Deomali Peak; check-in at Deomali Eco Cottages"},
                        {"time": "05:30 PM", "activity": "Breathtaking 360-degree sunset followed by stargazing and tribal dinner"}
                    ]
                },
                {
                    "day": 2,
                    "title": "Machkund Canyon & Roaring Duduma",
                    "schedule": [
                        {"time": "07:30 AM", "activity": "Scenic mountain highway drive toward Machkund River"},
                        {"time": "10:30 AM", "activity": "Marvel at the 175-meter drop of Duduma Waterfalls and canyon rainbow mists"},
                        {"time": "02:00 PM", "activity": "Picnic lunch by the upper Machkund stream"},
                        {"time": "04:30 PM", "activity": "Visit Rani Duduma cascaded falls in Nandapur"},
                        {"time": "07:30 PM", "activity": "Overnight in Jeypore/Koraput with cultural Dhemsa folk dance presentation"}
                    ]
                },
                {
                    "day": 3,
                    "title": "Mystic Caves & Vibrant Indigenous Market",
                    "schedule": [
                        {"time": "07:30 AM", "activity": "Journey through sal forests to ancient Gupteswar Cave Temple"},
                        {"time": "09:30 AM", "activity": "Explore natural limestone stalagmite sanctum on the banks of Kolab river"},
                        {"time": "01:00 PM", "activity": "Immerse in Kunduli Tribal Haat; meet Gadaba and Paroja artisans"},
                        {"time": "04:30 PM", "activity": "Farewell brew of freshly ground coffee and departure with unforgettable memories"}
                    ]
                }
            ]
        }
    ]

    for it in itineraries_data:
        refined = TourismContentRefiner.refine_content(
            raw_text=it["raw_content"],
            category="culture",
            title=it["title"]
        )

        cursor.execute("""
        INSERT INTO itineraries (
            title, subtitle, duration, theme, raw_content,
            refined_story, days, budget, difficulty, featured, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            it["title"], it["subtitle"], it["duration"], it["theme"],
            it["raw_content"], refined["refined_story"], json.dumps(it["days"]),
            it["budget"], it["difficulty"], 1, now
        ))

    # 4. SEED CULTURE, COFFEE & FAMOUS THINGS
    culture_articles = [
        {
            "title": "The Saga of Koraput Coffee: A Golden Bean Revolution",
            "category": "koraput_coffee",
            "image_url": "https://images.unsplash.com/photo-1447933601403-0c6688de566e?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1447933601403-0c6688de566e?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_notes": (
                "introduced in 1930s by maharaja of jeypore ram chandra deb. "
                "grown at 3000 feet elevation in shade of silver oak and jackfruit trees. "
                "100 percent arabica organic certified got geographical indication tag. "
                "empowered thousands of tribal women farmers and coffee cooperatives. "
                "noted for mild acidity sweet chocolate caramel undertones and rich aroma."
            ),
            "highlights": [
                "100% shade-grown Arabica coffee thriving at altitudes between 900m and 1,200m in the Eastern Ghats",
                "Awarded official Geographical Indication (GI Tag) certifying its unique soil-climate profile",
                "Fair-trade tribal cooperatives provide economic empowerment to over 3,000 indigenous farm families",
                "Cup profile: smooth body, delicate floral aroma, subtle hints of toasted almond, dark chocolate, and spice"
            ]
        },
        {
            "title": "The Indigenous Soul: Paroja, Gadaba, Bonda & Kondh Tribes",
            "category": "tribal_heritage",
            "image_url": "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_notes": (
                "koraput is home to diverse indigenous tribal communities living in peace with nature for millennia. "
                "gadaba women wear heavy brass neck rings called khagla and kerang handwoven clothes. "
                "bonda tribe considered one of oldest surviving primitive tribes in world living on high hills. "
                "parojas are agrarian dancers and poets of the hills. profound animist traditions respect for forests and rivers."
            ),
            "highlights": [
                "Over 62 distinct indigenous communities, each preserving distinct dialects, weaving traditions, and folklore",
                "Gadaba tribe renowned for 'Gotr' ancestral peace ceremonies and circular Kerang hand-loomed attire",
                "Bonda (Remo) tribe residing in isolated highlands, famous for bead regalia and ancient Austroasiatic roots",
                "Strict community eco-ethics: sustainable forest foraging without degrading sacred sal and banyan groves"
            ]
        },
        {
            "title": "Dhemsa: The Hypnotic Tribal Folk Dance of Harmony",
            "category": "dance_music",
            "image_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_notes": (
                "dhemsa is traditional folk dance of koraput tribes danced linking hands or shoulders in long curved chains. "
                "music played on dhol tamak mohuri wind flute and changu drums. "
                "rhythm starts slow then builds up into ecstatic energetic foot movements. "
                "danced during weddings festivals harvest celebrations all villagers dance together no barrier of age or status."
            ),
            "highlights": [
                "Performed with dancers interlocking arms in synchrony, symbolizing unbroken community unity",
                "Musical ensemble led by the soulful Mohuri (reed oboe) and pounding resonance of the Dholak and Tamak",
                "Variations include the nimble 'Kunda Dhemsa', 'Boda Dhemsa', and playful animal mimicry steps",
                "Visitors are warmly invited to join the chain during village festivals and cultural evenings"
            ]
        },
        {
            "title": "Famous Delicacies & Handicrafts: Mandia Pej, Kotpad Dye & Terracotta",
            "category": "handicrafts_cuisine",
            "image_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_notes": (
                "famous crafts include kotpad handloom woven with natural madder tree root dye first gi tag from odisha. "
                "ghatgaon terracotta pottery handmade roof tiles water jugs. "
                "dhokra lost wax bell metal craft made by local artisans. "
                "food specialties include mandia pej finger millet gruel cooling in summer bamboo shoot mutton curry wild forest honey."
            ),
            "highlights": [
                "Kotpad Handloom: Odisha's very first GI-tagged craft, dyed with natural Aal (Madder) roots by the Mirgan community",
                "Ghatgaon Terracotta: Renowned pottery village crafting unglazed earthware and intricate decorative tiles",
                "Tribal Cuisine: Mandia Pej (millet beverage), Bamboo shoot curries, and roasted country chicken",
                "Forest Delicacies: Raw wild floral honey harvested from Eastern Ghats sal and mahua canopies"
            ]
        },
        {
            "title": "Parab Festival: The Grand Cultural Confluence",
            "category": "festivals",
            "image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80",
            "image_urls": [
                "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=80"
            ],
            "raw_notes": (
                "annual cultural carnival organized in november by district administration koraput. "
                "tribal sports archery competitions traditional music craft fairs food festival. "
                "starts with torch ceremony from goddess taratarini or sacred hills. "
                "thousands of visitors come from all over india to witness pristine tribal art."
            ),
            "highlights": [
                "Celebrated annually across November/December as South Odisha's preeminent cultural festival",
                "Traditional sporting spectacles including tribal archery, kabaddi, and indigenous boat racing",
                "Grand handicraft haat showcasing Dhokra bell metal casting, terracotta pottery, and bamboo crafts",
                "Evenings lit by performances from regional and national folk troupes under the starlit sky"
            ]
        }
    ]

    for c in culture_articles:
        refined = TourismContentRefiner.refine_content(
            raw_text=c["raw_notes"],
            category="culture",
            title=c["title"]
        )

        cursor.execute("""
        INSERT INTO culture (
            title, category, raw_notes, refined_article, highlights, image_url, image_urls, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c["title"], c["category"], c["raw_notes"], refined["refined_story"],
            json.dumps(c["highlights"]), c["image_url"], json.dumps(c["image_urls"]), now
        ))

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database updated and backfilled with multiple images and rich Koraput content!")
