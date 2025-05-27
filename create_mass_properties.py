#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta
from textwrap import shorten
import requests
from requests.auth import HTTPBasicAuth

ENDPOINT = "http://127.0.0.1:8000/property/my/"
PASSWORD = "password"

LANDLORDS = [
    ("lord", 10),
    ("landlord_api_15_1120", 9),
    ("landlord_api_18_6465", 8),
    ("landlord_api_20_2369", 7),
    ("landlord_api_22_2561", 6),
    ("landlord_api_26_8962", 5),
]

PROPERTY_TYPES = ["apartment", "house", "studio", "villa", "other"]
CITIES = ["New York", "Los Angeles", "San Diego"]

TYPE_POOL = [t for t in PROPERTY_TYPES for _ in range(9)]
CITY_POOL = [c for c in CITIES for _ in range(15)]
random.shuffle(TYPE_POOL)
random.shuffle(CITY_POOL)

PRICE_RANGE = {
    "apartment": (110, 260),
    "house":     (160, 420),
    "studio":    ( 50, 120),
    "villa":     (320, 850),
    "other":     ( 40,  95),
}
BEDS_RANGE = {
    "apartment": (2, 4),
    "house":     (3, 6),
    "studio":    (1, 1),
    "villa":     (4, 8),
    "other":     (1, 3),
}

ADJ = [
    "Sunny", "Cozy", "Elegant", "Modern", "Spacious", "Quiet", "Charming",
    "Stylish", "Luxurious", "Bright", "Serene", "Vivid", "Airy", "Urban", "Classic",
    "Peaceful", "Lively", "Minimalist", "Green", "Sleek", "Rustic", "Vibrant", "Majestic",
    "Timeless", "Graceful", "Gleaming", "Fresh", "Bold", "Inviting", "Grand", "Pristine",
    "Tranquil", "Artistic", "Refined", "Warm", "Dreamy", "Smart", "Whimsical", "Opulent",
    "Sophisticated", "Picturesque", "Blissful", "Crisp", "Polished", "Shady", "Genteel"
]

NOUN = [
    "Retreat", "Hideaway", "Apartment", "Studio", "Residence", "Villa", "House",
    "Loft", "Flat", "Home", "Oasis", "Nest", "Haven", "Sanctuary", "Suite",
    "Den", "Bungalow", "Cottage", "Terrace", "Penthouse", "Domicile", "Corner",
    "Gallery", "Cabin", "Lodge", "Place", "Chalet", "Nook", "Space", "Abode",
    "Alcove", "Atrium", "Quarters", "Atrium", "Barn", "Porch", "Hall", "Mansion",
    "Manor", "Estate", "Quarters", "Shelter", "Pad"
]

STREET = [
    "Main St", "Broadway", "Maple Ave", "Park Ave", "Sunset Blvd", "Ocean Dr",
    "Pine St", "Fifth Ave", "Elm St", "Cedar Rd", "Hillcrest Dr", "Beacon St",
    "Linden Way", "Willow Lane", "King St", "Lakeview Dr", "River Rd", "Forest Ave",
    "Oak Blvd", "Cherry St", "Birch Rd", "Union Ave", "Garden Path", "Silver St",
    "Harbor Dr", "College Ave", "Bay Rd", "Central Blvd", "Aspen Ct", "Magnolia Way",
    "Bridge St", "Sycamore Ave", "Vineyard Rd", "Canyon Dr", "Rosemary Rd", "Spruce St",
    "Mill Ln", "Daisy Dr", "Pebble St", "Vista Blvd", "Crescent Ave", "Poplar Pl",
    "Sunrise Ter", "Dogwood Ln", "Maplewood Ave", "Foxglove Rd", "Chestnut St", "Olive Blvd"
]

