#!/usr/bin/env python3
"""
generate_dashboard.py — Reads data/travel_daily.json and generates docs/index.html.

Features:
  - 25 countries × 10 articles grid
  - 6 category badges with counts
  - Historical calendar (from dates in JSON)
  - Responsive design with dark/light mode
  - Auto-generated from data (no manual editing)
"""

import json
import sys
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("dashboard")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "travel_daily.json"
OUTPUT_FILE = BASE_DIR / "docs" / "index.html"

CATEGORY_META = {
    "visa":    {"label": "签证政策", "emoji": "🛂", "color": "#e74c3c"},
    "aviation": {"label": "航空交通", "emoji": "✈️", "color": "#3498db"},
    "tourism": {"label": "旅游推广", "emoji": "🏝️", "color": "#27ae60"},
    "digital": {"label": "数字便利", "emoji": "📱", "color": "#9b59b6"},
    "event":   {"label": "大型活动", "emoji": "🎪", "color": "#f39c12"},
    "policy":  {"label": "法规政策", "emoji": "📋", "color": "#1abc9c"},
}

FLAG_EMOJI = {
    "Thailand": "🇹🇭", "Japan": "🇯🇵", "South Korea": "🇰🇷", "Singapore": "🇸🇬",
    "Vietnam": "🇻🇳", "Indonesia": "🇮🇩", "Malaysia": "🇲🇾", "Philippines": "🇵🇭",
    "China": "🇨🇳", "India": "🇮🇳", "United States": "🇺🇸", "United Kingdom": "🇬🇧",
    "France": "🇫🇷", "Germany": "🇩🇪", "Spain": "🇪🇸", "Italy": "🇮🇹",
    "Australia": "🇦🇺", "New Zealand": "🇳🇿", "Canada": "🇨🇦", "Mexico": "🇲🇽",
    "UAE": "🇦🇪", "Turkey": "🇹🇷", "Egypt": "🇪🇬", "Brazil": "🇧🇷", "South Africa": "🇿🇦"
}


def load_data() -> dict:
    if not DATA_FILE.exists():
        log.error(f"Data file not found: {DATA_FILE}")
        sys.exit(1)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    log.info(f"Loaded data: today={data.get('today')}, dates={len(data.get('dates', {}))}")
    return data


def generate_calendar_html(dates: dict) -> str:
    """Generate HTML for the historical calendar section."""
    if not dates:
        return '<p class="empty">暂无历史数据</p>'

    sorted_dates = sorted(dates.keys(), reverse=True)[:30]  # Show last 30 days
    rows = ""
    for d in sorted_dates:
        day_data = dates[d]
        countries = day_data.get("countries", {})
        total = sum(len(arts) for arts in countries.values())
        fetch_time = day_data.get("fetch_time", "")
        try:
            ft = datetime.fromisoformat(fetch_time.replace("Z", "+00:00")).strftime("%H:%M UTC")
        except Exception:
            ft = "—"
        rows += f"""
        <tr>
            <td><strong>{d}</strong></td>
            <td>{total} 条</td>
            <td>{len(countries)} 国</td>
            <td>{ft}</td>
            <td>
                <button class="btn-small" onclick="showDate('{d}')">查看</button>
            </td>
        </tr>"""

    return f"""
    <table class="cal-table">
        <thead>
            <tr><th>日期</th><th>文章数</th><th>国家数</th><th>采集时间</th><th>操作</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>"""


def generate_country_card(country: str, articles: list) -> str:
    """Generate HTML card for a single country."""
    flag = FLAG_EMOJI.get(country, "🌐")

    # Category counts
    cat_counts = {}
    for a in articles:
        cat = a.get("category", "policy")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    cat_badges = ""
    for cat_key, meta in CATEGORY_META.items():
        count = cat_counts.get(cat_key, 0)
        if count > 0:
            cat_badges += f'<span class="badge" style="background:{meta["color"]}">{meta["emoji"]} {count}</span> '

    article_list = ""
    for a in articles:
        cat_meta = CATEGORY_META.get(a.get("category", "policy"), CATEGORY_META["policy"])
        pub = a.get("published", "")[:10] if a.get("published") else ""
        source = a.get("source", "")
        title = a.get("title", "无标题")
        url = a.get("url", "#")
        summary = a.get("summary", "")[:120]

        article_list += f"""
        <div class="article-item">
            <span class="cat-dot" style="background:{cat_meta['color']}" title="{cat_meta['label']}"></span>
            <div class="article-content">
                <a href="{url}" target="_blank" rel="noopener" class="article-title">{title}</a>
                <div class="article-meta">
                    <span>{source}</span>
                    {f' · <span>{pub}</span>' if pub else ''}
                </div>
                {f'<p class="article-summary">{summary}</p>' if summary else ''}
            </div>
        </div>"""

    return f"""
    <div class="country-card" id="country-{country.replace(' ', '-').lower()}">
        <div class="card-header">
            <h3>{flag} {country}</h3>
            <div class="cat-badges">{cat_badges}</div>
        </div>
        <div class="card-body">
            {article_list if article_list else '<p class="empty">今日暂无新闻</p>'}
        </div>
    </div>"""


