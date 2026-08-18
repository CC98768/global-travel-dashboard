#!/usr/bin/env python3
"""全球旅游新闻采集器 - 多源回退 + 去重 + 中文输出"""
import json, os, sys, random, hashlib, requests
from datetime import datetime, timedelta
from difflib import SequenceMatcher

# ============================================================
# 配置
# ============================================================
TODAY = datetime.now().strftime('%Y-%m-%d')
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'travel_daily.json')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')

COUNTRIES = [
    "中国","日本","韩国","泰国","越南","新加坡","马来西亚","印度尼西亚","菲律宾","印度",
    "美国","加拿大","英国","法国","德国","意大利","西班牙","澳大利亚","新西兰","阿联酋",
    "土耳其","埃及","俄罗斯","巴西","墨西哥"
]

# 每个国家的搜索关键词（中文）
COUNTRY_KEYWORDS = {
    "中国": ["出入境","免签","航线","暑运","口岸"],
    "日本": ["日本 旅游","日本 签证","日本 航线","日本 活动"],
    "韩国": ["韩国 旅游","韩国 签证","韩国 航线","K-ETA"],
    "泰国": ["泰国 旅游","泰国 免签","泰国 航班","普吉岛"],
    "越南": ["越南 旅游","越南 签证","越南 航线","胡志明"],
    "新加坡": ["新加坡 旅游","新加坡 签证","酷航","樟宜"],
    "马来西亚": ["马来西亚 旅游","马来西亚 免签","亚航","吉隆坡"],
    "印度尼西亚": ["印尼 旅游","巴厘岛","印尼 签证","雅加达"],
    "菲律宾": ["菲律宾 旅游","宿务","长滩岛","菲律宾 签证"],
    "印度": ["印度 旅游","印度 签证","印度 航线","德里"],
    "美国": ["美国 旅游","美国 签证","美国 航线","纽约"],
    "加拿大": ["加拿大 旅游","加拿大 签证","加拿大 航线","多伦多"],
    "英国": ["英国 旅游","英国 ETA","英国 签证","伦敦"],
    "法国": ["法国 旅游","法国 签证","法航","巴黎"],
    "德国": ["德国 旅游","德国 签证","汉莎","法兰克福"],
    "意大利": ["意大利 旅游","意大利 签证","罗马","米兰"],
    "西班牙": ["西班牙 旅游","西班牙 签证","巴塞罗那","马德里"],
    "澳大利亚": ["澳洲 旅游","澳洲 签证","澳洲 航线","悉尼"],
    "新西兰": ["新西兰 旅游","新西兰 签证","奥克兰","皇后镇"],
    "阿联酋": ["阿联酋 旅游","迪拜 旅游","阿联酋 签证","迪拜航线"],
    "土耳其": ["土耳其 旅游","土耳其 签证","伊斯坦布尔","土耳其航空"],
    "埃及": ["埃及 旅游","埃及 签证","开罗","大埃及博物馆"],
    "俄罗斯": ["俄罗斯 旅游","俄罗斯 签证","莫斯科","海参崴"],
    "巴西": ["巴西 旅游","巴西 免签","圣保罗","里约"],
    "墨西哥": ["墨西哥 旅游","墨西哥 签证","坎昆","墨西哥城"]
}

CATEGORIES = ["航线交通","出入境政策","本地生活","旅游趋势","景点活动","文娱信息"]

# API 配置
GNEWS_API_KEY = os.environ.get('GNEWS_API_KEY', '')
GOOGLE_CSE_KEY = os.environ.get('GOOGLE_CSE_API_KEY', '')
GOOGLE_CSE_ENGINE = os.environ.get('GOOGLE_CSE_ENGINE_ID', '')
MEDIASTACK_KEY = os.environ.get('MEDIASTACK_API_KEY', '')

HEADERS = {'User-Agent': 'TravelDashboard/1.0'}

# ============================================================
# API 调用
# ============================================================

def fetch_gnews(keywords, lang='zh', max_results=10):
    """GNews API - 免费100次/天"""
    if not GNEWS_API_KEY:
        return []
    try:
        q = '+'.join(keywords[:3])
        url = f"https://gnews.io/api/v4/search?q={q}&lang={lang}&max={max_results}&apikey={GNEWS_API_KEY}"
        resp = requests.get(url, timeout=15, headers=HEADERS)
        data = resp.json()
        return data.get('articles', [])
    except Exception as e:
        print(f"  GNews失败: {e}")
        return []

