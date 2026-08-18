#!/usr/bin/env python3
"""
fetch_news.py — Multi-source travel news fetcher with fallback chain.

Tries APIs in order; if one fails, moves to the next:
  1. GNews API (free 100 req/day)
  2. Google Custom Search JSON API (free 100 req/day)
  3. MediaStack API (free 500 req/month)
  4. Direct RSS feeds (feedparser)

Deduplicates against existing data/travel_daily.json.
Outputs structured JSON with today's travel news for 25 countries.
"""

import json
import os
import re
import sys
import time
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from difflib import SequenceMatcher

import requests
import feedparser

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("fetch_news")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "travel_daily.json"

# Import curated sources
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sources import COUNTRIES, CATEGORIES, get_all_country_names, SEARCH_TERMS

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def title_similarity(a: str, b: str) -> float:
    """Return sequence similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def make_article_id(title: str, url: str) -> str:
    """Generate a stable hash ID for an article."""
    raw = f"{title.strip().lower()}|{url.strip()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def load_existing_data() -> dict:
    """Load existing travel_daily.json or return empty structure."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            log.info(f"Loaded existing data: {len(data.get('dates', {}))} date entries")
            return data
        except (json.JSONDecodeError, IOError) as e:
            log.warning(f"Could not load existing data: {e}")
    return {"today": "", "window": "", "dates": {}}


def is_duplicate(new_title: str, new_summary: str, existing_articles: list, threshold: float = 0.80) -> bool:
    """Check if an article is a duplicate based on title + summary similarity."""
    for article in existing_articles:
        # Title similarity
        if title_similarity(new_title, article.get("title", "")) > threshold:
            return True
        # Summary overlap
        existing_summary = article.get("summary", "")
        if existing_summary and new_summary:
            if title_similarity(new_summary[:200], existing_summary[:200]) > threshold:
                return True
    return False


def classify_category(title: str, summary: str = "") -> str:
    """Classify an article into one of the defined categories."""
    combined = f"{title} {summary}".lower()
    scores = {}
    for cat_key, cat_data in CATEGORIES.items():
        score = sum(1 for kw in cat_data["keywords"] if kw.lower() in combined)
        scores[cat_key] = score
    if max(scores.values()) == 0:
        return "policy"  # default category
    return max(scores, key=scores.get)


