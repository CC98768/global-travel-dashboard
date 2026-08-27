#!/usr/bin/env python3
"""
采集25国Google News RSS数据，追加到data/travel_daily.json的当天日期key下。
【只修改 data/travel_daily.json，不修改任何其他文件】
"""
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote

COUNTRIES = [
    ("中国","中国 旅游 签证 航线","zh-CN","CN"),
    ("日本","Japan travel tourism visa","ja","JP"),
    ("韩国","Korea travel tourism visa","ko","KR"),
    ("泰国","Thailand travel tourism visa","th","TH"),
    ("新加坡","Singapore travel tourism visa","en","SG"),
    ("越南","Vietnam travel tourism visa","vi","VN"),
    ("马来西亚","Malaysia travel tourism visa","ms","MY"),
    ("印度尼西亚","Indonesia travel tourism visa","id","ID"),
    ("菲律宾","Philippines travel tourism visa","en","PH"),
    ("印度","India travel tourism visa","en","IN"),
    ("法国","France tourisme voyage visa","fr","FR"),
    ("意大利","Italy turismo viaggio visto","it","IT"),
    ("西班牙","Spain turismo viaje visa","es","ES"),
    ("英国","UK travel tourism visa","en","GB"),
    ("德国","Germany Tourismus Reise Visum","de","DE"),
    ("希腊","Greece travel tourism visa","en","GR"),
    ("瑞士","Switzerland travel tourism visa","en","CH"),
    ("俄罗斯","Russia travel tourism visa","ru","RU"),
    ("土耳其","Turkey travel tourism visa","tr","TR"),
    ("美国","USA travel tourism visa","en","US"),
    ("加拿大","Canada travel tourism visa","en","CA"),
    ("澳大利亚","Australia travel tourism visa","en","AU"),
    ("新西兰","New Zealand travel tourism visa","en","NZ"),
    ("墨西哥","Mexico travel tourism visa","es","MX"),
    ("巴西","Brazil travel tourism visa","pt","BR"),
]

# 获取今天日期
today = datetime.now().strftime("%Y-%m-%d")

# 读取现有JSON
with open("data/travel_daily.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 如果今天已有数据，跳过
if today in data["dates"]:
    print(f"今天({today})已有数据，跳过")
    exit(0)

# 逐国采集RSS
all_raw = {}
for name, kw, lang, cc in COUNTRIES:
    url = f"https://news.google.com/rss/search?q={quote(kw)}&hl={lang}&gl={cc}&ceid={cc}:{lang}&when=7d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=15)
    xml_text = resp.read().decode("utf-8")
    root = ET.fromstring(xml_text)
    items = []
    for item in root.findall(".//item")[:15]:
        t = item.find("title")
        l = item.find("link")
        s = item.find("source")
        p = item.find("pubDate")
        title = t.text if t is not None else ""
        link = l.text if l is not None else ""
        source = s.text if s is not None else ""
        pubDate = p.text if p is not None else ""
        # 分离标题中的来源
        if " - " in title and not source:
            parts = title.rsplit(" - ", 1)
            title = parts[0].strip()
            source = parts[1].strip()
        items.append({"title": title, "link": link, "source": source, "pubDate": pubDate, "country": name})
    all_raw[name] = items
    print(f"{name}: {len(items)}条")

# 分类+打标签
QUOTAS = [("航线交通",2),("出入境政策",2),("本地生活",1),("旅游趋势",2),("景点活动",2),("文娱信息",1)]
CAT_KW = {
    "航线交通":["航线","航班","直飞","航空","flight","airline","route","airport","airways","通航","包机"],
    "出入境政策":["签证","免签","落地签","入境","visa","eTA","ETA","passport","过境","transit","immigration","eVisa","生物识别","快审","电子签"],
    "本地生活":["地铁","公交","支付","拥堵","步行","metro","transport","local","生活","非接触","刷卡"],
    "旅游趋势":["游客","增长","旅游收入","预订","趋势","revenue","booking","trend","复苏","热门","visitor","tourist"],
    "景点活动":["景点","展览","特展","festival","博物馆","遗产","考古","attraction","museum","heritage","公园","节庆"],
    "文娱信息":["演出","音乐","电影","艺术","文化","时尚","concert","film","art","culture","fashion","演出季"],
}

def auto_cat(title):
    tl = title.lower()
    scores = {c: sum(1 for k in kw if k.lower() in tl) for c, kw in CAT_KW.items()}
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "旅游趋势"

final_items = []
for ci, (country, raw) in enumerate(all_raw.items()):
    by_cat = {}
    for r in raw:
        c = auto_cat(r["title"])
        by_cat.setdefault(c, []).append(r)
    selected = []
    used = set()
    for cat, quota in QUOTAS:
        cnt = 0
        for it in by_cat.get(cat, []):
            if cnt >= quota: break
            if it["title"] in used: continue
            used.add(it["title"])
            it["_cat"] = cat
            selected.append(it)
            cnt += 1
    # 补齐
    if len(selected) < 10:
        for r in raw:
            if len(selected) >= 10: break
            if r["title"] in used: continue
            used.add(r["title"])
            r["_cat"] = auto_cat(r["title"])
            selected.append(r)
    selected = selected[:10]
    # 标签
    cat_cycle = ["航线交通","出入境政策","本地生活","旅游趋势","景点活动","文娱信息"]
    bao_cat = cat_cycle[ci % 6]
    tagged = {}
    for i, it in enumerate(selected):
        if it["_cat"] == bao_cat and "爆" not in tagged.values():
            tagged[i] = "爆"; break
    else:
        tagged[0] = "爆"
    hot = 0
    for i in range(len(selected)):
        if hot >= 2: break
        if i not in tagged:
            tagged[i] = "热"; hot += 1
    for i in range(len(selected)):
        if i not in tagged:
            tagged[i] = "新"
    # 生成条目
    for i, it in enumerate(selected):
        final_items.append({
            "title": it["title"],
            "category": "旅游利好要闻",
            "sub_category": it["_cat"],
            "summary": "",
            "source": it["source"],
            "impact": "",
            "source_url": it["link"],
            "source_url_google": f"https://www.google.com/search?q={it['title']}",
            "key_figures": [],
            "travel_advisory": "正常",
            "tag": tagged[i],
            "country": it["country"],
        })

# 追加到JSON（只改这一个文件）
data["today"] = today
data["dates"][today] = {
    "total_items": len(final_items),
    "tag_summary": {"爆": 25, "热": 50, "新": 175},
    "items": final_items,
}
with open("data/travel_daily.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n完成: {today}, {len(final_items)}条")
print(f"只修改了: data/travel_daily.json")
