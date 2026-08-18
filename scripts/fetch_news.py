#!/usr/bin/env python3
"""全球旅游新闻采集器 v3 - 健壮版，任何情况下不崩溃"""
import json, os, sys, requests
from datetime import datetime, timedelta
from collections import Counter

TODAY = datetime.now().strftime('%Y-%m-%d')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE, 'data', 'travel_daily.json')
DOCS_DIR = os.path.join(BASE, 'docs')

COUNTRIES = [
    ("中国","China"),("日本","Japan"),("韩国","South Korea"),("泰国","Thailand"),("越南","Vietnam"),
    ("新加坡","Singapore"),("马来西亚","Malaysia"),("印度尼西亚","Indonesia"),("菲律宾","Philippines"),("印度","India"),
    ("美国","United States"),("加拿大","Canada"),("英国","United Kingdom"),("法国","France"),("德国","Germany"),
    ("意大利","Italy"),("西班牙","Spain"),("澳大利亚","Australia"),("新西兰","New Zealand"),("阿联酋","UAE"),
    ("土耳其","Turkey"),("埃及","Egypt"),("俄罗斯","Russia"),("巴西","Brazil"),("墨西哥","Mexico")
]

API_KEYS = {
    'gnews': os.environ.get('GNEWS_API_KEY', ''),
    'google': os.environ.get('GOOGLE_CSE_API_KEY', ''),
    'google_cx': os.environ.get('GOOGLE_CSE_ENGINE_ID', ''),
}

