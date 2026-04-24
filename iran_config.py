"""
iran_config.py — Sources, keywords, and topic classification for the Iran Monitor tab.
"""

# ---------------------------------------------------------------------------
# Main keyword filter  (applied to broad RSS feeds; skipped for pre_filtered)
# ---------------------------------------------------------------------------
KEYWORDS = [
    # Identity
    "Iran", "Iranian", "IRGC", "Tehran", "Khamenei", "Hormuz",
    # Conflict
    "Iran attack", "Iran missile", "Iran drone", "Iran war",
    "Iran nuclear", "Iran enrichment", "Iran sanction",
    "Red Sea", "tanker attack", "Gulf tanker", "Houthi", "Hezbollah",
    # Energy
    "Iran oil", "Iran crude", "Iran gas", "Iran LNG",
    "Iran energy", "Iran refinery", "Iran oil export",
    "Persian Gulf oil", "oil sanction",
    # Resources
    "Iran mineral", "Iran mining", "Iran copper", "Iran aluminum",
    "Iran aluminium", "Iran fertilizer", "Iran gold", "Iran uranium",
    "Iran resource",
]

# ---------------------------------------------------------------------------
# Topic classification  (applied post-fetch; articles may match >1 topic)
# ---------------------------------------------------------------------------
TOPIC_KEYWORDS = {
    "Fuels & Energy": [
        "oil", "crude", "petroleum", "natural gas", "lng",
        "liquefied natural gas", "fuel", "refinery", "gasoline",
        "diesel", "pipeline", "energy", "barrel", "opec",
        "tanker", "hormuz", "oil price", "gas price",
        "oil export", "oil supply", "oil sanction",
    ],
    "Minerals & Commodities": [
        "aluminum", "aluminium", "fertilizer", "fertiliser",
        "gold", "copper", "zinc", "iron ore", "potash",
        "phosphate", "nickel", "steel", "mineral", "mining",
        "commodity", "metal", "urea", "ammonia", "rare earth",
        "petrochemical",
    ],
    "Conflict & Security": [
        "attack", "missile", "drone", "military", "war", "conflict",
        "sanction", "nuclear", "irgc", "revolutionary guard",
        "blockade", "ceasefire", "airstrike", "hezbollah", "houthi",
        "strike", "bomb", "weapon", "threat", "hostage",
        "strait", "red sea", "persian gulf",
    ],
}

# ---------------------------------------------------------------------------
# RSS Sources
# pre_filtered=True  → skip keyword check (feed is already Iran-specific)
# pre_filtered=False → apply KEYWORDS filter to each title
# ---------------------------------------------------------------------------
SOURCES = [

    # ── Google News searches ─────────────────────────────────────────────
    # Aggregate Reuters, FT, Bloomberg, AP, etc. — most reliable option.
    {
        "name": "Google News — Iran Energy",
        "urls": [
            "https://news.google.com/rss/search"
            "?q=Iran+oil+gas+LNG+energy+sanction&hl=en&gl=US&ceid=US:en"
        ],
        "pre_filtered": True,
    },
    {
        "name": "Google News — Iran Conflict",
        "urls": [
            "https://news.google.com/rss/search"
            "?q=Iran+war+military+attack+nuclear+Hormuz&hl=en&gl=US&ceid=US:en"
        ],
        "pre_filtered": True,
    },
    {
        "name": "Google News — Iran Resources",
        "urls": [
            "https://news.google.com/rss/search"
            "?q=Iran+minerals+aluminum+copper+gold+fertilizer+commodities"
            "&hl=en&gl=US&ceid=US:en"
        ],
        "pre_filtered": True,
    },
    {
        "name": "Google News — Iran Canada",
        "urls": [
            "https://news.google.com/rss/search"
            "?q=Iran+Canada+oil+energy+sanctions&hl=en-CA&gl=CA&ceid=CA:en"
        ],
        "pre_filtered": True,
    },

    # ── Canadian sources ─────────────────────────────────────────────────
    {
        "name": "Google News — Iran CBC/CTV",
        "urls": [
            "https://news.google.com/rss/search"
            "?q=Iran+%28CBC+OR+CTV%29&hl=en-CA&gl=CA&ceid=CA:en"
        ],
        "pre_filtered": True,
    },
    {
        "name": "Globe and Mail",
        "urls": [
            "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/world/",
        ],
        "pre_filtered": False,
    },

    # ── International sources ─────────────────────────────────────────────
    {
        "name": "BBC Middle East",
        "urls": ["http://feeds.bbci.co.uk/news/world/middle_east/rss.xml"],
        "pre_filtered": False,
    },
    {
        "name": "Al Jazeera",
        "urls": ["https://www.aljazeera.com/xml/rss/all.xml"],
        "pre_filtered": False,
    },
    {
        "name": "The Guardian — Iran",
        "urls": ["https://www.theguardian.com/world/iran/rss"],
        "pre_filtered": True,
    },
    {
        "name": "France 24",
        "urls": ["https://www.france24.com/en/middle-east/rss"],
        "pre_filtered": False,
    },
    {
        "name": "Google News — Israel/Iran",
        "urls": [
            "https://news.google.com/rss/search"
            "?q=Iran+Israel+attack+war+nuclear&hl=en&gl=US&ceid=US:en"
        ],
        "pre_filtered": True,
    },
    {
        "name": "Financial Times",
        "urls": ["https://www.ft.com/rss/home/uk"],
        "pre_filtered": False,
    },
]
