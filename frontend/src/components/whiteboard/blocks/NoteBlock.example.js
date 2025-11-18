/**
 * NoteBlock Usage Example
 * 
 * This file demonstrates how to integrate NoteBlock into React Flow canvas
 * and connect it to the backend API for auto-saving.
 */

import React, { useCallback } from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import NoteBlock from './NoteBlock';
import 'reactflow/dist/style.css';

// ============================================
// Example 1: Basic NoteBlock Integration
// ============================================

const nodeTypes = {
  note: NoteBlock,
};

function WhiteboardExample() {
  // Sample note node data
  const initialNodes = [
    {
      id: 'note-1',
      type: 'note',
      position: { x: 100, y: 100 },
      data: {
        content: '<p>Buy extra avocados 🥑</p>',
        backgroundColor: '#fef3c7', // Yellow
        fontSize: '14px',
        onSave: async (noteData) => {
          console.log('Saving note:', noteData);
          // API call here
          await saveNoteToBackend(noteData);
        },
      },
      style: {
        width: 300,
        height: 250,
      },
    },
  ];

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={initialNodes}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

// ============================================
// Example 2: API Integration with Auto-Save
// ============================================

async function saveNoteToBackend(noteData) {
  const { id, content, backgroundColor, fontSize } = noteData;
  
  try {
    const response = await fetch(`/api/v2/whiteboards/objects/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({
        content: {
          type: 'note',
          html: content,  // Tiptap HTML content
          backgroundColor,
          fontSize,
        },
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to save note');
    }

    const data = await response.json();
    console.log('Note saved successfully:', data);
    return data;
  } catch (error) {
    console.error('Error saving note:', error);
    throw error;
  }
}

// ============================================
// Example 3: Creating New Note via API
// ============================================

async function createNewNote(whiteboardId, position) {
  try {
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

    if (!response.ok) {
      throw new Error('Failed to create note');
    }

    const data = await response.json();
    console.log('Note created:', data);
    return data;
  } catch (error) {
    console.error('Error creating note:', error);
    throw error;
  }
}

// ============================================
// Example 4: Complete Whiteboard Integration
// ============================================

function WhiteboardWithNotes() {
  const [nodes, setNodes] = React.useState([]);

  // Fetch notes from backend
  React.useEffect(() => {
    async function loadWhiteboard() {
      try {
        const response = await fetch('/api/v2/whiteboards/123');
        const data = await response.json();
        
        // Transform backend data to React Flow nodes
        const noteNodes = data.data.objects
          .filter(obj => obj.object_type === 'note')
          .map(obj => ({
            id: `note-${obj.id}`,
            type: 'note',
            position: { x: obj.position.x, y: obj.position.y },
            data: {
              content: obj.content.html,
              backgroundColor: obj.content.backgroundColor,
              fontSize: obj.content.fontSize,
              onSave: async (noteData) => {
                await saveNoteToBackend({ ...noteData, id: obj.id });
              },
            },
            style: {
              width: obj.position.width,
              height: obj.position.height,
            },
          }));

        setNodes(noteNodes);
      } catch (error) {
        console.error('Failed to load whiteboard:', error);
      }
    }

    loadWhiteboard();
  }, []);

  // Handle adding new note
  const handleAddNote = useCallback(async () => {
    const newNote = await createNewNote(123, { x: 200, y: 200 });
    
    setNodes(prev => [
      ...prev,
      {
        id: `note-${newNote.data.object.id}`,
        type: 'note',
        position: { x: 200, y: 200 },
        data: {
          content: '<p>New note...</p>',
          backgroundColor: '#fef3c7',
          fontSize: '14px',
          onSave: async (noteData) => {
            await saveNoteToBackend({ ...noteData, id: newNote.data.object.id });
          },
        },
        style: {
          width: 300,
          height: 250,
        },
      },
    ]);
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <button
        onClick={handleAddNote}
        style={{
          position: 'absolute',
          top: 20,
          right: 20,
          zIndex: 1000,
          padding: '10px 20px',
          background: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
        }}
      >
        + Add Note
      </button>
      
      <ReactFlow
        nodes={nodes}
        nodeTypes={nodeTypes}
        onNodesChange={(changes) => {
          // Handle position changes, deletions, etc.
          console.log('Node changes:', changes);
        }}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}

// ============================================
// Example 5: Backend Data Structure
// ============================================

/**
 * PostgreSQL Database Structure:
 * 
 * whiteboard_objects table:
 * {
 *   id: 1001,
 *   whiteboard_id: 123,
 *   object_type: 'note',
 *   position: {
 *     x: 250,
 *     y: 300,
 *     width: 300,
 *     height: 250,
 *     z_index: 1
 *   },
 *   content: {
 *     type: 'note',
 *     html: '<p>Buy extra <strong>avocados</strong> 🥑</p><ul><li>Hass avocados</li><li>3-4 pieces</li></ul>',
 *     backgroundColor: '#fef3c7',
 *     fontSize: '14px'
 *   },
 *   created_by: 789,
 *   created_at: '2025-11-06T10:00:00Z'
 * }
 */

// ============================================
// Example 6: Color Presets Reference
// ============================================

const COLOR_PRESETS = [
  { name: 'Yellow', value: '#fef3c7' },  // Sticky note classic
  { name: 'Blue', value: '#dbeafe' },    // Sky blue
  { name: 'Green', value: '#d1fae5' },   // Mint green
  { name: 'Pink', value: '#fce7f3' },    // Soft pink
  { name: 'Purple', value: '#e9d5ff' },  // Lavender
  { name: 'Orange', value: '#fed7aa' },  // Peach
];

// ============================================
// Example 7: Font Size Options
// ============================================

const FONT_SIZES = [
  { label: 'Small', value: '12px' },
  { label: 'Medium', value: '14px' },   // Default
  { label: 'Large', value: '16px' },
  { label: 'X-Large', value: '18px' },
];

// ============================================
// Example 8: Keyboard Shortcuts
// ============================================

/**
 * Tiptap Editor Keyboard Shortcuts:
 * - Ctrl+B / Cmd+B: Bold
 * - Ctrl+I / Cmd+I: Italic
 * - Ctrl+Shift+8: Bullet list
 * - Ctrl+Z / Cmd+Z: Undo
 * - Ctrl+Shift+Z / Cmd+Shift+Z: Redo
 */

export default WhiteboardExample;