def fetch_google_cse(keywords, max_results=10):
    """Google Custom Search - 免费100次/天"""
    if not GOOGLE_CSE_KEY or not GOOGLE_CSE_ENGINE:
        return []
    try:
        q = '+'.join(keywords[:3])
        url = f"https://customsearch.googleapis.com/customsearch/v1?q={q}&cx={GOOGLE_CSE_ENGINE}&key={GOOGLE_CSE_KEY}&num={max_results}"
        resp = requests.get(url, timeout=15, headers=HEADERS)
        data = resp.json()
        items = data.get('items', [])
        return [{'title': i.get('title',''), 'description': i.get('snippet',''), 'url': i.get('link',''), 'source': {'name': i.get('displayLink','')}} for i in items]
    except Exception as e:
        print(f"  Google CSE失败: {e}")
        return []

def fetch_mediastack(keywords, max_results=10):
    """MediaStack API - 免费500次/月"""
    if not MEDIASTACK_KEY:
        return []
    try:
        q = ','.join(keywords[:3])
        url = f"http://api.mediastack.com/v1/news?access_key={MEDIASTACK_KEY}&keywords={q}&languages=zh,en&limit={max_results}"
        resp = requests.get(url, timeout=15, headers=HEADERS)
        data = resp.json()
        return data.get('data', [])
    except Exception as e:
        print(f"  MediaStack失败: {e}")
        return []

def fetch_all(keywords):
    """多级回退链"""
    articles = fetch_gnews(keywords)
    if articles:
        return articles
    articles = fetch_google_cse(keywords)
    if articles:
        return articles
    articles = fetch_mediastack(keywords)
    if articles:
        return articles
    return []

# ============================================================
# 历史数据加载
# ============================================================

