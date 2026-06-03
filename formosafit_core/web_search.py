"""
Web Search Utility — Fetches real shopping links for recommended products.
Uses DuckDuckGo Search (no API key required).
"""

import logging
import urllib.parse
import re
from ddgs import DDGS
from formosafit_core.product_db import Product

logger = logging.getLogger(__name__)

# Mapping from lowercase brand name to expected domain substrings
BRAND_DOMAINS = {
    "uniqlo": ["uniqlo"],
    "gu": ["gu-global", "gu-japan"],
    "net": ["net-clothing"],
    "pazzo": ["pazzo"],
    "meier.q": ["meierq"],
    "無印良品": ["muji"],
    "nike": ["nike"],
    "converse": ["converse"],
    "vanger": ["vanger"],
    "teva": ["teva"],
    "grace gift": ["gracegift"],
    "new era": ["neweracap"],
    "dw": ["danielwellington"],
    "porter": ["ll-porter", "porter"],
    "mont-bell": ["montbell"],
    "lativ": ["lativ"],
    "decathlon": ["decathlon"],
    "plainme": ["plain-me", "plainme"],
    "charles & keith": ["charleskeith"],
    "owndays": ["owndays"],
    "gildan": ["gildan"]
}

# Domains that represent reviews, social media, blogs, or forums rather than direct shopping
BLACKLIST_DOMAINS = [
    "instagram.com", "facebook.com", "twitter.com", "x.com", "threads.net",
    "youtube.com", "youtu.be", "pinterest.com", "tiktok.com", "plurk.com",
    "pixnet.net", "dcard.tw", "ptt.cc", "mobile01.com", "xuite.net", "vocus.cc",
    "medium.com", "blogger.com", "blogspot.com", "line.me", "line-apps.com",
    "wikipedia.org", "en.wikipedia.org", "zh.wikipedia.org", "gitbook.io",
    "github.com", "gitlab.com", "bitbucket.org", "behance.net", "linkedin.com",
    "udn.com", "chinatimes.com", "ltn.com.tw", "ettoday.net", "setn.com",
    "tvbs.com.tw", "ftvnews.com.tw", "storm.mg", "thenewslens.com"
]

def normalize_string(s: str) -> str:
    """Remove all non-alphanumeric characters and lowercase a string."""
    return re.sub(r'[^a-zA-Z0-9]', '', s.lower())

