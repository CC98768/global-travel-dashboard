#!/usr/bin/env python3
"""全球旅游新闻采集器 v4 - Google News RSS 多语言多关键词，无需 API key"""
import json, os, re, time, sys, logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from difflib import SequenceMatcher

try:
    import feedparser
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"缺少依赖: {e}")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

TODAY = datetime.now().strftime('%Y-%m-%d')
BASE = Path(__file__).parent.parent
DATA_FILE = BASE / 'data' / 'travel_daily.json'
DOCS_DIR = BASE / 'docs'

LOCALE_MAP = {
    "中国": [("zh-CN","CN"),("en","US")],
    "日本": [("ja","JP"),("zh-CN","CN"),("en","US")],
    "韩国": [("ko","KR"),("zh-CN","CN"),("en","US")],
    "泰国": [("th","TH"),("zh-CN","CN"),("en","US")],
    "新加坡": [("en","SG"),("zh-CN","CN")],
    "越南": [("vi","VN"),("zh-CN","CN"),("en","US")],
    "马来西亚": [("ms","MY"),("zh-CN","CN"),("en","MY")],
    "印度": [("en","IN"),("zh-CN","CN")],
    "菲律宾": [("en","PH"),("zh-CN","CN")],
    "印度尼西亚": [("id","ID"),("zh-CN","CN"),("en","US")],
    "法国": [("fr","FR"),("zh-CN","CN"),("en","US")],
    "意大利": [("it","IT"),("zh-CN","CN"),("en","US")],
    "西班牙": [("es","ES"),("zh-CN","CN"),("en","US")],
    "英国": [("en","GB"),("zh-CN","CN")],
    "德国": [("de","DE"),("zh-CN","CN"),("en","US")],
    "希腊": [("el","GR"),("en","US")],
    "土耳其": [("tr","TR"),("en","US")],
    "瑞士": [("de","CH"),("en","US")],
    "俄罗斯": [("ru","RU"),("zh-CN","CN"),("en","US")],
    "美国": [("en","US"),("zh-CN","CN")],
    "加拿大": [("en","CA"),("fr","CA"),("zh-CN","CN")],
    "墨西哥": [("es","MX"),("en","US")],
    "巴西": [("pt","BR"),("en","US")],
    "阿根廷": [("es","AR"),("en","US")],
    "澳大利亚": [("en","AU"),("zh-CN","CN")],
    "新西兰": [("en","NZ"),("zh-CN","CN")],
    "阿联酋": [("en","AE"),("zh-CN","CN")],
    "埃及": [("ar","EG"),("en","US")],
    "南非": [("en","ZA"),("zh-CN","CN")],
}

COUNTRIES_25 = [
    ("中国","中国旅游 出入境 利好"),
    ("日本","Japan tourism travel"),
    ("韩国","Korea tourism travel"),
    ("泰国","Thailand tourism travel"),
    ("新加坡","Singapore tourism travel"),
    ("越南","Vietnam tourism travel"),
    ("马来西亚","Malaysia tourism travel"),
    ("印度","India tourism travel"),
    ("菲律宾","Philippines tourism travel"),
    ("印度尼西亚","Indonesia Bali tourism travel"),
    ("法国","France tourism travel"),
    ("意大利","Italy tourism travel"),
    ("西班牙","Spain tourism travel"),
    ("英国","UK Britain tourism travel"),
    ("德国","Germany tourism travel"),
    ("土耳其","Turkey tourism travel"),
    ("瑞士","Switzerland tourism travel"),
    ("俄罗斯","Russia tourism travel"),
    ("美国","USA travel tourism"),
    ("加拿大","Canada tourism travel"),
    ("墨西哥","Mexico tourism travel"),
    ("巴西","Brazil tourism travel"),
    ("阿根廷","Argentina tourism travel"),
    ("澳大利亚","Australia travel tourism"),
    ("新西兰","New Zealand travel tourism"),
    ("阿联酋","UAE Dubai tourism travel"),
    ("埃及","Egypt tourism travel 2026"),
    ("南非","South Africa tourism travel"),
]

