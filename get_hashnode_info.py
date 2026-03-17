"""Run this once to get your Hashnode Publication ID."""
import requests

token = input('Paste your Hashnode Personal Access Token: ').strip()

query = """
query {
  me {
    publications(first: 10) {
      edges {
        node {
          id
          title
          url
        }
      }
    }
  }
}
"""

r = requests.post(
    'https://gql.hashnode.com',
    headers={'Authorization': token, 'Content-Type': 'application/json'},
    json={'query': query},
    timeout=10
)
data = r.json()

if 'errors' in data:
    print(f'Error: {data["errors"][0]["message"]}')
else:
    pubs = data['data']['me']['publications']['edges']
    for p in pubs:
        n = p['node']
        print(f'\nTitle: {n["title"]}')
        print(f'URL:   {n["url"]}')
        print(f'ID:    {n["id"]}  ← add this as HASHNODE_PUBLICATION_ID secret')
