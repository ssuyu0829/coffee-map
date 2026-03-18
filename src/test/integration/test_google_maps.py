"""
Integration test — requires a valid GOOGLE_MAPS_API_KEY in .env
Run with: pytest src/test/integration/test_google_maps.py -v -s
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from services import GoogleMapsService


def test_search_returns_shops():
    svc = GoogleMapsService()
    shops = svc.search_coffee_shops(district="大安區")
    assert len(shops) > 0, "Should return at least one shop"
    shop = shops[0]
    assert shop.place_id
    assert shop.name
    assert shop.district == "大安區"
    print(f"\nFound {len(shops)} shops. First: {shop.name} ({shop.rating}★)")


def test_get_shop_details():
    svc = GoogleMapsService()
    shops = svc.search_coffee_shops(district="大安區")
    assert shops, "Need at least one shop to test details"

    shop = svc.get_shop_details(shops[0])
    assert shop.lat is not None
    assert shop.lng is not None
    print(f"\nDetails for: {shop.name}")
    print(f"  Phone: {shop.phone}")
    print(f"  Location: {shop.lat}, {shop.lng}")
    print(f"  High reviews: {len(shop.high_reviews)}")
    print(f"  Low reviews:  {len(shop.low_reviews)}")
    if shop.opening_hours:
        print(f"  Hours: {shop.opening_hours[0]}")
