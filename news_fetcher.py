import requests
import os

NEWSAPI_KEY = os.environ.get('NEWSAPI_KEY')

CATEGORIES = {
    'World-News': ['world', 'international', 'global'],
    'Technology': ['technology', 'tech', 'ai', 'software'],
    'Finance': ['business', 'finance', 'economy', 'markets'],
    'Health': ['health', 'medical', 'wellness'],
    'Entertainment': ['entertainment', 'celebrity', 'movies', 'music'],
    'Sports': ['sports', 'football', 'basketball', 'cricket']
}

FALLBACK_IMAGES = {
    'World-News':    'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=80',
    'Technology':    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80',
    'Finance':       'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80',
    'Health':        'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=1200&q=80',
    'Entertainment': 'https://images.unsplash.com/photo-1603190287605-e6ade32fa852?w=1200&q=80',
    'Sports':        'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&q=80',
}

NEWSAPI_CATEGORY_MAP = {
    'World-News': 'general',
    'Technology': 'technology',
    'Finance': 'business',
    'Health': 'health',
    'Entertainment': 'entertainment',
    'Sports': 'sports'
}

def fetch_articles(category, count=2):
    """Fetch top articles for a given category from NewsAPI."""
    newsapi_cat = NEWSAPI_CATEGORY_MAP.get(category, 'general')
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'apiKey': NEWSAPI_KEY,
        'category': newsapi_cat,
        'language': 'en',
        'pageSize': count
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        articles = []
        for article in data.get('articles', []):
            if article.get('title') and article.get('description'):
                articles.append({
                    'title': article['title'],
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'image': article.get('urlToImage') or FALLBACK_IMAGES.get(category, ''),
                    'category': category
                })
        return articles
    except Exception as e:
        print(f'Error fetching {category}: {e}')
        return []

def fetch_all_categories(articles_per_category=2):
    """Fetch articles for all categories."""
    all_articles = []
    for category in CATEGORIES.keys():
        print(f'Fetching {category}...')
        articles = fetch_articles(category, articles_per_category)
        all_articles.extend(articles)
        print(f'  Got {len(articles)} articles')
    return all_articles
