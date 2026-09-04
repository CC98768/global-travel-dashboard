import json
from collections import defaultdict

VALID_CATEGORIES = {
    '✈️ 航线交通',
    '📋 出入境政策',
    '📊 旅游趋势',
    '🎯 景点活动',
    '🎭 文娱信息',
    '🏙️ 本地生活',
}

with open('/sessions/exciting-laughing-mendel/mnt/Desktop/global-travel-dashboard/data/travel_daily.json') as f:
    data = json.load(f)

dates_data = data['dates']
all_dates = sorted(dates_data.keys())

# Fix all items with invalid categories on violation dates (Aug 9-13)
# These are items we replaced - they need category "📊 旅游趋势" and sub_category "市场分析"
fix_count = 0
for d in all_dates:
    if d < '2026-08-09' or d > '2026-08-13':
        continue
    items = dates_data[d]['items']
    for i, item in enumerate(items):
        if item['category'] not in VALID_CATEGORIES:
            print(f"Fixing {d} idx{i} [{item['country']}]: {item['category']} -> 📊 旅游趋势")
            item['category'] = '📊 旅游趋势'
            item['sub_category'] = '市场分析'
            fix_count += 1

print(f"\nFixed {fix_count} categories")

# Verify quota: each country should have exactly 2 旅游趋势 per date
for d in ['2026-08-09', '2026-08-10', '2026-08-11', '2026-08-12', '2026-08-13']:
    items = dates_data[d]['items']
    country_cat_count = defaultdict(lambda: defaultdict(int))
    for item in items:
        country_cat_count[item['country']][item['category']] += 1
    for country in sorted(country_cat_count.keys()):
        cats = country_cat_count[country]
        trend_count = cats.get('📊 旅游趋势', 0)
        if trend_count != 2:
            print(f"WARNING: {d} {country} has {trend_count} 旅游趋势 items (expected 2)")

# Recalculate tag_rank
for d in all_dates:
    items = dates_data[d]['items']
    for i, item in enumerate(items):
        item['tag_rank'] = i + 1

# Write
with open('/sessions/exciting-laughing-mendel/mnt/Desktop/global-travel-dashboard/data/travel_daily.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Data written successfully")
