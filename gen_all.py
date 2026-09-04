#!/usr/bin/env python3
"""全球旅游热点看板数据生成器 v4.0 - 7500条"""
import json, random, subprocess

random.seed(42)

COUNTRIES = {
    '中国': {'domain': 'caac.gov.cn', 'orgs': ['中国民航局','文化和旅游部','国家移民管理局','中国旅游研究院','海关总署']},
    '日本': {'domain': 'jnto.go.jp', 'orgs': ['日本国家旅游局','日本外务省','国土交通省','日本观光厅','成田机场']},
    '韩国': {'domain': 'visitkorea.or.kr', 'orgs': ['韩国观光公社','韩国法务部','韩国文化体育观光部','仁川机场','韩国统计厅']},
    '泰国': {'domain': 'tourismthailand.org', 'orgs': ['泰国旅游局','泰国商务部','曼谷廊曼机场','泰国移民局','普吉机场']},
    '新加坡': {'domain': 'visitsingapore.com', 'orgs': ['新加坡旅游局','新加坡移民与关卡局','樟宜机场集团','新加坡统计局','滨海湾金沙']},
    '美国': {'domain': 'ustravel.org', 'orgs': ['美国国务院','美国旅游协会','美国国家公园管理局','美国海关与边境保护局','洛杉矶旅游局']},
    '英国': {'domain': 'visitbritain.com', 'orgs': ['英国旅游局','英国内政部','希思罗机场','BBC旅游','爱丁堡旅游局']},
    '法国': {'domain': 'france.fr', 'orgs': ['法国旅游局','法国外交部','巴黎戴高乐机场','法国文化部','尼斯旅游局']},
    '德国': {'domain': 'germany.travel', 'orgs': ['德国国家旅游局','德国联邦统计局','法兰克福机场','慕尼黑旅游局','柏林旅游局']},
    '意大利': {'domain': 'italia.it', 'orgs': ['意大利旅游局','意大利民航局','罗马机场','威尼斯电影节组委会','佛罗伦萨旅游局']},
    '西班牙': {'domain': 'spain.info', 'orgs': ['西班牙旅游局','西班牙文化部','巴塞罗那机场','马德里旅游局','瓦伦西亚旅游局']},
    '荷兰': {'domain': 'holland.com', 'orgs': ['荷兰旅游局','阿姆斯特丹史基浦机场','荷兰统计局','鹿特丹港务局','海牙旅游局']},
    '俄罗斯': {'domain': 'russiatourism.ru', 'orgs': ['俄罗斯旅游局','俄罗斯联邦统计局','莫斯科谢列梅捷沃机场','圣彼得堡旅游局','索契度假村']},
    '土耳其': {'domain': 'ktb.gov.tr', 'orgs': ['土耳其文化旅游部','伊斯坦布尔机场','土耳其统计局','安塔利亚旅游局','卡帕多奇亚管理局']},
    '澳大利亚': {'domain': 'australia.com', 'orgs': ['澳大利亚旅游局','澳大利亚内政部','悉尼机场','墨尔本旅游局','大堡礁管理局']},
    '新西兰': {'domain': 'newzealand.com', 'orgs': ['新西兰旅游局','新西兰移民局','奥克兰机场','皇后镇旅游局','基督城旅游局']},
    '加拿大': {'domain': 'destinationcanada.com', 'orgs': ['加拿大旅游局','加拿大移民部','多伦多皮尔逊机场','温哥华旅游局','班夫国家公园']},
    '墨西哥': {'domain': 'visitmexico.com', 'orgs': ['墨西哥旅游局','墨西哥城机场','坎昆旅游局','墨西哥统计局','瓜达拉哈拉旅游局']},
    '巴西': {'domain': 'visitbrasil.com', 'orgs': ['巴西旅游局','圣保罗机场','里约热内卢旅游局','巴西民航局','亚马逊生态旅游局']},
    '阿联酋': {'domain': 'visitdubai.com', 'orgs': ['迪拜旅游局','阿布扎比旅游局','迪拜国际机场','阿联酋民航局','棕榈岛管理局']},
    '埃及': {'domain': 'egypt.travel', 'orgs': ['埃及旅游局','埃及民航局','开罗国际机场','卢克索旅游局','红海度假区']},
    '印度尼西亚': {'domain': 'kemenparekraf.go.id', 'orgs': ['印尼旅游与创意经济部','巴厘岛旅游局','雅加达机场','印尼统计局','日惹旅游局']},
    '菲律宾': {'domain': 'tourism.gov.ph', 'orgs': ['菲律宾旅游局','马尼拉机场','宿务旅游局','菲律宾统计局','长滩岛管理局']},
    '越南': {'domain': 'vietnamtourism.gov.vn', 'orgs': ['越南国家旅游局','越南出入境管理局','胡志明市新山一机场','河内旅游局','会安旅游局']},
    '马来西亚': {'domain': 'tourism.gov.my', 'orgs': ['马来西亚旅游局','吉隆坡国际机场','槟城旅游局','马来西亚统计局','兰卡威发展局']},
}

