"""
Publishes articles as JSON files to the scrollcorner-site repo via GitHub API.
Vercel auto-deploys on every push.
"""
import os
import re
import json
import time
import base64
import requests

GITHUB_API = 'https://api.github.com'
REPO = 'mystikemind/scrollcorner-site'


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug[:80]


def get_headers():
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GITHUB_PAT')
    if not token:
        raise ValueError('GITHUB_TOKEN or GITHUB_PAT secret not set')
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
    }


def file_exists(path: str, headers: dict):
    r = requests.get(f'{GITHUB_API}/repos/{REPO}/contents/{path}', headers=headers)
    if r.status_code == 200:
        return r.json().get('sha')
    return None


def publish_post(article: dict, headers: dict) -> dict | None:
    slug = slugify(article['title'])
    if not slug:
        return None

    category = article['category']
    path = f'content/{category}/{slug}.json'

    # Skip if file already exists (dedup)
    if file_exists(path, headers):
        print(f'  ⏭️  Already exists: {slug}')
        return None

    content = {
        'slug': slug,
        'title': article['title'],
        'body': article['body'],
        'category': category,
        'image': article.get('image', ''),
        'date': article.get('date', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())),
        'tags': article.get('labels', [category]),
        'source_url': article.get('url', ''),
        'discover': article.get('discover', False),
    }

    encoded = base64.b64encode(json.dumps(content, indent=2).encode()).decode()

    payload = {
        'message': f'add: {article["title"][:60]}',
        'content': encoded,
    }

    for attempt in range(3):
        try:
            r = requests.put(
                f'{GITHUB_API}/repos/{REPO}/contents/{path}',
                headers=headers,
                json=payload,
                timeout=15,
            )
            if r.status_code in (200, 201):
                url = f'https://scrollcorner.com/{category.lower()}/{slug}'
                print(f'  ✅ Published: {article["title"][:55]}')
                print(f'     {url}')
                return {'slug': slug, 'url': url, 'category': category}
            else:
                print(f'  ❌ Failed ({r.status_code}): {r.text[:120]}')
                if attempt < 2:
                    time.sleep(5)
        except Exception as e:
            print(f'  ❌ Error: {e}')
            if attempt < 2:
                time.sleep(5)

    return None


def publish_all(articles: list) -> tuple[list, list]:
    published, failed = [], []
    try:
        headers = get_headers()
    except ValueError as e:
        print(f'❌ {e}')
        return published, failed

    print(f'🔑 GitHub token loaded — publishing to {REPO}')

    for i, article in enumerate(articles):
        print(f'Publishing {i+1}/{len(articles)}: {article["title"][:50]}...')
        result = publish_post(article, headers)
        if result:
            published.append(result)
        else:
            failed.append(article)
        time.sleep(1)

    print(f'\n📊 Summary: {len(published)} published, {len(failed)} failed')
    return published, failed
