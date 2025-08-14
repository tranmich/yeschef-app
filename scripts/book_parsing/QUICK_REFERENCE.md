# 📚 Book Parsing System - Quick Reference

## 🎯 For Processing New PDF Cookbooks

### 🚀 Quick Start (Choose Your Parser)
```bash
# For most PDFs - Universal Parser (recommended)
cd "d:\Mik\Downloads\Me Hungie"
python scripts/book_parsing/complete_recipe_parser.py

# For difficult text extraction - String-based Parser
python scripts/book_parsing/breakthrough_parser.py

# For Canadian Living format - Specialized Parser
python scripts/book_parsing/complete_canadian_parser.py

# Always verify results
python scripts/book_parsing/check_books_db.py
```

### 📋 What Each Tool Does

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `complete_recipe_parser.py` | **Universal parser** for any cookbook | **Start here** - works with most PDFs |
| `breakthrough_parser.py` | String-based parsing for difficult PDFs | When text extraction is problematic |
| `complete_canadian_parser.py` | Specialized for Canadian Living format | Dual-column cookbooks with page numbers |
| `pdf_formatting_analyzer.py` | Analyze PDF layout | When universal parser needs adjustment |
| `refined_pdf_parser.py` | Extract ingredient pairings | Reference books like Flavor Bible |
| `complete_bible_parser.py` | Process very large documents | 500+ page reference books |
| `check_books_db.py` | Verify parsing results | After any parsing operation |

### 🔧 Common Adjustments Needed

Most PDFs will work with `complete_canadian_parser.py` but you may need to adjust:

```python
# In the parser file, common changes:
font_size >= 11        # Title detection threshold
column_boundary = 0.52 # Column split position  
recipe_patterns = [...]# Title recognition patterns
```

### 📊 Success Indicators

After parsing, you should see:
- ✅ Recipe titles properly extracted
- ✅ Ingredients in clean lists  
- ✅ Instructions as complete paragraphs
- ✅ Accurate page number references
- ✅ No text corruption or missing content

### 🔗 Integration with Main Database

After successful book parsing:
```bash
# Import to main database
python scripts/book_parsing/import_bonappetit_to_recipe_books.py

# Add analysis data
python recipe_analyzer.py

# Add flavor profiles  
python scripts/enhancement/generate_flavor_profiles.py
```

### 📁 File Locations
- **Place PDFs**: Project root directory
- **Parser scripts**: `scripts/book_parsing/`
- **Output database**: `recipe_books.db`
- **Documentation**: `scripts/book_parsing/README.md`

---

**Ready to process your next cookbook!** 🍳📖