def save_data(data: dict):
    """Save travel_daily.json."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info(f"Saved data to {DATA_FILE}")


def get_today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Source 1: GNews API
# ---------------------------------------------------------------------------
def fetch_gnews(country: str, keywords: list) -> list:
    """Fetch from GNews API. Free tier: 100 requests/day."""
    api_key = os.environ.get("GNEWS_API_KEY", "")
    if not api_key:
        log.info("GNews: No API key configured, skipping")
        return []

    articles = []
    base_url = "https://gnews.io/api/v4/search"

    # Use first 2 keywords per country to conserve quota
    search_queries = [
        f"{country} travel tourism",
        f"{country} visa immigration"
    ]

    for query in search_queries:
        try:
            params = {
                "q": query,
                "lang": "en",
                "max": 10,
                "sortby": "publishedAt",
                "from": (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "apikey": api_key
            }
            resp = requests.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("articles", []):
                articles.append({
                    "title": item.get("title", ""),
                    "summary": item.get("description", ""),
                    "url": item.get("url", ""),
                    "source": item.get("source", {}).get("name", "GNews"),
                    "published": item.get("publishedAt", ""),
                    "country": country,
                    "fetch_source": "gnews"
                })
            log.info(f"GNews [{country}]: {len(data.get('articles', []))} articles for '{query}'")
            time.sleep(1)  # Rate limit awareness
        except requests.exceptions.RequestException as e:
            log.warning(f"GNews [{country}] error: {e}")

    return articles


# ---------------------------------------------------------------------------
# Source 2: Google Custom Search JSON API
# ---------------------------------------------------------------------------
def fetch_google_cse(country: str, keywords: list) -> list:
    """Fetch from Google Custom Search JSON API. Free tier: 100 queries/day."""
    api_key = os.environ.get("GOOGLE_CSE_API_KEY", "")
    engine_id = os.environ.get("GOOGLE_CSE_ENGINE_ID", "")
    if not api_key or not engine_id:
        log.info("Google CSE: Missing API key or Engine ID, skipping")
        return []

    articles = []
    base_url = "https://customsearch.googleapis.com/customsearch/v1"

    search_query = f"travel tourism visa news {country} 2026"
    try:
        params = {
            "q": search_query,
            "cx": engine_id,
            "key": api_key,
            "num": 10,
            "sort": "date",
            "dateRestrict": "m1"  # past month
        }
        resp = requests.get(base_url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("items", []):
            articles.append({
                "title": item.get("title", ""),
                "summary": item.get("snippet", ""),
                "url": item.get("link", ""),
                "source": item.get("displayLink", "Google CSE"),
                "published": "",  # CSE doesn't always return dates
                "country": country,
                "fetch_source": "google_cse"
            })
        log.info(f"Google CSE [{country}]: {len(data.get('items', []))} results")
        time.sleep(1)
    except requests.exceptions.RequestException as e:
        log.warning(f"Google CSE [{country}] error: {e}")

    return articles


# ---------------------------------------------------------------------------
# Source 3: MediaStack API
# ---------------------------------------------------------------------------
def fetch_mediastack(country: str, keywords: list) -> list:
    """Fetch from MediaStack API. Free tier: 500 requests/month."""
    api_key = os.environ.get("MEDIASTACK_API_KEY", "")
    if not api_key:
        log.info("MediaStack: No API key configured, skipping")
        return []

    articles = []
    base_url = "http://api.mediastack.com/v1/news"

    search_keywords = f"travel,tourism,{country.lower()}"
    try:
        params = {
            "access_key": api_key,
            "keywords": search_keywords,
            "languages": "en",
            "limit": 10,
            "sort": "published_desc",
            "countries": _country_code(country)
        }
        resp = requests.get(base_url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("data", []):
            articles.append({
                "title": item.get("title", ""),
                "summary": item.get("description", ""),
                "url": item.get("url", ""),
                "source": item.get("source", "MediaStack"),
                "published": item.get("published_at", ""),
                "country": country,
                "fetch_source": "mediastack"
            })
        log.info(f"MediaStack [{country}]: {len(data.get('data', []))} articles")
        time.sleep(1)
    except requests.exceptions.RequestException as e:
        log.warning(f"MediaStack [{country}] error: {e}")

    return articles


def _country_code(country_name: str) -> str:
    """Map country name to ISO 3166-1 alpha-2 code for MediaStack."""
    mapping = {
        "Thailand": "TH", "Japan": "JP", "South Korea": "KR", "Singapore": "SG",
        "Vietnam": "VN", "Indonesia": "ID", "Malaysia": "MY", "Philippines": "PH",
        "China": "CN", "India": "IN", "United States": "US", "United Kingdom": "GB",
        "France": "FR", "Germany": "DE", "Spain": "ES", "Italy": "IT",
        "Australia": "AU", "New Zealand": "NZ", "Canada": "CA", "Mexico": "MX",
        "UAE": "AE", "Turkey": "TR", "Egypt": "EG", "Brazil": "BR", "South Africa": "ZA"
    }
    return mapping.get(country_name, "")


# ---------------------------------------------------------------------------
# Source 4: RSS Feeds (fallback)
# ---------------------------------------------------------------------------
def fetch_rss(country: str, keywords: list) -> list:
    """Fetch from RSS feeds. No API key needed. Unlimited but depends on feed freshness."""
    from sources import COUNTRIES as SRC
    articles = []

    country_data = SRC.get(country, {})
    rss_urls = []

    # Tourism board RSS
    tb = country_data.get("tourism_board", {})
    if tb.get("rss"):
        rss_urls.append((tb["rss"], tb["name"]))

    # Also try international feeds for this country
    from sources import INTERNATIONAL_RSS_FEEDS
    for feed_info in INTERNATIONAL_RSS_FEEDS:
        rss_urls.append((feed_info["url"], feed_info["name"]))

    for url, source_name in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                title = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))
                # Filter: only include if country name or relevant keyword in title/summary
                combined = f"{title} {summary}".lower()
                if country.lower() in combined or any(kw.lower() in combined for kw in ["travel", "tourism", "visa", "flight"]):
                    pub_date = ""
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        try:
                            pub_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%dT%H:%M:%SZ")
                        except Exception:
                            pass
                    articles.append({
                        "title": title,
                        "summary": re.sub(r'<[^>]+>', '', summary),  # strip HTML
                        "url": entry.get("link", ""),
                        "source": source_name,
                        "published": pub_date,
                        "country": country,
                        "fetch_source": "rss"
                    })
            log.info(f"RSS [{country}] via {source_name}: added {len(articles)} articles total so far")
        except Exception as e:
            log.warning(f"RSS [{country}] feed error ({url}): {e}")
        time.sleep(0.5)

    return articles


# ---------------------------------------------------------------------------
# Fallback chain orchestrator
# ---------------------------------------------------------------------------
def fetch_for_country(country: str, keywords: list) -> list:
    """Try each source in order. Use first source that returns results."""
    sources = [
        ("GNews", fetch_gnews),
        ("Google CSE", fetch_google_cse),
        ("MediaStack", fetch_mediastack),
        ("RSS", fetch_rss),
    ]

    for source_name, fetch_fn in sources:
        log.info(f"Trying {source_name} for {country}...")
        try:
            articles = fetch_fn(country, keywords)
            if articles:
                log.info(f"✅ {source_name} returned {len(articles)} articles for {country}")
                return articles
            else:
                log.info(f"⚠️ {source_name} returned 0 articles for {country}, trying next...")
        except Exception as e:
            log.error(f"❌ {source_name} failed for {country}: {e}")

    log.warning(f"🚨 ALL sources failed for {country}")
    return []


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main():
    log.info("=" * 60)
    log.info("🌍 Travel News Fetcher — Starting pipeline")
    log.info("=" * 60)

    today = get_today_str()
    log.info(f"Today (UTC): {today}")

    # Load existing data for deduplication
    existing_data = load_existing_data()
    all_existing_articles = []
    for date_key, date_data in existing_data.get("dates", {}).items():
        for country_articles in date_data.get("countries", {}).values():
            all_existing_articles.extend(country_articles)

    countries = get_all_country_names()
    log.info(f"Processing {len(countries)} countries")

    today_data = {
        "date": today,
        "fetch_time": datetime.now(timezone.utc).isoformat(),
        "countries": {}
    }

    source_stats = {"gnews": 0, "google_cse": 0, "mediastack": 0, "rss": 0, "failed": 0}
    total_new = 0
    total_dup = 0

    for country in countries:
        keywords = COUNTRIES.get(country, {}).get("keywords", [f"{country} travel"])
        raw_articles = fetch_for_country(country, keywords)

        if not raw_articles:
            source_stats["failed"] += 1
            today_data["countries"][country] = []
            continue

        # Classify + deduplicate
        country_articles = []
        for article in raw_articles:
            # Skip if duplicate
            if is_duplicate(article["title"], article["summary"], all_existing_articles + country_articles):
                total_dup += 1
                continue

            # Assign category
            article["category"] = classify_category(article["title"], article["summary"])
            article["id"] = make_article_id(article["title"], article["url"])
            country_articles.append(article)
            total_new += 1

            # Track source
            src = article.get("fetch_source", "unknown")
            if src in source_stats:
                source_stats[src] += 1

        # Enforce per-country limit (10 max) and category quotas
        country_articles = enforce_quotas(country_articles, country)
        today_data["countries"][country] = country_articles
        log.info(f"  {country}: {len(country_articles)} new articles (after dedup & quotas)")

    # Update the master data
    existing_data["today"] = today
    window_end = (datetime.now(timezone.utc) + timedelta(days=6)).strftime("%Y-%m-%d")
    existing_data["window"] = f"{today} ~ {window_end}"
    existing_data.setdefault("dates", {})[today] = today_data

    # Prune dates older than 30 days to keep file size manageable
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    old_keys = [k for k in existing_data["dates"] if k < cutoff]
    for k in old_keys:
        del existing_data["dates"][k]
        log.info(f"Pruned old date: {k}")

    save_data(existing_data)

    # Summary report
    log.info("=" * 60)
    log.info("📊 FETCH SUMMARY")
    log.info(f"  Date:          {today}")
    log.info(f"  Countries:     {len(countries)}")
    log.info(f"  New articles:  {total_new}")
    log.info(f"  Duplicates:    {total_dup}")
    log.info(f"  Sources used:  {source_stats}")
    log.info(f"  Failed:        {source_stats['failed']} countries with no data")
    log.info("=" * 60)

    if source_stats["failed"] == len(countries):
        log.error("❌ CRITICAL: All countries failed to fetch. Check API keys and network.")
        sys.exit(1)

    log.info("✅ Pipeline complete")


def enforce_quotas(articles: list, country: str) -> list:
    """Enforce per-category quotas to ensure diverse coverage."""
    # Count articles per category
    cat_counts = {}
    selected = []
    skipped = []

    for article in articles:
        cat = article.get("category", "policy")
        quota = CATEGORIES.get(cat, {}).get("quota", 2)
        current = cat_counts.get(cat, 0)

        if current < quota:
            selected.append(article)
            cat_counts[cat] = current + 1
        else:
            skipped.append(article)

    # If we have room (under 10 total), fill from skipped
    remaining = 10 - len(selected)
    if remaining > 0:
        selected.extend(skipped[:remaining])

    return selected[:10]


if __name__ == "__main__":
    main()
