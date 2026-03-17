"""
Run this script ONCE locally to generate your OAuth token.
After running, copy the token and add it to GitHub Secrets as BLOGGER_TOKEN.
"""
import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/blogger']

def get_token():
    creds = None

    # Check if token already exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                'credentials.json', SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            auth_url, _ = flow.authorization_url(prompt='consent')
            print('\n🌐 Open this URL in your browser:\n')
            print(auth_url)
            code = input('\n🔑 Paste the authorization code here: ').strip()
            flow.fetch_token(code=code)
            creds = flow.credentials

        # Save token for next time
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    print('\n✅ Authentication successful!')
    print('\n🔑 Your access token (add to GitHub Secrets as BLOGGER_TOKEN):')
    print(creds.token)
    print('\n🔄 Your refresh token (add to GitHub Secrets as BLOGGER_REFRESH_TOKEN):')
    print(creds.refresh_token)

    # Save to json for easy copying
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret
    }
    with open('token_data.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    print('\n💾 Saved to token_data.json')

if __name__ == '__main__':
    get_token()
