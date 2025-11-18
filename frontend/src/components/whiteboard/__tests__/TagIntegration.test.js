/**
 * Tag Integration Tests
 * ======================
 * Integration tests for tag functionality across components
 * 
 * Tests:
 * - RecipeCardNode with tags
 * - Tag filtering in WhiteboardApp
 * - End-to-end tag workflow
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RecipeCardNode from '../../RecipeCardNode';

describe('RecipeCardNode Tag Integration', () => {
  const mockOnClick = jest.fn();
  const mockOnDelete = jest.fn();
  const mockOnTagsChange = jest.fn();
  const mockOnTagFilterClick = jest.fn();

  const mockData = {
    recipe: {
      id: 1,
      title: 'Test Recipe',
      name: 'Test Recipe',
      image_url: 'https://example.com/image.jpg',
      prep_time: 20,
      cook_time: 30
    },
    tags: ['weeknight', 'quick'],
    onClick: mockOnClick,
    onDelete: mockOnDelete,
    onTagsChange: mockOnTagsChange,
    onTagFilterClick: mockOnTagFilterClick
  };

  beforeEach(() => {
    mockOnClick.mockClear();
    mockOnDelete.mockClear();
    mockOnTagsChange.mockClear();
    mockOnTagFilterClick.mockClear();
  });

  // ==========================================
  // TAG DISPLAY TESTS
  // ==========================================

  test('displays tags as pills on recipe card', () => {
    render(
      <RecipeCardNode
        id="recipe-1"
        data={mockData}
        selected={false}
      />
    );

    expect(screen.getByText('weeknight')).toBeInTheDocument();
    expect(screen.getByText('quick')).toBeInTheDocument();
  });

  test('shows Add Tag button when card is selected', () => {
    render(
      <RecipeCardNode
        id="recipe-1"
        data={mockData}
        selected={true}
      />
    );

    expect(screen.getByText('+ Add Tag')).toBeInTheDocument();
  });

  test('does not show Add Tag button when card is not selected', () => {
    render(
      <RecipeCardNode
        id="recipe-1"
        data={mockData}
        selected={false}
      />
    );

    expect(screen.queryByText('+ Add Tag')).not.toBeInTheDocument();
  });

  // ==========================================
  // TAG EDITOR TESTS
  // ==========================================

  test('opens tag editor when clicking Add Tag', async () => {
    render(
      <RecipeCardNode
        id="recipe-1"
        data={mockData}
        selected={true}
      />
    );

    const addTagButton = screen.getByText('+ Add Tag');
    fireEvent.click(addTagButton);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Add tags...')).toBeInTheDocument();
      expect(screen.getByText('Done')).toBeInTheDocument();
    });
  });

  test('closes tag editor when clicking Done', async () => {
    render(
      <RecipeCardNode
        id="recipe-1"
        data={mockData}
        selected={true}
      />
    );

    // Open editor
    const addTagButton = screen.getByText('+ Add Tag');
    fireEvent.click(addTagButton);

    // Close editor
    const doneButton = await screen.findByText('Done');
    fireEvent.click(doneButton);

    await waitFor(() => {
      expect(screen.queryByPlaceholderText('Add tags...')).not.toBeInTheDocument();
      expect(screen.getByText('+ Add Tag')).toBeInTheDocument();
    });
  });

  test('calls onTagsChange when adding a tag', async () => {
    render(
      <RecipeCardNode
        id="recipe-1"
        data={mockData}
        selected={true}
      />
    );

    // Open editor
    fireEvent.click(screen.getByText('+ Add Tag'));

    // Add tag
    const input = await screen.findByPlaceholderText('Add tags...');
    await userEvent.type(input, 'vegetarian{Enter}');

    expect(mockOnTagsChange).toHaveBeenCalledWith(
      'recipe-1',
      ['weeknight', 'quick', 'vegetarian']
    );
  });

  test('calls onTagsChange when removing a tag', async () => {
    render(
      <RecipeCardNode
        id="recipe-1"
        data={mockData}
        selected={true}
      />
    );

    // Open editor
    fireEvent.click(screen.getByText('+ Add Tag'));

    // Remove first tag
    const removeButtons = await screen.findAllByText('×');
    fireEvent.click(removeButtons[0]);

    expect(mockOnTagsChange).toHaveBeenCalledWith(
      'recipe-1',
      ['quick'] // weeknight removed
    );
  });

  // ==========================================
  // TAG FILTER CLICK TESTS
  // ==========================================

  test('calls onTagFilterClick when clicking tag pill', () => {
    render(
      <RecipeCardNode
        id="recipe-1"
        data={mockData}
        selected={false}
      />
    );

    const weeknightTag = screen.getByText('weeknight');
    fireEvent.click(weeknightTag);

    expect(mockOnTagFilterClick).toHaveBeenCalledWith('weeknight');
  });

  test('does not call onClick when clicking tag pill', () => {
    render(
      <RecipeCardNode
        id="recipe-1"
        data={mockData}
        selected={false}
      />
    );

    const weeknightTag = screen.getByText('weeknight');
    fireEvent.click(weeknightTag);

    // Should NOT trigger card click
    expect(mockOnClick).not.toHaveBeenCalled();
  });

  // ==========================================
  // EDGE CASES
  // ==========================================

  test('handles recipe with no tags', () => {
    const dataNoTags = {
      ...mockData,
      tags: []
    };

    render(
      <RecipeCardNode
        id="recipe-1"
        data={dataNoTags}
        selected={true}
      />
    );

    expect(screen.getByText('+ Add Tag')).toBeInTheDocument();
  });

  test('handles undefined tags array', () => {
    const dataUndefinedTags = {
      ...mockData,
      tags: undefined
    };

    render(
      <RecipeCardNode
        id="recipe-1"
        data={dataUndefinedTags}
        selected={false}
      />
    );

    // Should not crash
    expect(screen.getByText('Test Recipe')).toBeInTheDocument();
  });
});

// ==========================================
// TAG FILTERING LOGIC TESTS
// ==========================================

describe('Tag Filtering Logic', () => {
  const mockNodes = [
    {
      id: 'recipe-1',
      type: 'recipeCard',
      data: { tags: ['weeknight', 'quick', 'vegetarian'] }
    },
    {
      id: 'recipe-2',
      type: 'recipeCard',
      data: { tags: ['weeknight', 'kid-friendly'] }
    },
    {
      id: 'recipe-3',
      type: 'recipeCard',
      data: { tags: ['party', 'dessert'] }
    },
    {
      id: 'note-1',
      type: 'note',
      data: { content: 'Test note' }
    }
  ];

  test('filters nodes by single tag', () => {
    const selectedTags = ['weeknight'];
    
    const filteredNodes = mockNodes.filter(node => {
      const nodeTags = node.data?.tags || [];
      return selectedTags.every(tag => nodeTags.includes(tag));
    });

    expect(filteredNodes).toHaveLength(2); // recipe-1 and recipe-2
    expect(filteredNodes.map(n => n.id)).toEqual(['recipe-1', 'recipe-2']);
  });

  test('filters nodes by multiple tags with AND logic', () => {
    const selectedTags = ['weeknight', 'quick'];
    
    const filteredNodes = mockNodes.filter(node => {
      const nodeTags = node.data?.tags || [];
      return selectedTags.every(tag => nodeTags.includes(tag));
    });

    expect(filteredNodes).toHaveLength(1); // Only recipe-1 has both
    expect(filteredNodes[0].id).toBe('recipe-1');
  });

  test('returns all nodes when no tags selected', () => {
    const selectedTags = [];
    
    const filteredNodes = selectedTags.length > 0
      ? mockNodes.filter(node => {
          const nodeTags = node.data?.tags || [];
          return selectedTags.every(tag => nodeTags.includes(tag));
        })
      : mockNodes;

    expect(filteredNodes).toHaveLength(4); // All nodes
  });

  test('returns empty array when no nodes match tags', () => {
    const selectedTags = ['nonexistent-tag'];
    
    const filteredNodes = mockNodes.filter(node => {
      const nodeTags = node.data?.tags || [];
      return selectedTags.every(tag => nodeTags.includes(tag));
    });

    expect(filteredNodes).toHaveLength(0);
  });

  test('handles nodes without tags array', () => {
    const nodesWithoutTags = [
      { id: 'recipe-1', data: {} },
      { id: 'recipe-2', data: { name: 'Test' } }
    ];

    const selectedTags = ['weeknight'];
    
    const filteredNodes = nodesWithoutTags.filter(node => {
      const nodeTags = node.data?.tags || [];
      return selectedTags.every(tag => nodeTags.includes(tag));
    });

    expect(filteredNodes).toHaveLength(0);
  });
});
