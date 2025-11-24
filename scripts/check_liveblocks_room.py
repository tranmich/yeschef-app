"""
Check if the Liveblocks room exists and has proper permissions
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

# Get room info
response = requests.get(
    f'https://api.liveblocks.io/v2/rooms/{ROOM_ID}',
    headers={
        'Authorization': f'Bearer {LIVEBLOCKS_SECRET}',
    }
)

if response.status_code == 200:
    room = response.json()
    print(f"✅ Room exists: {ROOM_ID}")
    print(f"   defaultAccesses: {room.get('defaultAccesses')}")
    print(f"   Full response: {room}")
else:
    print(f"❌ Room not found or error: {response.status_code}")
    print(f"   Response: {response.text}")