def load_history():
    """读取历史数据，JSON损坏时从零开始"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and 'dates' in data:
                print(f"  📂 加载历史: {len(data.get('dates', {}))} 天数据")
                return data
            print("  ⚠️ JSON格式异常，从零开始")
        except (json.JSONDecodeError, Exception) as e:
            print(f"  ⚠️ 历史数据读取失败: {e}，从零开始")
    return {"today": TODAY, "window": "", "dates": {}}

def get_all_titles(history):
    titles = set()
    try:
        for d, dd in history.get("dates", {}).items():
            for item in dd.get("items", []):
                t = item.get("title", "")
                if t:
                    titles.add(t)
    except Exception:
        pass
    return titles

def search_gnews(query, max_results=5):
    if not API_KEYS['gnews']:
        return []
    try:
        url = f"https://gnews.io/api/v4/search?q={query}&lang=en&max={max_results}&apikey={API_KEYS['gnews']}"
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return []
        data = r.json()
        if not isinstance(data, dict):
            return []
        return data.get('articles', []) or []
    except Exception:
        return []

def search_google(query, max_results=5):
    if not API_KEYS['google'] or not API_KEYS['google_cx']:
        return []
    try:
        url = f"https://customsearch.googleapis.com/customsearch/v1?q={query}&cx={API_KEYS['google_cx']}&key={API_KEYS['google']}&num={max_results}"
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return []
        data = r.json()
        if not isinstance(data, dict):
            return []
        items = data.get('items', []) or []
        results = []
        for i in items:
            if not isinstance(i, dict):
                continue
            results.append({
                'title': i.get('title', ''),
                'description': i.get('snippet', ''),
                'url': i.get('link', '#'),
                'source': {'name': i.get('displayLink', 'Web')}
            })
        return results
    except Exception:
        return []

def search(query):
    results = search_gnews(query)
    if results:
        return results
    return search_google(query)

def classify_cat(title, desc):
    text = ((title or '') + ' ' + (desc or '')).lower()
    if any(k in text for k in ['flight','airline','airport','route','aviation','airfare','飞','航线','航班']):
        return "航线交通"
    if any(k in text for k in ['visa','immigration','entry','border','免签','签证','出入境']):
        return "出入境政策"
    if any(k in text for k in ['hotel','price','currency','exchange','rate','住宿','汇率','物价']):
        return "本地生活"
    if any(k in text for k in ['tourist','visitor','arrival','statistic','data','trend','游客','数据','人次']):
        return "旅游趋势"
    if any(k in text for k in ['festival','event','attraction','museum','exhibition','景点','活动','节日']):
        return "景点活动"
    if any(k in text for k in ['concert','music','film','show','演唱会','音乐','电影']):
        return "文娱信息"
    return "旅游趋势"

def article_to_item(art, zh_name):
    if not isinstance(art, dict):
        return None
    title = (art.get('title') or '').strip()
    desc = (art.get('description') or art.get('content') or '').strip()
    url = art.get('url') or art.get('link') or '#'
    source = art.get('source', {})
    source_name = source.get('name', 'Web') if isinstance(source, dict) else str(source or 'Web')

    if not title:
        return None

    return {
        "title": title,
        "category": "旅游利好要闻",
        "sub_category": classify_cat(title, desc),
        "summary": desc[:120] if desc else f"来自{source_name}的报道",
        "source": source_name,
        "impact": f"影响赴{zh_name}旅行",
        "source_url": url,
        "key_figures": [],
        "travel_advisory": "出行前核实最新政策",
        "tag": "新",
        "country": zh_name
    }

def is_dup(title, titles):
    if not title or title in titles:
        return True
    try:
        for t in titles:
            if len(t) > 10 and len(title) > 10:
                a, b = set(title.lower().split()), set(t.lower().split())
                if a and b and len(a & b) / max(len(a), len(b)) > 0.6:
                    return True
    except Exception:
        pass
    return False

def assign_tags(items):
    if not items:
        return
    ALL_CATS = ["航线交通","出入境政策","本地生活","旅游趋势","景点活动","文娱信息"]
    try:
        cat_idx = hash(items[0]["country"]) % len(ALL_CATS)
    except Exception:
        cat_idx = 0
    boom_cat = ALL_CATS[cat_idx]

    for item in items:
        item["tag"] = "新"

    boom_items = [i for i in items if i.get("sub_category") == boom_cat]
    if boom_items:
        boom_items[0]["tag"] = "爆"

    hot_count = 0
    for offset in range(1, len(ALL_CATS)):
        if hot_count >= 2:
            break
        hcat = ALL_CATS[(cat_idx + offset) % len(ALL_CATS)]
        h_items = [i for i in items if i.get("sub_category") == hcat and i.get("tag") == "新"]
        if h_items:
            h_items[0]["tag"] = "热"
            hot_count += 1

def run():
    print(f" {TODAY} 开始采集...")

    # 检查 API key
    has_api = False
    if API_KEYS['gnews']:
        has_api = True
    if API_KEYS['google'] and API_KEYS['google_cx']:
        has_api = True
    if not has_api:
        print("  ❌ 未配置任何 API key，无法采集新闻")
        print("  请在 GitHub Secrets 中设置 GNEWS_API_KEY 或 GOOGLE_CSE_API_KEY + GOOGLE_CSE_ENGINE_ID")
        sys.exit(1)

    history = load_history()
    all_titles = get_all_titles(history)
    new_items = []
    errors = []

    for zh_name, en_name in COUNTRIES:
        try:
            print(f"   {zh_name}...", end=' ')
            query = f"{en_name} travel tourism visa 2026"
            articles = search(query)
            print(f"API返回{len(articles)}条", end=' ')

            country_items = []
            for art in articles:
                try:
                    item = article_to_item(art, zh_name)
                    if item and not is_dup(item["title"], all_titles):
                        country_items.append(item)
                        all_titles.add(item["title"])
                except Exception as e:
                    continue

            # 不够10条，补充搜索
            max_attempts = 5
            attempt = 0
            while len(country_items) < 10 and attempt < max_attempts:
                query2 = f"{en_name} {['airline','visa','hotel','tourist','festival','concert'][len(country_items) % 6]} 2026"
                more = search(query2)
                if not more:
                    break
                added = False
                for art in more:
                    try:
                        item = article_to_item(art, zh_name)
                        if item and not is_dup(item["title"], all_titles):
                            country_items.append(item)
                            all_titles.add(item["title"])
                            added = True
                            break
                    except Exception:
                        continue
                if not added:
                    break
                attempt += 1

            if len(country_items) < 10:
                print(f"仅{len(country_items)}条", end=' ')

            assign_tags(country_items)
            new_items.extend(country_items)
            print(f"→ {len(country_items)}条")
        except Exception as e:
            errors.append(f"{zh_name}: {e}")
            print(f"❌ {e}")

    # 检查结果
    if len(new_items) == 0:
        print("\n  ❌ API 返回 0 条新闻，可能原因：")
        print("     1. GNews API key 额度耗尽（免费100次/天）")
        print("     2. Google CSE key 无效")
        print("     3. 网络连接问题")
        print("     历史数据已保留，今天数据为空")

    # 构建输出
    history["today"] = TODAY
    history["window"] = f"{(datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')} ~ {TODAY}"

    tc = Counter(i.get("tag", "新") for i in new_items)

    history["dates"][TODAY] = {
        "total_items": len(new_items),
        "tag_summary": {"爆": tc.get("爆",0), "热": tc.get("热",0), "新": tc.get("新",0)},
        "items": new_items
    }

    # 清理30天以上
    cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    for d in [k for k in history["dates"] if k < cutoff]:
        del history["dates"][d]
        print(f"  🗑️ 清理 {d}")

    # 保存
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  ❌ 保存失败: {e}")
        sys.exit(1)

    print(f"\n✅ 完成: {TODAY} | {len(new_items)}条 | 爆{tc.get('爆',0)} 热{tc.get('热',0)} 新{tc.get('新',0)}")
    print(f"📅 历史日期: {sorted(history['dates'].keys())}")

if __name__ == '__main__':
    run()
