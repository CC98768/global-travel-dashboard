#!/usr/bin/env python3
"""
Curated source list for 25 countries.

Each country maps to:
  - tourism_board: Official tourism authority (RSS / news URL)
  - immigration: Visa / immigration authority URL
  - news_sites: Major local / international travel news outlets
  - keywords: Country-specific search terms for API queries

This serves as both fallback content AND source attribution.
"""

COUNTRIES = {
    "Thailand": {
        "tourism_board": {
            "name": "Tourism Authority of Thailand (TAT)",
            "url": "https://www.tatnews.org/en/category/press-releases/",
            "rss": "https://www.tatnews.org/en/feed/"
        },
        "immigration": {
            "name": "Thai Immigration Bureau",
            "url": "https://www.immigration.go.th/"
        },
        "news_sites": [
            {"name": "Bangkok Post", "url": "https://www.bangkokpost.com/topic/travel"},
            {"name": "The Thaiger", "url": "https://thethaiger.com/news/tourism"},
            {"name": "Thai PBS World", "url": "https://www.thaipbsworld.com/category/travel/"}
        ],
        "keywords": ["Thailand travel", "Thailand visa", "Thailand tourism", "Bangkok travel", "Phuket tourism", "Thailand immigration"]
    },
    "Japan": {
        "tourism_board": {
            "name": "Japan National Tourism Organization (JNTO)",
            "url": "https://www.japan.travel/en/",
            "rss": "https://www.japan.travel/en/rss/"
        },
        "immigration": {
            "name": "Japan Immigration Services Agency",
            "url": "https://www.isa.go.jp/en/"
        },
        "news_sites": [
            {"name": "Japan Times Travel", "url": "https://www.japantimes.co.jp/tag/travel/"},
            {"name": "NHK World", "url": "https://www3.nhkworldjapan.com/en/tag/travel/"},
            {"name": "Asahi Shimbun", "url": "https://www.asahi.com/ajw/travel/"}
        ],
        "keywords": ["Japan travel", "Japan visa", "Japan tourism", "Tokyo tourism", "Visit Japan"]
    },
    "South Korea": {
        "tourism_board": {
            "name": "Korea Tourism Organization (KTO)",
            "url": "https://english.visitkorea.or.kr/",
            "rss": "https://english.visitkorea.or.kr/xml/rss/"
        },
        "immigration": {
            "name": "Korea Immigration Service",
            "url": "https://www.immigration.go.kr/"
        },
        "news_sites": [
            {"name": "Korea Herald Travel", "url": "https://www.koreaherald.com/travel"},
            {"name": "Korea JoongAng Daily", "url": "https://koreajoongangdaily.joins.com/news/travel/"}
        ],
        "keywords": ["South Korea travel", "Korea visa", "Korea tourism", "Seoul tourism", "K-ETA"]
    },
    "Singapore": {
        "tourism_board": {
            "name": "Singapore Tourism Board (STB)",
            "url": "https://www.stb.gov.sg/",
            "rss": "https://www.stb.gov.sg/content/dam/stb/rss/stb-news.xml"
        },
        "immigration": {
            "name": "Immigration & Checkpoints Authority (ICA)",
            "url": "https://www.ica.gov.sg/"
        },
        "news_sites": [
            {"name": "Straits Times Travel", "url": "https://www.straitstimes.com/travel"},
            {"name": "CNA Travel", "url": "https://www.channelnewsasia.com/travel"}
        ],
        "keywords": ["Singapore travel", "Singapore visa", "Singapore tourism", "Singapore immigration"]
    },
    "Vietnam": {
        "tourism_board": {
            "name": "Vietnam National Administration of Tourism (VNAT)",
            "url": "https://www.vietnamtourism.gov.vn/",
            "rss": "https://www.vietnamtourism.gov.vn/rss"
        },
        "immigration": {
            "name": "Vietnam Immigration Department",
            "url": "https://www.xuatnhapcanh.gov.vn/"
        },
        "news_sites": [
            {"name": "Vietnam News Travel", "url": "https://vietnamnews.vn/travel"},
            {"name": "VnExpress Travel", "url": "https://e.vnexpress.net/travel"}
        ],
        "keywords": ["Vietnam travel", "Vietnam visa", "Vietnam tourism", "Vietnam e-visa"]
    },
    "Indonesia": {
        "tourism_board": {
            "name": "Ministry of Tourism Indonesia",
            "url": "https://www.indonesia.travel/",
            "rss": "https://www.indonesia.travel/en/rss"
        },
        "immigration": {
            "name": "Directorate General of Immigration Indonesia",
            "url": "https://www.imigrasi.go.id/"
        },
        "news_sites": [
            {"name": "Jakarta Post Travel", "url": "https://www.thejakartapost.com/travel"},
            {"name": "Bali Discovery", "url": "https://balidiscovery.com/"}
        ],
        "keywords": ["Indonesia travel", "Bali tourism", "Indonesia visa", "Bali travel", "Indonesia immigration"]
    },
    "Malaysia": {
        "tourism_board": {
            "name": "Tourism Malaysia",
            "url": "https://www.tourism.gov.my/",
            "rss": "https://www.tourism.gov.my/en/news/rss"
        },
        "immigration": {
            "name": "Malaysian Immigration Department",
            "url": "https://www.imi.gov.my/"
        },
        "news_sites": [
            {"name": "New Straits Times Travel", "url": "https://www.nst.com.my/lifestyle/travel"},
            {"name": "Malay Mail Travel", "url": "https://www.malaymail.com/travel"}
        ],
        "keywords": ["Malaysia travel", "Malaysia visa", "Malaysia tourism", "Kuala Lumpur tourism", "Malaysia immigration"]
    },
    "Philippines": {
        "tourism_board": {
            "name": "Department of Tourism Philippines",
            "url": "https://dot.gov.ph/",
            "rss": "https://dot.gov.ph/rss"
        },
        "immigration": {
            "name": "Bureau of Immigration Philippines",
            "url": "https://immigration.gov.ph/"
        },
        "news_sites": [
            {"name": "Philippine Daily Inquirer Travel", "url": "https://travel.inquirer.net/"},
            {"name": "Rappler Travel", "url": "https://www.rappler.com/life-and-style/travel/"}
        ],
        "keywords": ["Philippines travel", "Philippines visa", "Philippines tourism", "Boracay", "Palawan tourism"]
    },
    "China": {
        "tourism_board": {
            "name": "China National Tourism Administration",
            "url": "https://www.visitbeijing.com.cn/",
            "rss": None
        },
        "immigration": {
            "name": "National Immigration Administration of China",
            "url": "https://www.nia.gov.cn/"
        },
        "news_sites": [
            {"name": "CGTN Travel", "url": "https://www.cgtn.com/travel"},
            {"name": "China Daily Travel", "url": "https://www.chinadaily.com.cn/life/travel"}
        ],
        "keywords": ["China travel", "China visa", "China tourism", "China inbound tourism", "China transit visa"]
    },
    "India": {
        "tourism_board": {
            "name": "Incredible India",
            "url": "https://www.incredibleindia.org/",
            "rss": None
        },
        "immigration": {
            "name": "Bureau of Immigration India",
            "url": "https://boi.gov.in/"
        },
        "news_sites": [
            {"name": "Times of India Travel", "url": "https://timesofindia.indiatimes.com/travel"},
            {"name": "Hindustan Times Travel", "url": "https://www.hindustantimes.com/travel"},
            {"name": "The Hindu Travel", "url": "https://www.thehindu.com/travel/"}
        ],
        "keywords": ["India travel", "India visa", "India tourism", "India e-visa", "India inbound tourism"]
    },
    "United States": {
        "tourism_board": {
            "name": "Brand USA",
            "url": "https://www.thebrandusa.com/",
            "rss": None
        },
        "immigration": {
            "name": "US Customs and Border Protection",
            "url": "https://www.cbp.gov/"
        },
        "news_sites": [
            {"name": "Travel + Leisure", "url": "https://www.travelandleisure.com/"},
            {"name": "Condé Nast Traveler", "url": "https://www.cntraveler.com/"},
            {"name": "Skift", "url": "https://skift.com/"}
        ],
        "keywords": ["US travel", "US visa", "US tourism", "ESTA", "US immigration policy"]
    },
    "United Kingdom": {
        "tourism_board": {
            "name": "VisitBritain",
            "url": "https://www.visitbritain.com/",
            "rss": "https://www.visitbritain.com/rss/news"
        },
        "immigration": {
            "name": "UK Visas and Immigration",
            "url": "https://www.gov.uk/government/organisations/uk-visas-and-immigration"
        },
        "news_sites": [
            {"name": "BBC Travel", "url": "https://www.bbc.com/travel"},
            {"name": "The Guardian Travel", "url": "https://www.theguardian.com/travel"},
            {"name": "Travel Weekly UK", "url": "https://www.travelweekly.co.uk/"}
        ],
        "keywords": ["UK travel", "UK visa", "UK tourism", "London tourism", "UK ETA"]
    },
    "France": {
        "tourism_board": {
            "name": "Atout France",
            "url": "https://www.france.fr/",
            "rss": "https://www.france.fr/en/rss"
        },
        "immigration": {
            "name": "France-Visas",
            "url": "https://france-visas.gouv.fr/"
        },
        "news_sites": [
            {"name": "France 24 Travel", "url": "https://www.france24.com/en/travel/"},
            {"name": "The Local France", "url": "https://www.thelocal.fr/tag/travel/"}
        ],
        "keywords": ["France travel", "France visa", "France tourism", "Paris tourism", "Schengen France"]
    },
    "Germany": {
        "tourism_board": {
            "name": "German National Tourist Board (GNTB)",
            "url": "https://www.germany.travel/",
            "rss": "https://www.germany.travel/en/rss/"
        },
        "immigration": {
            "name": "German Federal Foreign Office",
            "url": "https://www.auswaertiges-amt.de/en/visa-service"
        },
        "news_sites": [
            {"name": "Deutsche Welle Travel", "url": "https://www.dw.com/en/travel/"},
            {"name": "The Local Germany", "url": "https://www.thelocal.de/tag/travel/"}
        ],
        "keywords": ["Germany travel", "Germany visa", "Germany tourism", "Berlin tourism", "Schengen Germany"]
    },
    "Spain": {
        "tourism_board": {
            "name": "Turespaña",
            "url": "https://www.spain.info/",
            "rss": "https://www.spain.info/en/rss/"
        },
        "immigration": {
            "name": "Spanish Ministry of Interior",
            "url": "https://www.interior.gob.es/opencms/es/serviciosdelministerio/tramites-y-gestiones/extranjeria/"
        },
        "news_sites": [
            {"name": "Spain Travel News", "url": "https://www.spaintravelsnews.com/"},
            {"name": "The Local Spain", "url": "https://www.thelocal.es/tag/travel/"}
        ],
        "keywords": ["Spain travel", "Spain visa", "Spain tourism", "Barcelona tourism", "Schengen Spain"]
    },
    "Italy": {
        "tourism_board": {
            "name": "ENIT (Italian National Tourist Board)",
            "url": "https://www.italy.it/",
            "rss": "https://www.italy.it/en/rss"
        },
        "immigration": {
            "name": "Italian Ministry of Interior",
            "url": "https://www.interno.gov.it/"
        },
        "news_sites": [
            {"name": "The Local Italy", "url": "https://www.thelocal.it/tag/travel/"},
            {"name": "Italy Magazine", "url": "https://www.italymagazine.com/"}
        ],
        "keywords": ["Italy travel", "Italy visa", "Italy tourism", "Rome tourism", "Schengen Italy"]
    },
    "Australia": {
        "tourism_board": {
            "name": "Tourism Australia",
            "url": "https://www.australia.com/",
            "rss": "https://www.australia.com/en/rss"
        },
        "immigration": {
            "name": "Australian Department of Home Affairs",
            "url": "https://immi.homeaffairs.gov.au/"
        },
        "news_sites": [
            {"name": "Sydney Morning Herald Travel", "url": "https://www.smh.com.au/travel"},
            {"name": "Travel Weekly Australia", "url": "https://www.travelweekly.com.au/"}
        ],
        "keywords": ["Australia travel", "Australia visa", "Australia tourism", "Sydney tourism", "Australia ETA"]
    },
    "New Zealand": {
        "tourism_board": {
            "name": "Tourism New Zealand",
            "url": "https://www.newzealand.com/",
            "rss": "https://www.newzealand.com/en/rss/"
        },
        "immigration": {
            "name": "Immigration New Zealand",
            "url": "https://www.immigration.govt.nz/"
        },
        "news_sites": [
            {"name": "NZ Herald Travel", "url": "https://www.nzherald.co.nz/travel/"},
            {"name": "Stuff Travel", "url": "https://www.stuff.co.nz/travel"}
        ],
        "keywords": ["New Zealand travel", "New Zealand visa", "NZ tourism", "NZeTA"]
    },
    "Canada": {
        "tourism_board": {
            "name": "Destination Canada",
            "url": "https://en.destinationcanada.com/",
            "rss": None
        },
        "immigration": {
            "name": "Immigration, Refugees and Citizenship Canada (IRCC)",
            "url": "https://www.canada.ca/en/immigration-refugees-citizenship.html"
        },
        "news_sites": [
            {"name": "Travel Weekly Canada", "url": "https://www.travelweekly.com/Travel-News/Canada-Travel-News"},
            {"name": "CBC Travel", "url": "https://www.cbc.ca/travel"}
        ],
        "keywords": ["Canada travel", "Canada visa", "Canada tourism", "Canada eTA", "Canada immigration"]
    },
    "Mexico": {
        "tourism_board": {
            "name": "Visit Mexico",
            "url": "https://www.visitmexico.com/",
            "rss": None
        },
        "immigration": {
            "name": "Instituto Nacional de Migración",
            "url": "https://www.gob.mx/inm"
        },
        "news_sites": [
            {"name": "Mexico News Daily", "url": "https://mexiconewsdaily.com/category/travel/"},
            {"name": "Mexico Travel News", "url": "https://mexicotravelnews.com/"}
        ],
        "keywords": ["Mexico travel", "Mexico visa", "Mexico tourism", "Cancun tourism", "Mexico immigration"]
    },
    "UAE": {
        "tourism_board": {
            "name": "Dubai Department of Economy and Tourism",
            "url": "https://www.visitdubai.com/",
            "rss": "https://www.visitdubai.com/en/rss"
        },
        "immigration": {
            "name": "UAE Federal Authority for Identity and Citizenship",
            "url": "https://www.ica.gov.ae/"
        },
        "news_sites": [
            {"name": "Gulf News Travel", "url": "https://gulfnews.com/travel"},
            {"name": "Khaleej Times Travel", "url": "https://www.khaleejtimes.com/travel"}
        ],
        "keywords": ["UAE travel", "Dubai tourism", "UAE visa", "Dubai travel", "UAE immigration"]
    },
    "Turkey": {
        "tourism_board": {
            "name": "GoTurkiye",
            "url": "https://www.goturkiye.com/",
            "rss": "https://www.goturkiye.com/en/rss"
        },
        "immigration": {
            "name": "Presidency of Migration Management",
            "url": "https://www.goc.gov.tr/"
        },
        "news_sites": [
            {"name": "Daily Sabah Travel", "url": "https://www.dailysabah.com/turkey/travel"},
            {"name": "Hurriyet Daily News Travel", "url": "https://www.hurriyetdailynews.com/travel"}
        ],
        "keywords": ["Turkey travel", "Turkey visa", "Turkey tourism", "Istanbul tourism", "e-Visa Turkey"]
    },
    "Egypt": {
        "tourism_board": {
            "name": "Egyptian Tourism Authority",
            "url": "https://www.egypt.travel/",
            "rss": None
        },
        "immigration": {
            "name": "Egyptian Ministry of Interior",
            "url": "https://www.visa2egypt.gov.sg/"
        },
        "news_sites": [
            {"name": "Al-Ahram Travel", "url": "https://english.ahram.org.in/Category/10/Travel.htm"},
            {"name": "Egypt Independent Travel", "url": "https://egyptindependent.com/category/travel/"}
        ],
        "keywords": ["Egypt travel", "Egypt visa", "Egypt tourism", "Cairo tourism", "Egypt e-visa"]
    },
    "Brazil": {
        "tourism_board": {
            "name": "Visit Brasil",
            "url": "https://www.brazil.travel/",
            "rss": None
        },
        "immigration": {
            "name": "Polícia Federal (Immigration)",
            "url": "https://www.gov.br/pf/pt-br"
        },
        "news_sites": [
            {"name": "Folha Travel", "url": "https://www1.folha.uol.com.br/turismo/"},
            {"name": "Rio Times", "url": "https://riotimesonline.com/category/travel/"}
        ],
        "keywords": ["Brazil travel", "Brazil visa", "Brazil tourism", "Rio tourism", "Brazil e-visa"]
    },
    "South Africa": {
        "tourism_board": {
            "name": "South African Tourism (SANParks)",
            "url": "https://www.southafrica.net/",
            "rss": "https://www.southafrica.net/en/rss"
        },
        "immigration": {
            "name": "Department of Home Affairs South Africa",
            "url": "https://www.dha.gov.za/"
        },
        "news_sites": [
            {"name": "News24 Travel", "url": "https://www.news24.com/travel24"},
            {"name": "IOL Travel", "url": "https://www.iol.co.za/travel"}
        ],
        "keywords": ["South Africa travel", "South Africa visa", "South Africa tourism", "Cape Town tourism"]
    }
}

