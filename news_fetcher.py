import requests
import os
import hashlib
import xml.etree.ElementTree as ET

NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY')

# Royalty-free Unsplash image pools per category (10 images each)
# Used exclusively — no copyrighted CDN images from news sources
CATEGORY_IMAGE_POOLS = {
    'World-News': [
        'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1495020689067-958852a7765e?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1540910419892-943fd891f4f2?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1508615070457-ec59c23a4d96?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1551649001-1f56b2f99f3e?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1614849963640-d43e4e58d5b8?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&q=85&auto=format&fit=crop',
    ],
    'Technology': [
        'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=1200&q=85&auto=format&fit=crop',
    ],
    'Finance': [
        'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1565514020179-026b92b84bb6?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1559526324-593bc073d938?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1444653614127-0958b3adee40?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1502920917128-1aa671855523?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1604594849809-dfedbc827105?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1607944024060-0450380ddd33?w=1200&q=85&auto=format&fit=crop',
    ],
    'Science': [
        'https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1614730321146-b6fa6a46bcb4?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1576086213369-97a306d36557?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1628595351029-5cef0c6c14d9?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1559757148-5b63f2b5b30d?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1444703686981-a3abbc4d4fe3?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?w=1200&q=85&auto=format&fit=crop',
    ],
    'Entertainment': [
        'https://images.unsplash.com/photo-1603190287605-e6ade32fa852?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1533488765986-dae5c022b99c?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1567621936010-6e5d84f38bf3?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1561154464-5b60f4cc22cd?w=1200&q=85&auto=format&fit=crop',
    ],
    'Sports': [
        'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1517649763962-0c623066013b?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1556817411-31ae72c054a5?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1526676037019-dac8d39f1730?w=1200&q=85&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1594381898411-846e7d193883?w=1200&q=85&auto=format&fit=crop',
    ],
}

def _pick_image(category, seed):
    """Pick a royalty-free image deterministically from the pool using seed (slug/title)."""
    pool = CATEGORY_IMAGE_POOLS.get(category, CATEGORY_IMAGE_POOLS['World-News'])
    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(pool)
    return pool[idx]

# Primary RSS feeds per category
RSS_FEEDS = {
    'Technology':    'https://feeds.bbci.co.uk/news/technology/rss.xml',
    'Finance':       'https://feeds.bbci.co.uk/news/business/rss.xml',
    'Science':       'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
    'Entertainment': 'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml',
    'Sports':        'https://feeds.bbci.co.uk/news/sport/rss.xml',
}

# World-News: multiple international outlets for global coverage
WORLD_NEWS_FEEDS = [
    'https://feeds.bbci.co.uk/news/world/rss.xml',           # BBC World
    'https://www.aljazeera.com/xml/rss/all.xml',              # Al Jazeera
    'https://rss.dw.com/rdf/rss-en-world',                    # Deutsche Welle
    'https://feeds.reuters.com/reuters/worldNews',             # Reuters World
    'https://www.theguardian.com/world/rss',                   # The Guardian
]

NEWSAPI_CATEGORY_MAP = {
    'World-News': 'general',
    'Technology': 'technology',
    'Finance':    'business',
    'Science':    'science',
    'Entertainment': 'entertainment',
    'Sports':     'sports'
}

# Keywords that MUST appear in title/description for each category
# Articles from NewsAPI 'general' that don't match are rejected
CATEGORY_KEYWORDS = {
    'World-News': [
        'war', 'conflict', 'election', 'president', 'minister', 'government', 'military',
        'nato', 'un ', 'united nations', 'sanctions', 'treaty', 'diplomacy', 'attack',
        'killed', 'crisis', 'protest', 'coup', 'troops', 'border', 'refugee', 'nuclear',
        'missile', 'ukraine', 'russia', 'china', 'iran', 'israel', 'gaza', 'india',
        'trump', 'biden', 'congress', 'senate', 'court', 'supreme', 'policy', 'tariff',
    ],
    'Technology': [
        'ai', 'artificial intelligence', 'software', 'hardware', 'chip', 'gpu', 'cpu',
        'apple', 'google', 'microsoft', 'nvidia', 'meta', 'samsung', 'amazon', 'tech',
        'robot', 'algorithm', 'data', 'cyber', 'hack', 'app', 'startup', 'silicon',
        'iphone', 'android', 'cloud', 'open source', 'model', 'llm', 'computer',
    ],
    'Finance': [
        'stock', 'market', 'economy', 'gdp', 'inflation', 'bank', 'fed ', 'federal reserve',
        'interest rate', 'dollar', 'crypto', 'bitcoin', 'investment', 'fund', 'hedge',
        'revenue', 'earnings', 'profit', 'ipo', 'merger', 'acquisition', 'trade', 'tariff',
        'debt', 'budget', 'recession', 'tax', 'financial', 'wall street', 'nasdaq',
    ],
    'Science': [
        'research', 'study', 'scientists', 'nasa', 'space', 'planet', 'star', 'climate',
        'species', 'biology', 'physics', 'chemistry', 'genome', 'dna', 'fossil', 'vaccine',
        'disease', 'medical', 'health', 'brain', 'ocean', 'ai model', 'experiment',
        'telescope', 'launch', 'mission', 'probe', 'discovery', 'breakthrough', 'robot',
    ],
    'Entertainment': [
        'movie', 'film', 'music', 'album', 'artist', 'celebrity', 'actor', 'actress',
        'singer', 'band', 'concert', 'tour', 'oscar', 'emmy', 'grammy', 'award',
        'netflix', 'disney', 'hbo', 'streaming', 'tv show', 'series', 'season',
        'box office', 'trailer', 'premiere', 'hollywood', 'pop star', 'rapper',
    ],
    'Sports': [
        'nfl', 'nba', 'mlb', 'nhl', 'soccer', 'football', 'basketball', 'baseball',
        'tennis', 'golf', 'ufc', 'mma', 'olympic', 'championship', 'league', 'playoffs',
        'trade', 'draft', 'coach', 'player', 'team', 'game', 'match', 'score', 'win',
        'season', 'tournament', 'cup', 'title', 'athlete', 'transfer', 'injured',
    ],
}

