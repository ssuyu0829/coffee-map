"""
Scrapes article links about a coffee shop from food/lifestyle sites.
Uses DuckDuckGo HTML search (no API key required) and filters to trusted sources.
"""
import time
import requests
from bs4 import BeautifulSoup
from typing import List
from dataclasses import dataclass

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}

# Trusted food/lifestyle domains to keep
TRUSTED_DOMAINS = [
    "ifoodie.tw",
    "tasteful.tw",
    "timeout.com",
    "thecoffeetraveler.net",
    "barista.com.tw",
    "cafenomad.tw",
    "cw.com.tw",
    "cheers.com.tw",
    "cwlife.com.tw",
    "nomadcafe.tw",
    "tw.trip.com",
    "klook.com",
    "tripadvisor.com",
    "google.com/maps",
    "shop.coffee",
    "beautifullife.info",
    "colatour.com.tw",
]


@dataclass
class Article:
    title: str
    url: str
    source: str


def search_shop_articles(shop_name: str, max_results: int = 3) -> List[Article]:
    """Search DuckDuckGo for articles about a coffee shop."""
    query = f"{shop_name} 咖啡廳 評價 推薦"
    url = "https://html.duckduckgo.com/html/"
    try:
        resp = requests.post(
            url,
            data={"q": query, "kl": "tw-tzh"},
            headers=HEADERS,
            timeout=8,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []

    for result in soup.select(".result__body"):
        title_el = result.select_one(".result__title")
        link_el  = result.select_one(".result__url")
        if not title_el or not link_el:
            continue

        title = title_el.get_text(strip=True)
        raw_url = link_el.get_text(strip=True)

        # Skip non-trusted domains
        domain = _extract_domain(raw_url)
        if not any(trusted in domain for trusted in TRUSTED_DOMAINS):
            continue

        # Get the actual href from the <a> inside title
        href_el = title_el.find("a")
        href = href_el["href"] if href_el and href_el.get("href") else raw_url

        articles.append(Article(title=title, url=href, source=domain))
        if len(articles) >= max_results:
            break

    return articles


def enrich_shops_with_articles(shops: list, delay: float = 0.5) -> list:
    """Add articles to a list of CoffeeShop objects. Mutates in place."""
    for shop in shops:
        articles = search_shop_articles(shop.name)
        shop.articles = [a.url for a in articles]
        shop._article_details = [
            {"title": a.title, "url": a.url, "source": a.source}
            for a in articles
        ]
        time.sleep(delay)   # be polite to DuckDuckGo
    return shops


def _extract_domain(url: str) -> str:
    url = url.lower().replace("https://", "").replace("http://", "")
    return url.split("/")[0]
