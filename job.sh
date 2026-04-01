#!/bin/bash

sudo timedatectl set-timezone Africa/Nairobi
cd usr/local/bin/app
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib requests python-dotenv --break-system-packages
python3 fetch_email_and_send_msg.py
