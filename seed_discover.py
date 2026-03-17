"""
One-time script to tag random existing posts with the 'Discover' label.
"""
import requests
import os
import json
import random
import time

BLOG_ID = os.environ.get('BLOG_ID')
BLOGGER_TOKEN = os.environ.get('BLOGGER_TOKEN')
DISCOVER_COUNT = 3

def get_all_posts():
    url = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts'
    headers = {'Authorization': f'Bearer {BLOGGER_TOKEN}'}
    r = requests.get(url, headers=headers,
        params={'maxResults': 500, 'status': 'live', 'fields': 'items(id,title,labels)'},
        timeout=15)
    return r.json().get('items', [])

def add_discover_label(post):
    labels = post.get('labels', [])
    if 'Discover' in labels:
        return True  # already tagged
    labels.append('Discover')
    url = f'https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/{post["id"]}'
    headers = {'Authorization': f'Bearer {BLOGGER_TOKEN}', 'Content-Type': 'application/json'}
    r = requests.patch(url, headers=headers, json={'labels': labels}, timeout=15)
    return r.status_code == 200

posts = get_all_posts()
# Only pick posts that don't already have Discover
candidates = [p for p in posts if 'Discover' not in p.get('labels', [])]
picks = random.sample(candidates, min(DISCOVER_COUNT, len(candidates)))

print(f'Tagging {len(picks)} posts with Discover label...')
for post in picks:
    ok = add_discover_label(post)
    status = '✅' if ok else '❌'
    print(f'  {status} {post["title"][:65]}')
    time.sleep(1)

print('Done.')