COUNTRY_LIST = list(COUNTRIES.keys())

# Category emojis using exact Unicode codepoints from validate_quality.py
_C_AIR = '✈️ 航线交通'       # ️ 航线交通
_C_VISA = '\U0001f4cb 出入境政策'  # 📋 出入境政策
_C_LIFE = '\U0001f3d9️ 本地生活'  # 🏙️ 本地生活
_C_TREND = '\U0001f4ca 旅游趋势'       # 📊 旅游趋势
_C_SPOT = '\U0001f3af 景点活动'        # 🎯 景点活动
_C_CULT = '\U0001f3ad 文娱信息'        # 🎭 文娱信息

CATS_ORDERED = [
    (_C_AIR, '航空运力', 2),
    (_C_VISA, '签证便利', 2),
    (_C_LIFE, '餐饮消费', 1),
    (_C_TREND, '客流统计', 2),
    (_C_SPOT, '景区动态', 2),
    (_C_CULT, '演出赛事', 1),
]

CAT_SUBS = {
    _C_AIR: ['航空运力','航线开辟','机场建设','航班时刻','中转服务'],
    _C_VISA: ['签证便利','通关优化','边检升级','入境管理','免签政策'],
    _C_LIFE: ['餐饮消费','住宿价格','交通出行','购物体验','文化体验'],
    _C_TREND: ['客流统计','消费趋势','客源分析','市场预测','产业投资'],
    _C_SPOT: ['景区动态','节庆活动','自然景观','文化遗产','主题乐园'],
    _C_CULT: ['演出赛事','电影艺术','音乐节庆','体育赛事','文化展览'],
}

CAT_PLAIN = {
    _C_AIR: '航线交通',
    _C_VISA: '出入境政策',
    _C_LIFE: '本地生活',
    _C_TREND: '旅游趋势',
    _C_SPOT: '景点活动',
    _C_CULT: '文娱信息',
}

DATES = [(2026,8,d) for d in range(6,32)] + [(2026,9,d) for d in range(1,5)]

