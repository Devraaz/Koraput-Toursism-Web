"""
test_server.py - Automated verification test for Koraput Tourism Server and REST APIs.
"""
import urllib.request
import json
import time

def test_endpoints():
    base_url = "http://127.0.0.1:8080"
    print(f"Testing server at {base_url}...")

    # 1. Test Home page
    req = urllib.request.Request(base_url)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        assert resp.status == 200
        assert "Koraput" in html
        print("[PASS] GET / -> 200 OK (Served HTML with Koraput branding)")

    # 2. Test GET /api/stats
    req = urllib.request.Request(f"{base_url}/api/stats")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data["success"] is True
        print(f"[PASS] GET /api/stats -> {data['stats']['total_places']} places, {data['stats']['elevation']}")

    # 3. Test GET /api/places
    req = urllib.request.Request(f"{base_url}/api/places")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data["success"] is True
        assert len(data["places"]) >= 10
        print(f"[PASS] GET /api/places -> {len(data['places'])} verified places loaded")

    # 4. Test POST /api/refine (On-demand AI Refinement Engine)
    raw_sample = "rani duduma 45 km from koraput town near nandapur. shallow crystal clear water pools surrounded by dense forest. great for dipping feet family picnic. best time post monsoon."
    post_data = json.dumps({
        "raw_content": raw_sample,
        "category": "waterfall",
        "title": "Rani Duduma",
        "location": "Nandapur, Koraput"
    }).encode('utf-8')

    req = urllib.request.Request(f"{base_url}/api/refine", data=post_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data["success"] is True
        assert "refined" in data
        assert len(data["refined"]["highlights"]) > 0
        print(f"[PASS] POST /api/refine -> Successfully refined raw draft into:")
        print(f"       Headline: {data['refined']['refined_title']}")
        print(f"       Tagline:  {data['refined']['tagline']}")
        print(f"       Word expansion: {data['refined']['refinement_metadata']['improvement_factor']}")

    # 5. Test GET /api/hotels
    req = urllib.request.Request(f"{base_url}/api/hotels")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data["success"] is True
        print(f"[PASS] GET /api/hotels -> {len(data['hotels'])} eco-stays & hotels loaded")

    # 6. Test GET /api/itineraries
    req = urllib.request.Request(f"{base_url}/api/itineraries")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data["success"] is True
        print(f"[PASS] GET /api/itineraries -> {len(data['itineraries'])} handcrafted itineraries loaded")

    # 7. Test GET /api/culture
    req = urllib.request.Request(f"{base_url}/api/culture")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data["success"] is True
        print(f"[PASS] GET /api/culture -> {len(data['culture'])} cultural heritage articles loaded")

    print("\n>>> ALL TESTS PASSED! APPLICATION IS FULLY FUNCTIONAL! <<<")

if __name__ == "__main__":
    test_endpoints()
