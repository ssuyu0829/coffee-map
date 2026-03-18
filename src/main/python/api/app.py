import os
import sys

# Ensure imports resolve from src/main/python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, jsonify, request, abort, render_template
from services import GoogleMapsService, search_shop_articles
from core import infer_tags

app = Flask(__name__,
            template_folder="templates",
            static_folder="static")
maps = GoogleMapsService()

@app.route("/")
def index():
    return render_template("index.html")


# ── City → District mapping ───────────────────────────
CITY_DISTRICTS = {
    "台北市": [
        "中正區", "大同區", "中山區", "松山區", "大安區",
        "萬華區", "信義區", "士林區", "北投區", "內湖區",
        "南港區", "文山區",
    ],
    "新北市": [
        "板橋區", "三重區", "中和區", "永和區", "新莊區",
        "新店區", "樹林區", "鶯歌區", "三峽區", "淡水區",
        "汐止區", "瑞芳區", "土城區", "蘆洲區", "五股區",
        "泰山區", "林口區", "深坑區", "石碇區", "坪林區",
        "三芝區", "石門區", "八里區", "平溪區", "雙溪區",
        "貢寮區", "金山區", "萬里區", "烏來區",
    ],
}


@app.route("/api/cities")
def get_cities():
    """Return list of supported cities."""
    return jsonify({"cities": list(CITY_DISTRICTS.keys())})


@app.route("/api/districts")
def get_districts():
    """Return districts for a city. Query param: ?city=台北市"""
    city = request.args.get("city", "").strip()
    if not city:
        abort(400, description="city query param is required")
    if city not in CITY_DISTRICTS:
        abort(400, description=f"Unknown city: {city}")
    return jsonify({"city": city, "districts": CITY_DISTRICTS[city]})


@app.route("/api/shops")
def search_shops():
    """
    Search coffee shops by city + district.
    Query params:
      - city (required): e.g. 台北市
      - district (required): e.g. 大安區
      - tags (optional, comma-separated): e.g. 讀書,wifi
    """
    city     = request.args.get("city", "").strip()
    district = request.args.get("district", "").strip()

    if not city:
        abort(400, description="city query param is required")
    if not district:
        abort(400, description="district query param is required")
    if city not in CITY_DISTRICTS:
        abort(400, description=f"Unknown city: {city}")
    if district not in CITY_DISTRICTS[city]:
        abort(400, description=f"Unknown district '{district}' for {city}")

    tag_filter = [t.strip() for t in request.args.get("tags", "").split(",") if t.strip()]

    shops = maps.search_coffee_shops(district=district, city=city)

    results = []
    for shop in shops:
        shop = maps.get_shop_details(shop)
        all_reviews = shop.high_reviews + shop.low_reviews
        shop.tags = infer_tags(shop.name, all_reviews, shop.opening_hours)

        if tag_filter and not any(t in shop.tags for t in tag_filter):
            continue

        results.append(shop.to_dict())

    return jsonify({"city": city, "district": district, "count": len(results), "shops": results})


@app.route("/api/shops/<place_id>")
def get_shop(place_id: str):
    """Get full details for a single shop by Google Maps place_id."""
    from models import CoffeeShop
    stub = CoffeeShop(
        place_id=place_id,
        name="", address="", district="",
        rating=0.0, total_ratings=0,
    )
    shop = maps.get_shop_details(stub)
    all_reviews = shop.high_reviews + shop.low_reviews
    shop.tags = infer_tags(shop.name, all_reviews, shop.opening_hours)
    articles = search_shop_articles(shop.name)
    shop.articles = [{"title": a.title, "url": a.url, "source": a.source} for a in articles]
    return jsonify(shop.to_dict())


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5001))
    debug = os.getenv("FLASK_ENV") == "development"
    print(f"Starting Coffee Map API on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
