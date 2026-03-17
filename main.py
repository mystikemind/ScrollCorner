"""
ScrollCorner Automated News Pipeline
=====================================
Fetches news → Rewrites with AI → Publishes to Blogger
Runs automatically every 6 hours via GitHub Actions
"""
import os
import sys
import json
from datetime import datetime
from news_fetcher import fetch_all_categories
from article_writer import write_all_articles
from blogger_publisher import publish_all

# Configuration
ARTICLES_PER_CATEGORY = 2  # Articles to publish per category per run
CATEGORIES_PER_RUN = 6     # All 6 categories

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

    # Step 2: Fetch news
    print('\n📰 Step 1: Fetching latest news...')
    raw_articles = fetch_all_categories(ARTICLES_PER_CATEGORY)
    print(f'✅ Fetched {len(raw_articles)} articles total')

    if not raw_articles:
        print('❌ No articles fetched. Exiting.')
        sys.exit(1)

    # Step 3: Rewrite with AI
    print('\n✍️  Step 2: Rewriting articles with AI...')
    written_articles = write_all_articles(raw_articles)
    print(f'✅ Wrote {len(written_articles)} articles')

    if not written_articles:
        print('❌ No articles written. Exiting.')
        sys.exit(1)

    # Step 4: Publish to Blogger
    print('\n📤 Step 3: Publishing to ScrollCorner...')
    published, failed = publish_all(written_articles)

    # Step 5: Summary
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
