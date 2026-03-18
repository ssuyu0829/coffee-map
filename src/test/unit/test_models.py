import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main/python"))

from models import CoffeeShop, Review


def test_coffee_shop_to_dict():
    shop = CoffeeShop(
        place_id="abc123",
        name="測試咖啡",
        address="台北市大安區忠孝東路",
        district="大安區",
        rating=4.5,
        total_ratings=120,
        tags=["讀書", "不限時", "wifi"],
    )
    d = shop.to_dict()
    assert d["name"] == "測試咖啡"
    assert d["district"] == "大安區"
    assert "讀書" in d["tags"]
    assert d["high_reviews"] == []


def test_review_fields():
    r = Review(author="Alice", rating=5, text="很棒！", time="2024-01-01")
    assert r.rating == 5
    assert r.author == "Alice"
