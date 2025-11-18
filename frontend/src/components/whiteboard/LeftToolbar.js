/**
 * Left Toolbar Component
 * ======================
 * Minimal collapsible sidebar with essential whiteboard tools
 * Inspired by Figma/Miro left toolbars
 * 
 * Features:
 * - Icon-only by default (60px wide)
 * - Expands on hover to show labels (240px wide)
 * - Add Recipe, Add Note, Add Day Box, etc.
 * - Keyboard shortcuts hint at bottom
 */

import React, { useState } from 'react';
import Icon from '../Icon';
import './LeftToolbar.css';

const LeftToolbar = ({ 
  onAddRecipe, 
  onAddNote, 
  onAddDayBox,
  onAddActivityFeed,
  onToggleShortcuts,
  onToggleTags,
  isTagSidebarOpen,
  selectedTags = []
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const tools = [
    {
      id: 'add-recipe',
      icon: 'chef',
      label: 'Add Recipe',
      shortcut: 'Cmd+R',
      onClick: onAddRecipe,
      color: 'primary'
    },
    {
      id: 'add-note',
      icon: 'note',
      label: 'Add Note',
      shortcut: 'Cmd+M',
      onClick: onAddNote,
      color: 'warning'
    },
    {
      id: 'add-daybox',
      icon: 'calendar',
      label: 'Add Day Box',
      shortcut: 'Cmd+D',
      onClick: onAddDayBox,
      color: 'info'
    },
    {
      id: 'add-activity',
      icon: 'bell',
      label: 'Activity Feed',
      shortcut: '',
      onClick: onAddActivityFeed,
      color: 'success'
    },
    {
      id: 'divider-1',
      type: 'divider'
    },
    {
      id: 'toggle-tags',
      icon: 'tag',
      label: 'Filter Tags',
      shortcut: 'Cmd+K',
      onClick: onToggleTags,
      color: 'secondary',
      isActive: isTagSidebarOpen,
      badge: selectedTags.length > 0 ? selectedTags.length : null
    }
  ];

  return (
    <div 
      className={`left-toolbar ${isExpanded ? 'expanded' : 'collapsed'}`}
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      <div className="left-toolbar-content">
        {/* Tools */}
        <div className="toolbar-tools">
          {tools.map(tool => {
            if (tool.type === 'divider') {
              return <div key={tool.id} className="toolbar-divider" />;
            }
            
            return (
              <button
                key={tool.id}
                className={`toolbar-button ${tool.color} ${tool.isActive ? 'active' : ''}`}
                onClick={tool.onClick}
                title={isExpanded ? '' : `${tool.label} ${tool.shortcut ? `(${tool.shortcut})` : ''}`}
              >
                <span className="tool-icon">
                  <Icon name={tool.icon} size={24} />
                </span>
                {isExpanded && (
                  <span className="tool-label">{tool.label}</span>
                )}
                {isExpanded && tool.shortcut && (
                  <span className="tool-shortcut">{tool.shortcut}</span>
                )}
                {tool.badge && (
                  <span className="tool-badge">{tool.badge}</span>
                )}
              </button>
            );
          })}
        </div>

        {/* Spacer */}
        <div className="toolbar-spacer"></div>

        {/* Bottom Actions */}
        <div className="toolbar-bottom">
          <button
            className="toolbar-button secondary"
            onClick={onToggleShortcuts}
            title={isExpanded ? '' : 'Keyboard Shortcuts (?)'}
          >
            <span className="tool-icon">
              <Icon name="help" size={24} />
            </span>
            {isExpanded && (
              <span className="tool-label">Shortcuts</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LeftToolbar;
