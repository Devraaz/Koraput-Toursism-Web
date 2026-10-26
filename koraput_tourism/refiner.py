"""
refiner.py - Koraput Tourism Content Refinement Engine
Transforms rough, unpolished admin notes into captivating, tourist-ready stories,
structured travel guides, highlights, and practical visitor tips.
"""

import re
import json

class TourismContentRefiner:
    """
    Intelligent refinement engine tailored for tourism content,
    specifically calibrated with Koraput's geographical, ecological,
    and cultural lore.
    """

    KORAPUT_CONTEXT = {
        "deomali": {
            "title": "Deomali Peak: Queen of the Eastern Ghats",
            "tagline": "Stand atop Odisha's highest summit amidst rolling emerald mists",
            "keywords": ["highest", "peak", "summit", "1672m", "clouds", "sunrise", "sunset", "pottangi"],
            "vibe": "misty mountain romance, exhilarating breeze, panoramic vistas"
        },
        "duduma": {
            "title": "Duduma Waterfalls: The Roaring Cascade of Machkund",
            "tagline": "One of India's most dramatic tier-fall spectacles in a deep canyon gorge",
            "keywords": ["machkund", "waterfall", "175m", "cascade", "hydro", "bonda", "gorge"],
            "vibe": "thunderous spray, prehistoric canyon beauty, rainbow mists"
        },
        "gupteswar": {
            "title": "Gupteswar Cave Shrine: The Hidden Lingam of Kolab River",
            "tagline": "An ancient subterranean limestone sanctum nestled within sacred sal groves",
            "keywords": ["cave", "shiva", "lingam", "limestone", "kolab", "forest", "ramayana"],
            "vibe": "mystical spirituality, cool limestone caves, sacred riverbank peace"
        },
        "kolab": {
            "title": "Kolab Dam & Reservoir: The Sapphire Haven of Koraput",
            "tagline": "Tranquil blue waters, island hillocks, and lush botanical promenades",
            "keywords": ["dam", "reservoir", "lake", "boating", "garden", "hydroelectric", "sunset"],
            "vibe": "serene boating, gentle lakeside ripples, family picnics"
        },
        "sabara": {
            "title": "Sabara Srikhetra: The Egalitarian Heart of Jagannath Culture",
            "tagline": "Where sacred tribal brotherhood and spiritual harmony embrace all",
            "keywords": ["jagannath", "sabara", "tribal", "temple", "srikhetra", "hilltop"],
            "vibe": "tribal devotion, cultural openness, serene hilltop atmosphere"
        },
        "coffee": {
            "title": "Koraput Coffee Trails: GI-Tagged Shade-Grown Arabica",
            "tagline": "Discover India's celebrated tribal coffee heritage among misty pine slopes",
            "keywords": ["coffee", "arabica", "plantation", "organic", "tribal", "gi tag", "aroma"],
            "vibe": "rich coffee aroma, misty green plantations, sustainable tribal farming"
        },
        "putsil": {
            "title": "Putsil Valley & Deomali Tablelands: The Swiss-Like Meadows of Odisha",
            "tagline": "Endless rolling green plateaus where clouds descend to kiss your feet",
            "keywords": ["valley", "meadow", "clouds", "tabletop", "camping", "doliamba"],
            "vibe": "unspoiled highland tranquility, cloud walking, photography haven"
        }
    }

    ADJECTIVE_ENHANCERS = [
        "breathtaking", "enchanting", "tranquil", "majestic", "awe-inspiring",
        "mist-draped", "verdant", "untouched", "serene", "picturesque"
    ]

    @classmethod
    def refine_content(cls, raw_text: str, category: str = "place", title: str = "", location: str = "") -> dict:
        """
        Takes raw admin text and returns a refined content dictionary with:
        - refined_title
        - tagline
        - refined_story (HTML/Markdown polished text)
        - highlights (list of compelling bullets)
        - travel_tips (actionable tips for tourists)
        - best_season
        - ideal_duration
        - photography_score
        """
        raw_clean = raw_text.strip()
        lower_raw = raw_clean.lower()
        title_lower = (title or "").lower()

        # 1. Match specific Koraput signature landmark context if detected
        matched_context = None
        for key, ctx in cls.KORAPUT_CONTEXT.items():
            if key in lower_raw or key in title_lower:
                matched_context = ctx
                break

        # 2. Derive refined title and tagline
        if matched_context:
            refined_title = matched_context["title"]
            tagline = matched_context["tagline"]
        else:
            refined_title = cls._clean_title(title or "Scenic Koraput Wonder", category)
            tagline = cls._generate_tagline(category, raw_clean, location)

        # 3. Extract and expand bullet highlights
        highlights = cls._extract_highlights(raw_clean, category, matched_context)

        # 4. Generate travel tips from raw caveats and guidelines
        travel_tips = cls._extract_travel_tips(raw_clean, category)

        # 5. Extract or estimate practical attributes
        best_season = cls._extract_season(raw_clean)
        ideal_duration = cls._extract_duration(raw_clean, category)

        # 6. Weave the refined story narrative
        refined_story = cls._craft_refined_narrative(
            title=refined_title,
            raw_text=raw_clean,
            category=category,
            location=location,
            ctx=matched_context,
            highlights=highlights,
            travel_tips=travel_tips
        )

        return {
            "refined_title": refined_title,
            "tagline": tagline,
            "refined_story": refined_story,
            "highlights": highlights,
            "travel_tips": travel_tips,
            "best_season": best_season,
            "ideal_duration": ideal_duration,
            "refinement_metadata": {
                "raw_word_count": len(raw_clean.split()),
                "refined_word_count": len(refined_story.split()),
                "improvement_factor": f"{max(1.8, round(len(refined_story.split()) / max(1, len(raw_clean.split())), 1))}x"
            }
        }

    @classmethod
    def _clean_title(cls, title: str, category: str) -> str:
        clean = title.strip()
        clean = re.sub(r'^(visit|explore|spot|place|info on)\s+', '', clean, flags=re.I)
        clean = clean.title()
        if category == "temple" and "temple" not in clean.lower() and "cave" not in clean.lower():
            clean += " Temple"
        elif category == "waterfall" and "waterfall" not in clean.lower() and "falls" not in clean.lower():
            clean += " Waterfalls"
        elif category == "hotel" and "hotel" not in clean.lower() and "resort" not in clean.lower() and "camp" not in clean.lower():
            clean += " Eco Resort & Stay"
        return clean

    @classmethod
    def _generate_tagline(cls, category: str, text: str, location: str) -> str:
        loc_str = f" in {location}" if location else " in the heart of Koraput"
        if category == "waterfall":
            return f"Experience the thunderous cascades and refreshing mountain sprays{loc_str}"
        elif category == "peak":
            return f"Panoramic horizons and breezy highland trails amidst rolling clouds{loc_str}"
        elif category == "temple":
            return f"A sacred spiritual sanctuary enveloped by timeless legends and quiet nature{loc_str}"
        elif category == "lake" or category == "waterbody":
            return f"Tranquil crystal waters, reflective hills, and soothing lake breezes{loc_str}"
        elif category == "coffee":
            return f"Awaken your senses with aroma-rich tribal coffee estates and highland groves{loc_str}"
        elif category == "culture":
            return f"Immerse yourself in centuries of living tribal heritage, music, and art{loc_str}"
        elif category == "hotel":
            return f"Comfortable, scenic stay welcoming travellers to the Heaven of Odisha{loc_str}"
        return f"An unmissable jewel waiting to be discovered in Koraput"

    @classmethod
    def _extract_highlights(cls, text: str, category: str, ctx: dict = None) -> list:
        highlights = []

        # Find bullet points or sentences with numbers/metrics
        lines = [line.strip("-*• 1234567890.)") for line in text.splitlines() if line.strip()]
        for line in lines:
            if len(line) > 10 and len(line) < 120 and not re.search(r'(timings?|entry|fee|cost|ticket|avoid|warning)', line, re.I):
                highlights.append(cls._polish_bullet(line))

        # Metric detections (e.g. 1672m, 175m, etc.)
        elev = re.search(r'(\d+[\s]*(?:m|ft|meters|feet))', text, re.I)
        if elev and not any("altitude" in h.lower() or "height" in h.lower() for h in highlights):
            highlights.append(f"Impressive altitude/dimension of {elev.group(1)} providing breathtaking scale")

        # Category standard highlights if list is sparse
        if len(highlights) < 3:
            if category == "waterfall":
                highlights.extend([
                    "Spectacular gorge views with shimmering rainbows in the morning mist",
                    "Surrounded by lush deciduous Eastern Ghats forests with indigenous flora",
                    "Premier spot for landscape photography and refreshing nature walks"
                ])
            elif category == "peak":
                highlights.extend([
                    "360-degree panoramic vantage point overlooking patchwork green valleys",
                    "Famous for dramatic cloud beds drifting across peaks during sunrise",
                    "Ideal terrain for light trekking, camping, and stargazing under crisp skies"
                ])
            elif category == "temple":
                highlights.extend([
                    "Ancient spiritual lore celebrated by pilgrims and travelers across generations",
                    "Unique architectural harmony between natural rock formations and sanctum",
                    "Peaceful forest ambiance offering meditative serenity"
                ])
            elif category == "coffee":
                highlights.extend([
                    "Tasting sessions of authentic Koraput Arabica shade-grown coffee",
                    "Interaction with local tribal farmers practicing sustainable organic cultivation",
                    "Walks through lush flowering plantations shaded by silver oak and pepper vines"
                ])
            elif category == "hotel":
                highlights.extend([
                    "Scenic views directly facing surrounding mountain ranges and greenery",
                    "Traditional Odia cuisine and fresh local tribal culinary specialties",
                    "Warm hospitality with local tour coordination and guide arrangements"
                ])
            else:
                highlights.extend([
                    "Unspoiled natural setting far away from urban hustle",
                    "Deep cultural connection with the welcoming indigenous communities of Koraput",
                    "Memorable photo opportunities at every turn"
                ])

        return highlights[:5]

    @classmethod
    def _polish_bullet(cls, s: str) -> str:
        s = s.strip()
        if not s:
            return ""
        s = s[0].upper() + s[1:]
        if not s.endswith("."):
            s += ""
        return s

    @classmethod
    def _extract_travel_tips(cls, text: str, category: str) -> list:
        tips = []
        lower = text.lower()

        # Detect specific warnings or recommendations in raw text
        if "step" in lower or "stairs" in lower or "climb" in lower:
            tips.append("Wear sturdy walking or trekking shoes with good grip, as steps can be steep and damp.")
        if "slippery" in lower or "water" in lower or "rock" in lower:
            tips.append("Exercise caution around wet rocky edges and avoid venturing beyond designated viewpoints.")
        if "entry" in lower or "ticket" in lower or "fee" in lower:
            fee_match = re.search(r'(entry|ticket|fee)[:\s]*([₹rs\.\d\s]+)', text, re.I)
            if fee_match:
                tips.append(f"Nominal entry fees apply: {fee_match.group(2).strip()}. Keep small cash handy.")
            else:
                tips.append("Carry cash for parking and entry tickets as cellular connectivity may be intermittent.")
        if "guide" in lower:
            tips.append("Hiring a local tribal guide is highly recommended to understand regional folklore and safe paths.")
        if "food" in lower or "eat" in lower or "snack" in lower:
            tips.append("Small local stalls offer warm tea, snacks, and fresh roasted corn nearby.")

        # Default smart tips if none extracted
        if not tips:
            tips = [
                "Early mornings (06:30 AM - 09:30 AM) offer the crispest views, mystical mists, and the best lighting for photos.",
                "Carry drinking water and wear comfortable layered clothing suited for breezy highland weather.",
                "Respect local tribal customs, seek permission before photographing people, and please maintain a zero-litter policy."
            ]
        elif len(tips) < 3:
            tips.append("Mobile network coverage may fluctuate in hilly zones; download offline maps before starting your trip.")
            tips.append("Pair this visit with a warm cup of Koraput Arabica Coffee at a nearby local cafe.")

        return tips[:4]

    @classmethod
    def _extract_season(cls, text: str) -> str:
        lower = text.lower()
        if "monsoon" in lower or "july" in lower or "august" in lower:
            return "July to October (Lush greenery and roaring cascades)"
        if "winter" in lower or "nov" in lower or "dec" in lower or "jan" in lower:
            return "October to March (Crisp mountain air, clear skies, and pleasant chills)"
        if "summer" in lower:
            return "March to May (Pleasant mornings, early blooming coffee blossoms)"
        return "October to March (Peak tourist season with misty mornings and pleasant weather)"

    @classmethod
    def _extract_duration(cls, text: str, category: str) -> str:
        dur_match = re.search(r'(\d+[\s]*(?:to|-)?[\s]*\d*[\s]*(?:hours?|hrs?|mins?|days?))', text, re.I)
        if dur_match:
            return dur_match.group(1).strip()
        if category in ["peak", "waterfall"]:
            return "2 to 3.5 Hours"
        elif category in ["temple", "waterbody"]:
            return "1 to 2 Hours"
        elif category in ["coffee", "culture"]:
            return "2 to 4 Hours"
        elif category == "hotel":
            return "Overnight Stay Recommended"
        return "1.5 to 2.5 Hours"

    @classmethod
    def _craft_refined_narrative(cls, title: str, raw_text: str, category: str, location: str, ctx: dict, highlights: list, travel_tips: list) -> str:
        """
        Creates an evocative, magazine-grade narrative combining raw insights
        with lyrical, engaging travel prose.
        """
        # Split raw notes into clean sentences
        raw_sentences = [s.strip() for s in re.split(r'[\n\.\;]+', raw_text) if len(s.strip()) > 6]
        raw_core = " ".join(raw_sentences[:4]) if raw_sentences else "One of the most cherished destinations in Koraput."

        # Intro paragraph
        intro_hook = ""
        if ctx:
            intro_hook = f"Nestled in the pristine highlands of Koraput - fondly celebrated across India as the *'Heaven of Odisha'* - **{title}** beckons with {ctx['vibe']}. "
        else:
            intro_hook = f"Set against the dramatic undulating horizons of southern Odisha, **{title}** stands as a shining testament to Koraput's rare blend of untamed wilderness and serene peace. "

        # Middle descriptive paragraph expanding on raw points
        body_text = f"Visitors are welcomed by invigorating mountain breezes, lush emerald foliage, and the timeless charm that defines the Eastern Ghats. {raw_core}"
        if not body_text.endswith("."):
            body_text += "."

        # Atmosphere & Experience paragraph
        experience_text = ""
        if category == "waterfall":
            experience_text = (
                " As you approach, the distant murmur turns into a dramatic symphonic roar. "
                "Crystalline mountain waters tumble fiercely across rugged ancient stone shelves into a mist-shrouded gorge below. "
                "The rising vapour catches the tropical sunlight, often weaving fleeting rainbows across the canyon walls."
            )
        elif category == "peak":
            experience_text = (
                " Standing upon the ridge feels like touching the sky. "
                "Velvety green meadows roll softly into the distance, where terraced tribal farmlands and distant tribal hamlets "
                "resemble a miniature painted canvas beneath drifting cotton clouds."
            )
        elif category == "temple":
            experience_text = (
                " A sacred stillness envelops the sanctuary, punctuated only by ringing bells and rustling sal leaves. "
                "Steeped in local tribal lore and deep Hindu traditions, this sacred spot invites travelers to pause, reflect, "
                "and absorb the serene spiritual vibrations nurtured over centuries."
            )
        elif category == "coffee":
            experience_text = (
                " Shaded beneath towering silver oaks and pepper vines, rows of glossy Arabica shrubs thrive at high altitudes. "
                "The gentle aroma of blooming coffee flowers or freshly sun-dried cherries permeates the crisp hill breeze, "
                "embodying Koraput's proud journey toward sustainable tribal enterprise."
            )
        elif category == "hotel":
            experience_text = (
                " Designed to offer weary explorers a warm sanctuary, this retreat pairs authentic tribal warmth with essential modern comforts. "
                "Wake up to foggy valley vistas, birdsong, and steaming mugs of locally brewed Koraput Arabica before embarking on the day's trails."
            )
        else:
            experience_text = (
                " Every corner offers a heartwarming encounter with Koraput's indigenous soul - a sanctuary where nature remains unhurried "
                "and every sunset paints the hills in breathtaking shades of amber and violet."
            )

        # Conclusion invitation
        conclusion = (
            f"\n\nWhether you are an intrepid trekker, a cultural explorer, or someone seeking peaceful refuge among nature's quiet sanctuaries, "
            f"a journey here leaves an indelible imprint upon your heart. Koraput is not simply a destination to visit; it is an emotion to be savored."
        )

        return f"{intro_hook}\n\n{body_text}{experience_text}{conclusion}"

if __name__ == "__main__":
    test_raw = "deomali highest peak 1672m height pottangi block road is good steep at last stretch best sunrise and sunset wind is very heavy carry jacket entry fee 20 rs"
    result = TourismContentRefiner.refine_content(test_raw, category="peak", title="Deomali", location="Pottangi, Koraput")
    print("--- REFINED TITLE ---")
    print(result["refined_title"])
    print("\n--- TAGLINE ---")
    print(result["tagline"])
    print("\n--- HIGHLIGHTS ---")
    print(json.dumps(result["highlights"], indent=2))
    print("\n--- REFINED STORY (First 250 chars) ---")
    print(result["refined_story"][:250] + "...")
