import requests
import os
import re
import xml.etree.ElementTree as ET

NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY')

FALLBACK_IMAGES = {
    'World-News':    'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=80',
    'Technology':    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80',
    'Finance':       'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80',
    'Science':       'https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1200&q=80',
    'Entertainment': 'https://images.unsplash.com/photo-1603190287605-e6ade32fa852?w=1200&q=80',
    'Sports':        'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&q=80',
}

BLOCKED_DOMAINS = [
    'washingtonpost.com', 'nytimes.com', 'wsj.com', 'ft.com',
    'bloomberg.com', 'businessinsider.com', 'theatlantic.com',
]

# BBC RSS feeds — free, no API key, accurate categories
RSS_FEEDS = {
    'World-News':    'https://feeds.bbci.co.uk/news/world/rss.xml',
    'Technology':    'https://feeds.bbci.co.uk/news/technology/rss.xml',
    'Finance':       'https://feeds.bbci.co.uk/news/business/rss.xml',
    'Science':       'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
    'Entertainment': 'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml',
    'Sports':        'https://feeds.bbci.co.uk/news/sport/rss.xml',
}

NEWSAPI_CATEGORY_MAP = {
    'World-News': 'general',
    'Technology': 'technology',
    'Finance':    'business',
    'Science':    'science',
    'Entertainment': 'entertainment',
    'Sports':     'sports'
}

def _safe_image(url, category):
    if not url:
        return FALLBACK_IMAGES.get(category, '')
    if any(d in url for d in BLOCKED_DOMAINS):
        return FALLBACK_IMAGES.get(category, '')
    return url

def fetch_from_rss(category, count=12):
    feed_url = RSS_FEEDS.get(category)
    if not feed_url:
        return []
    try:
        r = requests.get(feed_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        root = ET.fromstring(r.content)
        ns = {'media': 'http://search.yahoo.com/mrss/'}
        articles = []
        for item in root.findall('.//item'):
            title = item.findtext('title', '').strip()
            desc  = item.findtext('description', '').strip()
            url   = item.findtext('link', '').strip()
            if not title or not desc or not url:
                continue
            thumb = item.find('media:thumbnail', ns)
            image = thumb.get('url', '') if thumb is not None else ''
            articles.append({
                'title': title, 'description': desc, 'content': desc,
                'source': 'BBC News', 'url': url,
                'image': image or FALLBACK_IMAGES.get(category, ''),
                'category': category
            })
            if len(articles) >= count:
                break
        return articles
    except Exception as e:
        print(f'  RSS error {category}: {e}')
        return []

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
                    'image': _safe_image(a.get('urlToImage'), category),
                    'category': category
                })
        return articles
    except Exception as e:
        print(f'  NewsAPI error {category}: {e}')
        return []

def fetch_articles(category, count=3):
    """Fetch from both NewsAPI and BBC RSS, merge and deduplicate by URL."""
    pool = []
    seen_urls = set()
    for a in fetch_from_newsapi(category, count * 4) + fetch_from_rss(category, count * 4):
        if a['url'] and a['url'] not in seen_urls:
            seen_urls.add(a['url'])
            pool.append(a)
    return pool

def fetch_all_categories(articles_per_category=3):
    all_articles = []
    for category in RSS_FEEDS.keys():
        print(f'Fetching {category}...')
        articles = fetch_articles(category, articles_per_category)
        all_articles.extend(articles)
        print(f'  Got {len(articles)} articles')
    return all_articles
