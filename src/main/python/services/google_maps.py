import os
import time
import requests
from typing import List
from dotenv import load_dotenv

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
        """Search coffee shops by district, fetching up to 3 pages (60 results)."""
        query = f"{city}{district} 咖啡廳"
        params = {
            "query": query,
            "type": "cafe",
            "language": "zh-TW",
            "key": self.api_key,
        }
        return self._fetch_pages(f"{PLACES_API_BASE}/textsearch/json", params, district)

    def search_nearby(self, lat: float, lng: float, radius: int = 1500) -> List[CoffeeShop]:
        """Search coffee shops near a lat/lng coordinate."""
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": "cafe",
            "keyword": "咖啡廳",
            "language": "zh-TW",
            "key": self.api_key,
        }
        return self._fetch_pages(f"{PLACES_API_BASE}/nearbysearch/json", params, district="附近")

    def _fetch_pages(self, url: str, params: dict, district: str,
                     max_results: int = 30) -> List[CoffeeShop]:
        """Fetch up to max_results shops across multiple pages."""
        all_shops = []
        for page in range(3):
            if page > 0:
                time.sleep(2)

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            status = data.get("status")
            if status == "ZERO_RESULTS":
                break
            if status not in ("OK", "INVALID_REQUEST"):
                raise RuntimeError(f"Google Maps API error: {status} — {data.get('error_message', '')}")

            for result in data.get("results", []):
                all_shops.append(self._parse_basic(result, district))
                if len(all_shops) >= max_results:
                    return all_shops

            next_token = data.get("next_page_token")
            if not next_token:
                break
            params = {"pagetoken": next_token, "key": self.api_key}

        return all_shops

    def get_shop_details(self, shop: CoffeeShop) -> CoffeeShop:
        """Fetch full details and reviews for a shop."""
        url = f"{PLACES_API_BASE}/details/json"
        params = {
            "place_id": shop.place_id,
            "fields": "name,formatted_phone_number,website,opening_hours,photos,reviews,geometry",
            "language": "zh-TW",
            "key": self.api_key,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json().get("result", {})

        shop.phone = result.get("formatted_phone_number")
        shop.website = result.get("website")

        hours_data = result.get("opening_hours", {})
        shop.opening_hours = hours_data.get("weekday_text", [])
        if shop.is_open_now is None:
            shop.is_open_now = hours_data.get("open_now")

        location = result.get("geometry", {}).get("location", {})
        shop.lat = location.get("lat")
        shop.lng = location.get("lng")

        photos = result.get("photos", [])[:3]
        shop.photos = [self._photo_url(p["photo_reference"]) for p in photos]

        for r in result.get("reviews", []):
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
        # Extract photo and coords available in basic search result (no Details call needed)
        location = result.get("geometry", {}).get("location", {})
        photos = []
        if result.get("photos"):
            photos = [self._photo_url(result["photos"][0]["photo_reference"])]
        address = result.get("formatted_address") or result.get("vicinity", "")
        return CoffeeShop(
            place_id=result["place_id"],
            name=result.get("name", ""),
            address=address,
            district=district,
            rating=result.get("rating", 0.0),
            total_ratings=result.get("user_ratings_total", 0),
            is_open_now=result.get("opening_hours", {}).get("open_now"),
            lat=location.get("lat"),
            lng=location.get("lng"),
            photos=photos,
        )

    def _photo_url(self, photo_reference: str, max_width: int = 400) -> str:
        return (
            f"{PLACES_API_BASE}/photo"
            f"?maxwidth={max_width}"
            f"&photo_reference={photo_reference}"
            f"&key={self.api_key}"
        )