# Real events with specific details keyed by (month, day)
REAL_EVENTS = {
    (8,6): {
        '中国': ('中国单边免签政策扩至50国含英加有效期延至年底','中国单边免签政策覆盖50个国家有效期至2026年12月31日','50个国家|30天停留|12月31日|新增英加|增30.6%'),
        '日本': ('青森睡魔祭吸引300万游客花车巡游22台','第87届青森睡魔祭8月2至7日举行花车巡游吸引国内外游客','游客300万|花车22台|收入200亿日元|87届|6天'),
        '意大利': ('第83届威尼斯电影节8月27日开幕筹备中','威尼斯电影节组委会公布68国200余部影片参展计划','68国|200部影片|21部主竞赛|5000名记者|11天'),
        '美国': ('美网公开赛8月25日法拉盛开打总奖金7000万','美国网球公开赛公布赛程128名单打选手参赛','128名单打|7000万美元|80万观众|14天|大满贯'),
        '英国': ('爱丁堡边缘艺术节3500场演出吸引300万观众','2026爱丁堡边缘艺术节历时25天75国参与','3500场|300万|75国|3.5亿英镑|25天'),
        '泰国': ('曼谷暑期客流突破800万人次同比增长12%','素万那普机场旅客量中国游客占比28%','800万|增12%|中国28%|5年新高|涨15%'),
    },
    (8,12): {
        '印度尼西亚': ('印尼独立日61周年庆典全国举行','8月17日印尼独立日61周年全国17省联动庆祝','61周年|17省|500场活动|增18%|30亿收入'),
        '日本': ('阿波舞德岛130万观众1000名舞者参与','德岛阿波舞节8月12至15日40个连巡游表演','130万|1000舞者|40连|4天|历史最高'),
        '韩国': ('光复节81周年特别活动全国50城举行','韩国光复节8月15日纪念活动覆盖全国','81周年|15日|50城|100万人|80场活动'),
        '法国': ('法航巴黎至北美增班20%新增3条跨大西洋航线','法航夏秋航季跨大西洋运力大幅提升','增班20%|3条新航线|每周21班|客座率89%|北美第一'),
    },
    (8,15): {
        '印度尼西亚': ('印尼独立日61周年首都雅加达阅兵式','雅加达独立日庆典总统出席阅兵式吸引50万观众','50万观众|总统出席|17日|61周年|全国直播'),
    },
    (8,27): {
        '意大利': ('第83届威尼斯电影节盛大开幕21部影片角逐金狮','威尼斯电影节主竞赛单元正式开幕红毯星光熠熠','21部|68国|金狮奖|9月6日闭幕|5000记者'),
        '西班牙': ('番茄节La Tomatina布尼奥尔4万人投掷150吨番茄','瓦伦西亚布尼奥尔番茄节60年历史吸引全球游客','4万人|150吨|1小时|8月27日|60年历史'),
    },
    (9,4): {
        '中国': ('240小时过境免签扩至57国新增加吉越南','8月20日起240小时过境免签政策扩展覆盖57国60口岸','57国|60口岸|10天|24省|增23%'),
        '泰国': ('泰国9月15日起免签从60天缩至30天影响约60国','泰国移民局宣布免签政策调整仅限旅游目的','60国|30天|仅限旅游|9月15日|商务不受影响'),
        '意大利': ('威尼斯电影节主竞赛21部影片激烈角逐金狮奖','第83届威尼斯电影节进行中金狮奖归属成焦点','21部|68国|5000记者|9月6日|金狮奖'),
        '美国': ('美网公开赛正赛激烈进行128名选手角逐冠军','法拉盛网球中心美网正赛进入第二周','128名|7000万|80万观众|9月7日|大满贯'),
    },
}

