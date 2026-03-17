import requests
import os
import json
import time

BLOG_ID = os.environ.get('BLOG_ID')
BLOGGER_API_URL = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts'

def get_valid_token():
    """Return a fresh OAuth token, refreshing if needed."""
    refresh_token = os.environ.get('BLOGGER_REFRESH_TOKEN')
    client_id = os.environ.get('BLOGGER_CLIENT_ID')
    client_secret = os.environ.get('BLOGGER_CLIENT_SECRET')

    if refresh_token and client_id and client_secret:
        r = requests.post('https://oauth2.googleapis.com/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }, timeout=10)
        if r.status_code == 200:
            return r.json()['access_token']

    return os.environ.get('BLOGGER_TOKEN')

def format_post_html(article):
    """Format article body as clean HTML for Blogger."""
    paragraphs = article['body'].split('\n\n')
    html = ''

    # Add featured image if available
    if article.get('image'):
        html += f'<div class="post-featured-image"><img src="{article["image"]}" alt="{article["title"]}" style="width:100%;max-height:400px;object-fit:cover;border-radius:8px;margin-bottom:20px;"/></div>\n'

    # Add paragraphs
    for para in paragraphs:
        para = para.strip()
        if para:
            html += f'<p>{para}</p>\n'

    # Add source disclaimer
    html += f'\n<p style="font-size:12px;color:#aaa;border-top:1px solid #eee;padding-top:10px;margin-top:20px;">This article was curated and rewritten by ScrollCorner editorial team for informational purposes.</p>'

    return html

def publish_post(article, token):
    """Publish a single article to Blogger."""
    html_body = format_post_html(article)

    labels = [article['category']]
    if article.get('discover'):
        labels.append('Discover')

    post_data = {
        'title': article['title'],
        'content': html_body,
        'labels': labels
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Fix ALL-CAPS titles which Blogger rejects
    post_data['title'] = post_data['title'].title() if post_data['title'].isupper() else post_data['title']

    for attempt in range(3):
        try:
            response = requests.post(
                BLOGGER_API_URL, headers=headers,
                json=post_data, params={'isDraft': False}, timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                print(f'  ✅ Published: {article["title"][:50]}')
                print(f'     URL: {data.get("url", "N/A")}')
                return data
            elif response.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f'  ⏳ Rate limited, waiting {wait}s...')
                time.sleep(wait)
            else:
                print(f'  ❌ Failed ({response.status_code}): {response.text[:150]}')
                return None
        except Exception as e:
            print(f'  ❌ Error: {e}')
            return None
    return None

def publish_all(articles):
    """Publish all written articles to Blogger."""
    published = []
    failed = []

    token = get_valid_token()
    print(f'🔑 OAuth token refreshed successfully')

    for i, article in enumerate(articles):
        print(f'Publishing {i+1}/{len(articles)}: {article["title"][:50]}...')
        result = publish_post(article, token)
        if result:
            published.append(result)
        else:
            failed.append(article)
        time.sleep(3)

    print(f'\n📊 Summary: {len(published)} published, {len(failed)} failed')
    return published, failed
