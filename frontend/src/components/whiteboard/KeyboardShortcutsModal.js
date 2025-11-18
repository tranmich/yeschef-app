/**
 * Keyboard Shortcuts Modal
 * Shows all available keyboard shortcuts
 */

import React from 'react';
import './KeyboardShortcutsModal.css';

const KeyboardShortcutsModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const shortcuts = [
    {
      category: 'General',
      items: [
        { keys: ['Ctrl/Cmd', 'S'], description: 'Save whiteboard' },
        { keys: ['Escape'], description: 'Close panels / Clear selection' },
        { keys: ['Ctrl/Cmd', 'A'], description: 'Select all cards' },
      ]
    },
    {
      category: 'Creating',
      items: [
        { keys: ['Ctrl/Cmd', 'R'], description: 'Toggle recipe picker' },
        { keys: ['Ctrl/Cmd', 'M'], description: 'Create new note' },
        { keys: ['Ctrl/Cmd', 'D'], description: 'Create day box' },
      ]
    },
    {
      category: 'Navigation',
      items: [
        { keys: ['Ctrl/Cmd', 'K'], description: 'Toggle tag filter' },
        { keys: ['Delete'], description: 'Delete selected items' },
      ]
    },
    {
      category: 'Canvas',
      items: [
        { keys: ['Scroll'], description: 'Zoom in/out' },
        { keys: ['Click + Drag'], description: 'Pan canvas' },
        { keys: ['Drag card'], description: 'Move items' },
      ]
    }
  ];

  return (
    <>
      <div className="shortcuts-backdrop" onClick={onClose} />
      <div className="shortcuts-modal">
        <div className="shortcuts-header">
          <h2>⌨️ Keyboard Shortcuts</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        <div className="shortcuts-content">
          {shortcuts.map((section) => (
            <div key={section.category} className="shortcut-section">
              <h3>{section.category}</h3>
              <div className="shortcut-list">
                {section.items.map((item, index) => (
                  <div key={index} className="shortcut-item">
                    <div className="shortcut-keys">
                      {item.keys.map((key, i) => (
                        <React.Fragment key={i}>
                          <kbd className="key">{key}</kbd>
                          {i < item.keys.length - 1 && <span className="plus">+</span>}
                        </React.Fragment>
                      ))}
                    </div>
                    <div className="shortcut-description">{item.description}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="shortcuts-footer">
          <p>💡 Tip: Hover over buttons to see their shortcuts</p>
        </div>
      </div>
    </>
  );
};

export default KeyboardShortcutsModal;
