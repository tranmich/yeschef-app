import React, { useState } from 'react';
import './SearchFilterBar.css';

const SearchFilterBar = ({ onSearch, onFilterChange, totalRecipes, currentPage, totalPages, onPageChange }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState({
    difficulty: [],
    time: [],
    mealType: []
  });
  const [showFilters, setShowFilters] = useState(false);

  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    onSearch(query);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    onSearch('');
  };

  const toggleFilter = (category, value) => {
    setActiveFilters(prev => {
      const newFilters = { ...prev };
      const categoryFilters = [...prev[category]];
      
      if (categoryFilters.includes(value)) {
        newFilters[category] = categoryFilters.filter(f => f !== value);
      } else {
        categoryFilters.push(value);
        newFilters[category] = categoryFilters;
      }
      
      onFilterChange(newFilters);
      return newFilters;
    });
  };

  const clearAllFilters = () => {
    setActiveFilters({
      difficulty: [],
      time: [],
      mealType: []
    });
    onFilterChange({
      difficulty: [],
      time: [],
      mealType: []
    });
  };

  const hasActiveFilters = 
    activeFilters.difficulty.length > 0 || 
    activeFilters.time.length > 0 || 
    activeFilters.mealType.length > 0;

  // Generate page numbers with ellipsis
  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 7; // Show max 7 page buttons (4 numbers + first + last + ellipsis)
    
    if (totalPages <= maxVisible) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);
      
      // Show 4 pages around current page
      if (currentPage > 4) {
        pages.push('...');
      }
      
      // Show pages around current page (show 4 numbers: current-1, current, current+1, current+2)
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 2);
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      
      if (currentPage < totalPages - 3) {
        pages.push('...');
      }
      
      // Always show last page
      pages.push(totalPages);
    }
    
    return pages;
  };

  return (
    <div className="search-filter-bar">
      {/* Search Bar - Always Visible */}
      <div className="search-bar-container">
        <div className="search-input-wrapper">
          <input
            type="text"
            className="search-input"
            placeholder="Search recipes by name, ingredient, or tag..."
            value={searchQuery}
            onChange={handleSearchChange}
          />
          {searchQuery && (
            <button className="clear-search-btn" onClick={handleClearSearch}>
              Clear
            </button>
          )}
        </div>
        <button 
          className={`filter-toggle-btn ${showFilters ? 'active' : ''}`}
          onClick={() => setShowFilters(!showFilters)}
        >
          Filters {hasActiveFilters && `(${activeFilters.difficulty.length + activeFilters.time.length + activeFilters.mealType.length})`}
        </button>
      </div>

      {/* Quick Filter Chips - Toggleable */}
      {showFilters && (
        <div className="quick-filters">
          <div className="filter-group">
            <span className="filter-group-label">Time:</span>
            <button
              className={`filter-chip ${activeFilters.time.includes('quick') ? 'active' : ''}`}
              onClick={() => toggleFilter('time', 'quick')}
            >
              Quick (&lt; 30 min)
            </button>
            <button
              className={`filter-chip ${activeFilters.time.includes('medium') ? 'active' : ''}`}
              onClick={() => toggleFilter('time', 'medium')}
            >
              30-60 min
            </button>
            <button
              className={`filter-chip ${activeFilters.time.includes('long') ? 'active' : ''}`}
              onClick={() => toggleFilter('time', 'long')}
            >
              &gt; 60 min
            </button>
          </div>

          <div className="filter-group">
            <span className="filter-group-label">Difficulty:</span>
            <button
              className={`filter-chip ${activeFilters.difficulty.includes('easy') ? 'active' : ''}`}
              onClick={() => toggleFilter('difficulty', 'easy')}
            >
              Easy
            </button>
            <button
              className={`filter-chip ${activeFilters.difficulty.includes('medium') ? 'active' : ''}`}
              onClick={() => toggleFilter('difficulty', 'medium')}
            >
              Medium
            </button>
            <button
              className={`filter-chip ${activeFilters.difficulty.includes('hard') ? 'active' : ''}`}
              onClick={() => toggleFilter('difficulty', 'hard')}
            >
              Hard
            </button>
          </div>

          <div className="filter-group">
            <span className="filter-group-label">Meal:</span>
            <button
              className={`filter-chip ${activeFilters.mealType.includes('breakfast') ? 'active' : ''}`}
              onClick={() => toggleFilter('mealType', 'breakfast')}
            >
              Breakfast
            </button>
            <button
              className={`filter-chip ${activeFilters.mealType.includes('lunch') ? 'active' : ''}`}
              onClick={() => toggleFilter('mealType', 'lunch')}
            >
              Lunch
            </button>
            <button
              className={`filter-chip ${activeFilters.mealType.includes('dinner') ? 'active' : ''}`}
              onClick={() => toggleFilter('mealType', 'dinner')}
            >
              Dinner
            </button>
            <button
              className={`filter-chip ${activeFilters.mealType.includes('snack') ? 'active' : ''}`}
              onClick={() => toggleFilter('mealType', 'snack')}
            >
              Snack
            </button>
            <button
              className={`filter-chip ${activeFilters.mealType.includes('dessert') ? 'active' : ''}`}
              onClick={() => toggleFilter('mealType', 'dessert')}
            >
              Dessert
            </button>
          </div>

          {hasActiveFilters && (
            <button className="clear-filters-btn" onClick={clearAllFilters}>
              Clear All Filters
            </button>
          )}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination-controls">
          <button
            className="pagination-btn"
            onClick={() => onPageChange(1)}
            disabled={currentPage === 1}
            title="First page"
          >
            First
          </button>
          
          <button
            className="pagination-btn"
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Previous
          </button>
          
          <div className="pagination-pages">
            {getPageNumbers().map((page, index) => (
              page === '...' ? (
                <span key={`ellipsis-${index}`} className="pagination-ellipsis">...</span>
              ) : (
                <button
                  key={page}
                  className={`pagination-page ${currentPage === page ? 'active' : ''}`}
                  onClick={() => onPageChange(page)}
                >
                  {page}
                </button>
              )
            ))}
          </div>
          
          <button
            className="pagination-btn"
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
          
          <button
            className="pagination-btn"
            onClick={() => onPageChange(totalPages)}
            disabled={currentPage === totalPages}
            title="Last page"
          >
            Last
          </button>
        </div>
      )}
    </div>
  );
};

export default SearchFilterBar;
