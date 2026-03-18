import os
import requests
from typing import List, Optional
from dotenv import load_dotenv

# Load .env from config directory
load_dotenv(os.path.join(os.path.dirname(__file__), "../../resources/config/.env"))

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from models import CoffeeShop, Review

PLACES_API_BASE = "https://maps.googleapis.com/maps/api/place"


class GoogleMapsService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not found in .env")

    def search_coffee_shops(self, district: str, city: str = "台北市") -> List[CoffeeShop]:
        """Search for coffee shops in a given district."""
        query = f"{city}{district} 咖啡廳"
        url = f"{PLACES_API_BASE}/textsearch/json"
        params = {
            "query": query,
            "type": "cafe",
            "language": "zh-TW",
            "key": self.api_key,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(f"Google Maps API error: {data.get('status')} — {data.get('error_message', '')}")

        shops = []
        for result in data.get("results", []):
            shop = self._parse_basic(result, district)
            shops.append(shop)
        return shops

    def get_shop_details(self, shop: CoffeeShop) -> CoffeeShop:
        """Fetch full details and reviews for a shop."""
        url = f"{PLACES_API_BASE}/details/json"
        params = {
            "place_id": shop.place_id,
            "fields": "name,formatted_phone_number,website,opening_hours,photos,reviews,geometry",
            "language": "zh-TW",
            "key": self.api_key,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json().get("result", {})

        shop.phone = result.get("formatted_phone_number")
        shop.website = result.get("website")
        shop.opening_hours = result.get("opening_hours", {}).get("weekday_text", [])

        # Location
        location = result.get("geometry", {}).get("location", {})
        shop.lat = location.get("lat")
        shop.lng = location.get("lng")

        # Photos (up to 3)
        photos = result.get("photos", [])[:3]
        shop.photos = [self._photo_url(p["photo_reference"]) for p in photos]

        # Reviews — split into high (4–5 stars) and low (1–2 stars)
        reviews = result.get("reviews", [])
        for r in reviews:
            review = Review(
                author=r.get("author_name", ""),
                rating=r.get("rating", 0),
                text=r.get("text", ""),
                time=r.get("relative_time_description", ""),
            )
            if review.rating >= 4:
                shop.high_reviews.append(review)
            elif review.rating <= 2:
                shop.low_reviews.append(review)

        return shop

    def _parse_basic(self, result: dict, district: str) -> CoffeeShop:
        return CoffeeShop(
            place_id=result["place_id"],
            name=result.get("name", ""),
            address=result.get("formatted_address", ""),
            district=district,
            rating=result.get("rating", 0.0),
            total_ratings=result.get("user_ratings_total", 0),
        )

    def _photo_url(self, photo_reference: str, max_width: int = 400) -> str:
        return (
            f"{PLACES_API_BASE}/photo"
            f"?maxwidth={max_width}"
            f"&photo_reference={photo_reference}"
            f"&key={self.api_key}"
        )