FLIGHT_QUERIES = {
    "中国":"中国 航班 航线 新开","日本":"Japan airline flight route new",
    "韩国":"Korea airline flight route","泰国":"Thailand airline flight Bangkok",
    "新加坡":"Singapore airline flight Changi","越南":"Vietnam airline flight",
    "马来西亚":"Malaysia airline flight KLIA","印度":"India airline flight route",
    "菲律宾":"Philippines airline flight","印度尼西亚":"Indonesia airline flight Bali",
    "法国":"France airline flight Paris","意大利":"Italy airline flight Rome",
    "西班牙":"Spain airline flight Barcelona","英国":"UK airline flight London",
    "德国":"Germany airline flight Frankfurt","希腊":"Greece flight Athens",
    "土耳其":"Turkey airline flight Istanbul","瑞士":"Switzerland airline flight Zurich",
    "俄罗斯":"Russia airline flight Moscow","美国":"USA airline flight route new",
    "加拿大":"Canada airline flight Toronto Vancouver","墨西哥":"Mexico airline flight Cancun",
    "巴西":"Brazil airline flight Sao Paulo",
    "阿根廷":"Argentina airline flight Buenos Aires",
    "澳大利亚":"Australia airline flight Sydney",
    "新西兰":"New Zealand airline flight Auckland",
    "阿联酋":"UAE airline flight Dubai",
    "埃及":"Egypt airline flight Cairo",
    "南非":"South Africa airline flight Johannesburg",
}

VISA_QUERIES = {
    "中国":"中国 免签 签证 入境 2026","日本":"Japan visa entry policy 2026",
    "韩国":"Korea visa entry policy 2026","泰国":"Thailand visa free extension 2026",
    "新加坡":"Singapore visa free China 2026","越南":"Vietnam visa e-visa policy",
    "马来西亚":"Malaysia visa free China 2026","印度":"India visa policy e-visa",
    "菲律宾":"Philippines visa policy 2026","印度尼西亚":"Indonesia visa free 2026",
    "法国":"France Schengen visa policy 2026","意大利":"Italy visa Schengen 2026",
    "西班牙":"Spain visa Schengen policy","英国":"UK ETA visa policy 2026",
    "德国":"Germany Schengen visa policy","希腊":"Greece visa Schengen 2026",
    "土耳其":"Turkey e-visa policy 2026","瑞士":"Switzerland Schengen visa",
    "俄罗斯":"Russia visa policy 2026","美国":"USA visa B1 B2 policy 2026",
    "加拿大":"Canada visa tourist policy 2026","墨西哥":"Mexico visa policy 2026",
    "巴西":"Brazil visa tourist policy 2026",
    "阿根廷":"Argentina visa tourist policy 2026",
    "澳大利亚":"Australia ETA visa 2026",
    "新西兰":"New Zealand NZeTA visa 2026",
    "阿联酋":"UAE visa free entry policy 2026",
    "埃及":"Egypt visa e-visa policy 2026",
    "南非":"South Africa visa policy 2026",
}

EXTRA_QUERIES = {
    "瑞士": ["Switzerland Zurich tourism travel","Switzerland Alps tourism","Switzerland train scenic"],
    "巴西": ["Brazil Rio tourism travel","Brazil Sao Paulo tourism","Brazil Amazon tourism"],
    "印度尼西亚": ["Indonesia Bali tourism travel 2026","Jakarta tourism news","Lombok tourism"],
    "土耳其": ["Turkey Cappadocia tourism","Turkey Antalya tourism","Istanbul tourism 2026"],
    "英国": ["UK Edinburgh tourism","UK Scotland Highlands tourism","UK Wales tourism"],
    "墨西哥": ["Mexico Riviera Maya tourism","Cancun tourism 2026","Mexico City tourism"],
}

CATEGORIES = ["航线交通","出入境政策","本地生活","旅游趋势","景点活动","文娱信息"]
SC_EXPECTED = {"航线交通":2,"出入境政策":2,"本地生活":1,"旅游趋势":2,"景点活动":2,"文娱信息":1}
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TravelDashboard/4.0)"}

