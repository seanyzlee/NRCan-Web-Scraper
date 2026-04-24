"""
Configuration for the NRCan Article Scraper.
Edit KEYWORDS and SOURCES to customize what gets collected.
"""

# ---------------------------------------------------------------------------
# SEARCH KEYWORDS
# Articles must contain at least one of these terms (case-insensitive).
# Group them by theme for readability; all are flattened into one list.
# ---------------------------------------------------------------------------
KEYWORD_GROUPS = {
    "Energy Projects": [
        "oil sands", "oilsands", "pipeline", "LNG", "liquefied natural gas",
        "offshore drilling", "upstream", "downstream", "midstream",
        "energy project", "fossil fuel", "petroleum",
    ],
    "Critical Minerals & Mining": [
        "critical mineral", "lithium", "cobalt", "nickel", "copper",
        "rare earth", "mining project", "mine development", "potash",
        "uranium", "gold mine", "silver mine",
    ],
    "Clean Energy & Transition": [
        "clean energy", "energy transition", "net zero", "decarbonization",
        "carbon capture", "CCUS", "CCS", "hydrogen", "small modular reactor",
        "SMR", "nuclear energy", "offshore wind", "onshore wind",
        "solar farm", "battery storage", "green hydrogen",
    ],
    "Policy & Regulation": [
        "carbon tax", "emissions cap", "impact assessment", "Bill C-69",
        "energy regulation", "NRCan", "Natural Resources Canada",
        "Canada Energy Regulator", "CER", "Alberta Energy", "Crown corporation",
    ],
    "Economic Reports": [
        "commodity prices", "energy prices", "oil price", "gas price",
        "resource economy", "investment in Canada", "capital expenditure",
        "upstream investment", "energy sector",
    ],
}

# Flatten all keywords into a single list
KEYWORDS = [kw for group in KEYWORD_GROUPS.values() for kw in group]

# ---------------------------------------------------------------------------
# SCRAPE WINDOW
# How many days back to look for articles. 7 = weekly, 14 = biweekly.
# ---------------------------------------------------------------------------
LOOKBACK_DAYS = 14

# ---------------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------------
OUTPUT_DIR = "output"
DB_FILE = "seen_articles.db"   # SQLite database for deduplication

