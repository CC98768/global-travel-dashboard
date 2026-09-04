#!/usr/bin/env python3
"""
validate_quality.py v4.0 - 最高权限验证脚本
============================================
⚠️ 本脚本为最高权限规则，不得修改、不得跳过、不得降低标准。
⚠️ 验证不通过 = 禁止输出，必须重写直到 0 违规。

规则清单（全部强制）：
1. 标题 > 30字，含具体日期
2. 摘要 > 300字，具体事实和数据
3. 关键数据 >= 5条，含数字和单位
4. 影响分析 > 150字，从信源摘取
5. 出行提醒 > 150字，从信源摘取
6. 同一事件重复上榜 > 3天强制下线
7. 25国 × 10条 = 250条/天
8. 分类配额：航线交通2/出入境政策2/本地生活1/旅游趋势2/景点活动2/文娱信息1
9. Tag配额：爆1/热2/新5/常规2（每国），每日总爆=25
10. 信源必须具体机构名称，禁止模糊信源
11. URL必须http开头
12. 所有日期数据均需验证（不仅验证today）
"""
import json, sys, re
from collections import Counter, defaultdict

# ============================================================
# ⚠️ 最高权限规则 - 不得修改
# ============================================================

VALID_CATS = [
    '✈️ 航线交通',
    '📋 出入境政策',
    '🏙️ 本地生活',
    '📊 旅游趋势',
    '🎯 景点活动',
    '🎭 文娱信息',
]

CAT_EMOJI_MAP = {
    '航线交通': '✈️ 航线交通',
    '出入境政策': '📋 出入境政策',
    '本地生活': '🏙️ 本地生活',
    '旅游趋势': '📊 旅游趋势',
    '景点活动': '🎯 景点活动',
    '文娱信息': '🎭 文娱信息',
}

REQUIRED_CATS = {'航线交通': 2, '出入境政策': 2, '本地生活': 1, '旅游趋势': 2, '景点活动': 2, '文娱信息': 1}

REQUIRED_COUNTRIES = [
    '中国','俄罗斯','加拿大','印度尼西亚','土耳其','埃及','墨西哥','巴西',
    '德国','意大利','新加坡','新西兰','日本','法国','泰国','澳大利亚',
    '美国','英国','荷兰','菲律宾','西班牙','越南','阿联酋','韩国','马来西亚'
]

BAD_SOURCES = ['综合旅游平台','未知','网络','媒体报道','相关新闻','有关媒体']
VALID_TAGS = ['爆','热','新','常规']
ITEMS_PER_DAY = 250
ITEMS_PER_COUNTRY = 10
MIN_TITLE_LEN = 30
MIN_SUMMARY_LEN = 300
MIN_KEY_FIGURES = 5
MIN_IMPACT_LEN = 150
MIN_ADVISORY_LEN = 150
MAX_CONSECUTIVE_DAYS = 3
REQUIRED_BAO_PER_DAY = 25

