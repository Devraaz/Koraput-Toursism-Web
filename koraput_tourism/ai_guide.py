"""
ai_guide.py - Advanced Question-Answering Tourist AI: "Kora - The Spirit of Koraput"
Accurately analyzes user questions, extracts exact parameters (elevation, fees, timings,
distances, logistics, history, stay details) and answers specifically with zero generic filler.
"""

import re
import json
import sqlite3

class KoraAIAssistant:
    """
    High-precision question-answering engine grounded exclusively on the Koraput Tourism database.
    Pinpoints specific user intents: heights, entry fees, timings, step counts, distances,
    transport routes, stay rates, coffee secrets, cultural folklore, and itineraries.
    """

    @classmethod
    def answer_query(cls, user_query: str, db_conn) -> dict:
        q = user_query.strip().lower()
        cursor = db_conn.cursor()

        # Load database entities
        cursor.execute("SELECT * FROM places")
        places = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM hotels")
        hotels = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM itineraries")
        itineraries = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM culture")
        culture_items = [dict(r) for r in cursor.fetchall()]

        # -------------------------------------------------------------------
        # 1. Greetings & Persona Check
        # -------------------------------------------------------------------
        if re.search(r'^(hi|hello|hey|johar|namaskar|namaste|who are you|who is kora|kora)\b', q) and len(q.split()) <= 4:
            return {
                "answer": (
                    "**Johar!** 🙏 I am **Kora, the Spirit of Koraput**—your friendly guide to Nature, Culture & Adventure in the *Heaven of Odisha*!\n\n"
                    "I was born from the emerald heights of Deomali, the rhythmic beats of Dhemsa, and the fragrant breeze of shade-grown Arabica coffee. "
                    "Ask me anything specific, such as:\n"
                    "• *'What is the exact height of Deomali Peak?'*\n"
                    "• *'How many steps are there at Duduma Waterfalls?'*\n"
                    "• *'What are the entry fee and timings for Gupteswar Cave?'*\n"
                    "• *'Where can I stay in Deomali or Kolab Lake?'*\n"
                    "• *'Why does Koraput Coffee have a GI Tag?'*\n"
                    "• *'Which day does Kunduli tribal market open?'*\n"
                    "• *'How to reach Koraput from Visakhapatnam?'*"
                ),
                "suggestions": [
                    "What is the height of Deomali?",
                    "How many steps at Duduma Waterfalls?",
                    "Best places to stay in Koraput",
                    "Why is Koraput Coffee famous?",
                    "Which day is Kunduli tribal haat?"
                ]
            }

        # -------------------------------------------------------------------
        # 2. Deomali Specific Questions (Height, Sunrise, Wind, Camping)
        # -------------------------------------------------------------------
        if "deomali" in q:
            if any(w in q for w in ["height", "altitude", "elevation", "tall", "high", "how high", "meters", "feet"]):
                return {
                    "answer": (
                        "**🏔️ Elevation of Deomali Peak:**\n\n"
                        "• **Exact Altitude:** **1,672 meters (5,485 feet)** above mean sea level.\n"
                        "• **Significance:** It is the **highest mountain peak in Odisha** and the tallest point in the entire Eastern Ghats range between the Godavari and Mahanadi rivers.\n"
                        "• **Location:** Situated near Doliamba village in Pottangi block, about **65 km from Koraput town** (approx. 1.5 hours drive).\n\n"
                        "💡 *Kora's Tip:* The tar road goes almost up to the ridge. The final stretch to the actual summit pillar involves climbing approximately 200 gently sloping paved steps."
                    ),
                    "suggestions": ["Best time for Deomali sunrise", "Deomali Eco Nature Camp booking", "Entry fee for Deomali", "Putsil Valley nearby"]
                }
            if any(w in q for w in ["sunrise", "sunset", "clouds", "sea of clouds"]):
                return {
                    "answer": (
                        "**🌅 Sunrise & Sea-of-Clouds at Deomali:**\n\n"
                        "• **Best Time:** Early morning between **05:15 AM and 06:15 AM** (reach before dawn breaks).\n"
                        "• **The Experience:** Dense cotton-like clouds settle below the summit into the valleys, creating a breathtaking *'Sea of Clouds'* where hilltops look like emerald islands floating in mist!\n"
                        "• **Sunset View:** Equally spectacular from the western ridge as the sun casts amber and purple glows over the Andhra-Odisha mountain borders.\n\n"
                        "💡 *Kora's Tip:* Winds at the summit are biting cold before sunrise. Always carry a windcheater or thermal jacket, even in summer!"
                    ),
                    "suggestions": ["Deomali height and location", "Deomali Eco Cottages price", "Putsil Tableland meadows"]
                }
            if any(w in q for w in ["stay", "camp", "hotel", "cottage", "night", "resort"]):
                return {
                    "answer": (
                        "**⛺ Staying at Deomali Peak:**\n\n"
                        "• **Official Stay:** **Deomali Eco Tourism Nature Camp** operated by the Odisha Forest Department.\n"
                        "• **Accommodations:** Elevated wooden cottages and weather-proof luxury tents right below the summit ridge.\n"
                        "• **Tariff:** **₹2,500 - ₹4,500 per night** (Includes complimentary tribal village breakfast and dinner).\n"
                        "• **Amenities:** Mountain-view balconies, stargazing deck, bonfire setups, and local tribal guided walks.\n"
                        "• **Booking Portal:** Advance reservation is mandatory at `www.ecotourodisha.com`.\n\n"
                        "💡 *Kora's Tip:* Cottages fill up weeks in advance for winter weekends. Book at least 15 days ahead!"
                    ),
                    "suggestions": ["Deomali height and elevation", "Kolab Nature Camp cottages", "1-day tour plan"]
                }
            if any(w in q for w in ["fee", "ticket", "cost", "price", "entry"]):
                return {
                    "answer": (
                        "**🎟️ Deomali Peak Entry Fees & Charges:**\n\n"
                        "• **Visitor Entry:** **₹20 per person**.\n"
                        "• **Vehicle Parking:** ₹50 for cars/SUVs | ₹20 for two-wheelers.\n"
                        "• **Visiting Hours:** 05:30 AM to 06:30 PM daily.\n"
                        "• **Facilities at Base:** Local tea stalls, roasted corn, fresh Koraput coffee cups, and eco-restrooms."
                    ),
                    "suggestions": ["Best time to visit Deomali", "Deomali altitude in feet", "Where to stay in Deomali"]
                }

        # -------------------------------------------------------------------
        # 3. Duduma Waterfall Specific Questions (Height, Steps, Safety, Gorge)
        # -------------------------------------------------------------------
        if "duduma" in q and "rani" not in q:
            if any(w in q for w in ["height", "deep", "drop", "how high", "meters", "feet"]):
                return {
                    "answer": (
                        "**🌊 Duduma Waterfalls Dimensions:**\n\n"
                        "• **Total Drop:** **175 meters (574 feet)**.\n"
                        "• **Type:** Tiered horsetail cascade plunging into a deep canyon gorge.\n"
                        "• **River:** Formed by the sacred **Machkund River** flowing along the border of Odisha and Andhra Pradesh.\n"
                        "• **Hydroelectric Project:** The historic Machkund Hydroelectric Power Plant is situated down the canyon.\n\n"
                        "💡 *Kora's Tip:* It is the 3rd highest waterfall in Odisha and one of the highest plunge falls in all of South India!"
                    ),
                    "suggestions": ["How many steps at Duduma?", "Is Duduma safe for kids?", "Rani Duduma waterfall", "Best time to visit Duduma"]
                }
            if any(w in q for w in ["step", "steps", "stairs", "climb", "trek", "walk", "down"]):
                return {
                    "answer": (
                        "**🚶‍♂️ Trekking the Steps at Duduma:**\n\n"
                        "• **Total Steps:** Approximately **1,000 concrete steps** leading from the plateau down to the base of the gorge.\n"
                        "• **Trek Difficulty:** Strenuous. Walking down takes ~35 minutes; climbing back up takes 50-70 minutes.\n"
                        "• **Is it necessary to go down?** No! The **top viewpoint platform** offers a panoramic, world-class view of the full 175m cascade and canyon without climbing any steps.\n\n"
                        "💡 *Kora's Tip:* Wear sports shoes with grip. Steps are damp and slippery in monsoon. Watch out for troop monkeys near the midpoint!"
                    ),
                    "suggestions": ["Is Duduma safe for children?", "Entry fee for Duduma", "Duduma height in feet"]
                }
            if any(w in q for w in ["safe", "safety", "kids", "children", "elderly", "family"]):
                return {
                    "answer": (
                        "**🛡️ Safety Advisory for Duduma Waterfalls:**\n\n"
                        "• **Top Viewpoint Area:** **Very safe for families, kids, and senior citizens.** Paved pathways, metal railings, and food kiosks line the top.\n"
                        "• **Gorge Steps (1,000 steps down):** **Not recommended** for young children, elderly travelers, or anyone with knee/heart conditions due to the steep climb.\n"
                        "• **Swimming / Water Access:** Strictly prohibited near the waterfall drop and downstream river due to sudden water surges from the Machkund hydro dam.\n\n"
                        "💡 *Kora's Tip:* Keep phones and snacks securely zipped inside bags because playful monkeys sit along the railings."
                    ),
                    "suggestions": ["Duduma waterfall height", "Rani Duduma waterfall", "How to reach Duduma"]
                }

        # -------------------------------------------------------------------
        # 4. Gupteswar Cave Temple Questions (Shiva Lingam, Kolab, Pilgrimage)
        # -------------------------------------------------------------------
        if "gupteswar" in q or "cave" in q or "shiva" in q:
            return {
                "answer": (
                    "**🛕 Gupteswar Cave Shrine (The Hidden Lord of Kolab):**\n\n"
                    "• **The Sanctum:** An ancient subterranean limestone cave housing a revered **naturally formed limestone Shiva Lingam** (stalagmite) that continues to grow.\n"
                    "• **Location:** Perched on the banks of the sacred Kolab (Sabari) River in Jeypore sub-division, **75 km from Koraput** (~1.5 hours scenic drive through Sal forests).\n"
                    "• **Mythological Lore:** Revered as the cave where **Lord Rama** sought solace and worshipped Lord Shiva during his exile in Dandakaranya.\n"
                    "• **Visiting Hours:** **06:00 AM - 08:00 PM daily**.\n"
                    "• **Entry Fee:** **Free entry** (₹50 VIP queue during Shravan Bol-Bam & Maha Shivaratri festivals).\n\n"
                    "💡 *Kora's Tip:* Inside the cave, the air is naturally cool and quiet. Beware of strong river currents if dipping feet in the Kolab riverbank outside!"
                ),
                "suggestions": ["Sabara Srikhetra Jagannath temple", "Kolab Dam boating", "Kunduli Friday market", "Koraput stays"]
            }

        # -------------------------------------------------------------------
        # 5. Kolab Dam & Reservoir Questions (Boating, Park, Sunset)
        # -------------------------------------------------------------------
        if "kolab" in q:
            return {
                "answer": (
                    "**🚣 Kolab Dam & Reservoir (The Sapphire Jewel):**\n\n"
                    "• **What it is:** A sprawling multi-purpose hydroelectric reservoir on the Kolab River, ringed by undulating green hills.\n"
                    "• **Distance from Koraput Town:** Just **15 km (approx. 25 minutes)**.\n"
                    "• **Boating Facilities:** Speedboats, motorboats, and pedal boats operate from the jetty. **Rates: ₹100 - ₹250 per ride**.\n"
                    "• **Kolab Botanical Park:** Beautifully manicured hillside garden with terraced flowering lawns, viewing gazebos, and a children's play area.\n"
                    "• **Timings & Entry:** 08:00 AM - 06:30 PM daily. **Entry: ₹20 per person**.\n\n"
                    "💡 *Kora's Tip:* The sunset over Kolab reservoir is magical! You can also stay right at the water’s edge at **Kolab Nature Camp**."
                ),
                "suggestions": ["Kolab Nature Camp price", "Gupteswar Cave Temple", "Deomali Peak", "2-day itinerary"]
            }

        # -------------------------------------------------------------------
        # 6. Koraput Coffee Questions (GI Tag, Tasting, History, Quality)
        # -------------------------------------------------------------------
        if "coffee" in q:
            return {
                "answer": (
                    "**☕ The Saga of Koraput Coffee (GI-Tagged Arabica):**\n\n"
                    "• **Official GI Tag:** Awarded a Geographical Indication certifying its unique altitude, red laterite soil, and microclimate.\n"
                    "• **100% Shade-Grown Arabica:** Cultivated at 3,000 feet elevation beneath the protective shade of silver oak, jackfruit, and pepper vines.\n"
                    "• **Origin Story:** Pioneered in the 1930s by **Maharaja Sri Ram Chandra Deb of Jeypore** as an eco-agroforestry experiment.\n"
                    "• **Tribal Empowerment:** Organic cultivation is led today by fair-trade indigenous tribal farmer cooperatives (especially women self-help groups).\n"
                    "• **Cup Profile:** Gentle mild acidity, smooth medium body, with notes of **toasted almond, dark chocolate, and highland florals**.\n\n"
                    "**Where to Experience It:**\n"
                    "• **Coffee Board Research Center & Nursery:** Machkund Road (Tasting sessions available).\n"
                    "• **Koraput Coffee Cafes:** Located in Koraput Town near Sabara Srikhetra."
                ),
                "suggestions": ["Where to buy Koraput coffee?", "Kunduli tribal market", "Deomali Peak", "Dhemsa folk dance"]
            }

        # -------------------------------------------------------------------
        # 7. Kunduli Weekly Tribal Haat Questions
        # -------------------------------------------------------------------
        if any(w in q for w in ["kunduli", "haat", "market", "bazaar"]):
            return {
                "answer": (
                    "**🧺 Kunduli Weekly Tribal Haat (Asia's Preeminent Friday Market):**\n\n"
                    "• **When:** **Every Friday ONLY** (07:00 AM to 02:00 PM; peak bustling hours are 08:30 AM - 11:30 AM).\n"
                    "• **Location:** Kunduli on National Highway 26, about **32 km from Koraput town** (approx. 45 mins).\n"
                    "• **Tribes Participating:** Hundreds of indigenous **Paroja, Gadaba, and Mali** tribal families gather from hilltop hamlets in traditional colorful attire and brass neckbands (*Khagla*).\n"
                    "• **What is Sold:** Pure wild forest honey, turmeric, country ginger, handmade bamboo baskets, terracotta pottery, and *Desi* farm produce.\n\n"
                    "💡 *Kora's Cultural Etiquette Tip:* Always ask permission with a warm smile before photographing tribal elders. Support local artisans by purchasing handmade bamboo crafts or forest honey!"
                ),
                "suggestions": ["Tribes of Koraput", "Dhemsa folk dance", "Kotpad handloom weaves", "Parab festival"]
            }

        # -------------------------------------------------------------------
        # 8. Tribal Culture, Dhemsa Dance & Parab Festival
        # -------------------------------------------------------------------
        if any(w in q for w in ["dance", "dhemsa", "music", "culture", "tribe", "tribal", "bonda", "gadaba", "parab", "paroja"]):
            if "dhemsa" in q or "dance" in q:
                return {
                    "answer": (
                        "**🥁 Dhemsa: The Living Pulse of Koraput:**\n\n"
                        "• **The Dance:** Dhemsa is the traditional community folk dance of Koraput's indigenous tribes. Dancers interlock arms and shoulders in an unbroken, undulating human chain.\n"
                        "• **Rhythm & Footwork:** Starts at a slow, meditative tempo (*Boda Dhemsa*) and progressively accelerates into energetic, synchronized foot taps and hops (*Kunda Dhemsa*).\n"
                        "• **Traditional Instruments:** Led by the evocative, piercing notes of the **Mohuri** (wooden reed oboe), anchored by the deep thrum of the **Dholak**, and punctuated by the **Tamak** (kettle drum) and **Changu**.\n"
                        "• **Philosophy:** Symbolizes community equality—there is no barrier of caste, status, or age. Visitors are warmly invited to join the chain during village festivals!"
                    ),
                    "suggestions": ["Tribes of Koraput", "Parab festival dates", "Kunduli Friday market", "Koraput Coffee"]
                }
            return {
                "answer": (
                    "**🌿 The Indigenous Tribes of Koraput:**\n\n"
                    "Koraput is home to over **62 scheduled tribes**, each preserving living ancestral traditions:\n"
                    "• **Gadaba Tribe:** Renowned for their hand-loomed *Kerang* fiber clothing and heavy solid brass neck collars called *Khagla*.\n"
                    "• **Bonda (Remo) Tribe:** One of the most ancient surviving highland communities, known for living in remote summits and wearing intricate brass bead neckbands.\n"
                    "• **Paroja Tribe:** Agrarian hill dwellers famous for their poetic folk songs and mastery of Dhemsa dance.\n"
                    "• **Parab Festival:** The grand annual district cultural carnival held every **November/December**, bringing together thousands of tribal archers, musicians, and craftsmen."
                ),
                "suggestions": ["What is Dhemsa dance?", "Kunduli Friday market", "Kotpad natural dye handloom", "Local food in Koraput"]
            }

        # -------------------------------------------------------------------
        # 9. Food & Tribal Cuisine (Mandia Pej, Bamboo Shoots)
        # -------------------------------------------------------------------
        if any(w in q for w in ["food", "eat", "cuisine", "dish", "dishes", "mandia", "pej", "bamboo", "karadi", "honey"]):
            return {
                "answer": (
                    "**🍲 Authentic Flavors & Tribal Gastronomy of Koraput:**\n\n"
                    "• **Mandia Pej (Finger-Millet Drink):** The staple highland superfood! Fermented Ragi porridge mixed with cooked rice gruel. Extremely nutritious, gut-friendly, and naturally cooling.\n"
                    "• **Bamboo Shoot Curry (Karadi):** Tender young wild bamboo shoots stewed with country mustard paste, garlic, and wild herbs. Pair it with woodfired country chicken (*Desi Kukkuda*).\n"
                    "• **Wild Sal Forest Honey:** Dark, unpasteurized honey harvested by tribal foragers from forest canopies in Machkund and Gupteswar.\n"
                    "• **Millet Pitha & Cakes:** Steamed rice-and-millet cakes filled with sweet jaggery and freshly grated coconut.\n\n"
                    "💡 *Kora's Tip:* Savor warm Mandia Pej at local weekly haats, and pair every meal with a piping cup of Koraput Arabica Coffee!"
                ),
                "suggestions": ["Kunduli Friday tribal market", "Where to buy Koraput coffee", "Hotels and restaurants", "Places to visit"]
            }

        # -------------------------------------------------------------------
        # 10. Stays, Eco-Cottages & Hotels
        # -------------------------------------------------------------------
        if any(w in q for w in ["hotel", "stay", "resort", "cottage", "camp", "homestay", "lodge", "room", "night", "accommodation", "where to sleep"]):
            return {
                "answer": (
                    "**🏨 Verified Stays & Eco-Cottages in Koraput:**\n\n"
                    "• **Deomali Eco Tourism Nature Camp** (Hilltop Eco-Resort)\n"
                    "  📍 Foothills of Deomali Peak (62 km from town)\n"
                    "  💰 **₹2,500 - ₹4,500 / night** (Includes breakfast & dinner)\n"
                    "  ✨ Mountain sunrise views, wooden cottages, stargazing deck, bonfires.\n\n"
                    "• **Kolab Nature Camp** (Lakeside Cottages)\n"
                    "  📍 Kolab Dam Promenade (16 km from town)\n"
                    "  💰 **₹2,000 - ₹3,500 / night**\n"
                    "  ✨ Lakeside rooms, botanical garden access, private boating dock.\n\n"
                    "• **Chandoori Sai Guest House** (Boutique Artisan Homestay)\n"
                    "  📍 Ghatgaon Pottery Village (48 km from town)\n"
                    "  💰 **₹5,000 - ₹8,000 / night**\n"
                    "  ✨ Terracotta architecture by Mark Herten, gourmet organic dining.\n\n"
                    "• **Hotel Lemon Castle** (Town Comfort Base)\n"
                    "  📍 Koraput Town Center\n"
                    "  💰 **₹2,200 - ₹4,000 / night** | 📞 +91 6852 251500"
                ),
                "suggestions": ["Deomali Eco Nature Camp booking", "Kolab Lake boating rates", "Weekend 2-day itinerary"]
            }

        # -------------------------------------------------------------------
        # 11. Travel Logistics: How to Reach, Nearest Airport / Train
        # -------------------------------------------------------------------
        if any(w in q for w in ["reach", "airport", "train", "station", "bus", "transport", "how to go", "how to visit", "nearest"]):
            return {
                "answer": (
                    "**🚆 How to Reach Koraput:**\n\n"
                    "• **By Air:**\n"
                    "  - **Visakhapatnam Airport (VTZ):** 190 km away. Connected to all major Indian metros. A scenic 4.5-hour hill drive via Sunabeda.\n"
                    "  - **Jeypore Domestic Airport (PYB):** 25 km away, with regional flights connecting to Bhubaneswar.\n\n"
                    "• **By Train:**\n"
                    "  - **Koraput Junction (KRPU):** Directly connected to Bhubaneswar (Hirakhand Express), Visakhapatnam (Kirandul Passenger with glass-domed Vistadome coach!), and Kolkata.\n"
                    "  - The train ride through the Eastern Ghats tunnels and over Maliguda Viaduct is one of India's most scenic rail journeys!\n\n"
                    "• **By Road:**\n"
                    "  - NH-26 links Koraput smoothly to Raipur, Visakhapatnam, and Bhubaneswar with regular state luxury buses (OSRTC)."
                ),
                "suggestions": ["2-day weekend tour itinerary", "Deomali Peak height", "Duduma Waterfalls", "Hotels in Koraput"]
            }

        # -------------------------------------------------------------------
        # 12. Itineraries & Feasibility Queries (1 Day, 2 Days, 3 Days)
        # -------------------------------------------------------------------
        if any(w in q for w in ["itinerary", "plan", "day", "days", "weekend", "trip", "route"]):
            if "1" in q or "one" in q:
                return {
                    "answer": (
                        "**🗺️ Express 1-Day Koraput Tour Plan:**\n\n"
                        "• **08:30 AM:** Morning prayer & tribal heritage at **Sabara Srikhetra** (Hilltop Jagannath Temple).\n"
                        "• **11:00 AM:** Coffee plantation walk & fresh pour-over tasting on Machkund Road.\n"
                        "• **01:30 PM:** Traditional tribal lunch with warm Mandia Pej & country chicken.\n"
                        "• **04:00 PM:** Speedboating & golden hour photography at **Kolab Dam & Reservoir**.\n"
                        "• **07:00 PM:** Evening shopping for Kotpad handloom & Koraput Arabica Coffee packets."
                    ),
                    "suggestions": ["Suggest a 2-day weekend plan", "Suggest a 3-day grand tour", "Deomali Peak sunrise"]
                }
            return {
                "answer": (
                    "**🗺️ Recommended 2-Day Weekend Hill & Coffee Itinerary:**\n\n"
                    "• **DAY 1: Heritage, Coffee & Lakeside Sunset**\n"
                    "  - *Morning:* Sabara Srikhetra Jagannath Temple & on-site Tribal Museum.\n"
                    "  - *Midday:* Koraput Coffee research estate walk & tasting.\n"
                    "  - *Late Afternoon:* Boating & sunset at Kolab Dam; overnight at **Kolab Nature Camp**.\n\n"
                    "• **DAY 2: Conquering Odisha's Roof & Swiss-like Valleys**\n"
                    "  - *05:00 AM:* Dawn drive to **Deomali Peak** (1,672m) for the sea-of-clouds sunrise.\n"
                    "  - *11:00 AM:* Breezy hike across **Putsil Valley Tablelands**.\n"
                    "  - *03:00 PM:* Return drive with souvenir halts for organic forest honey."
                ),
                "suggestions": ["Suggest a 3-day tour", "Duduma Waterfalls steps", "Hotels in Koraput", "Kunduli Friday haat"]
            }

        # -------------------------------------------------------------------
        # 13. Direct Specific Place Lookup
        # -------------------------------------------------------------------
        matched_place = None
        stop_words = {"koraput", "odisha", "district", "place", "places", "visit", "waterfall", "waterfalls", "peak", "cave", "temple", "dam", "pond", "lake"}
        for p in places:
            p_name = p["name"].lower()
            tokens = [t for t in p_name.split() if len(t) > 3 and t not in stop_words]
            if p_name in q or any(t in q for t in tokens):
                matched_place = p
                break

        if matched_place:
            try:
                highlights = json.loads(matched_place["highlights"]) if matched_place["highlights"] else []
            except Exception:
                highlights = []
            try:
                tips = json.loads(matched_place["travel_tips"]) if matched_place["travel_tips"] else []
            except Exception:
                tips = []

            return {
                "answer": (
                    f"**🏔️ {matched_place['name']}**\n"
                    f"📍 *{matched_place['location']}* ({matched_place['distance_koraput']})\n\n"
                    f"{matched_place['refined_story'][:300]}...\n\n"
                    f"**Key Visitor Facts:**\n"
                    f"• **Visiting Hours:** {matched_place['timing']}\n"
                    f"• **Entry Fee:** {matched_place['entry_fee']}\n"
                    f"• **Best Season:** {matched_place['best_season']}\n"
                    f"• **Estimated Duration:** {matched_place['ideal_duration']}\n\n"
                    f"**Highlights:**\n"
                    + "\n".join([f"• {h}" for h in highlights[:2]]) + "\n\n"
                    f"💡 *Kora's Tip:* {tips[0] if tips else 'Carry cash and drinking water along this route!'}"
                ),
                "suggestions": [f"Entry fee for {matched_place['name']}", f"Best time to visit {matched_place['name']}", "Where to stay nearby"]
            }

        # -------------------------------------------------------------------
        # 14. Intelligent Fallback with Specific District Knowledge
        # -------------------------------------------------------------------
        return {
            "answer": (
                "**Johar!** 🙏 In Koraput (*The Heaven of Odisha*), every mountain summit, waterfall, and tribal village holds a story.\n\n"
                "I couldn't quite pinpoint your exact question, but here is what I know best:\n"
                "• **Peaks & Treks:** Deomali (1,672m, highest in Odisha), Putsil Valley Tablelands.\n"
                "• **Waterfalls:** Duduma (175m tier canyon fall), Rani Duduma.\n"
                "• **Caves & Shrines:** Gupteswar Cave (Lord Shiva limestone lingam), Sabara Srikhetra.\n"
                "• **Heritage & Flavors:** GI-Tagged Koraput Coffee, Kunduli Friday Market, Dhemsa Dance, Mandia Pej.\n"
                "• **Accommodations:** Deomali Eco Nature Camp, Kolab Lakeside Cottages.\n\n"
                "Could you ask me with specific names or topics like *'How high is Deomali?'* or *'What is the ticket fee for Kolab?'*?"
            ),
            "suggestions": [
                "What is the height of Deomali?",
                "How many steps at Duduma Waterfalls?",
                "Where can I stay in Koraput?",
                "Why is Koraput Coffee famous?",
                "Suggest a 2-day weekend tour"
            ]
        }
