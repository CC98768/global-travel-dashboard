#!/usr/bin/env python3
"""Generate the travel dashboard HTML from travel_daily.json"""
import json, os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "travel_daily.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "docs", "index.html")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

today_str = data["today"]  # "2026-09-04"
today_data = data["dates"][today_str]
today_items = today_data["items"]
tag_summary = today_data["tag_summary"]

# Build calendar data (all dates tag_summary + total)
calendar_data = {}
for d, dd in sorted(data["dates"].items()):
    calendar_data[d] = {
        "total": dd["total_items"],
        "tags": dd["tag_summary"]
    }

# Region mapping for 25 countries in data
REGIONS = {
    "东亚": ["中国", "日本", "韩国", "蒙古"],
    "东南亚": ["泰国", "新加坡", "马来西亚", "越南", "印度尼西亚", "菲律宾"],
    "欧洲": ["英国", "法国", "德国", "意大利", "西班牙", "荷兰", "俄罗斯"],
    "美洲": ["美国", "加拿大", "墨西哥", "巴西"],
    "中东非洲": ["阿联酋", "土耳其", "埃及"],
    "大洋洲": ["澳大利亚", "新西兰"],
}

COUNTRY_FLAGS = {
    "中国": "🇨🇳", "日本": "🇯🇵", "韩国": "🇰🇷", "蒙古": "🇲🇳",
    "泰国": "🇹🇭", "新加坡": "🇸🇬", "马来西亚": "🇲🇾", "越南": "🇻🇳",
    "印度尼西亚": "🇮🇩", "菲律宾": "🇵🇭",
    "英国": "🇬🇧", "法国": "🇫🇷", "德国": "🇩🇪", "意大利": "🇮🇹",
    "西班牙": "🇪🇸", "荷兰": "🇳🇱", "俄罗斯": "🇷🇺",
    "美国": "🇺🇸", "加拿大": "🇨🇦", "墨西哥": "🇲🇽", "巴西": "🇧🇷",
    "阿联酋": "🇦🇪", "土耳其": "🇹🇷", "埃及": "🇪🇬",
    "澳大利亚": "🇦🇺", "新西兰": "🇳🇿",
}

# Only include regions/countries that have data
all_countries_in_data = set(it["country"] for it in today_items)

# Serialize today's items as JSON for embedding
items_json = json.dumps(today_items, ensure_ascii=False)
calendar_json = json.dumps(calendar_data, ensure_ascii=False)
regions_json = json.dumps(REGIONS, ensure_ascii=False)
flags_json = json.dumps(COUNTRY_FLAGS, ensure_ascii=False)

# Count streaks
streak_count = sum(1 for it in today_items if int(it.get("consecutive_days", 0)) >= 2)

# All categories & sub_categories
all_categories = sorted(set(it["category"] for it in today_items))
all_subcats = sorted(set(it["sub_category"] for it in today_items))
all_countries_list = sorted(all_countries_in_data)
all_tags = ["爆", "热", "新", "常规"]