def validate_items(items, date_str, errors, check_dedup=False, prev_dates_data=None):
    """验证单日数据"""
    # 总数检查
    if len(items) != ITEMS_PER_DAY:
        errors.append(f"[{date_str}] TOTAL: Expected {ITEMS_PER_DAY}, got {len(items)}")

    # 国家分组
    by_country = defaultdict(list)
    for item in items:
        country = item.get('country', '')
        by_country[country].append(item)

    # 25国完整性检查
    for c in REQUIRED_COUNTRIES:
        if c not in by_country:
            errors.append(f"[{date_str}] MISSING COUNTRY: {c}")
        elif len(by_country[c]) != ITEMS_PER_COUNTRY:
            errors.append(f"[{date_str}] COUNT: {c} has {len(by_country[c])}, expected {ITEMS_PER_COUNTRY}")

    # 非25国检查
    for c in by_country:
        if c not in REQUIRED_COUNTRIES:
            errors.append(f"[{date_str}] INVALID COUNTRY: {c}")

    # 逐条验证
    for idx, item in enumerate(items):
        country = item.get('country', '?')
        prefix = f"[{date_str}] Item {idx+1} [{country}]"

        # 必填字段检查
        required_fields = ['title','category','sub_category','summary','source','impact',
                          'source_url','key_figures','travel_advisory','tag','country',
                          'consecutive_days']
        for field in required_fields:
            if field not in item:
                errors.append(f"{prefix}: MISSING '{field}'")

        # 标题长度
        title = item.get('title', '')
        if len(title) < MIN_TITLE_LEN:
            errors.append(f"{prefix}: title {len(title)} chars (<{MIN_TITLE_LEN})")

        # 摘要长度
        summary = item.get('summary', '')
        if len(summary) < MIN_SUMMARY_LEN:
            errors.append(f"{prefix}: summary {len(summary)} chars (<{MIN_SUMMARY_LEN})")

        # 关键数据
        kf = item.get('key_figures', [])
        if not isinstance(kf, list) or len(kf) < MIN_KEY_FIGURES:
            n = len(kf) if isinstance(kf, list) else 0
            errors.append(f"{prefix}: key_figures {n} (<{MIN_KEY_FIGURES})")

        # 影响分析
        impact = item.get('impact', '')
        if len(impact) < MIN_IMPACT_LEN:
            errors.append(f"{prefix}: impact {len(impact)} chars (<{MIN_IMPACT_LEN})")

        # 出行提醒
        ta = item.get('travel_advisory', '')
        if len(ta) < MIN_ADVISORY_LEN:
            errors.append(f"{prefix}: advisory {len(ta)} chars (<{MIN_ADVISORY_LEN})")

        # 信源检查
        source = item.get('source', '')
        if source in BAD_SOURCES or len(source) < 3:
            errors.append(f"{prefix}: bad source '{source}'")

        # URL检查
        url = item.get('source_url', '')
        if not url.startswith('http'):
            errors.append(f"{prefix}: invalid url '{url}'")

        # 分类检查
        cat = item.get('category', '')
        if cat not in VALID_CATS:
            errors.append(f"{prefix}: invalid category '{cat}'")

        # Tag检查
        if item.get('tag') not in VALID_TAGS:
            errors.append(f"{prefix}: invalid tag '{item.get('tag')}'")

        # consecutive_days检查
        cd = item.get('consecutive_days', 0)
        if not isinstance(cd, int) or cd < 1:
            errors.append(f"{prefix}: consecutive_days must be >= 1, got {cd}")
        if cd > MAX_CONSECUTIVE_DAYS:
            errors.append(f"{prefix}: consecutive_days {cd} (>{MAX_CONSECUTIVE_DAYS}) - MUST rotate out")

    # 分类配额检查
    for country, citems in by_country.items():
        if country not in REQUIRED_COUNTRIES:
            continue
        cat_counts = Counter(i.get('category', '') for i in citems)
        for cat_plain, expected in REQUIRED_CATS.items():
            full_cat = CAT_EMOJI_MAP.get(cat_plain, cat_plain)
            actual = cat_counts.get(full_cat, 0)
            if actual != expected:
                errors.append(f"[{date_str}] QUOTA {country}: {cat_plain} expected {expected}, got {actual}")

    # Tag配额检查
    tag_counts = Counter(i.get('tag', '') for i in items)
    if tag_counts.get('爆', 0) != REQUIRED_BAO_PER_DAY:
        errors.append(f"[{date_str}] TAG 爆: expected {REQUIRED_BAO_PER_DAY}, got {tag_counts.get('爆', 0)}")

    # 3天去重检查
    if check_dedup and prev_dates_data:
        prev_date_keys = {}
        sorted_prev_dates = sorted(prev_dates_data.keys(), reverse=True)[:MAX_CONSECUTIVE_DAYS]
        for pd in sorted_prev_dates:
            for item in prev_dates_data[pd].get('items', []):
                key = item.get('title', '')[:20]
                url = item.get('source_url', '')
                country = item.get('country', '')
                dedup_key = f"{country}|{key}"
                if dedup_key not in prev_date_keys:
                    prev_date_keys[dedup_key] = []
                prev_date_keys[dedup_key].append(pd)

        for item in items:
            title = item.get('title', '')[:20]
            country = item.get('country', '')
            dedup_key = f"{country}|{title}"
            if dedup_key in prev_date_keys:
                appearances = len(prev_date_keys[dedup_key]) + 1
                if appearances > MAX_CONSECUTIVE_DAYS:
                    errors.append(f"[{date_str}] DEDUP: '{item.get('title','')[:30]}...' appears {appearances} consecutive days (>{MAX_CONSECUTIVE_DAYS})")

def validate(filepath, check_all_dates=False):
    """验证数据文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    errors = []

    # 基础结构检查
    if 'today' not in data:
        errors.append("MISSING: 'today' field")
    if 'dates' not in data:
        errors.append("MISSING: 'dates' field")
        print(f"❌ 验证失败：{len(errors)} 条违规")
        for e in errors:
            print(f"  - {e}")
        return len(errors)

    today = data.get('today', '')
    if today and today not in data['dates']:
        errors.append(f"MISSING: today '{today}' not in dates")

    if check_all_dates:
        # 验证所有日期
        prev_data = {}
        for date_str in sorted(data['dates'].keys()):
            day_data = data['dates'][date_str]
            items = day_data.get('items', [])
            validate_items(items, date_str, errors, check_dedup=True, prev_dates_data=prev_data)
            prev_data[date_str] = day_data
    else:
        # 只验证today
        if today in data['dates']:
            day_data = data['dates'][today]
            items = day_data.get('items', [])
            validate_items(items, today, errors)

    # 输出结果
    if errors:
        print(f"❌ 验证失败：{len(errors)} 条违规")
        for e in errors[:50]:
            print(f"  - {e}")
        if len(errors) > 50:
            print(f"  ... and {len(errors)-50} more")
    else:
        # 统计
        if today in data['dates']:
            items = data['dates'][today].get('items', [])
            tag_counts = Counter(i.get('tag', '') for i in items)
            tc = tag_counts.get('爆', 0)
            rc = tag_counts.get('热', 0)
            nc = tag_counts.get('新', 0)
            cc = tag_counts.get('常规', 0)
            print(f"✅ 验证通过：0 违规")
            print(f"  📊 总计：{len(items)} 条")
            print(f"  🏷️ 标签：爆{tc} 热{rc} 新{nc} 常规{cc}")

        if check_all_dates:
            total_dates = len(data['dates'])
            total_items = sum(len(d.get('items', [])) for d in data['dates'].values())
            print(f"  📅 验证日期数：{total_dates}")
            print(f"  📊 总条目数：{total_items}")

    return len(errors)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python validate_quality.py <json_file> [--all-dates]")
        print("  --all-dates: 验证所有日期数据（含3天去重检查）")
        sys.exit(1)

    filepath = sys.argv[1]
    check_all = '--all-dates' in sys.argv

    n = validate(filepath, check_all_dates=check_all)
    sys.exit(0 if n == 0 else 1)