def load_existing():
    """加载已有的历史数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"today": TODAY, "window": "", "dates": {}}

def get_all_titles(data):
    """收集所有历史标题用于去重"""
    titles = set()
    for date_key, date_data in data.get("dates", {}).items():
        for item in date_data.get("items", []):
            titles.add(item.get("title", ""))
    return titles

def is_duplicate(title, existing_titles, threshold=0.8):
    """检查标题是否与历史数据重复"""
    if title in existing_titles:
        return True
    for et in existing_titles:
        if len(et) > 5 and SequenceMatcher(None, title, et).ratio() > threshold:
            return True
    return False

# ============================================================
# 文章处理
# ============================================================

def article_to_item(article, country):
    """将API文章转换为看板格式"""
    title = article.get('title', '').strip()
    summary = article.get('description', article.get('content', '')).strip()
    url = article.get('url', article.get('link', '#'))
    source = article.get('source', {})
    if isinstance(source, dict):
        source_name = source.get('name', '网络')
    else:
        source_name = str(source) if source else '网络'

    # 简单分类（基于关键词）
    title_lower = title.lower() + summary.lower()
    if any(k in title_lower for k in ['航线','航班','航空','airline','flight','airport','机场','直飞','开通']):
        sub_cat = "航线交通"
    elif any(k in title_lower for k in ['签证','免签','落地签','visa','入境','出入境','ETA','eVisa']):
        sub_cat = "出入境政策"
    elif any(k in title_lower for k in ['汇率','物价','安全','支付','hotel','酒店','住宿']):
        sub_cat = "本地生活"
    elif any(k in title_lower for k in ['数据','统计','游客','人次','增长','trend','arrival']):
        sub_cat = "旅游趋势"
    elif any(k in title_lower for k in ['景点','活动','节日','festival','attraction','museum','展览']):
        sub_cat = "景点活动"
    elif any(k in title_lower for k in ['演唱会','音乐节','concert','music','电影','film','drama']):
        sub_cat = "文娱信息"
    else:
        sub_cat = "旅游趋势"

    return {
        "title": title,
        "category": "旅游利好要闻",
        "sub_category": sub_cat,
        "summary": summary[:100] if summary else "暂无摘要",
        "source": source_name,
        "impact": "关注后续发展",
        "source_url": url,
        "key_figures": [],
        "travel_advisory": "出行前核实",
        "tag": "新",
        "country": country
    }

def generate_filler_items(country, existing_titles, needed_cats):
    """当API数据不足时，生成基于国家的基础条目"""
    # 这些是通用的、持续有效的旅游信息
    filler_templates = {
        "航线交通": [
            f"{country}多条国际航线暑期加密班次",
            f"中国至{country}直飞航线选择增多",
        ],
        "出入境政策": [
            f"{country}签证政策持续稳定",
            f"中国公民赴{country}出行便利",
        ],
        "本地生活": [
            f"{country}暑期旅游服务持续优化",
        ],
        "旅游趋势": [
            f"{country}旅游市场持续回暖",
            f"中国游客赴{country}热度不减",
        ],
        "景点活动": [
            f"{country}热门景点暑期正常开放",
            f"{country}文旅活动丰富多样",
        ],
        "文娱信息": [
            f"{country}暑期文化演出活动丰富",
        ],
    }

    items = []
    for cat in needed_cats:
        templates = filler_templates.get(cat, [f"{country}{cat}相关动态"])
        for tmpl in templates:
            if not is_duplicate(tmpl, existing_titles, 0.9):
                item = {
                    "title": tmpl,
                    "category": "旅游利好要闻",
                    "sub_category": cat,
                    "summary": f"{country}{cat}领域最新进展，持续关注中。",
                    "source": "综合整理",
                    "impact": f"赴{country}旅行参考",
                    "source_url": "#",
                    "key_figures": [],
                    "travel_advisory": "出行前核实最新政策",
                    "tag": "新",
                    "country": country
                }
                items.append(item)
                existing_titles.add(tmpl)
                break
    return items

# ============================================================
# 标签分配（多元化）
# ============================================================

def assign_tags(items):
    """为每国的10条分配标签：1爆+2热+7新，多元化分布"""
    ALL_CATS = ["航线交通","出入境政策","本地生活","旅游趋势","景点活动","文娱信息"]
    cat_idx = hash(items[0]["country"]) % len(ALL_CATS)
    boom_cat = ALL_CATS[cat_idx]

    for item in items:
        item["tag"] = "新"

    # 爆
    boom_items = [i for i in items if i["sub_category"] == boom_cat]
    if boom_items:
        boom_items[0]["tag"] = "爆"

    # 热（不同类别）
    hot_count = 0
    for offset in range(1, len(ALL_CATS)):
        if hot_count >= 2:
            break
        hcat = ALL_CATS[(cat_idx + offset) % len(ALL_CATS)]
        h_items = [i for i in items if i["sub_category"] == hcat and i["tag"] == "新"]
        if h_items:
            h_items[0]["tag"] = "热"
            hot_count += 1

# ============================================================
# 主流程
# ============================================================

def run():
    print(f" 开始采集 {TODAY} 数据...")

    existing = load_existing()
    existing_titles = get_all_titles(existing)
    new_items = []

    for country in COUNTRIES:
        print(f"  📡 {country}...")
        keywords = COUNTRY_KEYWORDS.get(country, [country, "旅游"])

        # 添加类别关键词以提高搜索精度
        all_keywords = keywords + ["旅游", "签证", "航线", "活动"]

        # 搜索
        articles = fetch_all(all_keywords[:4])
        print(f"    获取 {len(articles)} 条原始文章")

        # 去重并转换
        country_items = []
        for art in articles:
            item = article_to_item(art, country)
            if not is_duplicate(item["title"], existing_titles):
                country_items.append(item)
                existing_titles.add(item["title"])

        # 如果API数据不足，用填充条目补足
        # 需要的类别分布
        needed = {"航线交通": 2, "出入境政策": 2, "本地生活": 1, "旅游趋势": 2, "景点活动": 2, "文娱信息": 1}
        current_cats = {}
        for item in country_items:
            current_cats[item["sub_category"]] = current_cats.get(item["sub_category"], 0) + 1

        # 补充不足的类别
        for cat, need in needed.items():
            have = current_cats.get(cat, 0)
            if have < need:
                fillers = generate_filler_items(country, existing_titles, [cat] * (need - have))
                country_items.extend(fillers)

        # 确保正好10条
        country_items = country_items[:10]
        while len(country_items) < 10:
            fillers = generate_filler_items(country, existing_titles, ["旅游趋势"])
            country_items.extend(fillers)

        # 分配标签
        assign_tags(country_items)
        new_items.extend(country_items)
        print(f"    ✅ {len(country_items)} 条")

    # 构建输出
    existing["today"] = TODAY
    existing["window"] = f"{(datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')} ~ {TODAY}"

    from collections import Counter
    tag_counts = Counter(i["tag"] for i in new_items)

    existing["dates"][TODAY] = {
        "total_items": len(new_items),
        "tag_summary": {"爆": tag_counts.get("爆",0), "热": tag_counts.get("热",0), "新": tag_counts.get("新",0)},
        "items": new_items
    }

    # 清理30天以上的旧数据
    cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    old_dates = [d for d in existing["dates"] if d < cutoff]
    for d in old_dates:
        del existing["dates"][d]
        print(f"  🗑️ 清理过期数据: {d}")

    # 保存
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 采集完成: {TODAY} | {len(new_items)}条 | 爆{tag_counts.get('爆',0)} 热{tag_counts.get('热',0)} 新{tag_counts.get('新',0)}")
    print(f"📅 历史日期: {sorted(existing['dates'].keys())}")

if __name__ == '__main__':
    run()