# Categories for news classification
CATEGORIES = {
    "visa": {
        "label": "签证政策",
        "keywords": ["visa", "e-visa", "eTA", "visa-free", "visa waiver", "visa exemption", "签证", "immigration policy", "entry requirements"],
        "quota": 2  # items per country
    },
    "aviation": {
        "label": "航空交通",
        "keywords": ["airline", "flight", "airport", "aviation", "direct flight", "new route", "航班", "airline expansion", "low-cost carrier"],
        "quota": 2
    },
    "tourism": {
        "label": "旅游推广",
        "keywords": ["tourism", "tourist", "visit", "campaign", "promotion", "marketing", "推广", "tourism board", "destination marketing"],
        "quota": 2
    },
    "digital": {
        "label": "数字/便利化",
        "keywords": ["digital nomad", "e-gate", "biometric", "mobile passport", "fast track", "digital", "自动化", "contactless", "smart border"],
        "quota": 1
    },
    "event": {
        "label": "大型活动",
        "keywords": ["festival", "event", "expo", "world cup", "olympic", "exhibition", "活动", "carnival", "conference", "summit"],
        "quota": 1
    },
    "policy": {
        "label": "法规政策",
        "keywords": ["policy", "regulation", "law", "reform", "agreement", "bilateral", "法规", "protocol", "treaty", "compliance"],
        "quota": 2
    }
}