def classify(title, summary=""):
    text = (title + " " + summary).lower()
    visa_strong = ['visa','免签','签证','入境政策','border control','passport','immigration policy',
                   '海关','通关政策','e-visa','落地签','entry ban','entry restriction',
                   'travel ban','travel restriction','quarantine policy','health protocol',
                   '边境','出入境','居留','停留期','过境免签','transit visa','working holiday']
    visa_weak = ['visa','passport','border','immigration','custom','海关','入境','出境',
                 '免签','签证','落地签','电子签','e-visa','permit','ban','restrict',
                 '政策','policy','regulation','measure','放宽','收紧','protocol']
    flight_strong = ['flight','airline','航线','航班','airport','机场','aviation',
                     '航空','直飞','airfare','boeing','airbus','qantas','airasia',
                     '新航线','新航班','增班','减班','停飞','复航','code share',
                     'non-stop','direct flight','connecting flight',
                     '航司','航空公司','廉价航空','low-cost carrier','budget airline']
    flight_weak = ['flight','airline','route','航线','航班','airport','机场','航空','直飞',
                   'airfare','ticket','fly','flew','boeing','airbus','opens new route',
                   'launches route','resume','恢复航线','通航','执飞','aircraft']
    event_strong = ['festival','concert','演唱会','exhibition','展览','celebration',
                    'carnival','parade','firework','opera','ballet','theater','theatre',
                    'biennale','film festival','music festival','art festival','jazz festival',
                    '演唱会','音乐节','艺术节','电影节','戏剧节','双年展',
                    'opening ceremony','gala','award ceremony',
                    '开幕式','闭幕式','颁奖典礼','文艺汇演','巡游']
    event_weak = ['festival','concert','exhibition','show','演出','celebration','art','艺术',
                  'carnival','parade','firework','competition','race','marathon','opera','ballet',
                  'theater','film','music','biennale','gala','ceremony','anniversary',
                  '节','演出','展览','文艺','赛事','比赛','颁奖']
    spot_strong = ['attraction','景区','museum','博物馆','temple','寺庙','hiking','徒步',
                   'beach','island','mountain','river','lake','resort','diving','snorkel','surf',
                   'national park','theme park','amusement park','botanical garden','zoo',
                   'heritage site','unesco','world heritage','ancient','ruins','castle',
                   'palace','cathedral','monument','landmark','scenic spot','viewpoint',
                   '景点','国家公园','主题公园','游乐园','植物园','动物园',
                   '遗产','遗址','古城','古堡','教堂','纪念碑','地标','观景台',
                   '缆车','索道','hot spring','温泉','ski resort','滑雪场']
    spot_weak = ['attraction','景区','museum','temple','beach','island','mountain',
                 'park','garden','resort','diving','snorkel','surf','hiking',
                 'tour','游览','open','开放','reopen','重新开放','upgrade','升级',
                 'reservation','预约','limit','限流','capacity',
                 '寺庙','公园','海滩','岛屿','山区','花园','度假村','潜水','冲浪',
                 '重新开放','升级改造','门票','ticket','admission','entrance fee']
    life_strong = ['hotel','酒店','restaurant','餐厅','餐饮','支付','payment',
                   'night market','夜市','shopping mall','购物中心','住宿','hostel','mrt',
                   'subway','metro','uber','grab','taxi','巴士','公交','高铁','railway',
                   '便利店','supermarket','超市','cafe','咖啡馆','bar','酒吧','nightlife',
                   'city pass','tourist card','sim card','e-sim','roaming','currency exchange',
                   '换汇','退税','tax refund','tipping','小费']
    life_weak = ['hotel','酒店','restaurant','餐饮','支付','payment','transport','交通',
                 '夜市','market','shopping','购物','住宿','hostel','mrt','subway','uber',
                 'grab','taxi','bus','train','地铁','公交','打车','外卖','delivery',
                 'wifi','5g','digital payment','cashless','无现金','atm','currency','货币']
    def score(strong_list, weak_list):
        s = sum(2 for kw in strong_list if kw in text)
        s += sum(1 for kw in weak_list if kw in text)
        return s
    scores = {
        "出入境政策": score(visa_strong, visa_weak),
        "航线交通": score(flight_strong, flight_weak),
        "文娱信息": score(event_strong, event_weak),
        "景点活动": score(spot_strong, spot_weak),
        "本地生活": score(life_strong, life_weak),
        "旅游趋势": 0,
    }
    max_score = max(scores.values())
    if max_score < 2:
        return "旅游趋势"
    best = [k for k, v in scores.items() if v == max_score and k != "旅游趋势"]
    if best:
        return best[0]
    return max(scores, key=scores.get)

