from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Review:
    author: str
    rating: int        # 1–5
    text: str
    time: str


@dataclass
class CoffeeShop:
    place_id: str                      # Google Maps unique ID
    name: str
    address: str
    district: str                      # e.g. 大安區, 信義區
    rating: float                      # overall Google Maps rating
    total_ratings: int
    tags: List[str] = field(default_factory=list)
    phone: Optional[str] = None
    website: Optional[str] = None
    opening_hours: List[str] = field(default_factory=list)
    photos: List[str] = field(default_factory=list)
    lat: Optional[float] = None
    lng: Optional[float] = None
    is_open_now: Optional[bool] = None          # from Google API open_now field
    high_reviews: List[Review] = field(default_factory=list)
    low_reviews: List[Review] = field(default_factory=list)
    articles: List[dict] = field(default_factory=list)
    # Café Nomad scores (0–5 float, or None if not matched)
    nomad_wifi: Optional[float] = None
    nomad_quiet: Optional[float] = None
    nomad_tasty: Optional[float] = None
    nomad_socket: Optional[str] = None       # "yes" | "no" | "maybe"
    nomad_limited_time: Optional[str] = None # "yes" | "no" | "maybe"

    def to_dict(self) -> dict:
        return {
            "place_id": self.place_id,
            "name": self.name,
            "address": self.address,
            "district": self.district,
            "rating": self.rating,
            "total_ratings": self.total_ratings,
            "tags": self.tags,
            "phone": self.phone,
            "website": self.website,
            "opening_hours": self.opening_hours,
            "photos": self.photos,
            "lat": self.lat,
            "lng": self.lng,
            "is_open_now": self.is_open_now,
            "high_reviews": [r.__dict__ for r in self.high_reviews],
            "low_reviews": [r.__dict__ for r in self.low_reviews],
            "articles": self.articles,
            "nomad_wifi": self.nomad_wifi,
            "nomad_quiet": self.nomad_quiet,
            "nomad_tasty": self.nomad_tasty,
            "nomad_socket": self.nomad_socket,
            "nomad_limited_time": self.nomad_limited_time,
        }
