"""
One-time script to remove duplicate posts from the Blogger site.
Keeps the most recent post when duplicates are found (same title).
"""
import requests
import os
import json
import time
from collections import defaultdict

BLOG_ID = os.environ.get('BLOG_ID')
BLOGGER_TOKEN = os.environ.get('BLOGGER_TOKEN')

def get_all_posts():
    """Fetch all posts from the blog."""
    posts = []
    page_token = None
    url = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts'

    print('📥 Fetching all posts from Blogger...')
    while True:
        params = {
            'maxResults': 500,
            'status': 'live',
            'fields': 'items(id,title,published,url),nextPageToken'
        }
        if page_token:
            params['pageToken'] = page_token

        headers = {'Authorization': f'Bearer {BLOGGER_TOKEN}'}
        response = requests.get(url, headers=headers, params=params, timeout=15)
        data = response.json()

        batch = data.get('items', [])
        posts.extend(batch)
        print(f'  Fetched {len(posts)} posts so far...')

        page_token = data.get('nextPageToken')
        if not page_token:
            break
        time.sleep(1)

    print(f'✅ Total posts fetched: {len(posts)}')
    return posts

def find_duplicates(posts):
    """Group posts by normalized title and find duplicates."""
    title_map = defaultdict(list)
    for post in posts:
        # Normalize title: lowercase and strip whitespace
        key = post['title'].lower().strip()
        title_map[key].append(post)

    duplicates = {k: v for k, v in title_map.items() if len(v) > 1}
    return duplicates

def delete_post(post_id):
    """Delete a single post by ID."""
    url = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}'
    headers = {'Authorization': f'Bearer {BLOGGER_TOKEN}'}
    response = requests.delete(url, headers=headers, timeout=15)
    return response.status_code == 204

def cleanup():
    posts = get_all_posts()
    duplicates = find_duplicates(posts)

    if not duplicates:
        print('\n✅ No duplicates found!')
        return

    total_dupes = sum(len(v) - 1 for v in duplicates.values())
    print(f'\n🔍 Found {len(duplicates)} duplicate groups ({total_dupes} posts to delete)')
    print('-' * 60)

    deleted = 0
    for title, group in duplicates.items():
        # Sort by published date descending — keep the newest, delete the rest
        group.sort(key=lambda x: x['published'], reverse=True)
        keep = group[0]
        to_delete = group[1:]

        print(f'\n📌 Keeping:  [{keep["published"][:10]}] {keep["title"][:60]}')
        for post in to_delete:
            print(f'  🗑️  Deleting: [{post["published"][:10]}] {post["title"][:60]}')
            if delete_post(post['id']):
                print(f'     ✅ Deleted')
                deleted += 1
            else:
                print(f'     ❌ Failed to delete {post["id"]}')
            time.sleep(2)  # Avoid rate limits

    print(f'\n{"=" * 60}')
    print(f'✅ Cleanup complete: {deleted}/{total_dupes} duplicates removed')
    print(f'{"=" * 60}')

if __name__ == '__main__':
    if not BLOG_ID or not BLOGGER_TOKEN:
        print('❌ Set BLOG_ID and BLOGGER_TOKEN environment variables first')
        exit(1)
    cleanup()
