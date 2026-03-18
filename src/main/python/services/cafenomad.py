"""
Café Nomad API integration.
API: https://cafenomad.tw/api/v1.2/cafes/{city}
Free, no API key required.
Data is cached in-memory for 6 hours to reduce redundant calls.
"""
import math
import time
import requests

# City name → Café Nomad slug
CITY_SLUGS = {
    "台北市": "taipei",
    "新北市": "new-taipei",
}

_CACHE: dict = {}         # slug → {"data": [...], "ts": float}
_CACHE_TTL = 6 * 3600     # 6 hours


def get_cafes(city: str) -> list:
    """Return all Café Nomad entries for a city (cached 6 hrs)."""
    slug = CITY_SLUGS.get(city)
    if not slug:
        return []

    entry = _CACHE.get(slug)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL:
        return entry["data"]

    try:
        resp = requests.get(
            f"https://cafenomad.tw/api/v1.2/cafes/{slug}",
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    _CACHE[slug] = {"data": data, "ts": time.time()}
    return data


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(d_lng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def match_shop(lat: float, lng: float, cafes: list, max_dist_m: float = 100) -> dict | None:
    """
    Return the closest Café Nomad entry within max_dist_m metres,
    or None if no match found.
    """
    if not lat or not lng:
        return None

    best = None
    best_dist = float("inf")
    for cafe in cafes:
        try:
            c_lat = float(cafe["latitude"])
            c_lng = float(cafe["longitude"])
        except (KeyError, ValueError, TypeError):
            continue

        dist_m = _haversine_km(lat, lng, c_lat, c_lng) * 1000
        if dist_m < best_dist:
            best_dist = dist_m
            best = cafe

    if best_dist <= max_dist_m:
        return best
    return None
