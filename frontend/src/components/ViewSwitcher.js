import React from 'react';
import './ViewSwitcher.css';

const ViewSwitcher = ({ currentView, onViewChange }) => {
  const views = [
    { id: 'gallery', label: 'Gallery', description: 'Visual grid' },
    { id: 'table', label: 'Table', description: 'Spreadsheet' }
  ];

  return (
    <div className="view-switcher">
      <div className="view-switcher-label">View:</div>
      <div className="view-buttons">
        {views.map(view => (
          <button
            key={view.id}
            className={`view-btn ${currentView === view.id ? 'active' : ''}`}
            onClick={() => onViewChange(view.id)}
            title={view.description}
          >
            <span className="view-label">{view.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ViewSwitcher;