def fetch_google_news(country, base_query, max_per_query=50):
    entries = []
    locales = LOCALE_MAP.get(country, [("zh-CN","CN"),("en","US")])
    fetch_tasks = []
    for hl, gl in locales:
        url = f"https://news.google.com/rss/search?q={quote(base_query)}&hl={hl}&gl={gl}&ceid={gl}:{hl}"
        fetch_tasks.append((url, hl, gl))
    if country in FLIGHT_QUERIES:
        hl, gl = locales[0]
        url = f"https://news.google.com/rss/search?q={quote(FLIGHT_QUERIES[country])}&hl={hl}&gl={gl}&ceid={gl}:{hl}"
        fetch_tasks.append((url, hl, gl))
    if country in VISA_QUERIES:
        hl, gl = locales[0]
        url = f"https://news.google.com/rss/search?q={quote(VISA_QUERIES[country])}&hl={hl}&gl={gl}&ceid={gl}:{hl}"
        fetch_tasks.append((url, hl, gl))
    if locales[0][0] != "en":
        url = f"https://news.google.com/rss/search?q={quote(base_query)}&hl=en&gl=US&ceid=US:en"
        fetch_tasks.append((url, "en", "US"))
    if country in EXTRA_QUERIES:
        hl, gl = locales[0]
        for eq in EXTRA_QUERIES[country]:
            url = f"https://news.google.com/rss/search?q={quote(eq)}&hl={hl}&gl={gl}&ceid={gl}:{hl}"
            fetch_tasks.append((url, hl, gl))
    try:
        all_feed_entries = []
        seen_urls = set()
        for url, hl, gl in fetch_tasks:
            try:
                feed = feedparser.parse(url, request_headers=HEADERS)
                if feed.entries:
                    for entry in feed.entries[:max_per_query]:
                        link = entry.get('link', '')
                        if link and link not in seen_urls:
                            seen_urls.add(link)
                            all_feed_entries.append(entry)
                time.sleep(0.2)
            except:
                pass
        if not all_feed_entries:
            return []
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        for entry in all_feed_entries:
            pub = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            if pub and pub < cutoff:
                continue
            title = entry.get('title', '').strip()
            summary_html = entry.get('summary', entry.get('description', '')).strip()
            # 清理 HTML 标签
            summary = summary_html
            if '<' in summary:
                try:
                    summary = BeautifulSoup(summary_html, 'html.parser').get_text(separator=' ', strip=True)
                except:
                    summary = re.sub(r'<[^>]+>', ' ', summary_html)
            summary = re.sub(r'\s+', ' ', summary).strip()[:200]
            if not title:
                continue
            entries.append({
                "raw_title": title,
                "raw_summary": summary,
                "source_name": entry.get('source', {}).get('title', 'Google News'),
                "source_url": entry.get('link', ''),
                "published": pub.isoformat() if pub else None,
                "country_hint": country,
            })
        if entries:
            log.info(f"  {country}: {len(entries)} 条")
    except Exception as e:
        log.error(f"  {country}: {e}")
    return entries

def fetch_article_details(url, timeout=10):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'lxml')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        return soup.get_text(separator=' ', strip=True)[:2000]
    except:
        return ""

def dedup_similar(entries, threshold=0.72):
    if not entries:
        return []
    unique = [entries[0]]
    for e in entries[1:]:
        t = e.get("raw_title", "").lower()
        if not any(SequenceMatcher(None, t, u.get("raw_title", "").lower()).ratio() > threshold for u in unique):
            unique.append(e)
    return unique

def dedup_vs_history(entries, history):
    hist_titles = set()
    for dd in history.get("dates", {}).values():
        for it in dd.get("items", []):
            hist_titles.add(it.get("title", "").lower())
    result = []
    for e in entries:
        t = e.get("raw_title", "").lower()
        if not any(SequenceMatcher(None, t, ht).ratio() > 0.7 for ht in hist_titles):
            result.append(e)
    return result

def assign_tags(items, country):
    for i in items:
        i["tag"] = "新"
    idx = hash(country) % len(CATEGORIES)
    boom_cat = CATEGORIES[idx]
    bc = [i for i in items if i["sub_category"] == boom_cat]
    if bc:
        bc[0]["tag"] = "爆"
    hot_n = 0
    for off in range(1, len(CATEGORIES)):
        if hot_n >= 2:
            break
        hc = CATEGORIES[(idx + off) % len(CATEGORIES)]
        hcd = [i for i in items if i["sub_category"] == hc and i["tag"] == "新"]
        if hcd:
            hcd[0]["tag"] = "热"
            hot_n += 1

