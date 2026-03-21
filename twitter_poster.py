import os
import time
import requests
from requests_oauthlib import OAuth1

API_KEY    = os.environ.get('TWITTER_API_KEY')
API_SECRET = os.environ.get('TWITTER_API_SECRET')
ACC_TOKEN  = os.environ.get('TWITTER_ACCESS_TOKEN')
ACC_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')

TWEET_URL = 'https://api.twitter.com/2/tweets'

CATEGORY_HASHTAGS = {
    'World-News':    '#WorldNews #BreakingNews',
    'Technology':    '#Tech #Technology',
    'Finance':       '#Finance #Economy',
    'Science':       '#Science',
    'Entertainment': '#Entertainment',
    'Sports':        '#Sports',
}

def post_tweet(article: dict) -> bool:
    """Post a single article to Twitter/X. Returns True on success."""
    if not all([API_KEY, API_SECRET, ACC_TOKEN, ACC_SECRET]):
        print('  ⚠️  Twitter credentials missing, skipping')
        return False

    import re
    category = article.get('category', '')
    title = article.get('title', '')
    hashtags = CATEGORY_HASHTAGS.get(category, '#News')
    slug = re.sub(r'-+', '-', re.sub(r'[\s_]+', '-', re.sub(r'[^\w\s-]', '', title.lower()))).strip('-')[:80]
    url = f"https://scrollcorner.com/{category.lower()}/{slug}"

    # Keep tweet under 280 chars: title + url + hashtags
    max_title = 280 - len(url) - len(hashtags) - 4  # 4 = spaces + newline
    if len(title) > max_title:
        title = title[:max_title - 1] + '…'

    tweet_text = f"{title}\n\n{url}\n\n{hashtags}"

    auth = OAuth1(API_KEY, API_SECRET, ACC_TOKEN, ACC_SECRET)
    try:
        r = requests.post(TWEET_URL, auth=auth, json={'text': tweet_text}, timeout=15)
        if r.status_code == 201:
            tweet_id = r.json().get('data', {}).get('id', '')
            print(f'  🐦 Tweeted: {title[:50]}...')
            print(f'     https://x.com/ScrollCorner/status/{tweet_id}')
            return True
        else:
            print(f'  ❌ Tweet failed ({r.status_code}): {r.text[:120]}')
            return False
    except Exception as e:
        print(f'  ❌ Tweet error: {e}')
        return False


def post_articles(articles: list, max_tweets: int = 3):
    """Post up to max_tweets articles, spacing them out."""
    posted = 0
    for article in articles:
        if posted >= max_tweets:
            break
        if post_tweet(article):
            posted += 1
            if posted < max_tweets:
                time.sleep(5)  # avoid rate limits
    print(f'  📊 Tweeted {posted}/{min(len(articles), max_tweets)} articles')