# ---------------------------------------------------------------------------
# SOURCES
# Each entry: {name, type ("rss" | "scrape"), url, [parser]}
# ---------------------------------------------------------------------------
SOURCES = [

    # -----------------------------------------------------------------------
    # NEWSPAPERS
    # -----------------------------------------------------------------------
    {
        "name": "Globe and Mail",
        "type": "rss",
        "category": "Newspaper",
        "urls": [
            "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/",
            "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/politics/",
        ],
    },
    {
        "name": "National Post",
        "type": "rss",
        "category": "Newspaper",
        "urls": [
            "https://nationalpost.com/feed",
            "https://financialpost.com/feed",
        ],
    },
    {
        "name": "Wall Street Journal",
        "type": "rss",
        "category": "Newspaper",
        "urls": [
            "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
            "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
        ],
    },
    {
        "name": "New York Times",
        "type": "rss",
        "category": "Newspaper",
        "urls": [
            "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/Climate.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/Energy-Environment.xml",
        ],
    },
    {
        "name": "USA Today",
        "type": "rss",
        "category": "Newspaper",
        "urls": [
            "https://rssfeeds.usatoday.com/UsatodaycomMoney-TopStories",
        ],
    },
    {
        "name": "Financial Times",
        "type": "rss",
        "category": "Newspaper",
        "urls": [
            "https://www.ft.com/rss/home/uk",
            "https://www.ft.com/myft/following/topics/a6a38e1a-f4c6-4706-a499-c34c4bcb61c1.rss",  # Energy
        ],
    },
    {
        "name": "The Economist",
        "type": "rss",
        "category": "Newspaper",
        "urls": [
            "https://www.economist.com/finance-and-economics/rss.xml",
            "https://www.economist.com/business/rss.xml",
            "https://www.economist.com/science-and-technology/rss.xml",
        ],
    },

    # -----------------------------------------------------------------------
    # NEWS NETWORKS
    # -----------------------------------------------------------------------
    {
        "name": "CBC",
        "type": "rss",
        "category": "News Network",
        "urls": [
            "https://www.cbc.ca/cmlink/rss-canada",
            "https://www.cbc.ca/cmlink/rss-business",
            "https://www.cbc.ca/cmlink/rss-politics",
        ],
    },
    {
        "name": "CTV News",
        "type": "rss",
        "category": "News Network",
        "urls": [
            "https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.822009",
            "https://www.ctvnews.ca/rss/ctvnews-ca-canada-public-rss-1.822009",
        ],
    },
    {
        "name": "Global News",
        "type": "rss",
        "category": "News Network",
        "urls": [
            "https://globalnews.ca/feed/",
            "https://globalnews.ca/canada/feed/",
            "https://globalnews.ca/money/feed/",
        ],
    },
    {
        "name": "CNN",
        "type": "rss",
        "category": "News Network",
        "urls": [
            "http://rss.cnn.com/rss/money_news_international.rss",
            "http://rss.cnn.com/rss/cnn_us.rss",
        ],
    },
    {
        "name": "MSNBC / NBC News",
        "type": "rss",
        "category": "News Network",
        "urls": [
            "http://feeds.nbcnews.com/nbcnews/public/business",
        ],
    },

    # -----------------------------------------------------------------------
    # CANADIAN BANKS
    # -----------------------------------------------------------------------
    {
        "name": "RBC Economics",
        "type": "scrape",
        "category": "Bank",
        "urls": ["https://thoughtleadership.rbc.com/economics/"],
        "parser": "rbc",
    },
    {
        "name": "TD Economics",
        "type": "scrape",
        "category": "Bank",
        "urls": ["https://economics.td.com/"],
        "parser": "td",
    },
    {
        "name": "Scotiabank Economics",
        "type": "scrape",
        "category": "Bank",
        "urls": ["https://www.scotiabank.com/ca/en/about/economics/economics-publications.html"],
        "parser": "scotiabank",
    },
    {
        "name": "BMO Economics",
        "type": "scrape",
        "category": "Bank",
        "urls": ["https://economics.bmo.com/en/"],
        "parser": "bmo",
    },
    {
        "name": "CIBC Economics",
        "type": "scrape",
        "category": "Bank",
        "urls": ["https://economics.cibc.com/en/home.html"],
        "parser": "cibc",
    },
    {
        "name": "National Bank Economics",
        "type": "scrape",
        "category": "Bank",
        "urls": ["https://www.nbc.ca/en/corporate/economics.html"],
        "parser": "nbc",
    },

    # -----------------------------------------------------------------------
    # INTERNATIONAL ORGANIZATIONS
    # -----------------------------------------------------------------------
    {
        "name": "IMF",
        "type": "rss",
        "category": "International Org",
        "urls": [
            "https://www.imf.org/en/Publications/RSS?language=eng&series=World%20Economic%20Outlook%20%28WEO%29",
            "https://www.imf.org/en/Publications/RSS?language=eng&series=IMF%20Working%20Papers",
        ],
    },
    {
        "name": "OECD",
        "type": "rss",
        "category": "International Org",
        "urls": [
            "https://www.oecd.org/newsroom/feeds/news.xml",
            "https://www.oecd-ilibrary.org/rss/content/oecd-ilibrary/economics?lang=en",
        ],
    },
    {
        "name": "World Bank",
        "type": "rss",
        "category": "International Org",
        "urls": [
            "https://feeds.worldbank.org/worldbank/blogs/all",
            "https://feeds.worldbank.org/worldbank/news",
        ],
    },
    {
        "name": "IEA",
        "type": "scrape",
        "category": "International Org",
        "urls": ["https://www.iea.org/news"],
        "parser": "iea",
    },

    # -----------------------------------------------------------------------
    # CENTRAL BANKS
    # -----------------------------------------------------------------------
    {
        "name": "Bank of Canada",
        "type": "rss",
        "category": "Central Bank",
        "urls": [
            "https://www.bankofcanada.ca/feed/",
            "https://www.bankofcanada.ca/publications/mpr/feed/",
        ],
    },
    {
        "name": "Federal Reserve",
        "type": "rss",
        "category": "Central Bank",
        "urls": [
            "https://www.federalreserve.gov/feeds/press_all.xml",
            "https://www.federalreserve.gov/feeds/speeches.xml",
        ],
    },

    # -----------------------------------------------------------------------
    # RESEARCH & CONSULTING
    # -----------------------------------------------------------------------
    {
        "name": "S&P Global",
        "type": "scrape",
        "category": "Research",
        "urls": ["https://www.spglobal.com/commodityinsights/en/ci/research-analysis.html"],
        "parser": "spglobal",
    },
    {
        "name": "Wood Mackenzie",
        "type": "scrape",
        "category": "Research",
        "urls": ["https://www.woodmac.com/latest-thinking/"],
        "parser": "woodmac",
    },
    {
        "name": "McKinsey",
        "type": "scrape",
        "category": "Research",
        "urls": ["https://www.mckinsey.com/industries/electric-power-and-natural-gas/our-insights"],
        "parser": "mckinsey",
    },
    {
        "name": "C.D. Howe Institute",
        "type": "rss",
        "category": "Research",
        "urls": ["https://www.cdhowe.org/rss.xml"],
    },
    {
        "name": "Deloitte Canada",
        "type": "scrape",
        "category": "Research",
        "urls": ["https://www2.deloitte.com/ca/en/pages/energy-and-resources/articles/energy-resources-insights.html"],
        "parser": "deloitte",
    },
    {
        "name": "Goldman Sachs",
        "type": "scrape",
        "category": "Research",
        "urls": ["https://www.goldmansachs.com/insights/"],
        "parser": "goldman",
    },
    {
        "name": "Signal49",
        "type": "scrape",
        "category": "Research",
        "urls": ["https://www.signal49.com/news"],
        "parser": "signal49",
    },
]
