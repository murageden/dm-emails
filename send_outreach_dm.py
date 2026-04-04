import os
import requests
from dotenv import load_dotenv 
load_dotenv()

RECIPIENT_ACCESS_TOKEN = os.getenv('RECIPIENT_ACCESS_TOKEN')
SENDER_IG_USER_GID = os.getenv('SENDER_IG_USER_GID')

def send_instagram_dm(text):
    url = f"https://graph.instagram.com/v25.0/me/messages"
    payload = {
        "recipient": {"id": SENDER_IG_USER_GID},
        "message": {"text": text}
    }
    headers = {"Authorization": f"Bearer {RECIPIENT_ACCESS_TOKEN}"}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    message = "Send more emails 😎"
    status = send_instagram_dm(message)
    id = status.get('recipient_id', 'Unknown')
    print(f"Sent Outreach IG DM to Recipient GID: {id}.")
