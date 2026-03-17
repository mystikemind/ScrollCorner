import requests
import os
import json
import time

BLOGGER_API_KEY = os.environ.get('BLOGGER_API_KEY')
BLOG_ID = os.environ.get('BLOG_ID')
BLOGGER_TOKEN = os.environ.get('BLOGGER_TOKEN')  # OAuth token

BLOGGER_API_URL = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts'

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

def publish_post(article):
    """Publish a single article to Blogger."""
    html_body = format_post_html(article)

    post_data = {
        'title': article['title'],
        'content': html_body,
        'labels': [article['category']]
    }

    headers = {
        'Authorization': f'Bearer {BLOGGER_TOKEN}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            BLOGGER_API_URL,
            headers=headers,
            json=post_data,
            params={'isDraft': False},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            print(f'  ✅ Published: {article["title"][:50]}')
            print(f'     URL: {data.get("url", "N/A")}')
            return data
        else:
            print(f'  ❌ Failed ({response.status_code}): {response.text[:200]}')
            return None
    except Exception as e:
        print(f'  ❌ Error publishing: {e}')
        return None

def publish_all(articles):
    """Publish all written articles to Blogger."""
    published = []
    failed = []

    for i, article in enumerate(articles):
        print(f'Publishing {i+1}/{len(articles)}: {article["title"][:50]}...')
        result = publish_post(article)
        if result:
            published.append(result)
        else:
            failed.append(article)
        time.sleep(3)

    print(f'\n📊 Summary: {len(published)} published, {len(failed)} failed')
    return published, failed
