# Third-Party Integrations Guide
**Date**: November 5, 2025  
**Status**: Implementation Ready

## 🎯 Overview

YesChef Whiteboard uses best-in-class third-party services to accelerate development and provide enterprise-grade features:

| Service | Purpose | Free Tier | Paid Tier |
|---------|---------|-----------|-----------|
| **Liveblocks** | Real-time collaboration, comments | 100 MAU | $249/mo @ 10k MAU |
| **Stream Chat** | Household messaging | 25 MAU | $99/mo @ 100 MAU |
| **Tiptap** | Rich text editor (notes) | Free forever | N/A |
| **React Color** | Color picker | Free forever | N/A |

**Time Savings**: ~8 weeks of development  
**Cost at Launch**: $0/month (free tiers)  
**Cost at Scale**: $348/month (both paid tiers at 100+ users)

---

## 🔧 1. Liveblocks Integration

### **Purpose**
- Real-time collaboration (cursors, presence)
- Comments on whiteboard objects
- Activity feed
- @mentions

### **Setup**

#### **Backend: Auth Endpoint**
```python
# app/api/v2/liveblocks.py

from flask import Blueprint, request, jsonify
from liveblocks import Liveblocks
import os

liveblocks_bp = Blueprint('liveblocks', __name__)
liveblocks_client = Liveblocks(secret_key=os.getenv('LIVEBLOCKS_SECRET_KEY'))

@liveblocks_bp.route('/auth', methods=['POST'])
@require_auth
def liveblocks_auth():
    """Generate Liveblocks room token for authenticated user"""
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    
    room_id = request.json.get('room')  # e.g., "whiteboard-123"
    
    # Verify user has access to this whiteboard
    whiteboard_id = int(room_id.split('-')[1])
    if not user_has_whiteboard_access(user_id, whiteboard_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Generate token
    token = liveblocks_client.prepare_session(
        user_id=str(user_id),
        user_info={
            'name': user.name,
            'avatar': user.avatar_url,
            'color': user.cursor_color or '#FF6B6B'
        }
    ).allow(room_id, ['room:write']).authorize()
    
    return jsonify({'token': token})
```

#### **Frontend: Provider Setup**
```jsx
// frontend/src/App.js

import { LiveblocksProvider } from "@liveblocks/react/suspense";

function App() {
  return (
    <LiveblocksProvider authEndpoint="/api/v2/liveblocks/auth">
      <Router>
        {/* Your app routes */}
      </Router>
    </LiveblocksProvider>
  );
}
```

#### **Frontend: Whiteboard Integration**
```jsx
// frontend/src/pages/WhiteboardApp.js

import { RoomProvider, useOthers } from "@liveblocks/react/suspense";

function WhiteboardApp({ whiteboardId }) {
  return (
    <RoomProvider id={`whiteboard-${whiteboardId}`}>
      <WhiteboardCanvas />
      <CollaboratorList />
      <CommentPanel />
    </RoomProvider>
  );
}

// Show live cursors
function CollaboratorList() {
  const others = useOthers();
  
  return (
    <div className="collaborators">
      {others.map((user) => (
        <div key={user.id}>
          <img src={user.info.avatar} />
          <span>{user.info.name}</span>
        </div>
      ))}
    </div>
  );
}
```

#### **Frontend: Comments on Objects**
```jsx
// frontend/src/components/whiteboard/CommentPanel.js

import { useThreads } from "@liveblocks/react/suspense";
import { Composer, Thread } from "@liveblocks/react-ui";
import "@liveblocks/react-ui/styles.css";

function CommentPanel({ selectedObjectId }) {
  const { threads } = useThreads({ 
    query: { 
      metadata: { 
        objectId: selectedObjectId 
      } 
    } 
  });
  
  return (
    <aside className="comment-panel">
      <h3>Comments</h3>
      
      {threads.map((thread) => (
        <Thread key={thread.id} thread={thread} />
      ))}
      
      <Composer 
        metadata={{ 
          objectId: selectedObjectId,
          objectType: 'recipe' // or 'meal_plan', 'note', etc.
        }} 
      />
    </aside>
  );
}
```

