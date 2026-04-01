import os
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv 
load_dotenv()

# Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
RECIPIENT_IG_USER_GID = os.getenv('RECIPIENT_IG_USER_GID')

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def send_instagram_dm(text):
    url = f"https://graph.instagram.com/v25.0/me/messages"
    payload = {
        "recipient": {"id": RECIPIENT_IG_USER_GID},
        "message": {"text": text}
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def fetch_new_emails():
    service = get_gmail_service()
    # Fetch unread messages from inbox
    results = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = results.get('messages', [])

    print(f"Found {len(messages)} new emails.")

    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        
        # Simple snippet extraction
        snippet = txt.get('snippet', 'No content')
        subject = next(h['value'] for h in txt['payload']['headers'] if h['name'] == 'Subject')
        
        notification = f"{subject}\n\n{snippet}"
        print(f"\n {notification} \n")
        print(f"Sending to IG: {subject}")
        
        status = send_instagram_dm(notification)
        print(f"Instagram DM response: {status}")
        
        # Mark as read so we don't resend
        service.users().messages().batchModify(
            userId='me', 
            body={'ids': [msg['id']], 'removeLabelIds': ['UNREAD']}
        ).execute()

if __name__ == '__main__':
    fetch_new_emails()