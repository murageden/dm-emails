#!/bin/bash

sudo timedatectl set-timezone Africa/Nairobi
cd usr/local/bin/app
pip install --quiet --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib requests python-dotenv --break-system-packages
python3 send_outreach_dm.py