### **Installation**
```bash
# Backend
pip install liveblocks

# Frontend
npm install @liveblocks/client @liveblocks/react @liveblocks/react-ui
```

### **Environment Variables**
```bash
# .env
LIVEBLOCKS_SECRET_KEY=sk_prod_xxxxxxxxxxxxx
```

### **Cost Tracking**
- Free: 0-100 MAU (Monthly Active Users)
- Starter: $249/mo for 10,000 MAU
- Track usage in Liveblocks dashboard

---

## 💬 2. Stream Chat Integration

### **Purpose**
- Household message board
- Direct messages between members
- Real-time messaging
- Push notifications

### **Setup**

#### **Backend: Auth Endpoint**
```python
# app/api/v2/stream_chat.py

from flask import Blueprint, request, jsonify
from stream_chat import StreamChat
import os

stream_bp = Blueprint('stream_chat', __name__)
stream_client = StreamChat(
    api_key=os.getenv('STREAM_API_KEY'),
    api_secret=os.getenv('STREAM_API_SECRET')
)

@stream_bp.route('/auth', methods=['POST'])
@require_auth
def stream_chat_auth():
    """Generate Stream Chat token for authenticated user"""
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)
    
    # Create/update user in Stream Chat
    stream_client.upsert_user({
        'id': str(user_id),
        'name': user.name,
        'image': user.avatar_url,
        'role': 'user'
    })
    
    # Generate token
    token = stream_client.create_token(str(user_id))
    
    return jsonify({
        'token': token,
        'api_key': os.getenv('STREAM_API_KEY'),
        'user_id': str(user_id)
    })

@stream_bp.route('/household/<int:household_id>/channel', methods=['POST'])
@require_auth
def create_household_channel(household_id):
    """Create or get household channel"""
    user_id = get_jwt_identity()
    
    # Verify user is in household
    if not is_household_member(user_id, household_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all household members
    members = get_household_member_ids(household_id)
    
    # Create channel
    channel = stream_client.channel(
        'messaging',
        f'household-{household_id}',
        {
            'name': f'Household {household_id}',
            'members': [str(m) for m in members]
        }
    )
    channel.create(str(user_id))
    
    return jsonify({'channel_id': channel.id})
```

#### **Frontend: Chat Setup**
```jsx
// frontend/src/components/HouseholdChat.js

import { StreamChat } from 'stream-chat';
import { Chat, Channel, ChannelHeader, MessageList, MessageInput } from 'stream-chat-react';
import 'stream-chat-react/dist/css/index.css';

function HouseholdChat({ householdId }) {
  const [chatClient, setChatClient] = useState(null);
  const [channel, setChannel] = useState(null);
  
  useEffect(() => {
    async function initChat() {
      // Get auth token from backend
      const { data } = await fetch('/api/v2/stream-chat/auth', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` }
      }).then(r => r.json());
      
      // Initialize Stream Chat client
      const client = StreamChat.getInstance(data.api_key);
      await client.connectUser(
        { id: data.user_id },
        data.token
      );
      
      // Get household channel
      const channel = client.channel('messaging', `household-${householdId}`);
      await channel.watch();
      
      setChatClient(client);
      setChannel(channel);
    }
    
    initChat();
    
    return () => {
      chatClient?.disconnectUser();
    };
  }, [householdId]);
  
  if (!chatClient || !channel) return <div>Loading chat...</div>;
  
  return (
    <Chat client={chatClient}>
      <Channel channel={channel}>
        <ChannelHeader />
        <MessageList />
        <MessageInput />
      </Channel>
    </Chat>
  );
}
```

#### **Frontend: Floating Chat Button**
```jsx
// frontend/src/components/HouseholdChatButton.js

function HouseholdChatButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  
  return (
    <>
      <button 
        className="floating-chat-button"
        onClick={() => setIsOpen(true)}
      >
        💬 Chat {unreadCount > 0 && `(${unreadCount})`}
      </button>
      
      {isOpen && (
        <Modal onClose={() => setIsOpen(false)}>
          <HouseholdChat householdId={currentHouseholdId} />
        </Modal>
      )}
    </>
  );
}
```

### **Installation**
```bash
# Backend
pip install stream-chat

# Frontend
npm install stream-chat stream-chat-react
```

### **Environment Variables**
```bash
# .env
STREAM_API_KEY=xxxxxxxxxxxxx
STREAM_API_SECRET=xxxxxxxxxxxxx
```

### **Cost Tracking**
- Free: 0-25 MAU
- Startup: $99/mo for 100 MAU
- Track usage in Stream Dashboard

---

## ✏️ 3. Tiptap Integration

### **Purpose**
- Rich text editor for note blocks
- Markdown support
- Auto-save

### **Setup**

```jsx
// frontend/src/components/whiteboard/blocks/NoteBlock.js

import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'

function NoteBlock({ noteId, initialContent, onSave }) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: 'Start typing...'
      })
    ],
    content: initialContent,
    onUpdate: ({ editor }) => {
      // Auto-save after 500ms of no typing
      debounce(() => {
        onSave(noteId, editor.getHTML());
      }, 500)();
    }
  });
  
  return (
    <div className="note-block">
      <EditorContent editor={editor} />
    </div>
  );
}
```

### **Installation**
```bash
npm install @tiptap/react @tiptap/starter-kit @tiptap/extension-placeholder
```

### **Custom Styling**
```css
/* frontend/src/styles/tiptap.css */

.ProseMirror {
  padding: 1rem;
  min-height: 150px;
  font-family: 'Inter', sans-serif;
}

.ProseMirror p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  color: #adb5bd;
  pointer-events: none;
  height: 0;
}

.ProseMirror:focus {
  outline: none;
  border: 2px solid #FF6B6B;
}
```

---

## 🎨 4. React Color Integration

### **Purpose**
- Color picker for note blocks
- Simple, accessible UI

### **Setup**

```jsx
// frontend/src/components/whiteboard/blocks/NoteColorPicker.js

import { SketchPicker } from 'react-color';

function NoteColorPicker({ color, onChange }) {
  const presetColors = [
    '#FFF475', // Yellow (sticky note)
    '#AEC8FD', // Blue
    '#B4F8C8', // Green
    '#FFC6D9', // Pink
    '#FFE5B4', // Peach
    '#E0BBE4'  // Lavender
  ];
  
  return (
    <SketchPicker
      color={color}
      onChange={(newColor) => onChange(newColor.hex)}
      presetColors={presetColors}
      disableAlpha
    />
  );
}
```

### **Installation**
```bash
npm install react-color
```

---

## 📊 Cost Summary

### **Monthly Costs by User Scale**

| Users | Liveblocks | Stream Chat | Total | Notes |
|-------|-----------|-------------|-------|-------|
| 0-25 | $0 | $0 | **$0** | Both free tiers |
| 26-100 | $0 | $99 | **$99** | Stream paid, Liveblocks free |
| 101-1,000 | $249 | $99 | **$348** | Both paid |
| 1,001-10,000 | $249 | $249 | **$498** | Stream scales up |

**Break-even Analysis:**
- At 100 users paying $9.99/mo = $999/mo revenue
- Third-party costs: $348/mo
- Profit margin: 65% ($651/mo)

---

## 🚀 Implementation Timeline

### **Week 9: Backend Setup**
- ✅ Liveblocks auth endpoint
- ✅ Stream Chat auth endpoint
- ✅ Environment variables configured

### **Week 10: Channel Setup**
- ✅ Auto-create Liveblocks rooms
- ✅ Auto-create Stream Chat channels
- ✅ Member management

### **Week 11: Frontend Integration**
- ✅ Liveblocks provider setup
- ✅ Stream Chat client setup
- ✅ Real-time cursors
- ✅ Comment UI
- ✅ Chat UI

### **Week 12-13: Polish**
- ✅ Custom theming
- ✅ Notification system
- ✅ Activity feed
- ✅ Error handling

---

## 🔒 Security Considerations

### **Liveblocks Security**
```python
# Only allow access to whiteboards user is member of
def user_has_whiteboard_access(user_id, whiteboard_id):
    whiteboard = get_whiteboard(whiteboard_id)
    household = whiteboard.household
    return is_household_member(user_id, household.id)