def generate_html(data: dict) -> str:
    """Generate the complete dashboard HTML."""
    today = data.get("today", "未知")
    window = data.get("window", "")
    dates = data.get("dates", {})
    today_data = dates.get(today, {})
    countries_data = today_data.get("countries", {})

    # Total stats
    total_articles = sum(len(arts) for arts in countries_data.values())
    total_countries = len(countries_data)

    # Category totals across all countries
    global_cats = {}
    for articles in countries_data.values():
        for a in articles:
            cat = a.get("category", "policy")
            global_cats[cat] = global_cats.get(cat, 0) + 1

    cat_summary_html = ""
    for cat_key, meta in CATEGORY_META.items():
        count = global_cats.get(cat_key, 0)
        cat_summary_html += f'<span class="global-badge" style="border-color:{meta["color"]}">{meta["emoji"]} {meta["label"]}: <strong>{count}</strong></span> '

    # Country cards
    country_cards = ""
    for country in sorted(countries_data.keys()):
        country_cards += generate_country_card(country, countries_data[country])

    calendar_html = generate_calendar_html(dates)

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全球旅游动态看板 — {today}</title>
    <style>
        :root {{
            --bg: #f0f2f5; --card-bg: #fff; --text: #1a1a2e; --text-muted: #6b7280;
            --border: #e5e7eb; --accent: #4f46e5; --shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg: #0f172a; --card-bg: #1e293b; --text: #e2e8f0; --text-muted: #94a3b8;
                --border: #334155; --accent: #818cf8; --shadow: 0 1px 3px rgba(0,0,0,0.4);
            }}
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', sans-serif;
            background: var(--bg); color: var(--text); line-height: 1.6;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 1rem; }}
        header {{
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white; padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem;
            text-align: center;
        }}
        header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        header .meta {{ opacity: 0.85; font-size: 0.95rem; }}
        .stats-bar {{
            display: flex; flex-wrap: wrap; gap: 0.75rem; justify-content: center;
            margin: 1rem 0;
        }}
        .global-badge {{
            background: var(--card-bg); padding: 0.4rem 0.8rem; border-radius: 20px;
            border: 2px solid; font-size: 0.85rem;
        }}
        .country-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
            gap: 1rem;
        }}
        .country-card {{
            background: var(--card-bg); border-radius: 12px;
            box-shadow: var(--shadow); overflow: hidden;
            transition: transform 0.2s;
        }}
        .country-card:hover {{ transform: translateY(-2px); }}
        .card-header {{
            padding: 1rem; border-bottom: 1px solid var(--border);
            display: flex; justify-content: space-between; align-items: center;
            flex-wrap: wrap; gap: 0.5rem;
        }}
        .card-header h3 {{ font-size: 1.1rem; }}
        .cat-badges {{ display: flex; flex-wrap: wrap; gap: 0.3rem; }}
        .badge {{
            color: white; padding: 0.15rem 0.5rem; border-radius: 10px;
            font-size: 0.75rem; font-weight: 600;
        }}
        .card-body {{ padding: 0.75rem; max-height: 500px; overflow-y: auto; }}
        .article-item {{
            display: flex; gap: 0.5rem; padding: 0.5rem 0;
            border-bottom: 1px solid var(--border);
        }}
        .article-item:last-child {{ border-bottom: none; }}
        .cat-dot {{
            width: 8px; height: 8px; border-radius: 50%;
            margin-top: 0.5rem; flex-shrink: 0;
        }}
        .article-content {{ flex: 1; min-width: 0; }}
        .article-title {{
            color: var(--accent); text-decoration: none; font-weight: 500;
            font-size: 0.9rem; display: block;
        }}
        .article-title:hover {{ text-decoration: underline; }}
        .article-meta {{
            color: var(--text-muted); font-size: 0.78rem; margin-top: 0.2rem;
        }}
        .article-summary {{
            color: var(--text-muted); font-size: 0.82rem; margin-top: 0.3rem;
            line-height: 1.4;
        }}
        .empty {{ color: var(--text-muted); font-style: italic; padding: 1rem; text-align: center; }}
        /* Calendar section */
        .calendar-section {{
            background: var(--card-bg); border-radius: 12px;
            box-shadow: var(--shadow); padding: 1.5rem; margin-top: 1.5rem;
        }}
        .calendar-section h2 {{ margin-bottom: 1rem; font-size: 1.3rem; }}
        .cal-table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
        .cal-table th, .cal-table td {{
            padding: 0.6rem; text-align: left; border-bottom: 1px solid var(--border);
        }}
        .cal-table th {{ background: var(--bg); font-weight: 600; }}
        .btn-small {{
            background: var(--accent); color: white; border: none;
            padding: 0.3rem 0.8rem; border-radius: 6px; cursor: pointer;
            font-size: 0.8rem;
        }}
        .btn-small:hover {{ opacity: 0.85; }}
        footer {{
            text-align: center; padding: 2rem; color: var(--text-muted); font-size: 0.85rem;
        }}
        @media (max-width: 768px) {{
            .country-grid {{ grid-template-columns: 1fr; }}
            header h1 {{ font-size: 1.5rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 全球旅游动态看板</h1>
            <div class="meta">
                <div>📅 {today} &nbsp;|&nbsp; 窗口期: {window}</div>
                <div>共 <strong>{total_articles}</strong> 条新闻 · <strong>{total_countries}</strong> 个国家</div>
            </div>
            <div class="stats-bar">{cat_summary_html}</div>
        </header>

        <div class="country-grid">{country_cards}</div>

        <div class="calendar-section">
            <h2>📆 历史采集日历</h2>
            {calendar_html}
        </div>

        <footer>
            <p>自动生成于 {now_str} · 数据来源: GNews / Google CSE / MediaStack / RSS</p>
            <p>GitHub Actions 每日 09:00 UTC 自动更新</p>
        </footer>
    </div>

    <script>
        function showDate(dateStr) {{
            alert('切换到日期: ' + dateStr + '\\n（完整历史切换功能开发中）');
        }}
    </script>
</body>
</html>"""


def main():
    log.info("Generating dashboard HTML...")
    data = load_data()
    html = generate_html(data)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    log.info(f"✅ Dashboard written to {OUTPUT_FILE}")
    log.info(f"   File size: {len(html):,} bytes")


if __name__ == "__main__":
    main()
