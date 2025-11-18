# 📝 NoteBlock Component Documentation

**React Flow Node Component with Tiptap Rich Text Editor**

---

## 📋 Overview

The `NoteBlock` component is a fully-featured sticky note implementation for the YesChef Whiteboard system. It provides:

- ✅ **Rich text editing** via Tiptap (markdown support)
- ✅ **Color customization** with presets and color picker
- ✅ **Font size controls** (4 size options)
- ✅ **Resize handles** via React Flow
- ✅ **Auto-save on blur** with loading indicator
- ✅ **Character limit** (500 chars with visual indicator)
- ✅ **Formatting toolbar** (bold, italic, bullet lists)

---

## 🎨 Features

### **1. Tiptap Rich Text Editor**
- Markdown support (headings, lists, bold, italic)
- Clean, intuitive editing experience
- Placeholder text for empty notes
- Keyboard shortcuts (Ctrl+B, Ctrl+I, etc.)

### **2. Color Picker**
- 6 preset colors (Yellow, Blue, Green, Pink, Purple, Orange)
- Full ChromePicker for custom colors
- Real-time color preview
- Auto-save on color change

### **3. Font Size Controls**
- Small (12px)
- Medium (14px) - Default
- Large (16px)
- X-Large (18px)

### **4. Formatting Toolbar**
- **Bold** (Ctrl+B)
- *Italic* (Ctrl+I)
- Bullet lists
- Active state indicators

### **5. Character Limit**
- 500 character maximum
- Visual counter (bottom right)
- Warning at 90% (450 chars) - turns orange
- Hard limit at 100% - turns red with pulse animation

### **6. Auto-Save**
- Saves on blur (when user clicks away)
- Saves on color change
- Saves on font size change
- Visual "Saving..." indicator

### **7. Resize Handles**
- Corner drag handles (React Flow)
- Min width: 200px
- Max width: 600px
- Min height: 150px
- Max height: 800px

---

## 📦 Installation

```bash
cd frontend
npm install @tiptap/react @tiptap/starter-kit react-color @reactflow/node-resizer
```

---

## 🚀 Usage

### **Basic Integration**

```javascript
import ReactFlow from 'reactflow';
import NoteBlock from './components/whiteboard/blocks/NoteBlock';
import 'reactflow/dist/style.css';

const nodeTypes = {
  note: NoteBlock,
};

function Whiteboard() {
  const nodes = [
    {
      id: 'note-1',
      type: 'note',
      position: { x: 100, y: 100 },
      data: {
        content: '<p>Your note content here</p>',
        backgroundColor: '#fef3c7',
        fontSize: '14px',
        onSave: async (noteData) => {
          // Save to backend
          await saveNote(noteData);
        },
      },
      style: {
        width: 300,
        height: 250,
      },
    },
  ];

  return (
    <ReactFlow nodes={nodes} nodeTypes={nodeTypes} />
  );
}
```

---

## 🔌 API Integration

### **Data Structure**

**Frontend (React Flow Node):**
```javascript
{
  id: 'note-1',
  type: 'note',
  position: { x: 250, y: 300 },
  data: {
    content: '<p>Buy <strong>avocados</strong> 🥑</p>',
    backgroundColor: '#fef3c7',
    fontSize: '14px',
    onSave: handleSave,
  },
  style: {
    width: 300,
    height: 250,
  },
}
```

**Backend (PostgreSQL JSONB):**
```sql
-- whiteboard_objects table
{
  id: 1001,
  whiteboard_id: 123,
  object_type: 'note',
  position: {
    x: 250,
    y: 300,
    width: 300,
    height: 250,
    z_index: 1
  },
  content: {
    type: 'note',
    html: '<p>Buy <strong>avocados</strong> 🥑</p>',
    backgroundColor: '#fef3c7',
    fontSize: '14px'
  },
  created_by: 789,
  created_at: '2025-11-06T10:00:00Z'
}
```

### **Save Function Example**

