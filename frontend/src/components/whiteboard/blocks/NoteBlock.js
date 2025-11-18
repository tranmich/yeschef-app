import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import Placeholder from '@tiptap/extension-placeholder';
import ResizableImage from './ResizableImage';
import './NoteBlock.css';

const MAX_CHARS = 5000;

// 12 Pastel color options (light hues for legibility)
const COLOR_OPTIONS = [
  { name: 'White', value: '#FFFFFF' },
  { name: 'Soft Yellow', value: '#FEF3C7' },
  { name: 'Peach', value: '#FED7AA' },
  { name: 'Light Pink', value: '#FCE7F3' },
  { name: 'Lavender', value: '#E9D5FF' },
  { name: 'Sky Blue', value: '#DBEAFE' },
  { name: 'Mint', value: '#D1FAE5' },
  { name: 'Sage', value: '#D1F4E0' },
  { name: 'Pale Green', value: '#E0F2D9' },
  { name: 'Light Coral', value: '#FFE4E1' },
  { name: 'Cream', value: '#FAF3DD' },
  { name: 'Light Gray', value: '#F3F4F6' },
];

const NoteBlock = ({ id, data, selected }) => {
  const [content, setContent] = useState(data.content || '');
  const [name, setName] = useState(data.name || 'Note');
  const [isEditingName, setIsEditingName] = useState(false);
  const [backgroundColor, setBackgroundColor] = useState(data.backgroundColor || '#FEF3C7');
  const [fontSize, setFontSize] = useState(data.fontSize || '18px'); // Increased from 14px to 18px for better readability
  const [charCount, setCharCount] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [showFontSizePicker, setShowFontSizePicker] = useState(false);
  const fileInputRef = useRef(null);
  const colorPickerRef = useRef(null);
  const fontSizePickerRef = useRef(null);
  const nameInputRef = useRef(null);

  const FONT_SIZES = [
    { label: 'Small', value: '18px' },      // Increased from 12px
    { label: 'Medium', value: '22px' },     // Increased from 14px (now default)
    { label: 'Large', value: '26px' },      // Increased from 16px
    { label: 'X-Large', value: '32px' },    // Increased from 18px
  ];

  // Tiptap editor setup
  const editor = useEditor({
    extensions: [
      StarterKit,
      ResizableImage.configure({
        inline: false,
        allowBase64: true,
        HTMLAttributes: {
          class: 'note-image',
        },
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'note-link',
          target: '_blank',
          rel: 'noopener noreferrer',
        },
      }),
      Placeholder.configure({
        placeholder: 'Start typing your note...',
      }),
    ],
    content: content,
    editorProps: {
      attributes: {
        class: 'note-editor',
        style: `font-size: ${fontSize}`,
      },
      handleDrop: (view, event, slice, moved) => {
        if (!moved && event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0]) {
          const file = event.dataTransfer.files[0];
          if (file.type.startsWith('image/')) {
            event.preventDefault();
            handleImageUpload(file);
            return true;
          }
        }
        return false;
      },
      handlePaste: (view, event, slice) => {
        const items = event.clipboardData?.items;
        if (items) {
          for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
              event.preventDefault();
              const file = items[i].getAsFile();
              if (file) {
                handleImageUpload(file);
                return true;
              }
            }
          }
        }
        return false;
      },
    },
    onUpdate: ({ editor }) => {
      const text = editor.getText();
      const newCharCount = text.length;
      
      if (newCharCount > MAX_CHARS) {
        editor.commands.setContent(content);
        return;
      }
      
      setCharCount(newCharCount);
      const newContent = editor.getHTML();
      setContent(newContent);
      
      // Auto-save after content changes (including image resizes)
      // Debounced via the onBlur handler, but we'll also trigger a delayed save
      if (data.onSave) {
        const saveTimeout = setTimeout(() => {
          data.onSave({
            id,
            content: newContent,
            backgroundColor,
            fontSize,
          });
        }, 1000); // Save 1 second after last change
        
        return () => clearTimeout(saveTimeout);
      }
    },
    onBlur: () => {
      handleAutoSave();
    },
  });

  // Update editor font size when changed
  useEffect(() => {
    if (editor && editor.view && editor.view.dom) {
      editor.view.dom.style.fontSize = fontSize;
      // Update all content to use new font size
      const editorElement = editor.view.dom.querySelector('.ProseMirror');
      if (editorElement) {
        editorElement.style.fontSize = fontSize;
        // Also update all paragraph elements to ensure override
        const paragraphs = editorElement.querySelectorAll('p, h1, h2, h3, li');
        paragraphs.forEach(p => {
          p.style.fontSize = 'inherit'; // Inherit from parent
        });
      }
    }
  }, [fontSize, editor]);

  // Calculate initial character count
  useEffect(() => {
    if (editor) {
      const text = editor.getText();
      setCharCount(text.length);
    }
  }, [editor]);

  // Sync name from data prop
  useEffect(() => {
    setName(data.name || 'Note');
  }, [data.name]);

  // Focus name input when editing
  useEffect(() => {
    if (isEditingName && nameInputRef.current) {
      nameInputRef.current.focus();
      nameInputRef.current.select();
    }
  }, [isEditingName]);

  // Name editing handlers
  const handleNameClick = () => {
    setIsEditingName(true);
  };

  const handleNameBlur = () => {
    setIsEditingName(false);
    if (name !== data.name) {
      handleAutoSave();
    }
  };

  const handleNameKeyDown = (e) => {
    e.stopPropagation();
    
    if (e.key === 'Enter') {
      setIsEditingName(false);
      handleAutoSave();
    } else if (e.key === 'Escape') {
      setName(data.name || 'Note');
      setIsEditingName(false);
    }
  };

  // Auto-save function
  const handleAutoSave = useCallback(async () => {
    if (!data.onSave) return;
    
    setIsSaving(true);
    
    try {
      console.log('💾 Auto-saving note content:', {
        name,
        contentLength: content.length,
        hasImages: content.includes('<img'),
        preview: content.substring(0, 200) + '...'
      });
      
      await data.onSave({
        id,
        name,
        content,
        backgroundColor,
        fontSize,
      });
      
      console.log('✅ Note saved successfully');
    } catch (error) {
      console.error('Failed to save note:', error);
    } finally {
      setTimeout(() => setIsSaving(false), 500);
    }
  }, [id, name, content, backgroundColor, fontSize, data]);

  // Update local state if parent changes (for initial load)
  useEffect(() => {
    if (data.backgroundColor && data.backgroundColor !== backgroundColor) {
      setBackgroundColor(data.backgroundColor);
    }
  }, [data.backgroundColor]); // Only depend on data.backgroundColor, not local state

  useEffect(() => {
    if (data.fontSize && data.fontSize !== fontSize) {
      setFontSize(data.fontSize);
    }
  }, [data.fontSize]); // Only depend on data.fontSize, not local state

  // Image upload handler
  const handleImageUpload = async (file) => {
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('Image too large. Maximum size is 5MB');
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('image', file);

      const token = localStorage.getItem('authToken'); // Fixed: was 'token', should be 'authToken'
      
      if (!token) {
        throw new Error('Not authenticated. Please log in.');
      }

      const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';
      
      console.log('🔐 Uploading image...');
      console.log('   Token:', token.substring(0, 20) + '...');
      console.log('   File:', file.name, `(${file.size} bytes)`);
      console.log('   API URL:', `${apiUrl}/api/v2/whiteboards/images/upload`);
      
      const response = await fetch(`${apiUrl}/api/v2/whiteboards/images/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      console.log('📤 Upload response:');
      console.log('   Status:', response.status);
      console.log('   Status Text:', response.statusText);
      console.log('   Headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error response body:', errorText);
        
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { error: errorText || 'Unknown error' };
        }
        
        console.error('❌ Parsed error:', errorData);
        throw new Error(errorData.message || errorData.error || `Upload failed with status ${response.status}`);
      }

      const result = await response.json();
      
      console.log('✅ Upload successful:', result);
      
      if (result.success && result.data.url) {
        const fullUrl = apiUrl + result.data.url;
        // Use setResizableImage instead of setImage
        editor?.chain().focus().setResizableImage({ 
          src: fullUrl,
          alt: file.name,
          width: result.data.width || 300,
          height: 'auto'
        }).run();
        console.log('🖼️ Image inserted:', fullUrl);
      }
    } catch (error) {
      console.error('Image upload failed:', error);
      alert(`Failed to upload image: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleImageFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleImageUpload(file);
    }
  };

  const handleColorChange = (color) => {
    setBackgroundColor(color);
    setShowColorPicker(false);
    // Trigger save with new color
    if (data.onSave) {
      data.onSave({
        id,
        content,
        backgroundColor: color,
        fontSize,
      });
    }
  };

  const handleFontSizeChange = (size) => {
    setFontSize(size);
    setShowFontSizePicker(false);
    // Trigger save with new font size
    if (data.onSave) {
      data.onSave({
        id,
        content,
        backgroundColor,
        fontSize: size,
      });
    }
  };

  const handlePhotoAttach = () => {
    fileInputRef.current?.click();
  };

  const handleDeleteNote = () => {
    if (window.confirm('Delete this note?')) {
      if (data.onDelete) {
        data.onDelete(id, data.objectId);
      }
    }
  };

  const toggleBold = () => {
    editor?.chain().focus().toggleBold().run();
  };

  const toggleItalic = () => {
    editor?.chain().focus().toggleItalic().run();
  };

  // Close color picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (colorPickerRef.current && !colorPickerRef.current.contains(event.target)) {
        setShowColorPicker(false);
      }
      if (fontSizePickerRef.current && !fontSizePickerRef.current.contains(event.target)) {
        setShowFontSizePicker(false);
      }
    };

    if (showColorPicker || showFontSizePicker) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showColorPicker, showFontSizePicker]);

  const isNearLimit = charCount >= MAX_CHARS * 0.9;
  const isAtLimit = charCount >= MAX_CHARS;

  return (
    <div className="note-block-wrapper" style={{ backgroundColor }}>
      {/* Comment badge */}
      {data.commentCount > 0 && (
        <div className="comment-badge">
          💬 {data.commentCount}
        </div>
      )}
      
      {/* Header - Drag handle + Title + Actions */}
      <div className="note-header" title="Drag to move note">
        <div className="header-left">
          {/* Comment Badge */}
          {data.commentCount > 0 && (
            <div className={`comment-badge-header ${data.hasNewComments ? 'has-new' : ''}`}>
              💬 {data.commentCount}
            </div>
          )}
          {isEditingName ? (
            <input
              ref={nameInputRef}
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onBlur={handleNameBlur}
              onKeyDown={handleNameKeyDown}
              className="name-input nodrag"
              maxLength={50}
              placeholder="Note title..."
            />
          ) : (
            <span className="note-title nodrag" onClick={handleNameClick}>
              📝 {name}
            </span>
          )}
        </div>
        <div className="header-right nodrag">
          {/* Color picker - only show when selected */}
          {selected && (
            <div className="color-picker-wrapper" ref={colorPickerRef}>
              <button
                className="header-btn color-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowColorPicker(!showColorPicker);
                }}
                title="Change color"
              >
                🎨
              </button>
              {showColorPicker && (
                <div className="color-picker-dropdown">
                  {COLOR_OPTIONS.map((color) => (
                    <button
                      key={color.value}
                      className="color-option"
                      style={{ backgroundColor: color.value }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleColorChange(color.value);
                      }}
                      title={color.name}
                    >
                      {backgroundColor === color.value && '✓'}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
          {/* Delete button */}
          <button 
            className="header-btn delete-btn"
            onClick={handleDeleteNote}
            title="Delete note"
          >
            ×
          </button>
        </div>
      </div>
      
      {/* Main note container */}
      <div 
        className="note-block noDrag"
      >
        {/* Hidden file input */}
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleImageFileSelect}
        />

        {/* Formatting Toolbar - only show when selected */}
        {selected && (
          <div className="note-toolbar">
            {/* Font size picker */}
            <div className="toolbar-group" ref={fontSizePickerRef}>
              <button 
                className="toolbar-button"
                onClick={() => setShowFontSizePicker(!showFontSizePicker)}
                title="Font size"
              >
                <span style={{ fontSize: '16px', fontWeight: 'bold' }}>A</span>
              </button>
              
              {/* Font size dropdown */}
              {showFontSizePicker && (
                <div className="font-size-dropdown">
                  {FONT_SIZES.map((size) => (
                    <button
                      key={size.value}
                      className={`font-size-option ${fontSize === size.value ? 'active' : ''}`}
                      onClick={() => handleFontSizeChange(size.value)}
                    >
                      {size.label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Bold button */}
            <button 
              className={`toolbar-button ${editor?.isActive('bold') ? 'active' : ''}`}
              onClick={toggleBold}
              title="Bold (Ctrl+B)"
            >
              <span style={{ fontWeight: 'bold', fontSize: '14px' }}>B</span>
            </button>

            {/* Italic button */}
            <button 
              className={`toolbar-button ${editor?.isActive('italic') ? 'active' : ''}`}
              onClick={toggleItalic}
              title="Italic (Ctrl+I)"
            >
              <span style={{ fontStyle: 'italic', fontSize: '14px' }}>I</span>
            </button>

            <div className="toolbar-divider"></div>

            {/* Photo attach button */}
            <button 
              className="toolbar-button"
              onClick={handlePhotoAttach}
              title="Attach photo"
            >
              📷
            </button>

            {/* Save indicators */}
            {isSaving && (
              <div className="save-indicator">
                Saving...
              </div>
            )}
            {isUploading && (
              <div className="save-indicator">
                Uploading...
              </div>
            )}
          </div>
        )}

        {/* Editor */}
        <div 
          className="note-content noDrag"
          onMouseDown={(e) => e.stopPropagation()}
          onPointerDown={(e) => e.stopPropagation()}
        >
          <EditorContent editor={editor} />
        </div>

        {/* Footer with Created By and Character Count */}
        <div className="note-footer">
          {data.createdBy && (
            <div className="created-by">
              By: {data.createdBy}
            </div>
          )}
          <div className={`char-count ${isNearLimit ? 'warning' : ''} ${isAtLimit ? 'limit' : ''}`}>
            {charCount} / {MAX_CHARS}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NoteBlock;
