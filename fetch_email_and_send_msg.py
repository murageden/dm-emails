import html
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
ACCESS_TOKEN = os.getenv('SENDER_ACCESS_TOKEN')
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

    how_many = len(messages)
    count_text = "Emails" if how_many >= 2 else "Email"

    print(f"Found {how_many} New {count_text}.")

    count = 1

    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()

        # Simple snippet extraction
        encoded_snippet = txt.get('snippet', 'No Content')
        snippet = html.unescape(encoded_snippet)

        subject = next(h['value'] for h in txt['payload']['headers'] if h['name'] == 'Subject')
        from_who = next(h['value'] for h in txt['payload']['headers'] if h['name'] == 'From')
        reply_to = next((h['value'] for h in txt['payload']['headers'] if h['name'] == 'Reply-To'), "No Reply-To address")
        notification = f"From: {from_who}\nReply-To: {reply_to}\n\n{subject}\n\n{snippet}"
        
        status = send_instagram_dm(notification)
        id = status.get('recipient_id', 'Unknown')
        dm_count_text = "DMs" if count >= 2 else "DM"
        print(f"Sent {count} IG {dm_count_text} to Recipient GID: {id}.")
        count += 1

        # Mark as read so we don't resend
        service.users().messages().batchModify(
            userId='me', 
            body={'ids': [msg['id']], 'removeLabelIds': ['UNREAD']}
        ).execute()

if __name__ == '__main__':
    fetch_new_emails()