/**
 * TagFilterSidebar Component Tests
 * =================================
 * Unit tests for the TagFilterSidebar component
 * 
 * Tests:
 * - Sidebar rendering
 * - Tag categorization
 * - Tag filtering
 * - Tag counts
 * - Clear all functionality
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import TagFilterSidebar from '../TagFilterSidebar';

describe('TagFilterSidebar Component', () => {
  const mockNodes = [
    {
      id: 'recipe-1',
      data: { tags: ['weeknight', 'quick', 'vegetarian'] }
    },
    {
      id: 'recipe-2',
      data: { tags: ['weeknight', 'kid-friendly'] }
    },
    {
      id: 'recipe-3',
      data: { tags: ['party', 'dessert'] }
    },
    {
      id: 'recipe-4',
      data: { tags: [] } // No tags
    }
  ];

  const mockOnTagToggle = jest.fn();
  const mockOnClearAll = jest.fn();
  const mockOnToggleSidebar = jest.fn();

  beforeEach(() => {
    mockOnTagToggle.mockClear();
    mockOnClearAll.mockClear();
    mockOnToggleSidebar.mockClear();
  });

  // ==========================================
  // RENDERING TESTS
  // ==========================================

  test('renders sidebar when open', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    expect(screen.getByText('Filter by Tag')).toBeInTheDocument();
  });

  test('renders collapsed button when closed', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={false}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    const toggleButton = screen.getByTitle('Show tag filters');
    expect(toggleButton).toBeInTheDocument();
    expect(toggleButton).toHaveTextContent('🏷️');
  });

  test('displays all unique tags from nodes', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    expect(screen.getByText('weeknight')).toBeInTheDocument();
    expect(screen.getByText('quick')).toBeInTheDocument();
    expect(screen.getByText('vegetarian')).toBeInTheDocument();
    expect(screen.getByText('kid-friendly')).toBeInTheDocument();
    expect(screen.getByText('party')).toBeInTheDocument();
    expect(screen.getByText('dessert')).toBeInTheDocument();
  });

  test('displays correct tag usage counts', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    // "weeknight" appears in 2 recipes
    const weeknightTag = screen.getByText('weeknight').closest('.tag-filter-pill');
    expect(weeknightTag).toHaveTextContent('2');

    // "quick" appears in 1 recipe
    const quickTag = screen.getByText('quick').closest('.tag-filter-pill');
    expect(quickTag).toHaveTextContent('1');
  });

  test('shows no tags message when no tags exist', () => {
    render(
      <TagFilterSidebar
        nodes={[{ id: 'recipe-1', data: { tags: [] } }]}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    expect(screen.getByText('No tags yet!')).toBeInTheDocument();
  });

  // ==========================================
  // TAG SELECTION TESTS
  // ==========================================

  test('calls onTagToggle when clicking a tag', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    const weeknightTag = screen.getByText('weeknight');
    fireEvent.click(weeknightTag);

    expect(mockOnTagToggle).toHaveBeenCalledWith('weeknight');
  });

  test('highlights selected tags', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={['weeknight', 'quick']}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    const weeknightTag = screen.getByText('weeknight').closest('.tag-filter-pill');
    const quickTag = screen.getByText('quick').closest('.tag-filter-pill');

    expect(weeknightTag).toHaveClass('selected');
    expect(quickTag).toHaveClass('selected');
  });

  // ==========================================
  // FILTER SUMMARY TESTS
  // ==========================================

  test('shows filter summary when tags are selected', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={['weeknight']}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    // Should show filtered count (2 recipes have "weeknight")
    const filterInfo = screen.getByText(/recipes match/i).closest('.filter-info');
    expect(filterInfo).toHaveTextContent('2');
    expect(screen.getByText(/recipes match/i)).toBeInTheDocument();
  });

  test('calculates correct filtered count with AND logic', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={['weeknight', 'quick']}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    // Only recipe-1 has both "weeknight" AND "quick"
    const filterInfo = screen.getByText(/recipe match/i).closest('.filter-info');
    expect(filterInfo).toHaveTextContent('1');
  });

  test('shows "Clear All" button when tags selected', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={['weeknight']}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    expect(screen.getByText('Clear All')).toBeInTheDocument();
  });

  test('calls onClearAll when clicking Clear All', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={['weeknight']}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    const clearButton = screen.getByText('Clear All');
    fireEvent.click(clearButton);

    expect(mockOnClearAll).toHaveBeenCalled();
  });

  // ==========================================
  // SIDEBAR TOGGLE TESTS
  // ==========================================

  test('calls onToggleSidebar when clicking close button', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    const closeButton = screen.getByTitle('Hide sidebar');
    fireEvent.click(closeButton);

    expect(mockOnToggleSidebar).toHaveBeenCalled();
  });

  test('calls onToggleSidebar when clicking collapsed button', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={false}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    const toggleButton = screen.getByTitle('Show tag filters');
    fireEvent.click(toggleButton);

    expect(mockOnToggleSidebar).toHaveBeenCalled();
  });

  // ==========================================
  // TAG CATEGORIZATION TESTS
  // ==========================================

  test('categorizes tags correctly', () => {
    render(
      <TagFilterSidebar
        nodes={mockNodes}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    // Check for category headers
    expect(screen.getByText('Occasion')).toBeInTheDocument(); // "weeknight" is in Occasion
    expect(screen.getByText('Speed')).toBeInTheDocument(); // "quick" is in Speed
    expect(screen.getByText('Diet')).toBeInTheDocument(); // "vegetarian" is in Diet
    expect(screen.getByText('Family')).toBeInTheDocument(); // "kid-friendly" is in Family
  });

  // ==========================================
  // EDGE CASES
  // ==========================================

  test('handles empty nodes array', () => {
    render(
      <TagFilterSidebar
        nodes={[]}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    expect(screen.getByText('No tags yet!')).toBeInTheDocument();
  });

  test('handles nodes without tag data', () => {
    render(
      <TagFilterSidebar
        nodes={[
          { id: 'recipe-1', data: {} },
          { id: 'recipe-2', data: { name: 'Test' } }
        ]}
        selectedTags={[]}
        onTagToggle={mockOnTagToggle}
        onClearAll={mockOnClearAll}
        isOpen={true}
        onToggleSidebar={mockOnToggleSidebar}
      />
    );

    expect(screen.getByText('No tags yet!')).toBeInTheDocument();
  });
});
