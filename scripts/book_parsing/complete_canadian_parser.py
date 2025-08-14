"""
Complete Canadian Living Cookbook Parser
Process the entire cookbook with the improved dual-column splitting
"""

import pdfplumber
import re
import json
import sqlite3
import hashlib
from typing import List, Dict, Optional
from pathlib import Path

class CompleteCanadianLivingParser:
    """
    Complete parser for the entire Canadian Living cookbook
    """
    
    def __init__(self, db_path: str = "recipe_books.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                file_path TEXT NOT NULL,
                file_hash TEXT UNIQUE,
                total_recipes INTEGER DEFAULT 0,
                parsing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'processing'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                title TEXT NOT NULL,
                page_number INTEGER,
                servings TEXT,
                hands_on_time TEXT,
                total_time TEXT,
                ingredients TEXT,
                instructions TEXT,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database ready for complete parsing")
    
    def process_complete_cookbook(self, pdf_path: str) -> bool:
        """Process the entire cookbook"""
        
        try:
            file_hash = self._calculate_file_hash(pdf_path)
            
            if self._book_exists(file_hash):
                print("⚠️ Book already processed - clearing and re-processing")
                self._clear_existing_book(file_hash)
            
            print("📚 Processing Canadian Living Ultimate Cookbook...")
            
            # Extract all recipes
            all_recipes = self._extract_all_recipes(pdf_path)
            
            # Store in database
            book_id = self._store_book_metadata(pdf_path, file_hash)
            stored_count = self._store_recipes(book_id, all_recipes)
            self._update_book_status(book_id, stored_count)
            
            print(f"\\n🎉 COMPLETE! Processed {stored_count} recipes total!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_all_recipes(self, pdf_path: str) -> List[Dict]:
        """Extract recipes from entire cookbook"""
        
        all_recipes = []
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"📄 Processing {total_pages} pages...")
            
            # Process recipe pages (skip intro pages, stop before index)
            start_page = 10  # Start around page 10
            end_page = min(total_pages, 400)  # Stop around page 400
            
            pages_processed = 0
            recipes_found = 0
            
            for page_num in range(start_page, end_page):
                try:
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    
                    if text and len(text) > 500:  # Page has substantial content
                        page_recipes = self._extract_recipes_from_page_text(text, page_num + 1)
                        
                        if page_recipes:
                            all_recipes.extend(page_recipes)
                            recipes_found += len(page_recipes)
                            print(f"   📄 Page {page_num + 1}: {len(page_recipes)} recipes (total: {recipes_found})")
                    
                    pages_processed += 1
                    
                    # Progress update every 50 pages
                    if pages_processed % 50 == 0:
                        print(f"   🔄 Processed {pages_processed}/{end_page - start_page} pages, found {recipes_found} recipes")
                
                except Exception as e:
                    print(f"   ⚠️ Error on page {page_num + 1}: {e}")
                    continue
            
            print(f"\\n✅ Extraction complete: {len(all_recipes)} total recipes from {pages_processed} pages")
            
        return all_recipes
    
    def _extract_recipes_from_page_text(self, text: str, page_number: int) -> List[Dict]:
        """Extract recipes from page text - improved version"""
        
        lines = [line.strip() for line in text.split('\\n') if line.strip()]
        
        # Quick check: does this page have recipes?
        has_recipe_indicators = any(indicator in text for indicator in [
            'HANDS-ON TIME', 'INGREDIENTS INGREDIENTS', 'DIRECTIONS DIRECTIONS'
        ])
        
        if not has_recipe_indicators:
            return []
        
        # Find recipe structure
        title_lines = []
        hands_on_idx = -1
        ingredients_idx = -1
        directions_idx = -1
        
        for i, line in enumerate(lines):
            if 'HANDS-ON TIME' in line and hands_on_idx == -1:
                hands_on_idx = i
                # Title is usually the line before hands-on time
                if i > 0 and len(lines[i-1]) > 10 and not any(skip in lines[i-1] for skip in ['ULTIMATE', 'CANADIAN LIVING']):
                    title_lines.append(lines[i-1])
            elif 'INGREDIENTS INGREDIENTS' in line:
                ingredients_idx = i + 1
            elif 'DIRECTIONS DIRECTIONS' in line:
                directions_idx = i + 1
                break
        
        if hands_on_idx == -1 or ingredients_idx == -1:
            return []
        
        # Extract ingredient lines
        ingredient_lines = []
        end_idx = directions_idx - 1 if directions_idx > 0 else min(ingredients_idx + 15, len(lines))
        
        for i in range(ingredients_idx, end_idx):
            if i < len(lines):
                line = lines[i]
                if line and not line.startswith('DIRECTIONS'):
                    ingredient_lines.append(line)
        
        if len(ingredient_lines) < 2:
            return []
        
        # Split ingredients into two recipes
        recipe1_ingredients = []
        recipe2_ingredients = []
        
        for line in ingredient_lines:
            left, right = self._split_ingredient_line(line)
            if left:
                recipe1_ingredients.append(left)
            if right:
                recipe2_ingredients.append(right)
        
        # Extract timing info
        timing_line = lines[hands_on_idx] if hands_on_idx >= 0 else ""
        hands_on_times = re.findall(r'(\\d+)\\s*minutes', timing_line)
        
        # Look for total time line
        total_time_line = ""
        if hands_on_idx + 1 < len(lines):
            total_time_line = lines[hands_on_idx + 1]
        total_times = re.findall(r'(\\d+[½¼¾]?)\\s*(hours?|minutes?)', total_time_line)
        
        # Look for servings
        servings_line = ""
        if hands_on_idx + 2 < len(lines):
            servings_line = lines[hands_on_idx + 2]
        servings = re.findall(r'(\\d+\\s*to\\s*\\d+)\\s*servings', servings_line)
        
        # Extract directions (simplified)
        direction_lines = []
        if directions_idx > 0:
            for i in range(directions_idx, min(directions_idx + 20, len(lines))):
                if i < len(lines):
                    line = lines[i]
                    if 'NUTRITIONAL INFORMATION' in line:
                        break
                    if line and len(line) > 10:
                        direction_lines.append(line)
        
        # Create recipes
        recipes = []
        
        # Determine titles
        if title_lines:
            title_text = ' '.join(title_lines)
            # Try to split title
            title_words = title_text.split()
            
            # Look for recipe name patterns
            if len(title_words) > 2:
                mid_point = len(title_words) // 2
                title1 = ' '.join(title_words[:mid_point])
                title2 = ' '.join(title_words[mid_point:])
            else:
                title1 = title_text
                title2 = f"Recipe 2 (Page {page_number})"
        else:
            title1 = f"Recipe 1 (Page {page_number})"
            title2 = f"Recipe 2 (Page {page_number})"
        
        # Recipe 1
        if recipe1_ingredients:
            recipe1 = {
                'title': title1,
                'page_number': page_number,
                'hands_on_time': f"{hands_on_times[0]} minutes" if hands_on_times else "",
                'total_time': f"{total_times[0][0]} {total_times[0][1]}" if total_times else "",
                'servings': f"makes {servings[0]} servings" if servings else "",
                'ingredients': recipe1_ingredients,
                'instructions': direction_lines[:len(direction_lines)//2] if direction_lines else []
            }
            recipes.append(recipe1)
        
        # Recipe 2
        if recipe2_ingredients:
            recipe2 = {
                'title': title2,
                'page_number': page_number,
                'hands_on_time': f"{hands_on_times[1]} minutes" if len(hands_on_times) > 1 else "",
                'total_time': f"{total_times[1][0]} {total_times[1][1]}" if len(total_times) > 1 else "",
                'servings': f"makes {servings[1]} servings" if len(servings) > 1 else "",
                'ingredients': recipe2_ingredients,
                'instructions': direction_lines[len(direction_lines)//2:] if direction_lines else []
            }
            recipes.append(recipe2)
        
        return recipes
    
    def _split_ingredient_line(self, line: str) -> tuple:
        """Split ingredient line - using the improved algorithm"""
        
        # Look for measurement-based boundaries
        measurement_pattern = r'\\b(\\d+(?:[½¼¾]|\\.?\\d*)?\\s*(?:cups?|tbsp|tsp|lbs?|oz|g|kg|ml|L|cloves?)\\b)'
        measurements = list(re.finditer(measurement_pattern, line, re.IGNORECASE))
        
        if len(measurements) >= 2:
            # Find boundary after complete first ingredient
            first_end = measurements[0].end()
            second_start = measurements[1].start()
            
            # Look for natural boundaries (closing parentheses, complete words)
            for i in range(first_end, second_start):
                if i < len(line) and line[i] == ')' and i + 1 < len(line) and line[i + 1] == ' ':
                    remaining = line[i + 1:].strip()
                    if re.match(r'^\\d+(?:[½¼¾])?\\s*(?:cups?|tbsp|tsp|g|ml)', remaining, re.IGNORECASE):
                        return line[:i + 1].strip(), remaining
            
            # Fallback to midpoint between measurements
            mid = (first_end + second_start) // 2
            for offset in range(10):
                if mid + offset < len(line) and line[mid + offset] == ' ':
                    return line[:mid + offset].strip(), line[mid + offset:].strip()
        
        # Simple midpoint split for shorter lines
        if len(line) > 20:
            mid = len(line) // 2
            for offset in range(15):
                if mid + offset < len(line) and line[mid + offset] == ' ':
                    left = line[:mid + offset].strip()
                    right = line[mid + offset:].strip()
                    if len(left) > 3 and len(right) > 3:
                        return left, right
        
        return line.strip(), ""
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate file hash"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _book_exists(self, file_hash: str) -> bool:
        """Check if book exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM books WHERE file_hash = ?", (file_hash,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def _clear_existing_book(self, file_hash: str):
        """Clear existing book data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get book ID
        cursor.execute("SELECT id FROM books WHERE file_hash = ?", (file_hash,))
        result = cursor.fetchone()
        if result:
            book_id = result[0]
            cursor.execute("DELETE FROM recipes WHERE book_id = ?", (book_id,))
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        
        conn.commit()
        conn.close()
    
    def _store_book_metadata(self, file_path: str, file_hash: str) -> int:
        """Store book metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO books (title, author, file_path, file_hash)
            VALUES (?, ?, ?, ?)
        ''', (
            "Canadian Living Ultimate Cookbook",
            "Canadian Living Test Kitchen",
            file_path,
            file_hash
        ))
        
        book_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return book_id
    
    def _store_recipes(self, book_id: int, recipes: List[Dict]) -> int:
        """Store recipes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stored_count = 0
        for recipe in recipes:
            try:
                cursor.execute('''
                    INSERT INTO recipes (
                        book_id, title, page_number, servings, 
                        hands_on_time, total_time, ingredients, instructions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    book_id,
                    recipe['title'],
                    recipe['page_number'],
                    recipe['servings'],
                    recipe['hands_on_time'],
                    recipe['total_time'],
                    json.dumps(recipe['ingredients']),
                    json.dumps(recipe['instructions'])
                ))
                stored_count += 1
            except Exception as e:
                print(f"⚠️ Error storing '{recipe['title']}': {e}")
                continue
        
        conn.commit()
        conn.close()
        return stored_count
    
    def _update_book_status(self, book_id: int, recipe_count: int):
        """Update book status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE books 
            SET status = 'completed', total_recipes = ?
            WHERE id = ?
        ''', (recipe_count, book_id))
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM books WHERE status = 'completed'")
        total_books = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT title, hands_on_time, total_time, servings, page_number
            FROM recipes 
            WHERE title != ''
            ORDER BY RANDOM()
            LIMIT 15
        ''')
        sample_recipes = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_books': total_books,
            'total_recipes': total_recipes,
            'sample_recipes': sample_recipes
        }
    
    def print_stats(self):
        """Print final statistics"""
        stats = self.get_stats()
        
        print("\\n" + "="*70)
        print("🎉 CANADIAN LIVING ULTIMATE COOKBOOK - COMPLETE RESULTS")
        print("="*70)
        
        print(f"📚 Books Processed: {stats['total_books']}")
        print(f"🍽️ Total Recipes: {stats['total_recipes']}")
        
        if stats['sample_recipes']:
            print("\\n🍳 Sample Recipes:")
            for title, hands_on, total, servings, page in stats['sample_recipes']:
                print(f"   📄 {title} (Page {page})")
                if hands_on or total:
                    print(f"      ⏱️ Time: {hands_on} / {total}")
                if servings:
                    print(f"      👥 {servings}")
                print()
        
        print("="*70)
        print("🎉 COOKBOOK PARSING COMPLETE!")
        print("="*70)


def main():
    """Process the complete cookbook"""
    
    parser = CompleteCanadianLivingParser()
    
    print("🍳 Complete Canadian Living Cookbook Parser")
    print("=" * 50)
    
    # Find the PDF
    pdf_path = None
    for folder in [Path("Books"), Path("books"), Path("books_archive")]:
        if folder.exists():
            pdf_files = list(folder.glob("Canadian-Living*.pdf"))
            if pdf_files:
                pdf_path = str(pdf_files[0])
                break
    
    if not pdf_path:
        print("❌ Canadian Living cookbook PDF not found")
        return
    
    print(f"📚 Found cookbook: {pdf_path}")
    
    # Process the entire cookbook
    success = parser.process_complete_cookbook(pdf_path)
    
    if success:
        parser.print_stats()
    else:
        print("❌ Failed to process cookbook")


if __name__ == "__main__":
    main()