def score_link(href: str, title: str, p_brand: str, p_name: str) -> float:
    """
    Score a search result based on how likely it is to be a direct shopping link.
    Returns a score where higher is better, or a negative value if it should be rejected.
    """
    href_lower = href.lower()
    title_lower = title.lower()
    
    # Parse domain
    try:
        parsed_url = urllib.parse.urlparse(href_lower)
        domain = parsed_url.netloc
    except Exception:
        domain = href_lower

    # 1. Blacklist check (automatic rejection if matches)
    for bad_domain in BLACKLIST_DOMAINS:
        if bad_domain in domain:
            return -100.0
            
    # Blacklist title keywords (typically reviews, blogs, social media)
    blacklist_title_keywords = [
        "心得", "分享", "推薦", "評價", "開箱", "比較", "討論", 
        "新聞", "社群", "影音", "部落格", "blog", "dcard", "ptt", 
        "mobile01", "整理", "懶人包"
    ]
    for keyword in blacklist_title_keywords:
        if keyword in title_lower:
            return -50.0

    score = 0.0
    
    # 2. Check brand-specific domains (Brand site)
    brand_key = normalize_string(p_brand)
    expected_domains = BRAND_DOMAINS.get(p_brand.lower(), [brand_key])
    
    brand_domain_match = False
    for exp in expected_domains:
        if exp in domain:
            brand_domain_match = True
            break
            
    if brand_domain_match:
        score += 15.0  # Very high score for official brand site

    # 3. Check popular e-commerce platform domains
    major_platforms = [
        "shopee.tw", "momoshop.com.tw", "pchome.com.tw", "buy123.com.tw", 
        "etmall.com.tw", "ruten.com.tw", "pcstore.com.tw", "yahoo.com"
    ]
    platform_match = False
    for platform in major_platforms:
        if platform in domain:
            # For Yahoo, make sure it's shopping/auction and not news/portal
            if "yahoo.com" in platform and not any(sub in domain for sub in ["buy.yahoo.com", "mall.yahoo.com", "bid.yahoo.com"]):
                continue
            platform_match = True
            break
            
    if platform_match:
        score += 8.0  # High score for major shopping platforms

    # 4. Check for general shopping keywords in URL path or title
    shopping_url_keywords = ["shop", "store", "buy", "product", "item", "detail", "goods", "category"]
    for kw in shopping_url_keywords:
        if kw in parsed_url.path:
            score += 2.0
            
    shopping_title_keywords = ["購物", "商城", "官網", "商店", "線上購", "購買", "官方", "專區"]
    for kw in shopping_title_keywords:
        if kw in title_lower:
            score += 2.0

    # 5. Check if it's a price aggregator (deprioritize compared to direct shops)
    aggregators = ["findprice.com.tw", "feebee.com.tw", "biggo.com.tw"]
    is_aggregator = False
    for agg in aggregators:
        if agg in domain:
            is_aggregator = True
            break
            
    if is_aggregator:
        score += 1.0  # Give it a very small score so it's a last resort
    else:
        # If it's not a known aggregator and not blacklisted, it gets a default baseline if it looks like a shop
        score += 3.0

    # 6. Title match boost (if the product name is in the title, it's highly relevant)
    # Split product name into keywords (excluding very short ones)
    name_keywords = [kw for kw in re.split(r'\s+', p_name) if len(kw) > 1]
    match_count = 0
    for kw in name_keywords:
        if kw.lower() in title_lower:
            match_count += 1
    if match_count > 0:
        score += match_count * 2.0

    return score

def get_shopping_links(products: list[Product], max_results_per_item: int = 1, detected_gender: str = None) -> dict[str, list[dict]]:
    """
    Search the web for shopping links for the given products, filtering out non-shopping links.
    
    Args:
        products: list of Product objects to search for
        max_results_per_item: number of filtered results to return per product
        detected_gender: "Men" or "Women" or None — appended to search query for gender-appropriate results
    
    Returns a dictionary mapping product ID to a list of filtered search result dictionaries (title, href).
    """
    links_map = {}
    
    # Map detected gender to a Chinese search keyword
    gender_keyword = ""
    if detected_gender == "masculine":
        gender_keyword = "男裝"
    elif detected_gender == "feminine":
        gender_keyword = "女裝"
    
    try:
        ddgs = DDGS()
        for p in products:
            # Construct a highly targeted query based on the local curated data
            # Include gender keyword to bias results toward the correct gender
            query = f"{p.brand} {p.name} {gender_keyword} 台灣 購買".strip()
            logger.info(f"Searching web for: {query}")
            
            try:
                # Retrieve more results so we have candidates to filter through
                candidates = list(ddgs.text(query, max_results=8))
                
                scored_results = []
                for res in candidates:
                    href = res.get("href", "")
                    title = res.get("title", "")
                    if not href or not title:
                        continue
                        
                    score = score_link(href, title, p.brand, p.name)
                    logger.debug(f"Candidate Link: {href} | Score: {score} | Title: {title}")
                    
                    if score > 0:
                        scored_results.append((score, res))
                
                # Sort by score descending
                scored_results.sort(key=lambda x: x[0], reverse=True)
                
                # Take top max_results_per_item
                filtered_results = [res for _, res in scored_results[:max_results_per_item]]
                links_map[p.id] = filtered_results
                
            except Exception as e:
                logger.warning(f"Failed to search for '{query}': {e}")
                links_map[p.id] = []
                
    except Exception as e:
        logger.error(f"Failed to initialize DDGS: {e}")
        
    return links_map
