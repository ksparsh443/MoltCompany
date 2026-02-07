"""
One-time Google Drive OAuth2 setup.

This script opens a browser window for you to log in with your Google account.
After login, it saves a refresh token to ./credentials/drive_token.json.
The server uses this token for all future uploads (no browser needed again).

PREREQUISITES:
1. Go to https://console.cloud.google.com
2. Select your project (or create one)
3. Go to APIs & Services -> Credentials
4. Click "Create Credentials" -> "OAuth client ID"
5. Application type: "Desktop app"
6. Download the JSON and save it as: ./credentials/client_secret.json
7. Run this script: python setup_drive_auth.py
"""

import os
import json

CLIENT_SECRET_FILE = "./credentials/client_secret.json"
TOKEN_FILE = "./credentials/drive_token.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]


def main():
    if not os.path.exists(CLIENT_SECRET_FILE):
        print("ERROR: client_secret.json not found!")
        print()
        print("Steps to create it:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Select your project")
        print("3. Go to APIs & Services -> Credentials")
        print("4. Click 'Create Credentials' -> 'OAuth client ID'")
        print("5. Application type: 'Desktop app'")
        print("6. Download the JSON")
        print(f"7. Save it as: {os.path.abspath(CLIENT_SECRET_FILE)}")
        return

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Missing package. Run: pip install google-auth-oauthlib")
        return

    print("Opening browser for Google sign-in...")
    print("Log in with the Google account that owns your Drive folder.")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the token
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    print()
    print(f"Token saved to: {os.path.abspath(TOKEN_FILE)}")
    print("Google Drive uploads will now work!")
    print()
    print("Restart your server to pick up the new credentials.")


if __name__ == "__main__":
    main()
