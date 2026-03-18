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
    tags: List[str] = field(default_factory=list)   # 讀書、不限時、外帶店, etc.
    phone: Optional[str] = None
    website: Optional[str] = None
    opening_hours: List[str] = field(default_factory=list)
    photos: List[str] = field(default_factory=list)  # photo URLs
    lat: Optional[float] = None
    lng: Optional[float] = None
    high_reviews: List[Review] = field(default_factory=list)  # top-rated reviews
    low_reviews: List[Review] = field(default_factory=list)   # critical reviews
    articles: List[dict] = field(default_factory=list)   # [{"title":..,"url":..,"source":..}]

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
            "high_reviews": [r.__dict__ for r in self.high_reviews],
            "low_reviews": [r.__dict__ for r in self.low_reviews],
            "articles": self.articles,
        }