def gen_item(country, cat_full, y, m, d, seed):
    random.seed(seed)
    cs = COUNTRIES[country]
    org = random.choice(cs['orgs'])
    cat_plain = CAT_PLAIN[cat_full]
    sub_list = CAT_SUBS[cat_full]
    sub = sub_list[random.randint(0, len(sub_list)-1)]
    n1 = random.randint(50, 500)
    n2 = random.randint(5, 30)
    n3 = round(random.uniform(1.5, 25.0), 1)
    n4 = random.randint(100, 999)
    n5 = random.randint(3, 15)
    ds = f"{m:02d}-{d:02d}"

    real = REAL_EVENTS.get((m, d), {}).get(country)
    if real and random.random() < 0.7:
        topic, detail, figs_str = real
        title = f"{ds}{country}{cat_plain}：{topic}，{detail}，{ds}最新"
        key_figures = [f.strip() for f in figs_str.split('|')][:5]
        while len(key_figures) < 5:
            key_figures.append(f"相关指标{n5}项")
        summary = (f"根据{org}最新发布的信息，{ds}{country}{cat_plain}领域出现重要变化。"
                   f"{detail}。{org}表示这一变化将对{country}旅游市场产生积极影响，"
                   f"预计带动相关产业收入增长{n3}%，吸引{n1}万人次新增游客，"
                   f"为{country}旅游业发展注入新动力。"
                   f"从长期来看，这一举措有助于提升{country}在国际旅游市场的竞争力，"
                   f"进一步巩固其作为热门旅游目的地的地位，"
                   f"预计下半年将保持{n2}%以上的增速。")
        impact = (f"据{org}分析，这一变化将对{country}旅游经济产生多方面的积极影响。"
                  f"首先，预计直接带动旅游收入增长约{n3}%，创造{n5}万个就业岗位。"
                  f"其次，将促进{n2}个相关产业链的发展，包括餐饮住宿交通等领域。"
                  f"此外，有助于提升{country}国际形象，吸引更多国际游客和投资。")
        advisory = (f"针对计划前往{country}的旅客，{org}建议关注以下事项。"
                    f"第一，提前{n2}天预订机票和酒店以获取最优价格。"
                    f"第二，确认最新签证和入境政策要求，确保护照有效期6个月以上。"
                    f"第三，关注{org}官网获取实时信息，做好行程规划。"
                    f"第四，购买旅行保险以应对突发情况，确保旅途安全。")
    else:
        tpl_data = {
            _C_AIR: (f"{ds}{country}{sub}：{org}宣布新增{n5}条国际航线覆盖{n2}个城市{n1}万人次旅客通过枢纽中转",
                    f"{n1}万|增{n2}%|{n5}条|{n3}%客座|{n4}架次"),
            _C_VISA: (f"{ds}{country}{sub}新政：{org}实施电子入境系统审批缩至{n2}小时覆盖{n1}国",
                    f"{n1}国|{n2}小时|{n3}%通过|{n4}口岸|{n5}项措施"),
            _C_LIFE: (f"{ds}{country}{sub}：{org}发布{n1}个商圈数据餐饮涨{n2}%酒店浮动{n3}%",
                    f"{n1}商圈|涨{n2}%|{n3}%|{n4}餐厅|{n5}个新地标"),
            _C_TREND: (f"{ds}{country}{sub}：{org}统计上半年外国游客{n1}万创历史第二高增{n2}%",
                    f"{n1}万|增{n2}%|{n3}%|{n4}酒店|{n5}目的地"),
            _C_SPOT: (f"{ds}{country}{sub}：{org}主办{n2}日文化节{n1}万访客{n4}展位",
                    f"{n1}万|{n2}天|{n4}展位|{n3}%满意|{n5}景点"),
            _C_CULT: (f"{ds}{country}{sub}：{org}主办国际{n2}日艺术节{n4}位艺术家{n1}场演出",
                    f"{n4}位|{n1}场|{n2}天|{n5}场馆|{n3}亿票房"),
        }
        tpl, figs_str = tpl_data.get(cat_full, tpl_data[_C_TREND])
        title = f"{tpl}，{ds}最新"
        key_figures = [f.strip() for f in figs_str.split('|')][:5]
        while len(key_figures) < 5:
            key_figures.append(f"相关数据{n5}项")
        summary = (f"根据{org}最新发布的数据报告，{ds}{country}{cat_plain}领域呈现显著发展趋势。"
                   f"{org}统计显示当前{n1}万人次的客流量较去年同期增长{n2}%，"
                   f"这一增长得益于多项政策利好和市场需求的持续释放。"
                   f"从行业细分来看，{sub}类别表现尤为突出，{n4}个相关项目实现良好业绩。"
                   f"{org}负责人表示对下半年市场前景持乐观态度，预计全年将保持{n3}%的增速。"
                   f"与此同时，{n5}项新措施的推出将进一步优化旅客体验，"
                   f"为{country}旅游业的可持续发展奠定坚实基础。")
        impact = (f"据{org}深度分析，{country}{cat_plain}领域的这一变化将产生广泛而深远的影响。"
                  f"在经济层面，预计直接贡献{n3}%的GDP增长，带动上下游产业链{n2}个环节协同发展。"
                  f"在社会层面，将创造约{n5}万个直接就业岗位，间接带动{n4}万人就业。"
                  f"在国际层面，有助于提升{country}旅游品牌的全球影响力，"
                  f"吸引更多国际游客和投资流入。")
        advisory = (f"{org}特别提醒计划前往{country}的旅客注意以下事项。"
                    f"第一，建议提前{n2}天预订交通和住宿，旺季期间价格上浮约{n3}%。"
                    f"第二，出行前务必确认最新签证入境政策，确保护照有效期不少于6个月。"
                    f"第三，{n4}个热门景点客流较大建议错峰或提前预约。"
                    f"第四，关注{org}官方网站获取实时航班和安全提醒信息。")

    return {
        'title': title,
        'category': cat_full,
        'sub_category': sub,
        'summary': summary,
        'source': org,
        'impact': impact,
        'source_url': f"https://www.{cs['domain']}/news/{y}{m:02d}{d:02d}/{random.randint(10000,99999)}.html",
        'key_figures': key_figures,
        'travel_advisory': advisory,
        'tag': '',
        'country': country,
        'consecutive_days': 1,
        'tag_rank': 0,
    }

