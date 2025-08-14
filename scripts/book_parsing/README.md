# Book Parsing Scripts

This directory contains scripts for parsing PDF cookbooks and extracting recipe data into structured databases.

## 📚 Core Parsing Scripts

### **`complete_recipe_parser.py`** - Universal Recipe Book Parser
- **Purpose**: Comprehensive system for parsing any PDF recipe book
- **Features**: 
  - Automatic cuisine detection and categorization
  - Table of contents extraction
  - Recipe structure analysis with multiple format support
  - Ingredient and instruction parsing with smart boundaries
  - Database integration with hash-based duplicate prevention
- **Best for**: Complex recipe books with varied layouts
- **Usage**: 
  ```bash
  python complete_recipe_parser.py
  ```

### **`breakthrough_parser.py`** - String-Based Recipe Parser
- **Purpose**: Parse recipes from continuous text (single string format)
- **Features**:
  - Works with PDFs that extract as one continuous string
  - Pattern-based title, timing, and ingredient detection
  - Dual-column recipe support
  - Simple database storage
- **Best for**: PDFs with challenging text extraction
- **Usage**:
  ```bash
  python breakthrough_parser.py
  ```

### **`complete_canadian_parser.py`** - Canadian Living Format Parser
- **Purpose**: Parse the entire Canadian Living cookbook PDF
- **Features**: 
  - Dual-column text extraction
  - Recipe title recognition with page numbers
  - Ingredient and instruction parsing
  - Automatic recipe boundary detection
- **Best for**: Canadian Living cookbook and similar layouts
- **Usage**: 
  ```bash
  python complete_canadian_parser.py
  ```

### **`refined_pdf_parser.py`** - Enhanced PDF Parser for Flavor Bible
- **Purpose**: Extract ingredient pairings from The Flavor Bible
- **Features**:
  - Food ingredient keyword recognition
  - Pairing relationship extraction
  - Multi-page processing with progress tracking
  - Clean data export to JSON
- **Output**: Flavor pairing data in JSON format
- **Usage**:
  ```bash
  python refined_pdf_parser.py
  ```

### **`complete_bible_parser.py`** - Full Flavor Bible Processor
- **Purpose**: Parse the entire 962-page Flavor Bible document
- **Features**:
  - Chunked processing to avoid memory issues
  - Progress tracking and resumption capability
  - Safety checkpoints for large document processing
- **Usage**:
  ```bash
  python complete_bible_parser.py
  ```

## 🔧 Utility Scripts

### **`pdf_formatting_analyzer.py`** - PDF Structure Analysis
- **Purpose**: Analyze PDF structure and formatting
- **Features**:
  - Font analysis and text layout detection
  - Column identification for multi-column documents
  - Text extraction quality assessment
- **Usage**: Run before parsing to understand document structure

### **`check_books_db.py`** - Database Verification
- **Purpose**: Verify parsed book data in database
- **Features**:
  - Recipe count validation
  - Data quality checks
  - Sample recipe display
- **Usage**:
  ```bash
  python check_books_db.py
  ```

### **`check_books_structure.py`** - Book Database Schema Checker
- **Purpose**: Verify database structure for book data
- **Features**:
  - Table structure validation
  - Schema compatibility checking
  - Database integrity verification

### **`comprehensive_test.py`** - Parser Testing Suite
- **Purpose**: Test and validate parsing functionality
- **Features**:
  - Test different parser configurations
  - Validate parsing accuracy
  - Performance benchmarking
- **Usage**: Run after parser modifications

### **`comprehensive_page_scanner.py`** - Page Analysis Tool
- **Purpose**: Scan and analyze individual pages before parsing
- **Features**:
  - Page structure analysis
  - Text layout detection
  - Quality assessment for parsing readiness
- **Usage**: Diagnostic tool for problematic pages

### **`import_bonappetit_to_recipe_books.py`** - Cross-Database Import
- **Purpose**: Import Bon Appétit data into recipe books database
- **Features**:
  - Data migration between databases
  - Schema mapping and conversion
  - Duplicate prevention

## 📖 Supported Book Formats

### Current Support:
- **Canadian Living Cookbook** - Multi-column layout with page numbers
- **The Flavor Bible** - Ingredient pairing reference book
- **Standard PDF Cookbooks** - Basic recipe extraction

### Adding New Books:
1. **Analyze Structure**: Use `pdf_formatting_analyzer.py` to understand layout
2. **Adapt Parser**: Modify `complete_canadian_parser.py` for new format
3. **Test Extraction**: Run on sample pages first
4. **Verify Results**: Use verification scripts to check output quality

## 🎯 Workflow for New PDFs

### 1. Preparation
```bash
# Place PDF in project root or specify path
# Analyze document structure
python scripts/book_parsing/pdf_formatting_analyzer.py
```

### 2. Parser Configuration
- Review analyzer output to understand:
  - Column layout (single/dual column)
  - Font patterns for titles vs content
  - Page numbering system
  - Recipe boundary markers

### 3. Parsing Process
```bash
# For Canadian Living format books:
python scripts/book_parsing/complete_canadian_parser.py

# For flavor reference books:
python scripts/book_parsing/refined_pdf_parser.py
```

### 4. Verification
```bash
# Check parsing results
python scripts/book_parsing/check_books_db.py

# Verify database structure
python scripts/book_parsing/check_books_structure.py
```

## 📊 Output Formats

### Recipe Database (`recipe_books.db`)
- **Table**: `recipes` - Complete recipe data with ingredients and instructions
- **Table**: `books` - Book metadata and source information
- **Table**: `ingredients` - Extracted ingredient list with normalization

### Flavor Data (JSON files)
- **Format**: Ingredient pairing relationships
- **Structure**: `{"ingredient": [list_of_pairings]}`
- **Usage**: Integration with flavor profile system

## 🔗 Integration Points

### With Main Database (`hungie.db`)
- Recipe analysis and enhancement scripts can process book data
- Flavor pairing data enhances recipe recommendations
- Cross-database recipe searching and comparison

### With Enhancement System
- Parsed recipes automatically get analysis and flavor profiles
- Book data contributes to comprehensive recipe database
- Ingredient normalization improves search accuracy

## ⚙️ Prerequisites

### Required Python Packages:
```bash
pip install pdfplumber PyMuPDF sqlite3 pathlib
```

### Required Files:
- PDF cookbook files in accessible location
- Write access for database creation
- Sufficient disk space for extracted data

---

*Book Parsing System - August 8, 2025*
*Ready for additional PDF cookbook processing*