cats_json = json.dumps(all_categories, ensure_ascii=False)
subcats_json = json.dumps(all_subcats, ensure_ascii=False)
countries_list_json = json.dumps(all_countries_list, ensure_ascii=False)
tags_json = json.dumps(all_tags, ensure_ascii=False)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全球出入境旅游热点看板 - {today_str}</title>
<style>
:root {{
  --bg: #f0f2f5; --card-bg: #fff; --text: #1a1a2e; --text-secondary: #555;
  --border: #e2e8f0; --accent: #6366f1; --accent-light: #e0e7ff;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-lg: 0 4px 14px rgba(0,0,0,0.1);
  --tag-boom: #ef4444; --tag-hot: #f97316; --tag-new: #6366f1; --tag-normal: #94a3b8;
  --radius: 12px;
}}
[data-theme="dark"] {{
  --bg: #0f172a; --card-bg: #1e293b; --text: #e2e8f0; --text-secondary: #94a3b8;
  --border: #334155; --accent: #818cf8; --accent-light: #312e81;
  --shadow: 0 1px 3px rgba(0,0,0,0.3); --shadow-lg: 0 4px 14px rgba(0,0,0,0.4);
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}

/* Header */
.header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%); color: #fff; padding: 28px 32px; position: relative; }}
.header-top {{ display: flex; justify-content: space-between; align-items: center; }}
.header h1 {{ font-size: 26px; font-weight: 700; letter-spacing: 0.5px; }}
.header .subtitle {{ font-size: 13px; opacity: 0.85; margin-top: 4px; }}
.header-controls {{ display: flex; gap: 10px; align-items: center; }}
.theme-toggle {{ background: rgba(255,255,255,0.2); border: none; color: #fff; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 16px; transition: background 0.2s; }}
.theme-toggle:hover {{ background: rgba(255,255,255,0.3); }}

/* Stats bar */
.stats-bar {{ display: flex; gap: 16px; padding: 16px 32px; background: var(--card-bg); border-bottom: 1px solid var(--border); flex-wrap: wrap; }}
.stat-card {{ display: flex; align-items: center; gap: 10px; padding: 8px 16px; background: var(--bg); border-radius: 10px; min-width: 120px; }}
.stat-icon {{ font-size: 24px; }}
.stat-info .stat-label {{ font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }}
.stat-info .stat-value {{ font-size: 22px; font-weight: 700; color: var(--text); }}

/* Filters */
.filters {{ padding: 16px 32px; background: var(--card-bg); border-bottom: 1px solid var(--border); display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }}
.filter-group {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }}
.filter-label {{ font-size: 12px; color: var(--text-secondary); font-weight: 600; white-space: nowrap; }}
.filter-btn {{ padding: 4px 12px; border-radius: 20px; border: 1px solid var(--border); background: var(--card-bg); color: var(--text); font-size: 12px; cursor: pointer; transition: all 0.2s; white-space: nowrap; }}
.filter-btn:hover {{ border-color: var(--accent); color: var(--accent); }}
.filter-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
.search-box {{ padding: 6px 14px; border-radius: 20px; border: 1px solid var(--border); background: var(--bg); color: var(--text); font-size: 13px; width: 200px; outline: none; transition: border-color 0.2s; }}
.search-box:focus {{ border-color: var(--accent); }}
.date-select {{ padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border); background: var(--card-bg); color: var(--text); font-size: 13px; cursor: pointer; outline: none; }}

/* Main content */
.main {{ padding: 20px 32px; max-width: 1600px; margin: 0 auto; }}
.region-section {{ margin-bottom: 28px; }}
.region-title {{ font-size: 18px; font-weight: 700; color: var(--text); margin-bottom: 14px; padding-left: 14px; border-left: 4px solid var(--accent); display: flex; align-items: center; gap: 8px; }}
.region-title .count {{ font-size: 13px; color: var(--text-secondary); font-weight: 400; }}

/* Cards grid */
.cards-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 14px; }}
.country-card {{ background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; transition: transform 0.2s, box-shadow 0.2s; }}
.country-card:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-lg); }}
.country-header {{ padding: 14px 16px; background: linear-gradient(135deg, var(--accent-light), transparent); display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); }}
.country-name {{ font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 6px; }}
.country-flag {{ font-size: 22px; }}
.news-list {{ padding: 0; }}