def select_quota(items, target=10):
    sel, rem = [], list(items)
    for cat, cnt in SC_EXPECTED.items():
        ci = [i for i in rem if i["sub_category"] == cat]
        sel.extend(ci[:cnt])
        for i in ci[:cnt]:
            if i in rem:
                rem.remove(i)
    if len(sel) < target:
        sel.extend(rem[:target - len(sel)])
    return sel[:target]

def extract_figures_from_text(text):
    figures = []
    figures.extend(re.findall(r'[\d.]+%', text)[:2])
    figures.extend(re.findall(r'[\d,]+(?:\.\d+)?[亿美元欧镑日元韩元泰铢澳元加元]', text)[:2])
    figures.extend(re.findall(r'[\d.]+[万千百]?[人次]', text)[:2])
    figures.extend(re.findall(r'(?:增长|增加|上升|提升|下降|减少|缩减)[\d.]+[%百分之]*', text[:300])[:2])
    figures.extend(re.findall(r'\d{4}年\d{1,2}月(?:\d{1,2}日)?', text)[:2])
    figures.extend(re.findall(r'[\d,]+(?:万|亿|百万)', text)[:2])
    seen = set()
    unique = []
    for f in figures:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique[:5] if unique else ['详见原文']

def gen_impact(title, summary, full_text, cat):
    text = (title + " " + summary + " " + full_text).lower()
    impacts = {
        "航线交通": [
            (['new','新增','开通','恢复','resume','launch'], '新航线/新运力投入运营，旅客出行选择增加，关注初期促销票价'),
            (['取消','停飞','cancel','suspend','delay'], '航线调整影响旅客出行计划，建议尽早改签或选择替代方案'),
            (['sale','促销','discount','优惠','低价'], '票价优惠降低出行成本，适合灵活日期的旅客抓住窗口期'),
        ],
        "出入境政策": [
            (['visa-free','免签','exempt','waive'], '免签政策降低出行门槛，预计带动相关目的地客流显著增长'),
            (['restrict','限制','ban','禁令','收紧'], '政策收紧增加出行复杂度，需提前确认最新要求并留足办理时间'),
            (['extend','延长','扩大','expand'], '政策放宽利好跨境出行，商务和旅游往来更加便利'),
        ],
        "本地生活": [
            (['new','新','open','开业','推出','launch'], '新设施/新服务提升当地旅游体验，值得纳入行程规划'),
            (['price','涨价','上涨','increase','rise'], '当地消费成本上升，建议提前做好预算规划'),
        ],
        "景点活动": [
            (['reopen','重新开放','升级','upgrade','renovat'], '景区升级后体验提升，但需确认预约要求和最新开放信息'),
            (['limit','限流','预约','reservation','capacity'], '限流措施保障游览品质，务必提前预约避免扑空'),
        ],
        "文娱信息": [
            (['ticket','票','booking','预订'], '热门活动票务紧张，建议尽早购票并确认退改政策'),
        ],
    }
    defaults = {
        "航线交通": '航空运力变化影响出行成本和便利性，建议比价后预订',
        "出入境政策": '出入境政策调整，出行前务必确认最新要求',
        "本地生活": '当地生活服务变化，出行前了解最新情况',
        "旅游趋势": '旅游市场动态值得关注，影响目的地选择和出行时机',
        "景点活动": '景点/活动信息更新，建议提前确认开放时间和门票政策',
        "文娱信息": '文化娱乐活动丰富目的地体验，可纳入行程但需提前规划',
    }
    for kw_list, msg in impacts.get(cat, []):
        if any(kw in text for kw in kw_list):
            return msg
    if cat == "旅游趋势":
        numbers = re.findall(r'[\d.]+%', text)
        if numbers:
            return f'数据显示旅游市场变化明显（{numbers[0]}），旅客可根据趋势调整出行计划'
    return defaults.get(cat, '关注最新动态，出行前核实相关信息')

def gen_advisory(title, summary, full_text, cat):
    text = (title + " " + summary + " " + full_text).lower()
    advisories = []
    dates = re.findall(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{1,2}月\d{1,2}日|\d{1,2}月)', text)
    if dates:
        advisories.append(f'注意关键时间节点：{dates[0]}')
    adv_map = {
        "航线交通": ['关注航司官网获取最新航班动态'],
        "出入境政策": ['政策可能随时调整，出发前48小时再次确认', '确保护照有效期不少于6个月'],
        "景点活动": ['关注景区官方渠道获取最新开放信息'],
        "文娱信息": ['热门场次建议提前2-4周购票'],
    }
    if cat == "航线交通" and ('sale' in text or '促销' in text):
        advisories.append('促销票限时限量，确认行程后尽快下单')
    if cat == "景点活动" and ('预约' in text or 'reservation' in text):
        advisories.insert(0, '需提前在线预约，现场可能不售票')
    advisories.extend(adv_map.get(cat, ['出行前关注目的地官方旅游信息']))
    return '；'.join(advisories[:3]) if advisories else '出行前核实最新信息'

