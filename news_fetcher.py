import requests
import os
import re
import xml.etree.ElementTree as ET

NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY')

# Fallback images (Unsplash) used only when source has no image or is from a blocked domain
FALLBACK_IMAGES = {
    'World-News':    'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=85',
    'Technology':    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=85',
    'Finance':       'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=85',
    'Science':       'https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1200&q=85',
    'Entertainment': 'https://images.unsplash.com/photo-1603190287605-e6ade32fa852?w=1200&q=85',
    'Sports':        'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&q=85',
}

# Domains that block hotlinking — use Unsplash fallback instead
BLOCKED_DOMAINS = [
    'washingtonpost.com', 'nytimes.com', 'wsj.com', 'ft.com',
    'bloomberg.com', 'businessinsider.com', 'theatlantic.com',
    'usatoday.com', 'floridatoday.com', 'gannett-cdn.com', 'gcdn.co',
    'media.cnn.com', 'static01.nyt.com', 'i.insider.com', 'fortune.com',
    's.yimg.com', 'media.zenfs.com', 'images.axios.com',
]

def _safe_image(url, category):
    """Return source image URL upgraded to high-res, or Unsplash fallback if blocked/missing."""
    if not url:
        return FALLBACK_IMAGES.get(category, '')
    if any(d in url for d in BLOCKED_DOMAINS):
        return FALLBACK_IMAGES.get(category, '')
    # BBC ace/* = InDepth/branded watermark images → use Unsplash fallback
    if 'ichef.bbci.co.uk/ace/' in url:
        return FALLBACK_IMAGES.get(category, '')
    # BBC news: upgrade to 1024px
    url = re.sub(r'(ichef\.bbci\.co\.uk/news)/\d+/', r'\1/1024/', url)
    return url

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

# Keywords that disqualify an article from World-News (entertainment/sports/lifestyle)
WORLD_NEWS_REJECT = [
    # Celebrity / lifestyle
    'meghan', 'harry', 'royal family', 'kardashian', 'celebrity', 'influencer',
    'reality tv', 'dating', 'wedding', 'divorce', 'baby', 'pregnant', 'instagram',
    'tiktok viral', 'trending', 'gossip',
    # Music / entertainment
    'album', 'new album', 'music video', 'bts', 'k-pop', 'kpop', 'pop star',
    'rapper', 'singer', 'band', 'concert', 'tour', 'billboard', 'grammy',
    'oscar', 'emmy', 'box office', 'streaming', 'netflix', 'disney',
    'movie trailer', 'film premiere', 'hollywood', 'actor', 'actress',
    # Sports
    'march madness', 'nba', 'nfl', 'mlb', 'nhl', 'super bowl', 'world series',
    'playoffs', 'championship game', 'slam dunk', 'touchdown', 'home run',
    'march madness bracket', 'ncaa', 'college basketball', 'college football',
    'transfer portal', 'nfl draft', 'nba draft',
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
            # Prefer media:content (higher res) over media:thumbnail, then enclosure
            media_content = item.find('media:content', ns)
            media_thumb   = item.find('media:thumbnail', ns)
            enclosure     = item.find('enclosure')
            if media_content is not None and media_content.get('url'):
                raw_image = media_content.get('url', '')
            elif media_thumb is not None and media_thumb.get('url'):
                raw_image = media_thumb.get('url', '')
            elif enclosure is not None and enclosure.get('url', '').startswith('http'):
                raw_image = enclosure.get('url', '')
            else:
                raw_image = ''
            # Skip BBC InDepth articles (ace/ path = branded watermark images)
            if 'ichef.bbci.co.uk/ace/' in raw_image:
                continue
            # Skip articles with no real image
            if not raw_image:
                continue
            image = _safe_image(raw_image, category)
            # Skip if image resolved to Unsplash fallback (blocked domain etc.)
            if 'unsplash' in image:
                continue
            articles.append({
                'title': title, 'description': desc, 'content': desc,
                'source': source_name, 'url': url,
                'image': image,
                'image_source': source_name if raw_image and 'unsplash' not in image else '',
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
            if not (a.get('title') and a.get('description') and a.get('urlToImage')):
                continue
            image = _safe_image(a.get('urlToImage'), category)
            if 'unsplash' in image:
                continue
            articles.append({
                'title': a['title'], 'description': a.get('description', ''),
                'content': a.get('content', ''),
                'source': a.get('source', {}).get('name', 'Unknown'),
                'url': a.get('url', ''),
                'image': image,
                'image_source': a.get('source', {}).get('name', ''),
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
