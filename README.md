# 🌍 Travel Dashboard Automation Kit

Daily automated travel news dashboard for 25 countries, powered by GitHub Actions.

## Overview

This kit automatically fetches travel/tourism/visa/aviation news from multiple API sources, deduplicates against historical data, and generates a responsive HTML dashboard deployed via GitHub Pages.

**Why multiple sources?** Several free APIs were tried on GitHub Actions and failed:
- ❌ DuckDuckGo → IP blocked on GitHub Actions servers
- ❌ Hugging Face → DNS failure
- ❌ NewsData.io → returned 0 results
- ❌ Google News RSS → returned messy HTML

This kit uses a **fallback chain** — if one source fails, it automatically tries the next.

---

## Architecture

```
.github/workflows/daily-travel.yml   ← GitHub Actions workflow (cron + manual)
scripts/
  fetch_news.py                      ← Multi-source news fetcher with fallback chain
  generate_dashboard.py              ← HTML dashboard generator
  sources.py                         ← 25-country curated source list + categories
data/
  travel_daily.json                  ← Persistent JSON data store
docs/
  index.html                         ← Generated dashboard (GitHub Pages)
requirements.txt                     ← Python dependencies
```

---

## Quick Start

### 1. Copy to your repository

```bash
# From your repo root
cp -r github-auto-kit/.github .
cp -r github-auto-kit/scripts .
cp -r github-auto-kit/data .
cp -r github-auto-kit/docs .
cp github-auto-kit/requirements.txt .
```

### 2. Configure API Keys as GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name | Required? | How to Get |
|---|---|---|
| `GNEWS_API_KEY` | Recommended (first choice) | [gnews.io](https://gnews.io/) — Free 100 req/day |
| `GOOGLE_CSE_API_KEY` | Recommended (fallback #1) | [Google Cloud Console](https://console.cloud.google.com/) — Free 100 queries/day |
| `GOOGLE_CSE_ENGINE_ID` | Required with above | [Programmable Search Engine](https://programmablesearchengine.google.com/) |
| `MEDIASTACK_API_KEY` | Fallback #2 | [mediastack.com](https://mediastack.com/) — Free 500 req/month |

> 💡 **Tip:** At least one API key is needed for best results. The RSS fallback works without keys but has less structured results.

### 3. Set Up Google Custom Search (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable "Custom Search JSON API"
3. Create API credentials → Copy the API key → Add as `GOOGLE_CSE_API_KEY` secret
4. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
5. Create a new search engine → Enable "Search the entire web"
6. Copy the Search Engine ID → Add as `GOOGLE_CSE_ENGINE_ID` secret

### 4. Enable GitHub Pages

Go to **Settings** → **Pages** → Source: **Deploy from a branch** → Branch: `main` / folder: `/docs` → **Save**

Your dashboard will be at: `https://<your-username>.github.io/<repo-name>/`

### 5. First Run

Go to **Actions** → **Daily Travel Dashboard Update** → **Run workflow** → **Run workflow**

---

## Customization

### Change the schedule

Edit `.github/workflows/daily-travel.yml`:
```yaml
schedule:
  - cron: '0 9 * * *'  # Change this cron expression (UTC time)
```

Common options:
- `'0 9 * * *'` — Daily at 9:00 AM UTC
- `'0 2 * * *'` — Daily at 2:00 AM UTC (low traffic)
- `'0 */12 * * *'` — Every 12 hours
- `'0 9 * * 1-5'` — Weekdays only at 9:00 AM UTC

### Add/remove countries

Edit `scripts/sources.py` → `COUNTRIES` dict. Each country needs:
```python
"CountryName": {
    "tourism_board": {"name": "...", "url": "...", "rss": "..."},
    "immigration": {"name": "...", "url": "..."},
    "news_sites": [{"name": "...", "url": "..."}],
    "keywords": ["search term 1", "search term 2"]
}
```

### Adjust category quotas

Edit `scripts/sources.py` → `CATEGORIES` dict. The `quota` field controls max articles per category per country.

### Change dedup threshold

In `scripts/fetch_news.py`, the `is_duplicate()` function has a `threshold` parameter (default `0.80`). Lower = stricter dedup, higher = more lenient.

---

## How It Works

### Fetch Pipeline

```
For each of 25 countries:
  1. Try GNews API → if results, use them
  2. Else try Google CSE → if results, use them
  3. Else try MediaStack → if results, use them
  4. Else try RSS feeds → if results, use them
  5. If all fail → mark country as failed

For each fetched article:
  - Classify into category (visa/aviation/tourism/digital/event/policy)
  - Check against historical data for duplicates (>80% title/summary similarity)
  - Enforce per-category quotas (max articles per type)
  - Cap at 10 articles per country

Save to data/travel_daily.json
Generate docs/index.html
Commit and push
GitHub Pages deploys automatically
```

### Rate Limit Budget

| API | Free Tier | Daily Usage (25 countries) |
|---|---|---|
| GNews | 100 req/day | ~50 req (2 queries × 25 countries) |
| Google CSE | 100 queries/day | ~25 queries (1 per country) |
| MediaStack | 500 req/month | ~25 req/day = 750/month (may exceed) |

> The fallback chain means only ONE API is used per day (whichever succeeds first), so you stay well within free tiers.

---

## Troubleshooting

### "All countries failed to fetch"

- **Check API keys:** Go to Actions → latest run → check environment variables
- **Check logs:** The fetch script logs each source attempt
- **Verify secrets:** Settings → Secrets → ensure keys are set correctly (no extra spaces)

### "Dashboard shows 0 articles"

- The data file might be empty. Trigger a manual run from Actions tab.
- Check if the API returned results in the workflow logs.

### "GitHub Pages not updating"

- Ensure Pages is configured: Settings → Pages → Source: `main` branch, `/docs` folder
- Check if the commit was pushed: the workflow commits `data/travel_daily.json` and `docs/index.html`
- GitHub Pages may take 1-2 minutes to deploy after push

### "Running out of API quota"

- The fallback chain is designed to use minimal API calls
- If GNews consistently works, other APIs are never called
- MediaStack monthly quota (500) may run out if used daily — that's fine, it's a fallback

### "Duplicate articles appearing"

- The dedup threshold is 80% similarity by default
- Lower it to 0.70 in `is_duplicate()` for stricter matching
- Very similar headlines from different sources may still pass — this is intentional

---

## File Structure

```
.
├── .github/
│   └── workflows/
│       └── daily-travel.yml      # GitHub Actions workflow
├── scripts/
│   ├── fetch_news.py             # Multi-source news fetcher
│   ├── generate_dashboard.py     # HTML dashboard generator
│   └── sources.py                # Curated source list
├── data/
│   └── travel_daily.json         # Persistent data store
├── docs/
│   └── index.html                # GitHub Pages output
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## License

MIT — Use freely for your travel dashboard projects.
