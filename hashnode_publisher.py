import requests
import os
import time

HASHNODE_API_URL = 'https://gql.hashnode.com'

CATEGORY_TAGS = {
    'World-News':    {'slug': 'news',          'name': 'News'},
    'Technology':    {'slug': 'technology',    'name': 'Technology'},
    'Finance':       {'slug': 'finance',       'name': 'Finance'},
    'Science':       {'slug': 'science',       'name': 'Science'},
    'Entertainment': {'slug': 'entertainment', 'name': 'Entertainment'},
    'Sports':        {'slug': 'sports',        'name': 'Sports'},
}

PUBLISH_MUTATION = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post {
      id
      url
      title
    }
  }
}
"""

def format_post_markdown(article):
    """Format article body as Markdown for Hashnode."""
    paragraphs = article['body'].split('\n\n')
    md = '\n\n'.join(p.strip() for p in paragraphs if p.strip())
    md += '\n\n---\n*This article was curated and rewritten by ScrollCorner editorial team for informational purposes.*'
    return md

def publish_post(article, token, publication_id):
    """Publish a single article to Hashnode."""
    tags = []
    cat_tag = CATEGORY_TAGS.get(article['category'])
    if cat_tag:
        tags.append(cat_tag)
    if article.get('discover'):
        tags.append({'slug': 'discover', 'name': 'Discover'})

    variables = {
        'input': {
            'title': article['title'],
            'publicationId': publication_id,
            'contentMarkdown': format_post_markdown(article),
            'tags': tags,
        }
    }

    if article.get('image'):
        variables['input']['coverImageOptions'] = {
            'coverImageURL': article['image']
        }

    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    for attempt in range(3):
        try:
            response = requests.post(
                HASHNODE_API_URL,
                headers=headers,
                json={'query': PUBLISH_MUTATION, 'variables': variables},
                timeout=15
            )
            data = response.json()

            if 'errors' in data:
                msg = data['errors'][0].get('message', str(data['errors']))
                print(f'  ❌ Failed: {msg[:150]}')
                if attempt < 2:
                    time.sleep(5)
                continue

            post = data.get('data', {}).get('publishPost', {}).get('post', {})
            if post:
                print(f'  ✅ Published: {article["title"][:50]}')
                print(f'     URL: {post.get("url", "N/A")}')
                return post
            else:
                print(f'  ❌ Unexpected response: {str(data)[:150]}')
                return None
        except Exception as e:
            print(f'  ❌ Error: {e}')
            if attempt < 2:
                time.sleep(5)
    return None

def publish_all(articles):
    """Publish all written articles to Hashnode."""
    published = []
    failed = []

    token = os.environ.get('HASHNODE_TOKEN')
    publication_id = os.environ.get('HASHNODE_PUBLICATION_ID')

    if not token or not publication_id:
        missing = [k for k, v in {'HASHNODE_TOKEN': token, 'HASHNODE_PUBLICATION_ID': publication_id}.items() if not v]
        print(f'❌ Missing env vars: {missing}')
        return published, failed

    print(f'🔑 Hashnode token loaded')

    for i, article in enumerate(articles):
        print(f'Publishing {i+1}/{len(articles)}: {article["title"][:50]}...')
        result = publish_post(article, token, publication_id)
        if result:
            published.append(result)
        else:
            failed.append(article)
        time.sleep(2)

    print(f'\n📊 Summary: {len(published)} published, {len(failed)} failed')
    return published, failed
