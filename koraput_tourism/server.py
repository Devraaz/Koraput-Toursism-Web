"""
server.py - High-Performance Tornado Web Application & REST API
for Koraput Tourism ("Heaven of Odisha").
Features:
- Dedicated Admin Portal (/admin/login and /admin)
- Multi-Image Card Galleries
- Dedicated Hotel Management
- Culture, Coffee & Famous Things Manager
- Kora Mascot & Database-Grounded AI Tour Guide (/api/ai/ask)
"""

import os
import sys
import json
import sqlite3
import tornado.ioloop
import tornado.web
from datetime import datetime

try:
    from database import get_db, init_db
    from refiner import TourismContentRefiner
    from ai_guide import KoraAIAssistant
except ImportError:
    from koraput_tourism.database import get_db, init_db
    from koraput_tourism.refiner import TourismContentRefiner
    from koraput_tourism.ai_guide import KoraAIAssistant

ADMIN_TOKEN = "koraput-admin-auth-token-2026"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization, x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def get_json_body(self):
        try:
            return json.loads(self.request.body.decode('utf-8'))
        except Exception:
            return {}

    def json_response(self, data, status_code=200):
        self.set_status(status_code)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.write(json.dumps(data, ensure_ascii=False))


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class AdminLoginViewHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("admin_login.html")


class AdminDashboardViewHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("admin_dashboard.html")


class AuthHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if (username.lower() == "admin" and password == "koraput2026") or (data.get("quick_admin") is True):
            self.json_response({
                "success": True,
                "token": ADMIN_TOKEN,
                "role": "admin",
                "name": "District Tourism Officer",
                "message": "Welcome to Koraput Tourism Administration Portal."
            })
        else:
            self.json_response({
                "success": False,
                "message": "Invalid credentials. Use 'admin' and 'koraput2026'."
            }, 401)


class AskKoraAIHandler(BaseHandler):
    """
    AI Tour Guide mode: Answers any question about Koraput based on real database records.
    """
    def post(self):
        data = self.get_json_body()
        query = data.get("query", "").strip()
        if not query:
            self.json_response({"error": "Query cannot be empty."}, 400)
            return

        conn = get_db()
        try:
            response = KoraAIAssistant.answer_query(query, conn)
            self.json_response({
                "success": True,
                "query": query,
                "answer": response["answer"],
                "suggestions": response.get("suggestions", [])
            })
        finally:
            conn.close()


class RefineHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        raw_content = data.get("raw_content", "").strip()
        category = data.get("category", "place")
        title = data.get("title", "")
        location = data.get("location", "")

        if not raw_content:
            self.json_response({"error": "raw_content is required to generate refinement."}, 400)
            return

        refined = TourismContentRefiner.refine_content(
            raw_text=raw_content,
            category=category,
            title=title,
            location=location
        )

        self.json_response({
            "success": True,
            "raw_input": raw_content,
            "refined": refined
        })


def parse_image_urls(raw_urls, single_url=""):
    """Helper to ensure a clean list of multiple image URLs"""
    urls = []
    if isinstance(raw_urls, list):
        urls = [u.strip() for u in raw_urls if u and isinstance(u, str) and u.strip()]
    elif isinstance(raw_urls, str) and raw_urls.strip():
        try:
            parsed = json.loads(raw_urls)
            if isinstance(parsed, list):
                urls = [u.strip() for u in parsed if u and isinstance(u, str) and u.strip()]
        except Exception:
            urls = [u.strip() for u in raw_urls.replace('\r', '\n').split('\n') if u.strip()]
            if not urls:
                urls = [u.strip() for u in raw_urls.split(',') if u.strip()]

    if not urls and single_url and single_url.strip():
        urls = [single_url.strip()]

    if not urls:
        urls = ["https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80"]

    return urls


