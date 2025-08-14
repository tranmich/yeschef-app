"""
Refined PDF Flavor Data Parser for The Flavor Bible
Focuses on extracting actual food ingredients and their pairings
"""
import fitz  # PyMuPDF
import re
import json
from typing import Dict, List, Set
from collections import defaultdict

class RefinedFlavorBibleParser:
    """Enhanced parser that focuses on actual food ingredients"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
        # Common food ingredient keywords to help identify food sections
        self.food_keywords = {
            # Proteins
            'chicken', 'beef', 'pork', 'lamb', 'fish', 'salmon', 'tuna', 'shrimp', 'crab',
            'lobster', 'turkey', 'duck', 'goose', 'veal', 'venison', 'rabbit', 'quail',
            
            # Vegetables
            'onion', 'garlic', 'tomato', 'carrot', 'celery', 'pepper', 'mushroom', 'spinach',
            'lettuce', 'cabbage', 'broccoli', 'cauliflower', 'asparagus', 'artichoke',
            'potato', 'sweet potato', 'corn', 'peas', 'beans', 'cucumber', 'zucchini',
            
            # Fruits
            'apple', 'orange', 'lemon', 'lime', 'banana', 'strawberry', 'blueberry',
            'raspberry', 'grape', 'peach', 'pear', 'cherry', 'plum', 'apricot', 'mango',
            'pineapple', 'avocado', 'coconut', 'fig', 'date',
            
            # Herbs & Spices
            'basil', 'oregano', 'thyme', 'rosemary', 'sage', 'parsley', 'cilantro', 'dill',
            'mint', 'chives', 'tarragon', 'bay', 'cinnamon', 'cumin', 'paprika', 'ginger',
            'turmeric', 'cardamom', 'nutmeg', 'cloves', 'vanilla', 'saffron',
            
            # Grains & Nuts
            'rice', 'wheat', 'barley', 'quinoa', 'oats', 'almond', 'walnut', 'pecan',
            'pistachio', 'cashew', 'hazelnut', 'pine nut', 'peanut',
            
            # Dairy & Others
            'cheese', 'milk', 'cream', 'butter', 'yogurt', 'egg', 'honey', 'maple',
            'chocolate', 'coffee', 'tea', 'wine', 'olive oil', 'vinegar'
        }
    
    def extract_ingredient_sections(self) -> Dict[str, str]:
        """Extract text and identify ingredient sections"""
        
        print("🔍 Extracting ingredient sections from PDF...")
        
        doc = fitz.open(self.pdf_path)
        ingredient_sections = {}
        
        # Look for pages that likely contain ingredient listings
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            # Split into potential ingredient blocks
            blocks = self._split_into_ingredient_blocks(text)
            
            for block in blocks:
                ingredient_name = self._extract_ingredient_name(block)
                if ingredient_name and self._is_likely_food_ingredient(ingredient_name):
                    # Clean and store the ingredient data
                    clean_content = self._clean_ingredient_content(block)
                    if clean_content:
                        ingredient_sections[ingredient_name.lower()] = clean_content
            
            if page_num % 100 == 0:
                print(f"   Processed {page_num + 1}/{len(doc)} pages...")
        
        doc.close()
        print(f"✅ Found {len(ingredient_sections)} ingredient sections")
        return ingredient_sections
    
    def _split_into_ingredient_blocks(self, text: str) -> List[str]:
        """Split page text into potential ingredient blocks"""
        
        # Look for blocks that start with an ingredient name (often in all caps or bold)
        lines = text.split('\n')
        blocks = []
        current_block = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line looks like an ingredient header
            if self._looks_like_ingredient_header(line):
                # Save previous block
                if current_block:
                    blocks.append('\n'.join(current_block))
                # Start new block
                current_block = [line]
            else:
                # Add to current block
                current_block.append(line)
        
        # Don't forget the last block
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def _looks_like_ingredient_header(self, line: str) -> bool:
        """Check if a line looks like an ingredient header"""
        
        # Skip very long lines (likely paragraphs)
        if len(line) > 50:
            return False
        
        # Skip lines with too many non-alphabetic characters
        if len(re.sub(r'[^a-zA-Z\s]', '', line)) < len(line) * 0.7:
            return False
        
        # Check for ingredient patterns
        patterns = [
            r'^[A-Z][A-Z\s-]+$',  # ALL CAPS
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title Case
            r'^[A-Z][a-z]+(?:\s+[a-z]+)*$',  # Sentence case
        ]
        
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        
        return False
    
    def _extract_ingredient_name(self, block: str) -> str:
        """Extract the ingredient name from a block"""
        
        lines = block.split('\n')
        if not lines:
            return ""
        
        # The first line is usually the ingredient name
        first_line = lines[0].strip()
        
        # Clean up the ingredient name
        # Remove parenthetical info
        clean_name = re.sub(r'\([^)]+\)', '', first_line).strip()
        
        # Remove extra formatting
        clean_name = re.sub(r'[^\w\s-]', '', clean_name).strip()
        
        return clean_name
    
    def _is_likely_food_ingredient(self, name: str) -> bool:
        """Check if a name is likely a food ingredient"""
        
        name_lower = name.lower()
        
        # Direct match with known ingredients
        if name_lower in self.food_keywords:
            return True
        
        # Partial match (e.g., "chicken breast" contains "chicken")
        for keyword in self.food_keywords:
            if keyword in name_lower:
                return True
        
        # Skip obvious non-food items
        non_food_indicators = [
            'chapter', 'page', 'index', 'preface', 'acknowledgment', 'introduction',
            'copyright', 'publisher', 'author', 'book', 'recipe', 'cooking', 'chef',
            'restaurant', 'cuisine', 'technique', 'method', 'temperature', 'time'
        ]
        
        for indicator in non_food_indicators:
            if indicator in name_lower:
                return False
        
        # If it's a reasonable length and has food-like characteristics
        if 2 <= len(name_lower) <= 30 and name_lower.replace(' ', '').isalpha():
            return True
        
        return False
    
    def _clean_ingredient_content(self, block: str) -> str:
        """Clean the ingredient content block"""
        
        lines = block.split('\n')[1:]  # Skip the first line (ingredient name)
        
        # Filter out obvious non-pairing content
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line and len(line) < 200:  # Skip very long lines
                clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def parse_pairings_from_content(self, content: str) -> List[str]:
        """Extract pairing ingredients from content"""
        
        pairings = set()
        
        # Common pairing patterns
        pairing_indicators = [
            r'(?:pairs?\s+(?:well\s+)?with|goes?\s+(?:well\s+)?with|complements?)[:\s]*([^.!?]+)',
            r'(?:combines?\s+(?:well\s+)?with|works?\s+(?:well\s+)?with)[:\s]*([^.!?]+)',
            r'(?:served?\s+with|accompanied\s+by)[:\s]*([^.!?]+)'
        ]
        
        for pattern in pairing_indicators:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Split on common delimiters
                ingredients = re.split(r'[,;]|\s+and\s+|\s+or\s+', match)
                for ing in ingredients:
                    clean_ing = self._clean_pairing_ingredient(ing)
                    if clean_ing and self._is_valid_pairing(clean_ing):
                        pairings.add(clean_ing)
        
        # Also look for simple comma-separated lists
        lines = content.split('\n')
        for line in lines:
            if ',' in line and len(line) < 150:  # Likely a list
                ingredients = [ing.strip() for ing in line.split(',')]
                for ing in ingredients:
                    clean_ing = self._clean_pairing_ingredient(ing)
                    if clean_ing and self._is_valid_pairing(clean_ing):
                        pairings.add(clean_ing)
        
        return list(pairings)
    
    def _clean_pairing_ingredient(self, ingredient: str) -> str:
        """Clean a pairing ingredient name"""
        
        # Remove extra whitespace and punctuation
        clean = re.sub(r'[^\w\s-]', '', ingredient).strip()
        
        # Convert to lowercase
        clean = clean.lower()
        
        # Remove extra whitespace
        clean = re.sub(r'\s+', ' ', clean)
        
        return clean
    
    def _is_valid_pairing(self, ingredient: str) -> bool:
        """Check if an ingredient is a valid pairing"""
        
        # Basic validation
        if len(ingredient) < 2 or len(ingredient) > 30:
            return False
        
        # Must be mostly alphabetic
        if not re.match(r'^[a-z\s-]+$', ingredient):
            return False
        
        # Skip common non-ingredient words
        skip_words = {
            'and', 'or', 'the', 'a', 'an', 'with', 'in', 'on', 'at', 'to', 'for',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'this', 'that', 'these', 'those', 'very', 'well', 'good', 'best'
        }
        
        if ingredient in skip_words:
            return False
        
        return True
    
    def run_extraction(self) -> Dict[str, List[str]]:
        """Run the complete extraction process"""
        
        print("🚀 Starting refined ingredient extraction...")
        
        # Extract ingredient sections
        ingredient_sections = self.extract_ingredient_sections()
        
        # Parse pairings for each ingredient
        ingredient_pairings = {}
        
        print("🔬 Parsing pairings for each ingredient...")
        for ingredient, content in ingredient_sections.items():
            pairings = self.parse_pairings_from_content(content)
            if len(pairings) >= 3:  # Only keep ingredients with meaningful pairings
                ingredient_pairings[ingredient] = pairings
        
        print(f"✅ Successfully extracted {len(ingredient_pairings)} ingredients with pairings")
        
        # Save results
        output_data = {
            'metadata': {
                'source': 'The Flavor Bible PDF - Refined Extraction',
                'extraction_date': '2025-08-02',
                'total_ingredients': len(ingredient_pairings),
                'parser_version': '2.0'
            },
            'ingredient_pairings': {}
        }
        
        for ingredient, pairings in ingredient_pairings.items():
            output_data['ingredient_pairings'][ingredient] = {
                'complementary_ingredients': pairings,
                'pairing_count': len(pairings)
            }
        
        # Save to file
        with open('refined_flavor_data.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print("📤 Saved refined data to refined_flavor_data.json")
        
        # Show sample results
        print("\\n📋 Sample extracted ingredients:")
        sample_items = list(ingredient_pairings.items())[:10]
        for ingredient, pairings in sample_items:
            print(f"   {ingredient}: {len(pairings)} pairings")
            print(f"      {pairings[:5]}...")
        
        return ingredient_pairings

def main():
    """Main function"""
    
    print("🍳 Refined Flavor Bible Parser v2.0")
    print("=" * 50)
    
    try:
        parser = RefinedFlavorBibleParser("The-Flavor-Bible (1).pdf")
        extracted_data = parser.run_extraction()
        
        print(f"\\n🎉 Extraction complete!")
        print(f"   Total ingredients: {len(extracted_data)}")
        print(f"   Average pairings per ingredient: {sum(len(p) for p in extracted_data.values()) / len(extracted_data):.1f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