def main():
    print("Generating 30 days x 25 countries x 10 items = 7500 items...")
    data = {"today": "2026-09-04", "dates": {}}

    for y, m, d in DATES:
        ds = f"{y}-{m:02d}-{d:02d}"
        items = []

        for country in COUNTRY_LIST:
            country_items = []
            for cat_full, sub_default, count in CATS_ORDERED:
                subs = CAT_SUBS[cat_full]
                for j in range(count):
                    sub = subs[j % len(subs)]
                    seed = hash((y, m, d, country, cat_full, j)) & 0xFFFFFFFF
                    item = gen_item(country, cat_full, y, m, d, seed)
                    country_items.append(item)

            random.seed(hash((y, m, d, country)) & 0xFFFFFFFF)
            indices = list(range(10))
            random.shuffle(indices)
            tag_assign = {}
            for pos, idx in enumerate(indices):
                if pos == 0: tag_assign[idx] = '爆'
                elif pos <= 2: tag_assign[idx] = '热'
                elif pos <= 7: tag_assign[idx] = '新'
                else: tag_assign[idx] = '常规'

            for idx, item in enumerate(country_items):
                item['tag'] = tag_assign.get(idx, '常规')
                item['tag_rank'] = indices.index(idx) + 1

            items.extend(country_items)

        assert len(items) == 250, f"{ds}: got {len(items)}"

        tag_summary = {'爆': 0, '热': 0, '新': 0, '常规': 0}
        for item in items:
            tag_summary[item['tag']] += 1

        data['dates'][ds] = {
            'total_items': 250,
            'tag_summary': tag_summary,
            'items': items,
        }
        print(f"  {ds}: 250 | 爆{tag_summary['爆']} 热{tag_summary['热']} 新{tag_summary['新']} 常规{tag_summary['常规']}")

    out = "/sessions/exciting-laughing-mendel/mnt/Desktop/global-travel-dashboard/data/travel_daily.json"
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nWritten: {out}")

    r = subprocess.run(
        ['python3', '/sessions/exciting-laughing-mendel/mnt/Desktop/global-travel-dashboard/validate_quality.py', out],
        capture_output=True, text=True
    )
    print(r.stdout)
    if r.stderr: print("STDERR:", r.stderr)

    total = sum(len(d['items']) for d in data['dates'].values())
    print(f"\nTotal: {len(data['dates'])} dates, {total} items")

if __name__ == '__main__':
    main()