```javascript
async function handleSave(noteData) {
  const { id, content, backgroundColor, fontSize } = noteData;
  
  const response = await fetch(`/api/v2/whiteboards/objects/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      content: {
        type: 'note',
        html: content,
        backgroundColor,
        fontSize,
      },
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to save note');
  }

  return await response.json();
}
```

### **Create New Note**

```javascript
async function createNote(whiteboardId, position) {
  const response = await fetch(`/api/v2/whiteboards/${whiteboardId}/objects`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      object_type: 'note',
      position: {
        x: position.x,
        y: position.y,
        width: 300,
        height: 250,
        z_index: 0,
      },
      content: {
        type: 'note',
        html: '<p>New note...</p>',
        backgroundColor: '#fef3c7',
        fontSize: '14px',
      },
    }),
  });

  return await response.json();
}
```

---

## 🎨 Customization

### **Color Presets**

Modify `COLOR_PRESETS` array in `NoteBlock.js`:

```javascript
const COLOR_PRESETS = [
  { name: 'Yellow', value: '#fef3c7' },
  { name: 'Blue', value: '#dbeafe' },
  { name: 'Green', value: '#d1fae5' },
  { name: 'Pink', value: '#fce7f3' },
  { name: 'Purple', value: '#e9d5ff' },
  { name: 'Orange', value: '#fed7aa' },
];
```

### **Font Sizes**

Modify `FONT_SIZES` array in `NoteBlock.js`:

```javascript
const FONT_SIZES = [
  { label: 'Small', value: '12px' },
  { label: 'Medium', value: '14px' },
  { label: 'Large', value: '16px' },
  { label: 'X-Large', value: '18px' },
];
```

### **Character Limit**

Change `MAX_CHARS` constant in `NoteBlock.js`:

```javascript
const MAX_CHARS = 500;  // Change to your desired limit
```

### **Styling**

Modify `NoteBlock.css` to customize:
- Note appearance
- Toolbar styling
- Editor font families
- Color picker popup
- Resize handles

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+B` / `Cmd+B` | Toggle bold |
| `Ctrl+I` / `Cmd+I` | Toggle italic |
| `Ctrl+Shift+8` | Toggle bullet list |
| `Ctrl+Z` / `Cmd+Z` | Undo |
| `Ctrl+Shift+Z` / `Cmd+Shift+Z` | Redo |

---

## 📱 Responsive Design

The component is responsive and adapts to different screen sizes:

- **Desktop**: Full toolbar, all features
- **Tablet**: Touch-optimized controls, larger touch targets
- **Mobile**: Scaled-down UI, essential features only

---

## 🌙 Dark Mode Support

The component includes dark mode styles via CSS media query:

```css
@media (prefers-color-scheme: dark) {
  /* Dark mode styles automatically applied */
}
```

---

## 🧪 Testing

### **Manual Testing Checklist**

- [ ] Text editing works smoothly
- [ ] Bold/italic formatting applies correctly
- [ ] Bullet lists render properly
- [ ] Color picker changes background
- [ ] Preset colors work
- [ ] Font size changes apply
- [ ] Character counter updates
- [ ] Warning appears at 450 chars
- [ ] Limit enforced at 500 chars
- [ ] Auto-save triggers on blur
- [ ] Save indicator appears
- [ ] Resize handles work in all corners
- [ ] Min/max size constraints enforced
- [ ] Component renders on mobile
- [ ] Dark mode styles apply

---

## 🐛 Troubleshooting

### **Issue: Editor not rendering**
- Ensure Tiptap packages are installed
- Check browser console for errors
- Verify `content` prop is valid HTML string

### **Issue: Auto-save not working**
- Verify `onSave` function is provided in `data` prop
- Check network tab for API errors
- Ensure authentication token is valid

### **Issue: Colors not changing**
- Check if color picker popup is visible
- Verify `backgroundColor` state is updating
- Ensure CSS styles are loaded

### **Issue: Resize not working**
- Verify `@reactflow/node-resizer` is installed
- Check if `selected` prop is true
- Ensure React Flow wrapper is properly configured

---

## 📚 Related Documentation

- [Tiptap Documentation](https://tiptap.dev/docs)
- [React Flow Documentation](https://reactflow.dev/)
- [React Color Documentation](https://casesandberg.github.io/react-color/)
- [Whiteboard Technical Architecture](../../../docs/whiteboard_feature/02_TECHNICAL_ARCHITECTURE.md)

---

## 🔄 Version History

### **v1.0.0** (November 6, 2025)
- Initial release
- Tiptap rich text editor
- Color picker with presets
- Font size controls
- Auto-save functionality
- Character limit (500)
- Resize handles

---

## 📝 License

Part of the YesChef Whiteboard System  
© 2025 YesChef

---

## 🤝 Contributing

When modifying NoteBlock:

1. Update this README with any new features
2. Add tests for new functionality
3. Update `NoteBlock.example.js` with examples
4. Ensure backward compatibility with existing notes
5. Test on all screen sizes (desktop, tablet, mobile)

---

## 💡 Future Enhancements

Potential features for future versions:

- [ ] Headings support in toolbar
- [ ] Strike-through formatting
- [ ] Text highlight colors
- [ ] Markdown import/export
- [ ] Collaborative editing (Liveblocks)
- [ ] Voice-to-text input
- [ ] Image embedding
- [ ] Link support
- [ ] Emoji picker
- [ ] Tags/categories
- [ ] Note templates
- [ ] Print styling

---

**Questions?** Contact the YesChef dev team or check the [Implementation Plan](../../../docs/whiteboard_feature/03_IMPLEMENTATION_PLAN.md).