PHRASES = [
    "boasting panoramic windows",
    "equipped with high-speed Wi-Fi",
    "surrounded by cafés and parks",
    "featuring a fully stocked kitchen",
    "decorated in warm earthy tones",
    "perfect for work-from-home stays",
    "offering complimentary parking",
    "with quick access to public transit",
    "nestled in a vibrant neighborhood",
    "providing smart-home automation",
    "overlooking the city skyline",
    "just steps away from the beach",
    "finished with designer furniture",
    "imbued with artistic flair",
    "embracing eco-friendly materials",
    "filled with natural light",
    "adorned with unique art pieces",
    "ideal for families and groups",
    "walking distance to downtown",
    "pet-friendly with a cozy yard",
    "offering breathtaking views",
    "minutes from shopping and dining",
    "with a private balcony or terrace",
    "complete with in-unit laundry",
    "surrounded by green spaces",
    "featuring a tranquil courtyard",
    "including all modern conveniences",
    "with a bright open-concept layout",
    "located in a secure community",
    "with on-site fitness facilities",
    "enriched by vibrant local culture",
    "highlighted by chic decor",
    "connected to major highways",
    "with a fully fenced backyard",
    "enjoying morning sun exposure",
    "perfect for relaxing evenings",
    "with dedicated workspace",
    "cooled by central air conditioning",
    "steps from public transportation",
    "outfitted with premium appliances",
    "including free Netflix and coffee",
    "within a gated community",
    "enhanced by rooftop access",
    "offering storage for bikes",
    "enjoying evening sunsets",
    "steps away from nightlife",
    "in a pet-friendly complex",
    "with a spacious walk-in closet",
    "with custom built-in shelving"
]

TODAY = datetime(2025, 5, 27)
ALWAYS_TOTAL = 15

def unique_title():
    return f"{random.choice(ADJ)} {random.choice(NOUN)}"

def unique_description(ptype, city):
    random.shuffle(PHRASES)
    core = ", ".join(PHRASES[:5])
    base = (
        f"This {ptype} located in {city} is {core}. "
        f"Enjoy authentic {city} vibes and book your stay today!"
    )
    return shorten(base, width=1000, placeholder="")

def random_address():
    return f"{random.randint(10, 9999)} {random.choice(STREET)}"

def rand_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def compose_payload(ptype, city, always_available):
    price = random.randint(*PRICE_RANGE[ptype])
    beds = random.randint(*BEDS_RANGE[ptype])
    available_from = rand_date(TODAY, datetime(2025, 12, 15))
    if always_available:
        available_to = None
    else:
        earliest_end = available_from + timedelta(days=7)
        latest_end = min(available_from + timedelta(days=120), datetime(2025, 12, 30))
        if earliest_end > latest_end:
            earliest_end, latest_end = available_from, available_from + timedelta(days=14)
        available_to = rand_date(earliest_end, latest_end).strftime("%Y-%m-%d")
    return {
        "title": unique_title(),
        "type": ptype,
        "description": unique_description(ptype, city),
        "price_per_day": price,
        "city": city,
        "address": random_address(),
        "beds": beds,
        "status": "active",
        "available_from": available_from.strftime("%Y-%m-%d"),
        "available_to": available_to,
        "always_available": always_available,
    }

def main():
    type_idx = 0
    city_idx = 0
    always_left = ALWAYS_TOTAL
    for username, quota in LANDLORDS:
        print(f"\n###  {username}  —  creating {quota} properties")
        auth = HTTPBasicAuth(username, PASSWORD)
        for _ in range(quota):
            ptype = TYPE_POOL[type_idx]; type_idx += 1
            city = CITY_POOL[city_idx]; city_idx += 1
            always_available = always_left > 0
            if always_available:
                always_left -= 1
            payload = compose_payload(ptype, city, always_available)
            try:
                r = requests.post(ENDPOINT, json=payload, auth=auth, timeout=15)
            except Exception as exc:
                print(f"  ✗  {payload['title']:<26}  network error: {exc}")
                continue
            if r.status_code in (200, 201):
                print(f"  ✓  {payload['title']:<26}  ({ptype}, {city})")
            else:
                print(f"  ✗  {payload['title']:<26}  HTTP {r.status_code}: {r.text[:120]}")
    print("\n=== Completed seeding 45 properties ===")

if __name__ == "__main__":
    main()
