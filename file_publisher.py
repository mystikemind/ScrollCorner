"""
Publishes articles as JSON files to the scrollcorner-site repo via GitHub API.
All articles in a run are committed in a single batch commit using the Git Trees API.
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


def get_existing_slugs(headers: dict) -> set:
    """Fetch all existing file paths in content/ to skip duplicates."""
    existing = set()
    for cat in ['World-News', 'Technology', 'Finance', 'Science', 'Entertainment', 'Sports']:
        r = requests.get(
            f'{GITHUB_API}/repos/{REPO}/contents/content/{cat}',
            headers=headers,
            timeout=15,
        )
        if r.status_code == 200:
            for f in r.json():
                existing.add(f['path'])
    return existing


def get_latest_commit_sha(headers: dict) -> str:
    r = requests.get(
        f'{GITHUB_API}/repos/{REPO}/git/refs/heads/main',
        headers=headers,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()['object']['sha']


def get_tree_sha(commit_sha: str, headers: dict) -> str:
    r = requests.get(
        f'{GITHUB_API}/repos/{REPO}/git/commits/{commit_sha}',
        headers=headers,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()['tree']['sha']


def create_blob(content: str, headers: dict) -> str:
    r = requests.post(
        f'{GITHUB_API}/repos/{REPO}/git/blobs',
        headers=headers,
        json={'content': content, 'encoding': 'utf-8'},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()['sha']


def publish_all(articles: list) -> tuple[list, list]:
    published, failed = [], []

    try:
        headers = get_headers()
    except ValueError as e:
        print(f'❌ {e}')
        return published, failed

    print(f'🔑 GitHub token loaded — publishing to {REPO}')

    # Get existing files to skip duplicates
    print('🔍 Fetching existing articles...')
    existing_paths = get_existing_slugs(headers)

    # Prepare blobs for all new articles
    tree_items = []
    for i, article in enumerate(articles):
        slug = slugify(article['title'])
        if not slug:
            failed.append(article)
            continue

        category = article['category']
        path = f'content/{category}/{slug}.json'

        if path in existing_paths:
            print(f'  ⏭️  Already exists: {slug}')
            continue

        content = {
            'slug': slug,
            'title': article['title'],
            'body': article['body'],
            'category': category,
            'image': article.get('image', ''),
            'image_source': article.get('image_source', ''),
            'date': article.get('date', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())),
            'tags': article.get('labels', [category]),
            'source_url': article.get('original_url', '') or article.get('url', ''),
            'discover': article.get('discover', False),
        }

        try:
            blob_sha = create_blob(json.dumps(content, indent=2), headers)
            tree_items.append({
                'path': path,
                'mode': '100644',
                'type': 'blob',
                'sha': blob_sha,
            })
            url = f'https://scrollcorner.com/{category.lower()}/{slug}'
            print(f'  ✅ Prepared: {article["title"][:55]}')
            published.append({'slug': slug, 'url': url, 'category': category})
        except Exception as e:
            print(f'  ❌ Error preparing {slug}: {e}')
            failed.append(article)

    if not tree_items:
        print('ℹ️  No new articles to publish.')
        return published, failed

    # Create tree, commit, and update ref in one shot
    try:
        print(f'\n📦 Committing {len(tree_items)} articles in a single deployment...')
        latest_sha = get_latest_commit_sha(headers)
        base_tree_sha = get_tree_sha(latest_sha, headers)

        # Create new tree
        r = requests.post(
            f'{GITHUB_API}/repos/{REPO}/git/trees',
            headers=headers,
            json={'base_tree': base_tree_sha, 'tree': tree_items},
            timeout=30,
        )
        r.raise_for_status()
        new_tree_sha = r.json()['sha']

        # Create commit
        r = requests.post(
            f'{GITHUB_API}/repos/{REPO}/git/commits',
            headers=headers,
            json={
                'message': f'add: {len(tree_items)} articles',
                'tree': new_tree_sha,
                'parents': [latest_sha],
            },
            timeout=15,
        )
        r.raise_for_status()
        new_commit_sha = r.json()['sha']

        # Update main branch ref
        r = requests.patch(
            f'{GITHUB_API}/repos/{REPO}/git/refs/heads/main',
            headers=headers,
            json={'sha': new_commit_sha},
            timeout=15,
        )
        r.raise_for_status()
        print(f'🚀 Published {len(tree_items)} articles in one commit!')

    except Exception as e:
        print(f'❌ Batch commit failed: {e}')
        return [], articles

    print(f'\n📊 Summary: {len(published)} published, {len(failed)} failed')
    return published, failed