/* News items */
.news-item {{ padding: 12px 16px; border-bottom: 1px solid var(--border); transition: background 0.15s; }}
.news-item:last-child {{ border-bottom: none; }}
.news-item:hover {{ background: var(--bg); }}
.news-meta {{ display: flex; align-items: center; gap: 6px; margin-bottom: 6px; flex-wrap: wrap; }}
.tag-badge {{ display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; color: #fff; }}
.tag-爆 {{ background: var(--tag-boom); }}
.tag-热 {{ background: var(--tag-hot); }}
.tag-新 {{ background: var(--tag-new); }}
.tag-常规 {{ background: var(--tag-normal); }}
.cat-badge {{ font-size: 11px; color: var(--accent); background: var(--accent-light); padding: 2px 8px; border-radius: 4px; }}
.streak-badge {{ font-size: 10px; color: #d97706; background: #fef3c7; padding: 1px 6px; border-radius: 4px; border: 1px solid #fcd34d; }}
[data-theme="dark"] .streak-badge {{ background: #78350f; color: #fbbf24; border-color: #92400e; }}
.news-title {{ font-size: 14px; font-weight: 600; color: var(--text); line-height: 1.5; margin-bottom: 4px; }}
.news-title a {{ color: inherit; text-decoration: none; }}
.news-title a:hover {{ color: var(--accent); text-decoration: underline; }}

/* Collapsible sections */
.collapsible-toggle {{ font-size: 12px; color: var(--accent); cursor: pointer; user-select: none; padding: 2px 0; display: inline-flex; align-items: center; gap: 4px; }}
.collapsible-toggle:hover {{ text-decoration: underline; }}
.collapsible-content {{ display: none; font-size: 13px; color: var(--text-secondary); line-height: 1.6; padding: 6px 0; }}
.collapsible-content.open {{ display: block; }}
.key-figures {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0; }}
.key-figure {{ font-size: 11px; background: var(--bg); padding: 3px 8px; border-radius: 4px; color: var(--accent); border: 1px solid var(--border); }}
.news-source {{ font-size: 11px; color: var(--text-secondary); margin-top: 4px; }}
.news-source a {{ color: var(--accent); text-decoration: none; }}
.news-source a:hover {{ text-decoration: underline; }}

/* Calendar */
.calendar-section {{ margin-bottom: 32px; }}
.calendar-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 8px; }}
.cal-day {{ background: var(--card-bg); border-radius: 8px; padding: 10px; text-align: center; box-shadow: var(--shadow); cursor: default; transition: transform 0.15s; border: 2px solid transparent; }}
.cal-day:hover {{ transform: scale(1.03); }}
.cal-day.today {{ border-color: var(--accent); }}
.cal-date {{ font-size: 13px; font-weight: 600; color: var(--text); }}
.cal-total {{ font-size: 11px; color: var(--text-secondary); margin-top: 2px; }}
.cal-tags {{ display: flex; gap: 3px; justify-content: center; margin-top: 4px; flex-wrap: wrap; }}
.cal-tag {{ font-size: 9px; padding: 1px 4px; border-radius: 3px; color: #fff; }}

/* Loading message */
.loading-msg {{ text-align: center; padding: 40px; color: var(--text-secondary); font-size: 15px; }}

/* Responsive */
@media (max-width: 768px) {{
  .header {{ padding: 20px 16px; }}
  .header h1 {{ font-size: 20px; }}
  .stats-bar, .filters, .main {{ padding: 12px 16px; }}
  .cards-grid {{ grid-template-columns: 1fr; }}
  .calendar-grid {{ grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); }}
  .search-box {{ width: 100%; }}
}}

/* Hidden */
.hidden {{ display: none !important; }}
.no-results {{ text-align: center; padding: 60px 20px; color: var(--text-secondary); }}
.no-results .emoji {{ font-size: 48px; margin-bottom: 12px; }}
</style>
</head>
<body>
<div class="header">
  <div class="header-top">
    <div>
      <h1>🌍 全球出入境旅游热点看板</h1>
      <div class="subtitle">数据来源：Google News RSS + 各国旅游局/政府官网 | 25国 × 10条/天 | 覆盖30天历史</div>
    </div>
    <div class="header-controls">
      <select class="date-select" id="dateSelector"></select>
      <button class="theme-toggle" id="themeToggle" title="切换深色模式">🌙</button>
    </div>
  </div>
</div>

<div class="stats-bar" id="statsBar">
  <div class="stat-card"><span class="stat-icon">🌐</span><div class="stat-info"><div class="stat-label">覆盖国家</div><div class="stat-value">25</div></div></div>
  <div class="stat-card"><span class="stat-icon">📰</span><div class="stat-info"><div class="stat-label">今日要闻</div><div class="stat-value" id="statTotal">250</div></div></div>
  <div class="stat-card"><span class="stat-icon">🔥</span><div class="stat-info"><div class="stat-label">爆款</div><div class="stat-value" id="statBoom">{tag_summary.get('爆', 0)}</div></div></div>
  <div class="stat-card"><span class="stat-icon">⚡</span><div class="stat-info"><div class="stat-label">热点</div><div class="stat-value" id="statHot">{tag_summary.get('热', 0)}</div></div></div>
  <div class="stat-card"><span class="stat-icon">🆕</span><div class="stat-info"><div class="stat-label">新动态</div><div class="stat-value" id="statNew">{tag_summary.get('新', 0)}</div></div></div>
  <div class="stat-card"><span class="stat-icon">📆</span><div class="stat-info"><div class="stat-label">连续上榜</div><div class="stat-value" id="statStreak">{streak_count}</div></div></div>
</div>

<div class="filters">
  <div class="filter-group">
    <span class="filter-label">🏷️ 标签</span>
    <div id="tagFilters"></div>
  </div>
  <div class="filter-group">
    <span class="filter-label">📂 分类</span>
    <div id="catFilters"></div>
  </div>
  <div class="filter-group">
    <span class="filter-label">🌏 国家</span>
    <div id="countryFilters" style="max-width:600px;"></div>
  </div>
  <input type="text" class="search-box" id="searchBox" placeholder="🔍 搜索标题/摘要...">
</div>

<div class="main">
  <div class="calendar-section">
    <div class="region-title">📅 历史日历 <span class="count">(8月6日 - 9月4日)</span></div>
    <div class="calendar-grid" id="calendarGrid"></div>
  </div>
  <div id="contentArea"></div>
  <div class="no-results hidden" id="noResults">
    <div class="emoji">🔍</div>
    <p>没有匹配的结果，请调整筛选条件</p>
  </div>
</div>

<script>
// ===== DATA =====
const TODAY = {json.dumps(today_str)};
const ALL_ITEMS = {items_json};
const CALENDAR = {calendar_json};
const REGIONS = {regions_json};
const FLAGS = {flags_json};
const ALL_CATS = {cats_json};
const ALL_SUBCATS = {subcats_json};
const ALL_COUNTRIES = {countries_list_json};
const ALL_TAGS = {tags_json};

// ===== STATE =====
let activeTags = new Set();
let activeCats = new Set();
let activeCountries = new Set();
let searchQuery = '';

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {{
  initDateSelector();
  initCalendar();
  initFilters();
  renderContent();
  initThemeToggle();
}});

// ===== DATE SELECTOR =====
function initDateSelector() {{
  const sel = document.getElementById('dateSelector');
  const dates = Object.keys(CALENDAR).sort();
  dates.forEach(d => {{
    const opt = document.createElement('option');
    opt.value = d;
    opt.textContent = d === TODAY ? `📌 ${{d}} (今天)` : d;
    if (d === TODAY) opt.selected = true;
    sel.appendChild(opt);
  }});
  sel.addEventListener('change', (e) => {{
    if (e.target.value !== TODAY) {{
      alert('历史数据加载中...\\n当前仅嵌入今天(${{TODAY}})的完整数据。\\n日历视图已包含所有30天的摘要统计。');
      e.target.value = TODAY;
    }}
  }});
}}

// ===== CALENDAR =====
function initCalendar() {{
  const grid = document.getElementById('calendarGrid');
  const dates = Object.keys(CALENDAR).sort();
  dates.forEach(d => {{
    const info = CALENDAR[d];
    const isToday = d === TODAY;
    const div = document.createElement('div');
    div.className = 'cal-day' + (isToday ? ' today' : '');
    const shortDate = d.slice(5); // MM-DD
    const tagsHtml = Object.entries(info.tags).map(([t, c]) =>
      `<span class="cal-tag tag-${{t}}">${{t}}${{c}}</span>`
    ).join('');
    div.innerHTML = `
      <div class="cal-date">${{isToday ? '📌 ' : ''}}${{shortDate}}</div>
      <div class="cal-total">${{info.total}}条</div>
      <div class="cal-tags">${{tagsHtml}}</div>
    `;
    grid.appendChild(div);
  }});
}}

// ===== FILTERS =====
function initFilters() {{
  // Tags
  const tagDiv = document.getElementById('tagFilters');
  ALL_TAGS.forEach(t => {{
    const btn = document.createElement('button');
    btn.className = 'filter-btn';
    btn.textContent = t;
    btn.dataset.value = t;
    btn.addEventListener('click', () => {{
      btn.classList.toggle('active');
      if (activeTags.has(t)) activeTags.delete(t); else activeTags.add(t);
      renderContent();
    }});
    tagDiv.appendChild(btn);
  }});

  // Categories
  const catDiv = document.getElementById('catFilters');
  ALL_CATS.forEach(c => {{
    const btn = document.createElement('button');
    btn.className = 'filter-btn';
    btn.textContent = c;
    btn.dataset.value = c;
    btn.addEventListener('click', () => {{
      btn.classList.toggle('active');
      if (activeCats.has(c)) activeCats.delete(c); else activeCats.add(c);
      renderContent();
    }});
    catDiv.appendChild(btn);
  }});

  // Countries
  const cDiv = document.getElementById('countryFilters');
  ALL_COUNTRIES.forEach(c => {{
    const btn = document.createElement('button');
    btn.className = 'filter-btn';
    btn.textContent = (FLAGS[c] || '') + ' ' + c;
    btn.dataset.value = c;
    btn.addEventListener('click', () => {{
      btn.classList.toggle('active');
      if (activeCountries.has(c)) activeCountries.delete(c); else activeCountries.add(c);
      renderContent();
    }});
    cDiv.appendChild(btn);
  }});

  // Search
  document.getElementById('searchBox').addEventListener('input', (e) => {{
    searchQuery = e.target.value.trim().toLowerCase();
    renderContent();
  }});
}}

// ===== RENDER =====
function renderContent() {{
  const area = document.getElementById('contentArea');
  area.innerHTML = '';
  let totalShown = 0;
  let anyVisible = false;

  for (const [region, countries] of Object.entries(REGIONS)) {{
    let regionHtml = '';
    let regionCount = 0;

    for (const country of countries) {{
      if (!ALL_ITEMS.some(it => it.country === country)) continue;
      if (activeCountries.size > 0 && !activeCountries.has(country)) continue;

      const items = ALL_ITEMS.filter(it => it.country === country);
      const filtered = items.filter(it => {{
        if (activeTags.size > 0 && !activeTags.has(it.tag)) return false;
        if (activeCats.size > 0 && !activeCats.has(it.category)) return false;
        if (searchQuery) {{
          const hay = (it.title + ' ' + it.summary + ' ' + (it.key_figures||[]).join(' ')).toLowerCase();
          if (!hay.includes(searchQuery)) return false;
        }}
        return true;
      }});

      if (filtered.length === 0) continue;
      anyVisible = true;
      regionCount += filtered.length;
      totalShown += filtered.length;

      const flag = FLAGS[country] || '🏳️';
      let newsHtml = '';
      filtered.forEach(it => {{
        const streak = parseInt(it.consecutive_days || 0);
        const streakBadge = streak >= 2 ? `<span class="streak-badge">📆 已上榜${{streak}}天</span>` : '';
        const keyFigHtml = (it.key_figures && it.key_figures.length > 0)
          ? `<div class="key-figures">${{it.key_figures.map(f => `<span class="key-figure">${{f}}</span>`).join('')}}</div>` : '';
        const uid = 's_' + Math.random().toString(36).slice(2,8);
        const uid2 = 'i_' + Math.random().toString(36).slice(2,8);
        const uid3 = 't_' + Math.random().toString(36).slice(2,8);

        newsHtml += `
        <div class="news-item">
          <div class="news-meta">
            <span class="tag-badge tag-${{it.tag}}">${{it.tag}}</span>
            <span class="cat-badge">${{it.sub_category}}</span>
            ${{streakBadge}}
          </div>
          <div class="news-title"><a href="${{it.source_url || '#'}}" target="_blank" rel="noopener">${{it.title}}</a></div>
          ${{keyFigHtml}}
          <span class="collapsible-toggle" onclick="toggleEl('${{uid}}')">▶ 摘要</span>
          <div class="collapsible-content" id="${{uid}}">${{it.summary}}</div>
          <span class="collapsible-toggle" onclick="toggleEl('${{uid2}}')">▶ 影响分析</span>
          <div class="collapsible-content" id="${{uid2}}">${{it.impact || ''}}</div>
          <span class="collapsible-toggle" onclick="toggleEl('${{uid3}}')">▶ 出行建议</span>
          <div class="collapsible-content" id="${{uid3}}">${{it.travel_advisory || ''}}</div>
          <div class="news-source">来源：<a href="${{it.source_url || '#'}}" target="_blank">${{it.source || 'N/A'}}</a></div>
        </div>`;
      }});

      regionHtml += `
      <div class="country-card">
        <div class="country-header">
          <span class="country-name"><span class="country-flag">${{flag}}</span> ${{country}}</span>
          <span style="font-size:12px;color:var(--text-secondary)">${{filtered.length}}条</span>
        </div>
        <div class="news-list">${{newsHtml}}</div>
      </div>`;
    }}

    if (regionHtml) {{
      area.innerHTML += `
      <div class="region-section">
        <div class="region-title">${{region}} <span class="count">(${{regionCount}}条)</span></div>
        <div class="cards-grid">${{regionHtml}}</div>
      </div>`;
    }}
  }}

  document.getElementById('noResults').classList.toggle('hidden', anyVisible);
  document.getElementById('statTotal').textContent = totalShown;
}}

function toggleEl(id) {{
  const el = document.getElementById(id);
  if (el) el.classList.toggle('open');
}}

// ===== THEME =====
function initThemeToggle() {{
  const btn = document.getElementById('themeToggle');
  const saved = localStorage.getItem('dashboard-theme');
  if (saved === 'dark') {{
    document.documentElement.setAttribute('data-theme', 'dark');
    btn.textContent = '☀️';
  }}
  btn.addEventListener('click', () => {{
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (isDark) {{
      document.documentElement.removeAttribute('data-theme');
      btn.textContent = '🌙';
      localStorage.setItem('dashboard-theme', 'light');
    }} else {{
      document.documentElement.setAttribute('data-theme', 'dark');
      btn.textContent = '☀️';
      localStorage.setItem('dashboard-theme', 'dark');
    }}
  }});
}}
</script>
</body>
</html>'''

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Dashboard generated: {OUT_PATH}")
print(f"   Date: {today_str}")
print(f"   Items: {len(today_items)}")
print(f"   Size: {os.path.getsize(OUT_PATH):,} bytes")
