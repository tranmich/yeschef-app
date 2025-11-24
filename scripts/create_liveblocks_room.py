"""
Quick script to create a Liveblocks room with public access
Run this once to enable access to whiteboard-52
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LIVEBLOCKS_SECRET = os.getenv('LIVEBLOCKS_SECRET_KEY')
ROOM_ID = 'whiteboard-52'

if not LIVEBLOCKS_SECRET:
    print("❌ LIVEBLOCKS_SECRET_KEY not found in .env")
    exit(1)

# Create room with public write access
response = requests.post(
    'https://api.liveblocks.io/v2/rooms',
    headers={
        'Authorization': f'Bearer {LIVEBLOCKS_SECRET}',
        'Content-Type': 'application/json'
    },
    json={
        'id': ROOM_ID,
        'defaultAccesses': ['room:write'],  # Public write access
        'metadata': {
            'name': 'YesChef Whiteboard',
            'householdId': '11',
            'whiteboardId': '52'
        }
    }
)

if response.status_code in [200, 201]:
    print(f"✅ Successfully created Liveblocks room: {ROOM_ID}")
    print(f"   Room has public write access")
    print(f"   Response: {response.json()}")
else:
    print(f"❌ Failed to create room: {response.status_code}")
    print(f"   Response: {response.text}")
