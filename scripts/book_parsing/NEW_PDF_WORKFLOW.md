# Adding New PDF Cookbooks - Workflow Guide

Complete step-by-step process for integrating new PDF cookbooks into the Hungie database.

## 🎯 Overview
This workflow will help you parse any new PDF cookbook and integrate it with the existing recipe database.

## 📋 Step-by-Step Process

### Step 1: Preparation
```bash
# 1. Place your PDF in the project root
# Example: "new_cookbook.pdf"

# 2. Navigate to book parsing directory
cd "d:\Mik\Downloads\Me Hungie"
```

### Step 2: Analyze PDF Structure
```bash
# Analyze the document layout and formatting
python scripts/book_parsing/pdf_formatting_analyzer.py
```

**What to look for in the analysis:**
- ✅ Single vs dual-column layout
- ✅ Font sizes for titles vs body text
- ✅ Page numbering system
- ✅ Recipe boundary patterns (lines, spacing, etc.)
- ✅ Ingredient list formatting
- ✅ Instruction paragraph structure

### Step 3: Configure Parser

Based on the analysis, you may need to adapt the parser. The main options are:

#### Option A: Canadian Living Format (Most cookbooks)
If your PDF has similar structure to Canadian Living:
- Dual-column layout
- Clear recipe titles
- Page numbers with recipes
- Ingredient lists followed by instructions

**Use**: `complete_canadian_parser.py` (may need minor adjustments)

#### Option B: Custom Parser Required
If the format is significantly different, create a copy of the parser and modify:

```bash
# Create custom parser
copy scripts/book_parsing/complete_canadian_parser.py scripts/book_parsing/new_book_parser.py
```

**Common modifications needed:**
- Font size thresholds for title detection
- Column splitting parameters
- Recipe boundary detection patterns
- Ingredient vs instruction separation logic

### Step 4: Test Parsing on Sample Pages
```bash
# Test on a few pages first (modify parser to limit page range)
# Edit the parser to process pages 10-15 for testing
python scripts/book_parsing/complete_canadian_parser.py
```

### Step 5: Verify Test Results
```bash
# Check what was extracted
python scripts/book_parsing/check_books_db.py
```

**Look for:**
- ✅ Recipe titles are correctly identified
- ✅ Ingredients are properly separated
- ✅ Instructions are complete paragraphs
- ✅ Page numbers are accurate
- ✅ No text corruption or missing content

### Step 6: Full Document Processing
Once satisfied with test results:

```bash
# Process the entire document
python scripts/book_parsing/complete_canadian_parser.py
```

### Step 7: Database Integration
```bash
# Import parsed recipes into main hungie.db
python scripts/book_parsing/import_bonappetit_to_recipe_books.py

# Or create a new integration script if needed
```

### Step 8: Enhancement Process
```bash
# Generate analysis data for new recipes
python recipe_analyzer.py

# Generate flavor profiles
python scripts/enhancement/generate_flavor_profiles.py

# Verify complete enhancement
python scripts/verification/final_verification.py
```

## 🔧 Common Parser Adjustments

### Title Detection
```python
# Adjust font size threshold
if font_size >= 11:  # Change this value based on analysis
    # This might be a title
```

### Column Splitting
```python
# Adjust column boundary
column_boundary = page_width * 0.52  # Adjust percentage
```

### Recipe Boundaries
```python
# Modify pattern matching for recipe separation
recipe_patterns = [
    r'^[A-Z][A-Za-z\s]+\s+\d+$',  # Title with page number
    r'^\d+\s+[A-Z]',              # Page number then title
    # Add patterns specific to your book
]
```

## 📊 Quality Assurance Checklist

After parsing, verify:

- [ ] **Recipe Count**: Does it match expected number?
- [ ] **Title Quality**: Are titles clean and readable?
- [ ] **Ingredient Lists**: Complete and properly formatted?
- [ ] **Instructions**: No missing steps or merged paragraphs?
- [ ] **Page Numbers**: Accurate references?
- [ ] **Special Characters**: Proper encoding (fractions, degrees, etc.)?

## 🐛 Troubleshooting

### Common Issues:

**Problem**: Titles not detected
**Solution**: Adjust font size threshold or add title patterns

**Problem**: Ingredients and instructions mixed
**Solution**: Improve text classification logic

**Problem**: Column splitting errors  
**Solution**: Adjust column boundary percentage

**Problem**: Missing recipes
**Solution**: Check recipe boundary detection patterns

**Problem**: Garbled text
**Solution**: Try different PDF extraction libraries or OCR

## 📁 File Organization

After successful parsing:
```
📂 scripts/book_parsing/
├── 🐍 your_new_book_parser.py    # Custom parser if created
├── 📊 parsing_results_bookname.json  # Backup of extracted data
└── 📋 parsing_log_bookname.txt   # Processing log

📂 databases/
├── 💾 recipe_books.db            # Book-specific database
└── 💾 hungie.db                 # Main integrated database
```

## 🎉 Success Metrics

A successful integration should result in:
- ✅ All recipes extracted and readable
- ✅ Proper categorization and analysis data
- ✅ Searchable through main API endpoints
- ✅ Enhanced with flavor profiles
- ✅ No duplicate entries
- ✅ Consistent formatting across sources

---

*Ready to process your next PDF cookbook!* 📚✨
