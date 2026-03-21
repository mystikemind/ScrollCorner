import os
import re
import time
import tweepy

API_KEY    = os.environ.get('TWITTER_API_KEY')
API_SECRET = os.environ.get('TWITTER_API_SECRET')
ACC_TOKEN  = os.environ.get('TWITTER_ACCESS_TOKEN')
ACC_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')

CATEGORY_HASHTAGS = {
    'World-News':    '#WorldNews #BreakingNews',
    'Technology':    '#Tech #Technology',
    'Finance':       '#Finance #Economy',
    'Science':       '#Science',
    'Entertainment': '#Entertainment',
    'Sports':        '#Sports',
}

def _slugify(title):
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_]+', '-', slug)
    return re.sub(r'-+', '-', slug).strip('-')[:80]

def _get_client():
    if not all([API_KEY, API_SECRET, ACC_TOKEN, ACC_SECRET]):
        return None
    return tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACC_TOKEN,
        access_token_secret=ACC_SECRET,
    )

def post_tweet(client, article: dict) -> bool:
    category = article.get('category', '')
    title    = article.get('title', '')
    hashtags = CATEGORY_HASHTAGS.get(category, '#News')
    slug     = _slugify(title)
    url      = f"https://scrollcorner.com/{category.lower()}/{slug}"

    max_title = 280 - len(url) - len(hashtags) - 4
    if len(title) > max_title:
        title = title[:max_title - 1] + '…'

    tweet_text = f"{title}\n\n{url}\n\n{hashtags}"

    try:
        response = client.create_tweet(text=tweet_text)
        tweet_id = response.data['id']
        print(f'  🐦 Tweeted: {title[:55]}')
        print(f'     https://x.com/ScrollCorner/status/{tweet_id}')
        return True
    except tweepy.TweepyException as e:
        print(f'  ❌ Tweet failed: {e}')
        return False

def post_articles(articles: list, max_tweets: int = 3):
    client = _get_client()
    if not client:
        print('  ⚠️  Twitter credentials missing, skipping')
        return

    posted = 0
    for article in articles:
        if posted >= max_tweets:
            break
        if post_tweet(client, article):
            posted += 1
            if posted < max_tweets:
                time.sleep(5)

    print(f'  📊 Tweeted {posted}/{min(len(articles), max_tweets)} articles')
