/**
 * TagSystem Component Tests
 * =========================
 * Unit tests for the TagSystem autocomplete component
 * 
 * Tests:
 * - Component rendering
 * - Tag addition/removal
 * - Autocomplete suggestions
 * - Keyboard navigation
 * - Custom tag creation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TagSystem from '../TagSystem';

describe('TagSystem Component', () => {
  const mockOnChange = jest.fn();
  
  beforeEach(() => {
    mockOnChange.mockClear();
  });

  // ==========================================
  // RENDERING TESTS
  // ==========================================

  test('renders empty tag input with placeholder', () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} placeholder="Add tags..." />);
    
    const input = screen.getByPlaceholderText('Add tags...');
    expect(input).toBeInTheDocument();
  });

  test('renders existing tags as pills', () => {
    render(
      <TagSystem 
        tags={['weeknight', 'quick', 'vegetarian']} 
        onChange={mockOnChange} 
      />
    );
    
    expect(screen.getByText('weeknight')).toBeInTheDocument();
    expect(screen.getByText('quick')).toBeInTheDocument();
    expect(screen.getByText('vegetarian')).toBeInTheDocument();
  });

  test('renders remove button for each tag', () => {
    render(
      <TagSystem 
        tags={['weeknight', 'quick']} 
        onChange={mockOnChange} 
      />
    );
    
    const removeButtons = screen.getAllByText('×');
    expect(removeButtons).toHaveLength(2);
  });

  // ==========================================
  // AUTOCOMPLETE TESTS
  // ==========================================

  test('shows suggestions when typing', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'qui');
    
    await waitFor(() => {
      expect(screen.getByText(/quick/i)).toBeInTheDocument();
    });
  });

  test('filters suggestions based on input', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'veg');
    
    await waitFor(() => {
      expect(screen.getByText(/vegetarian/i)).toBeInTheDocument();
      expect(screen.getByText(/vegan/i)).toBeInTheDocument();
    });
  });

  test('hides already-added tags from suggestions', async () => {
    render(<TagSystem tags={['quick']} onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'qui');
    
    await waitFor(() => {
      // "quick" should not appear in suggestions since it's already added
      const suggestions = screen.queryByText('🏷️ quick');
      expect(suggestions).not.toBeInTheDocument();
    });
  });

  // ==========================================
  // TAG ADDITION TESTS
  // ==========================================

  test('adds tag from suggestion on Enter', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'quick');
    await userEvent.keyboard('{Enter}');
    
    expect(mockOnChange).toHaveBeenCalledWith(['quick']);
  });

  test('adds tag from suggestion on click', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'week');
    
    await waitFor(() => {
      const suggestion = screen.getByText(/weeknight/i);
      fireEvent.click(suggestion);
    });
    
    expect(mockOnChange).toHaveBeenCalledWith(['weeknight']);
  });

  test('creates custom tag when allowCustom is true', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} allowCustom={true} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'family-favorite{Enter}');
    
    expect(mockOnChange).toHaveBeenCalledWith(['family-favorite']);
  });

  test('does not allow duplicate tags', async () => {
    render(<TagSystem tags={['quick']} onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'quick{Enter}');
    
    // Should not add duplicate
    expect(mockOnChange).not.toHaveBeenCalled();
  });

  test('clears input after adding tag', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'quick{Enter}');
    
    expect(input.value).toBe('');
  });

  // ==========================================
  // TAG REMOVAL TESTS
  // ==========================================

  test('removes tag when clicking × button', async () => {
    render(
      <TagSystem 
        tags={['weeknight', 'quick']} 
        onChange={mockOnChange} 
      />
    );
    
    const removeButtons = screen.getAllByText('×');
    fireEvent.click(removeButtons[0]); // Remove first tag
    
    expect(mockOnChange).toHaveBeenCalledWith(['quick']);
  });

  test('removes last tag on backspace when input is empty', async () => {
    render(
      <TagSystem 
        tags={['weeknight', 'quick']} 
        onChange={mockOnChange} 
      />
    );
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, '{Backspace}');
    
    expect(mockOnChange).toHaveBeenCalledWith(['weeknight']);
  });

  // ==========================================
  // KEYBOARD NAVIGATION TESTS
  // ==========================================

  test('navigates suggestions with arrow keys', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'quick');
    
    // Arrow down should select suggestion
    await userEvent.keyboard('{ArrowDown}');
    
    // First suggestion should be highlighted (check via class or aria)
    const suggestions = screen.getByText(/quick/i);
    expect(suggestions.closest('.tag-suggestion')).toHaveClass('selected');
  });

  test('closes suggestions on Escape', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'quick');
    
    await waitFor(() => {
      expect(screen.getByText(/quick/i)).toBeInTheDocument();
    });
    
    await userEvent.keyboard('{Escape}');
    
    await waitFor(() => {
      expect(screen.queryByText(/quick/i)).not.toBeInTheDocument();
    });
  });

  // ==========================================
  // EDGE CASES
  // ==========================================

  test('handles empty input gracefully', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, '   {Enter}'); // Whitespace only
    
    expect(mockOnChange).not.toHaveBeenCalled();
  });

  test('trims whitespace from tags', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} allowCustom={true} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, '  custom-tag  {Enter}');
    
    expect(mockOnChange).toHaveBeenCalledWith(['custom-tag']);
  });

  test('converts tags to lowercase', async () => {
    render(<TagSystem tags={[]} onChange={mockOnChange} allowCustom={true} />);
    
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'QUICK{Enter}');
    
    expect(mockOnChange).toHaveBeenCalledWith(['quick']);
  });
});
