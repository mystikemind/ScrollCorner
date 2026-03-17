"""
One-time script to remove duplicate posts from the Blogger site.
Uses fuzzy title matching to catch AI-rewritten variants of the same article.
Keeps the most recent post when duplicates are found.
"""
import requests
import os
import re
import time
from collections import defaultdict

BLOG_ID = os.environ.get('BLOG_ID')
BLOGGER_TOKEN = os.environ.get('BLOGGER_TOKEN')
SIMILARITY_THRESHOLD = 0.4  # Jaccard word overlap to consider titles duplicates

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
        page_token = data.get('nextPageToken')
        if not page_token:
            break
        time.sleep(1)

    print(f'✅ Total posts fetched: {len(posts)}')
    return posts

def title_words(title):
    """Extract meaningful words from a title for comparison."""
    # Remove punctuation, lowercase, split
    words = re.sub(r'[^a-z0-9\s]', '', title.lower()).split()
    # Remove common stop words
    stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
                 'for', 'of', 'with', 'as', 'is', 'are', 'was', 'were', 'be'}
    return set(w for w in words if w not in stopwords and len(w) > 2)

def jaccard_similarity(set1, set2):
    """Compute Jaccard similarity between two word sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union

def find_duplicates(posts):
    """Group posts by fuzzy title similarity."""
    groups = []
    assigned = set()

    for i, post in enumerate(posts):
        if i in assigned:
            continue
        group = [post]
        words_i = title_words(post['title'])
        for j, other in enumerate(posts):
            if j <= i or j in assigned:
                continue
            words_j = title_words(other['title'])
            if jaccard_similarity(words_i, words_j) >= SIMILARITY_THRESHOLD:
                group.append(other)
                assigned.add(j)
        if len(group) > 1:
            assigned.add(i)
            groups.append(group)

    return groups

def delete_post(post_id):
    """Delete a single post by ID."""
    url = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post_id}'
    headers = {'Authorization': f'Bearer {BLOGGER_TOKEN}'}
    response = requests.delete(url, headers=headers, timeout=15)
    return response.status_code == 204

def cleanup():
    posts = get_all_posts()
    duplicate_groups = find_duplicates(posts)

    if not duplicate_groups:
        print('\n✅ No duplicates found!')
        return

    total_dupes = sum(len(g) - 1 for g in duplicate_groups)
    print(f'\n🔍 Found {len(duplicate_groups)} duplicate groups ({total_dupes} posts to delete)')
    print('-' * 60)

    deleted = 0
    for group in duplicate_groups:
        # Keep newest, delete the rest
        group.sort(key=lambda x: x['published'], reverse=True)
        keep = group[0]
        to_delete = group[1:]

        print(f'\n📌 Keeping:  [{keep["published"][:16]}] {keep["title"][:65]}')
        for post in to_delete:
            print(f'  🗑️  Deleting: [{post["published"][:16]}] {post["title"][:65]}')
            if delete_post(post['id']):
                print(f'     ✅ Deleted')
                deleted += 1
            else:
                print(f'     ❌ Failed to delete {post["id"]}')
            time.sleep(2)

    print(f'\n{"=" * 60}')
    print(f'✅ Cleanup complete: {deleted}/{total_dupes} duplicates removed')
    print(f'{"=" * 60}')

if __name__ == '__main__':
    if not BLOG_ID or not BLOGGER_TOKEN:
        print('❌ Set BLOG_ID and BLOGGER_TOKEN environment variables first')
        exit(1)
    cleanup()
