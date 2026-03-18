import os
import sys

# Ensure imports resolve from src/main/python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, jsonify, request, abort, render_template
from services import GoogleMapsService
from core import infer_tags

app = Flask(__name__,
            template_folder="templates",
            static_folder="static")
maps = GoogleMapsService()

@app.route("/")
def index():
    return render_template("index.html")


DISTRICTS = [
    "中正區", "大同區", "中山區", "松山區", "大安區",
    "萬華區", "信義區", "士林區", "北投區", "內湖區",
    "南港區", "文山區",
]


@app.route("/api/districts")
def get_districts():
    """Return list of Taipei districts."""
    return jsonify({"districts": DISTRICTS})


@app.route("/api/shops")
def search_shops():
    """
    Search coffee shops by district.
    Query params:
      - district (required): e.g. 大安區
      - tags (optional, comma-separated): filter by tags e.g. 讀書,wifi
    """
    district = request.args.get("district", "").strip()
    if not district:
        abort(400, description="district query param is required")
    if district not in DISTRICTS:
        abort(400, description=f"Unknown district. Choose from: {', '.join(DISTRICTS)}")

    tag_filter = [t.strip() for t in request.args.get("tags", "").split(",") if t.strip()]

    shops = maps.search_coffee_shops(district)

    # Enrich each shop with details + inferred tags
    results = []
    for shop in shops:
        shop = maps.get_shop_details(shop)
        all_reviews = shop.high_reviews + shop.low_reviews
        shop.tags = infer_tags(shop.name, all_reviews, shop.opening_hours)

        # Apply tag filter if provided
        if tag_filter and not any(t in shop.tags for t in tag_filter):
            continue

        results.append(shop.to_dict())

    return jsonify({"district": district, "count": len(results), "shops": results})


@app.route("/api/shops/<place_id>")
def get_shop(place_id: str):
    """Get full details for a single shop by Google Maps place_id."""
    from models import CoffeeShop
    # Minimal stub to fetch details — name/address filled by details call
    stub = CoffeeShop(
        place_id=place_id,
        name="", address="", district="",
        rating=0.0, total_ratings=0,
    )
    shop = maps.get_shop_details(stub)
    all_reviews = shop.high_reviews + shop.low_reviews
    shop.tags = infer_tags(shop.name, all_reviews, shop.opening_hours)
    return jsonify(shop.to_dict())


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    print(f"Starting Coffee Map API on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