class PlacesHandler(BaseHandler):
    def get(self):
        category = self.get_argument("category", None)
        search = self.get_argument("search", None)

        conn = get_db()
        cursor = conn.cursor()

        query = "SELECT * FROM places WHERE 1=1"
        params = []

        if category and category != "all":
            query += " AND category = ?"
            params.append(category)

        if search:
            search_pattern = f"%{search.strip()}%"
            query += " AND (name LIKE ? OR location LIKE ? OR raw_content LIKE ? OR refined_story LIKE ?)"
            params.extend([search_pattern, search_pattern, search_pattern, search_pattern])

        query += " ORDER BY featured DESC, rating DESC, id ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        places = []
        for r in rows:
            item = dict(r)
            try:
                item["highlights"] = json.loads(item["highlights"]) if item["highlights"] else []
            except Exception:
                item["highlights"] = []
            try:
                item["travel_tips"] = json.loads(item["travel_tips"]) if item["travel_tips"] else []
            except Exception:
                item["travel_tips"] = []
            try:
                item["image_urls"] = json.loads(item["image_urls"]) if item["image_urls"] else [item["image_url"]]
            except Exception:
                item["image_urls"] = [item["image_url"]] if item.get("image_url") else []
            places.append(item)

        conn.close()
        self.json_response({"success": True, "count": len(places), "places": places})

    def post(self):
        data = self.get_json_body()
        name = data.get("name", "").strip()
        category = data.get("category", "peak")
        location = data.get("location", "Koraput District").strip()
        distance = data.get("distance_koraput", "N/A").strip()
        raw_images = data.get("image_urls") or data.get("image_url")
        image_urls_list = parse_image_urls(raw_images, data.get("image_url", ""))
        primary_image = image_urls_list[0]

        raw_content = data.get("raw_content", "").strip()
        entry_fee = data.get("entry_fee", "Free Entry").strip()
        timing = data.get("timing", "06:00 AM - 06:00 PM").strip()
        rating = float(data.get("rating", 4.8))

        if not name or not raw_content:
            self.json_response({"error": "Name and raw_content are mandatory fields."}, 400)
            return

        refined = TourismContentRefiner.refine_content(
            raw_text=raw_content,
            category=category,
            title=name,
            location=location
        )

        refined_title = data.get("refined_title") or refined["refined_title"]
        tagline = data.get("tagline") or refined["tagline"]
        refined_story = data.get("refined_story") or refined["refined_story"]
        highlights = data.get("highlights") or refined["highlights"]
        travel_tips = data.get("travel_tips") or refined["travel_tips"]
        best_season = data.get("best_season") or refined["best_season"]
        ideal_duration = data.get("ideal_duration") or refined["ideal_duration"]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO places (
            name, category, location, distance_koraput, image_url, image_urls,
            raw_content, refined_title, tagline, refined_story,
            highlights, travel_tips, best_season, ideal_duration,
            entry_fee, timing, rating, featured, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, category, location, distance, primary_image, json.dumps(image_urls_list),
            raw_content, refined_title, tagline, refined_story,
            json.dumps(highlights), json.dumps(travel_tips),
            best_season, ideal_duration, entry_fee, timing, rating, 1, now
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        self.json_response({
            "success": True,
            "id": new_id,
            "message": f"'{name}' posted successfully with multiple images and AI refinement!",
            "refined": refined
        }, 201)


class SinglePlaceHandler(BaseHandler):
    def get(self, place_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM places WHERE id = ?", (place_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            self.json_response({"error": "Place not found."}, 404)
            return

        item = dict(row)
        try:
            item["highlights"] = json.loads(item["highlights"]) if item["highlights"] else []
        except Exception:
            item["highlights"] = []
        try:
            item["travel_tips"] = json.loads(item["travel_tips"]) if item["travel_tips"] else []
        except Exception:
            item["travel_tips"] = []
        try:
            item["image_urls"] = json.loads(item["image_urls"]) if item["image_urls"] else [item["image_url"]]
        except Exception:
            item["image_urls"] = [item["image_url"]] if item.get("image_url") else []

        self.json_response({"success": True, "place": item})

    def delete(self, place_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM places WHERE id = ?", (place_id,))
        conn.commit()
        conn.close()
        self.json_response({"success": True, "message": "Place deleted successfully."})


class HotelsHandler(BaseHandler):
    def get(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hotels ORDER BY rating DESC, id ASC")
        rows = cursor.fetchall()
        hotels = []
        for r in rows:
            item = dict(r)
            try:
                item["amenities"] = json.loads(item["amenities"]) if item["amenities"] else []
            except Exception:
                item["amenities"] = []
            try:
                item["image_urls"] = json.loads(item["image_urls"]) if item["image_urls"] else [item["image_url"]]
            except Exception:
                item["image_urls"] = [item["image_url"]] if item.get("image_url") else []
            hotels.append(item)
        conn.close()
        self.json_response({"success": True, "count": len(hotels), "hotels": hotels})

    def post(self):
        data = self.get_json_body()
        name = data.get("name", "").strip()
        category = data.get("category", "eco_resort")
        location = data.get("location", "Koraput District").strip()
        distance = data.get("distance_koraput", "10 km").strip()
        price = data.get("price_range", "₹2,500 / night").strip()
        raw = data.get("raw_content", "").strip()
        amenities = data.get("amenities", ["Mountain View", "Restaurant", "Wi-Fi"])
        contact = data.get("contact", "+91 94370 00000").strip()
        booking_url = data.get("booking_url", "").strip()

        raw_images = data.get("image_urls") or data.get("image_url")
        image_urls_list = parse_image_urls(raw_images, data.get("image_url", ""))
        primary_image = image_urls_list[0]

        if not name or not raw:
            self.json_response({"error": "Hotel name and raw content are required."}, 400)
            return

        refined = TourismContentRefiner.refine_content(raw, category="hotel", title=name, location=location)

        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO hotels (
            name, category, location, distance_koraput, image_url, image_urls,
            price_range, raw_content, refined_title, tagline,
            refined_story, amenities, contact, rating, booking_url, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, category, location, distance, primary_image, json.dumps(image_urls_list),
            price, raw, refined["refined_title"], refined["tagline"],
            refined["refined_story"], json.dumps(amenities), contact, 4.8, booking_url, now
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        self.json_response({"success": True, "id": new_id, "message": "Hotel listed with refined narrative!"}, 201)


class SingleHotelHandler(BaseHandler):
    def delete(self, hotel_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hotels WHERE id = ?", (hotel_id,))
        conn.commit()
        conn.close()
        self.json_response({"success": True, "message": "Hotel deleted successfully."})


class CultureHandler(BaseHandler):
    def get(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM culture ORDER BY id ASC")
        rows = cursor.fetchall()
        culture_list = []
        for r in rows:
            item = dict(r)
            try:
                item["highlights"] = json.loads(item["highlights"]) if item["highlights"] else []
            except Exception:
                item["highlights"] = []
            try:
                item["image_urls"] = json.loads(item["image_urls"]) if item["image_urls"] else [item["image_url"]]
            except Exception:
                item["image_urls"] = [item["image_url"]] if item.get("image_url") else []
            culture_list.append(item)
        conn.close()
        self.json_response({"success": True, "culture": culture_list})

    def post(self):
        data = self.get_json_body()
        title = data.get("title", "").strip()
        category = data.get("category", "tribal_heritage").strip()
        raw_notes = data.get("raw_notes", "").strip()
        raw_images = data.get("image_urls") or data.get("image_url")
        image_urls_list = parse_image_urls(raw_images, data.get("image_url", ""))
        primary_image = image_urls_list[0]

        if not title or not raw_notes:
            self.json_response({"error": "Title and raw notes are required."}, 400)
            return

        refined = TourismContentRefiner.refine_content(raw_notes, category="culture", title=title)
        highlights = data.get("highlights") or refined["highlights"]

        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO culture (
            title, category, raw_notes, refined_article, highlights, image_url, image_urls, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, category, raw_notes, refined["refined_story"],
            json.dumps(highlights), primary_image, json.dumps(image_urls_list), now
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        self.json_response({"success": True, "id": new_id, "message": "Cultural article created and refined!"}, 201)


class SingleCultureHandler(BaseHandler):
    def delete(self, culture_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM culture WHERE id = ?", (culture_id,))
        conn.commit()
        conn.close()
        self.json_response({"success": True, "message": "Cultural item deleted successfully."})


class ItinerariesHandler(BaseHandler):
    def get(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM itineraries ORDER BY id ASC")
        rows = cursor.fetchall()
        itineraries = []
        for r in rows:
            item = dict(r)
            try:
                item["days"] = json.loads(item["days"]) if item["days"] else []
            except Exception:
                item["days"] = []
            itineraries.append(item)
        conn.close()
        self.json_response({"success": True, "count": len(itineraries), "itineraries": itineraries})


class StatsHandler(BaseHandler):
    def get(self):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM places")
        total_places = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM places WHERE category = 'waterfall'")
        waterfalls = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM places WHERE category = 'temple'")
        temples = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM places WHERE category = 'peak'")
        peaks = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM hotels")
        hotels = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM itineraries")
        itineraries = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM culture")
        culture_count = cursor.fetchone()[0]

        conn.close()

        self.json_response({
            "success": True,
            "stats": {
                "total_places": total_places,
                "waterfalls": waterfalls,
                "temples": temples,
                "peaks": peaks,
                "hotels": hotels,
                "itineraries": itineraries,
                "culture_count": culture_count,
                "district": "Koraput, Odisha",
                "elevation": "1672m (Deomali Peak)",
                "specialty": "Koraput GI Arabica Coffee & Living Tribal Lore"
            }
        })


def make_app():
    init_db()

    settings = {
        "template_path": TEMPLATES_DIR,
        "static_path": STATIC_DIR,
        "debug": False,
        "autoreload": False
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/admin/login", AdminLoginViewHandler),
        (r"/admin", AdminDashboardViewHandler),
        (r"/api/auth/login", AuthHandler),
        (r"/api/ai/ask", AskKoraAIHandler),
        (r"/api/refine", RefineHandler),
        (r"/api/places", PlacesHandler),
        (r"/api/places/([0-9]+)", SinglePlaceHandler),
        (r"/api/hotels", HotelsHandler),
        (r"/api/hotels/([0-9]+)", SingleHotelHandler),
        (r"/api/culture", CultureHandler),
        (r"/api/culture/([0-9]+)", SingleCultureHandler),
        (r"/api/itineraries", ItinerariesHandler),
        (r"/api/stats", StatsHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": STATIC_DIR}),
    ], **settings)


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    app = make_app()
    app.listen(port)
    print(f"============================================================")
    print(f"  KORAPUT TOURISM APPLICATION RUNNING (HEAVEN OF ODISHA)")
    print(f"  Public Portal:      http://localhost:{port}")
    print(f"  Dedicated Admin:    http://localhost:{port}/admin/login")
    print(f"  Mascot:             Kora - The Spirit of Koraput")
    print(f"  AI Mode Enabled:    Ask Kora (Grounded on Tourism Database)")
    print(f"============================================================")
    tornado.ioloop.IOLoop.current().start()