def collect_all():
    all_entries = []
    for country, query in COUNTRIES_25:
        entries = fetch_google_news(country, query)
        all_entries.extend(entries)
        time.sleep(0.3)
    log.info(f"  RSS总计: {len(all_entries)} 条原始")
    all_entries = dedup_similar(all_entries)
    log.info(f"  去重后: {len(all_entries)} 条")
    return all_entries

def build_daily(entries, history):
    entries = dedup_vs_history(entries, history)
    log.info(f"  与历史去重: {len(entries)} 条")
    by_c = {c[0]: [] for c in COUNTRIES_25}
    for e in entries:
        country = e.get("country_hint", "")
        if country and country in by_c:
            cat = classify(e["raw_title"], e.get("raw_summary", ""))
            full_text = ""
            if e.get("source_url") and e["source_url"] != "#":
                full_text = fetch_article_details(e["source_url"])
                time.sleep(0.3)
            search_text = e["raw_summary"] + " " + full_text
            key_figures = extract_figures_from_text(search_text)
            impact = gen_impact(e["raw_title"], e["raw_summary"], full_text, cat)
            advisory = gen_advisory(e["raw_title"], e["raw_summary"], full_text, cat)
            by_c[country].append({
                "title": e["raw_title"][:80],
                "category": "旅游利好要闻",
                "sub_category": cat,
                "summary": e.get("raw_summary", "")[:150],
                "source": e["source_name"],
                "impact": impact,
                "source_url": e.get("source_url", "#"),
                "key_figures": key_figures,
                "travel_advisory": advisory,
                "tag": "新",
                "country": country,
            })
    # 每国选10条，按分类配额分配
    all_items = []
    for c in COUNTRIES_25:
        country_name = c[0]
        ci = by_c.get(country_name, [])
        sel = select_quota(ci, target=10)
        assign_tags(sel, country_name)
        all_items.extend(sel)
    sc_cnt = {}
    for i in all_items:
        sc_cnt[i["sub_category"]] = sc_cnt.get(i["sub_category"], 0) + 1
    log.info(f"  最终分类: {sc_cnt}")
    tag_s = {"爆": 0, "热": 0, "新": 0}
    for i in all_items:
        tag_s[i["tag"]] += 1
    return {"today": TODAY, "window": f"{(datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')} ~ {TODAY}",
            "dates": {TODAY: {"total_items": len(all_items), "tag_summary": tag_s, "items": all_items}}}

def run():
    log.info(f" 全球旅游热点看板 v4 - {TODAY} 采集开始")
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    history = {"today": "", "window": "", "dates": {}}
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                h = json.load(f)
            if isinstance(h, dict) and "dates" in h:
                history = h
        except:
            pass
    log.info(f"  历史: {len(history.get('dates', {}))} 天")
    entries = collect_all()
    if not entries:
        log.error(" 无数据，保留历史数据不更新")
        return
    if len(entries) < 50:
        log.warning(f" 仅采集到{len(entries)}条，数据不足，保留历史数据不更新")
        return
    today_data = build_daily(entries, history)
    n = len(today_data["dates"][TODAY]["items"])
    for dk, dd in today_data["dates"].items():
        history["dates"][dk] = dd
    all_dates = sorted(history["dates"].keys())
    history["today"] = TODAY
    history["window"] = f"{all_dates[-7] if len(all_dates) >= 7 else all_dates[0]} ~ {all_dates[-1]}"
    if len(all_dates) > 30:
        for od in all_dates[:-30]:
            del history["dates"][od]
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    tags = today_data["dates"][TODAY]["tag_summary"]
    log.info(f"\n{'=' * 50}")
    log.info(f" 完成!  {TODAY} |  25国 |  {n}条 |  爆{tags.get('爆', 0)} 热{tags.get('热', 0)} 新{tags.get('新', 0)}")

if __name__ == '__main__':
    run()
