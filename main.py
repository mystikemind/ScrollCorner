"""
ScrollCorner Automated News Pipeline
=====================================
Fetches news → Rewrites with AI → Publishes to Blogger
Runs automatically every 3 hours via GitHub Actions
"""
import os
import sys
import json
import random
from datetime import datetime
from news_fetcher import fetch_all_categories
from article_writer import write_all_articles
from blogger_publisher import publish_all

# Configuration
ARTICLES_PER_CATEGORY = 3  # Articles to fetch per category per run
DISCOVER_PER_RUN = 3       # How many articles to also tag as "Discover"
TRACKING_FILE = 'published_urls.json'
MAX_TRACKED = 1000         # Max URLs to keep in history

def load_published_urls():
    """Load set of already-published article URLs."""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE) as f:
            return set(json.load(f))
    return set()

def save_published_urls(urls):
    """Save published URLs, keeping only the most recent MAX_TRACKED."""
    url_list = list(urls)[-MAX_TRACKED:]
    with open(TRACKING_FILE, 'w') as f:
        json.dump(url_list, f, indent=2)

def check_env_vars():
    """Verify all required environment variables are set."""
    required = ['GROQ_API_KEY', 'NEWSAPI_KEY', 'BLOG_ID', 'BLOGGER_TOKEN']
    missing = [var for var in required if not os.environ.get(var)]
    if missing:
        print(f'❌ Missing environment variables: {", ".join(missing)}')
        sys.exit(1)
    print('✅ All environment variables found')

def run_pipeline():
    """Run the full news pipeline."""
    print('=' * 60)
    print(f'🚀 ScrollCorner Pipeline Starting')
    print(f'⏰ Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)

    # Step 1: Check environment
    check_env_vars()

    # Step 2: Load already-published URLs for deduplication
    published_urls = load_published_urls()
    print(f'\n🔍 Tracking {len(published_urls)} previously published URLs')

    # Step 3: Fetch news
    print('\n📰 Step 1: Fetching latest news...')
    raw_articles = fetch_all_categories(ARTICLES_PER_CATEGORY)
    print(f'✅ Fetched {len(raw_articles)} articles total')

    # Step 4: Deduplicate — skip articles already published
    new_articles = [a for a in raw_articles if a.get('url') not in published_urls]
    skipped = len(raw_articles) - len(new_articles)
    if skipped:
        print(f'⏭️  Skipped {skipped} duplicate articles')
    print(f'✅ {len(new_articles)} new articles to process')

    if not new_articles:
        print('ℹ️  No new articles this run. Exiting.')
        sys.exit(0)

    # Step 5: Rewrite with AI
    print('\n✍️  Step 2: Rewriting articles with AI...')
    written_articles = write_all_articles(new_articles)
    print(f'✅ Wrote {len(written_articles)} articles')

    if not written_articles:
        print('❌ No articles written. Exiting.')
        sys.exit(1)

    # Step 6: Tag random articles as "Discover"
    discover_picks = random.sample(written_articles, min(DISCOVER_PER_RUN, len(written_articles)))
    for article in discover_picks:
        article['discover'] = True
    print(f'🔎 Tagged {len(discover_picks)} articles for Discover section')

    # Step 7: Publish to Blogger
    print('\n📤 Step 3: Publishing to ScrollCorner...')
    published, failed = publish_all(written_articles)

    # Step 8: Update tracking file with newly published URLs
    for article in new_articles[:len(published)]:
        if article.get('url'):
            published_urls.add(article['url'])
    save_published_urls(published_urls)

    # Step 9: Summary
    print('\n' + '=' * 60)
    print('📊 PIPELINE COMPLETE')
    print('=' * 60)
    print(f'✅ Published: {len(published)} articles')
    print(f'❌ Failed:    {len(failed)} articles')
    print(f'⏰ Finished:  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)

    # Save run log
    log = {
        'timestamp': datetime.now().isoformat(),
        'fetched': len(raw_articles),
        'skipped_duplicates': skipped,
        'written': len(written_articles),
        'published': len(published),
        'failed': len(failed)
    }
    with open('last_run.json', 'w') as f:
        json.dump(log, f, indent=2)

    return len(published) > 0

if __name__ == '__main__':
    success = run_pipeline()
    sys.exit(0 if success else 1)