```

### **Stream Chat Security**
```python
# Only add household members to channel
def get_household_member_ids(household_id):
    return [m.user_id for m in Household.query.get(household_id).members]
```

### **Rate Limiting**
```python
# Limit token generation to prevent abuse
@limiter.limit("10 per minute")
@liveblocks_bp.route('/auth', methods=['POST'])
def liveblocks_auth():
    ...
```

---

## 📈 Monitoring & Analytics

### **Liveblocks Dashboard**
- Track MAU (Monthly Active Users)
- Monitor room activity
- View comment volume
- Check API usage

### **Stream Chat Dashboard**
- Track MAU
- Monitor message volume
- View channel activity
- Check webhook delivery

### **Custom Analytics**
```python
# Log third-party usage
@app.after_request
def log_third_party_usage(response):
    if '/liveblocks/auth' in request.path:
        log_metric('liveblocks.auth', user_id)
    if '/stream-chat/auth' in request.path:
        log_metric('stream_chat.auth', user_id)
    return response
```

---

## 🐛 Troubleshooting

### **Common Issues**

#### **Liveblocks: "Unauthorized" errors**
```javascript
// Check auth endpoint is being called
console.log('Calling Liveblocks auth:', authEndpoint);

// Verify token format
const token = await fetch(authEndpoint).then(r => r.json());
console.log('Token received:', token);
```

#### **Stream Chat: Messages not appearing**
```javascript
// Check channel connection
channel.on('message.new', (event) => {
  console.log('New message:', event.message);
});

// Verify user is connected
console.log('Connected user:', chatClient.user);
```

#### **Tiptap: Editor not saving**
```javascript
// Add debug logging
onUpdate: ({ editor }) => {
  console.log('Content changed:', editor.getHTML());
  debouncedSave(editor.getHTML());
}
```

---

## 📚 Documentation Links

- **Liveblocks**: https://liveblocks.io/docs
- **Stream Chat**: https://getstream.io/chat/docs/
- **Tiptap**: https://tiptap.dev/
- **React Color**: https://casesandberg.github.io/react-color/

---

## ✅ Checklist for Launch

### **Backend**
- [ ] Liveblocks auth endpoint deployed
- [ ] Stream Chat auth endpoint deployed
- [ ] Environment variables set
- [ ] Rate limiting configured
- [ ] Error handling tested

### **Frontend**
- [ ] Liveblocks provider configured
- [ ] Stream Chat client configured
- [ ] Tiptap editor working
- [ ] React Color picker working
- [ ] Custom theming applied
- [ ] Error boundaries added

### **Testing**
- [ ] Multi-user collaboration tested
- [ ] Comments system tested
- [ ] Messaging system tested
- [ ] Mobile compatibility verified
- [ ] Load testing completed

### **Monitoring**
- [ ] Usage analytics configured
- [ ] Cost tracking dashboard
- [ ] Alert thresholds set
- [ ] Backup plan if free tier exceeded

---

**Status**: Ready for implementation  
**Risk Level**: LOW (battle-tested third-party services)  
**Time to Launch**: 3 weeks (Weeks 9-11)