# Search terms (used for API queries)
SEARCH_TERMS = [
    "travel news {country}",
    "tourism policy {country}",
    "visa update {country}",
    "airline routes {country}",
    "immigration {country} 2026"
]

# RSS feed URLs for fallback (official tourism boards + major outlets)
RSS_FEEDS = []
for country_data in COUNTRIES.values():
    rss_url = country_data["tourism_board"].get("rss")
    if rss_url:
        RSS_FEEDS.append({
            "country": None,  # Will be set per feed
            "url": rss_url,
            "source": country_data["tourism_board"]["name"]
        })

# Add international travel news RSS feeds
INTERNATIONAL_RSS_FEEDS = [
    {"name": "UNWTO News", "url": "https://www.unwto.org/rss"},
    {"name": "WTTC News", "url": "https://wttc.org/rss"},
    {"name": "Skift Travel", "url": "https://skift.com/feed/"},
    {"name": "Travel Weekly", "url": "https://www.travelweekly.com/RSS-Feeds"},
    {"name": "Phocuswire", "url": "https://www.phocuswire.com/RSS-Feeds"},
    {"name": "Lonely Planet News", "url": "https://www.lonelyplanet.com/thorntree/rss"},
]


def get_country_keywords(country_name: str) -> list:
    """Get search keywords for a specific country."""
    if country_name in COUNTRIES:
        return COUNTRIES[country_name]["keywords"]
    return [f"{country_name} travel", f"{country_name} tourism"]


def get_all_country_names() -> list:
    """Return sorted list of all country names."""
    return sorted(COUNTRIES.keys())


def get_rss_urls_for_country(country_name: str) -> list:
    """Get all RSS feed URLs relevant to a country."""
    urls = []
    if country_name in COUNTRIES:
        data = COUNTRIES[country_name]
        rss = data["tourism_board"].get("rss")
        if rss:
            urls.append(rss)
    return urls
