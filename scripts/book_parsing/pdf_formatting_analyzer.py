#!/usr/bin/env python3
"""
PDF Formatting Analysis Tool
============================

Explore what formatting information pdfplumber can extract:
- Font sizes, families, colors
- Text positioning (x, y coordinates)
- Character-level formatting
- Bounding boxes and spacing
"""

import pdfplumber
from pathlib import Path
import json
from collections import defaultdict

def analyze_pdf_formatting(pdf_path, page_num=100):
    """Analyze the formatting structure of a specific page"""
    
    print(f"🔍 ANALYZING PDF FORMATTING: Page {page_num}")
    print("=" * 60)
    
    with pdfplumber.open(pdf_path) as pdf:
        if page_num > len(pdf.pages):
            print(f"❌ Page {page_num} not found. Total pages: {len(pdf.pages)}")
            return
        
        page = pdf.pages[page_num - 1]  # Convert to 0-based index
        
        # Extract characters with formatting
        chars = page.chars
        print(f"📄 Page {page_num} has {len(chars)} characters")
        
        # Analyze formatting patterns
        analyze_font_patterns(chars)
        analyze_positioning_patterns(chars)
        analyze_text_structure(page)
        
        # Look for dual-column indicators
        analyze_column_structure(chars)

def analyze_font_patterns(chars):
    """Analyze font size, family, and color patterns"""
    print(f"\n🎨 FONT ANALYSIS:")
    print("-" * 30)
    
    # Group by font properties
    font_groups = defaultdict(list)
    
    for char in chars:
        font_key = (
            char.get('fontname', 'unknown'),
            round(char.get('size', 0), 1),
            char.get('stroking_color', None)
        )
        font_groups[font_key].append(char)
    
    # Show most common font patterns
    sorted_fonts = sorted(font_groups.items(), key=lambda x: len(x[1]), reverse=True)
    
    for i, ((fontname, size, color), char_list) in enumerate(sorted_fonts[:10]):
        sample_text = ''.join([c.get('text', '') for c in char_list[:50]])
        print(f"  {i+1:2d}. Font: {fontname}, Size: {size}, Color: {color}")
        print(f"      Count: {len(char_list)} chars")
        print(f"      Sample: '{sample_text.strip()}'")
        print()

def analyze_positioning_patterns(chars):
    """Analyze text positioning to identify columns and sections"""
    print(f"\n📐 POSITIONING ANALYSIS:")
    print("-" * 30)
    
    # Group by Y coordinate (horizontal lines)
    y_groups = defaultdict(list)
    
    for char in chars:
        y_pos = round(char.get('y0', 0), 1)
        y_groups[y_pos].append(char)
    
    # Sort by Y position (top to bottom)
    sorted_lines = sorted(y_groups.items(), key=lambda x: x[0], reverse=True)
    
    print(f"Found {len(sorted_lines)} distinct Y positions (text lines)")
    
    # Analyze X positioning to detect columns
    x_positions = []
    for y_pos, chars_on_line in sorted_lines[:20]:  # Check first 20 lines
        line_text = ''.join([c.get('text', '') for c in chars_on_line])
        min_x = min([c.get('x0', 0) for c in chars_on_line])
        max_x = max([c.get('x1', 0) for c in chars_on_line])
        
        x_positions.append(min_x)
        
        print(f"  Y: {y_pos:6.1f}, X: {min_x:6.1f}-{max_x:6.1f}, Text: '{line_text.strip()[:60]}'")
    
    # Detect column boundaries
    unique_x = sorted(set([round(x, 0) for x in x_positions]))
    print(f"\n📊 Unique X starting positions: {unique_x}")
    
    if len(unique_x) >= 2:
        print(f"🔍 DUAL-COLUMN DETECTED: Left column ~{unique_x[0]}, Right column ~{unique_x[-1]}")

def analyze_text_structure(page):
    """Analyze text extraction methods"""
    print(f"\n📝 TEXT STRUCTURE ANALYSIS:")
    print("-" * 30)
    
    # Extract text using different methods
    simple_text = page.extract_text()
    
    # Extract text with layout preservation
    text_with_layout = page.extract_text(layout=True)
    
    # Extract words with positioning
    words = page.extract_words()
    
    print(f"Simple text length: {len(simple_text) if simple_text else 0}")
    print(f"Layout text length: {len(text_with_layout) if text_with_layout else 0}")
    print(f"Word count: {len(words)}")
    
    # Show first few words with positioning
    if words:
        print(f"\n📍 FIRST 10 WORDS WITH POSITIONS:")
        for i, word in enumerate(words[:10]):
            x0 = word.get('x0', 0)
            x1 = word.get('x1', 0) 
            y0 = word.get('top', word.get('y0', 0))
            print(f"  {i+1:2d}. '{word['text']}' at X:{x0:.1f}-{x1:.1f}, Y:{y0:.1f}")

def analyze_column_structure(chars):
    """Specifically analyze dual-column structure"""
    print(f"\n🏛️ COLUMN STRUCTURE ANALYSIS:")
    print("-" * 30)
    
    # Find all X positions where text starts
    x_starts = [char.get('x0', 0) for char in chars if char.get('text', '').strip()]
    
    if not x_starts:
        return
        
    # Round to nearest 10 pixels to group similar positions
    x_rounded = [round(x / 10) * 10 for x in x_starts]
    x_counts = defaultdict(int)
    
    for x in x_rounded:
        x_counts[x] += 1
    
    # Find major column boundaries
    major_columns = [(x, count) for x, count in x_counts.items() if count >= 10]
    major_columns.sort(key=lambda x: x[1], reverse=True)
    
    print(f"📊 Major text starting positions:")
    for x, count in major_columns[:5]:
        print(f"  X: {x:6.0f} pixels - {count:4d} characters")
    
    if len(major_columns) >= 2:
        left_col = major_columns[0][0]
        right_col = major_columns[1][0]
        print(f"\n🎯 DETECTED COLUMNS:")
        print(f"  Left column:  ~{left_col} pixels")
        print(f"  Right column: ~{right_col} pixels")
        print(f"  Column gap:   ~{right_col - left_col} pixels")

def test_formatting_analysis():
    """Test the formatting analysis on Canadian Living cookbook"""
    
    # Look for the Canadian Living cookbook
    cookbook_path = None
    possible_paths = [
        "Books/Canadian-Living-The-Ultimate-Cookbook.pdf",
        "books_archive/Canadian-Living-The-Ultimate-Cookbook.pdf",
        "Canadian Living - The Complete Cookbook.pdf",
        "canadian_living_cookbook.pdf",
        "cookbook.pdf"
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            cookbook_path = path
            break
    
    if not cookbook_path:
        print("❌ Canadian Living cookbook not found. Please ensure the PDF is in the current directory.")
        print("Expected filename: 'Canadian-Living-The-Ultimate-Cookbook.pdf'")
        return
    
    print(f"📚 Found cookbook: {cookbook_path}")
    
    # Analyze page 100 (our problem page)
    analyze_pdf_formatting(cookbook_path, page_num=100)

if __name__ == "__main__":
    test_formatting_analysis()