# Keywords that disqualify an article from World-News (too soft/entertainment)
WORLD_NEWS_REJECT = [
    'meghan', 'harry', 'royal family', 'kardashian', 'celebrity', 'influencer',
    'reality tv', 'dating', 'wedding', 'divorce', 'baby', 'pregnant', 'instagram',
    'tiktok viral', 'trending', 'gossip',
]

def _matches_category(article, category):
    """Return True if article title+description matches expected category."""
    text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
    keywords = CATEGORY_KEYWORDS.get(category, [])
    if not any(kw in text for kw in keywords):
        return False
    if category == 'World-News' and any(kw in text for kw in WORLD_NEWS_REJECT):
        return False
    return True


def _parse_rss(feed_url, category, count=12):
    """Parse a single RSS feed and return articles."""
    try:
        r = requests.get(feed_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        root = ET.fromstring(r.content)
        ns = {'media': 'http://search.yahoo.com/mrss/'}
        source_name = root.findtext('.//channel/title') or feed_url.split('/')[2]
        articles = []
        for item in root.findall('.//item'):
            title = item.findtext('title', '').strip()
            desc  = item.findtext('description', '').strip()
            url   = item.findtext('link', '').strip()
            if not title or not desc or not url:
                continue
            articles.append({
                'title': title, 'description': desc, 'content': desc,
                'source': source_name, 'url': url,
                'image': _pick_image(category, url),
                'category': category
            })
            if len(articles) >= count:
                break
        return articles
    except Exception as e:
        print(f'  RSS error {feed_url[:40]}: {e}')
        return []

def fetch_from_rss(category, count=12):
    if category == 'World-News':
        articles = []
        seen = set()
        per_feed = max(6, count // len(WORLD_NEWS_FEEDS) + 2)
        for feed_url in WORLD_NEWS_FEEDS:
            for a in _parse_rss(feed_url, category, per_feed):
                if a['url'] not in seen:
                    seen.add(a['url'])
                    articles.append(a)
        return articles
    feed_url = RSS_FEEDS.get(category)
    if not feed_url:
        return []
    return _parse_rss(feed_url, category, count)

def fetch_from_newsapi(category, count=12):
    if not NEWSAPI_KEY:
        return []
    try:
        r = requests.get('https://newsapi.org/v2/top-headlines', params={
            'apiKey': NEWSAPI_KEY,
            'category': NEWSAPI_CATEGORY_MAP.get(category, 'general'),
            'language': 'en', 'pageSize': count
        }, timeout=10)
        articles = []
        for a in r.json().get('articles', []):
            if a.get('title') and a.get('description'):
                articles.append({
                    'title': a['title'], 'description': a.get('description', ''),
                    'content': a.get('content', ''),
                    'source': a.get('source', {}).get('name', 'Unknown'),
                    'url': a.get('url', ''),
                    'image': _pick_image(category, a.get('url', a.get('title', ''))),
                    'category': category
                })
        return articles
    except Exception as e:
        print(f'  NewsAPI error {category}: {e}')
        return []

def fetch_articles(category, count=3):
    """Fetch from BBC RSS + NewsAPI, deduplicate, filter by category keywords."""
    pool = []
    seen_urls = set()
    rejected = 0
    # BBC RSS first (most accurate categories), then NewsAPI
    for a in fetch_from_rss(category, count * 6) + fetch_from_newsapi(category, count * 4):
        if not a['url'] or a['url'] in seen_urls:
            continue
        if not _matches_category(a, category):
            rejected += 1
            continue
        seen_urls.add(a['url'])
        pool.append(a)
    if rejected:
        print(f'  Rejected {rejected} off-category articles from {category}')
    return pool

ALL_CATEGORIES = ['World-News', 'Technology', 'Finance', 'Science', 'Entertainment', 'Sports']

def fetch_all_categories(articles_per_category=3):
    all_articles = []
    for category in ALL_CATEGORIES:
        print(f'Fetching {category}...')
        articles = fetch_articles(category, articles_per_category)
        all_articles.extend(articles)
        print(f'  Got {len(articles)} articles')
    return all_articles
