import requests
import os
import json
import time

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'

def rewrite_article(article):
    """Rewrite a news article into an original piece using Groq API."""
    title = article['title']
    description = article['description']
    content = article.get('content', '')
    source = article['source']
    category = article['category']

    prompt = f"""You are a professional news writer for ScrollCorner.com, a global news aggregator.

Based on the following news information, write a completely original, well-structured news article.

Original Title: {title}
Source: {source}
Category: {category}
Summary: {description}
Additional Info: {content}

Requirements:
- Write an entirely original article in your own words (do NOT copy the source)
- Length: 400-600 words
- Start with a strong opening paragraph summarizing the key news
- Include 4-6 paragraphs with analysis and context
- Professional journalistic tone
- End with a forward-looking conclusion
- Do NOT include any title in your response, just the article body
- Do NOT mention the source publication by name

Write the article now:"""

    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'llama-3.1-8b-instant',
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': 1000,
        'temperature': 0.7
    }

    for attempt in range(3):
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            data = response.json()
            if 'choices' not in data:
                raise ValueError(data.get('error', {}).get('message', 'No choices'))
            body = data['choices'][0]['message']['content'].strip()

            title_prompt = f"Create a compelling, SEO-friendly news headline for an article about: {title}. Return ONLY the headline, nothing else. Max 15 words."
            payload['messages'] = [{'role': 'user', 'content': title_prompt}]
            payload['max_tokens'] = 50

            time.sleep(3)
            title_response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
            title_data = title_response.json()
            if 'choices' not in title_data:
                raise ValueError(title_data.get('error', {}).get('message', 'No choices'))
            new_title = title_data['choices'][0]['message']['content'].strip().strip('"')

            return {
                'title': new_title,
                'body': body,
                'category': article['category'],
                'image': article.get('image', ''),
                'original_url': article.get('url', '')
            }
        except Exception as e:
            print(f'  Attempt {attempt+1} failed: {e}')
            if attempt < 2:
                time.sleep(10)
    return None

def write_all_articles(raw_articles):
    """Rewrite all fetched articles."""
    written = []
    for i, article in enumerate(raw_articles):
        print(f'Writing article {i+1}/{len(raw_articles)}: {article["title"][:50]}...')
        result = rewrite_article(article)
        if result:
            written.append(result)
            print(f'  ✅ Done: {result["title"][:50]}...')
        else:
            print(f'  ❌ Failed')
    return written
