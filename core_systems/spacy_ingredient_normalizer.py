"""
🧠 SPACY INGREDIENT NORMALIZER - BACKEND ENHANCEMENT LAYER

Provides intelligent combining enhancement for grocery lists using spaCy NLP.
Works as Tier 2 enhancement layer - JavaScript handles instant combining,
this provides smarter refinement when backend is available.

Features:
- Semantic similarity matching
- Novel ingredient handling
- Cross-list merging
- Preparation extraction
- Learning from patterns

Author: YesChef Team
Date: October 8, 2025
"""

import spacy
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict
import re
import logging

logger = logging.getLogger(__name__)

class SpaCyIngredientNormalizer:
    """
    Intelligent ingredient normalizer using spaCy NLP
    """
    
    def __init__(self):
        """Initialize spaCy with medium English model"""
        try:
            self.nlp = spacy.load("en_core_web_md")
            logger.info("✅ spaCy model loaded successfully")
        except OSError:
            logger.error("❌ spaCy model not found. Run: python -m spacy download en_core_web_md")
            raise
        
        # Similarity threshold for combining
        self.similarity_threshold = 0.75
        
        # Known ingredient families (shared with JavaScript for consistency)
        self.ingredient_families = self._load_ingredient_families()
        
        # Preparation keywords
        self.preparation_keywords = {
            'minced', 'chopped', 'diced', 'sliced', 'crushed', 
            'grated', 'shredded', 'julienned', 'cubed', 'whole',
            'fresh', 'dried', 'canned', 'frozen', 'jarred'
        }
    
    def enhance_combining(self, items: List[Dict]) -> Dict:
        """
        Enhance JavaScript combining with spaCy intelligence
        
        Args:
            items: List of grocery items (possibly already combined by JavaScript)
            
        Returns:
            Dict with enhanced items and improvement stats
        """
        logger.info(f"🧠 Enhancing {len(items)} items with spaCy...")
        
        # Extract items that might benefit from enhancement
        needs_enhancement = self._find_items_needing_enhancement(items)
        
        if not needs_enhancement:
            logger.info("✅ JavaScript combining is perfect, no enhancement needed")
            return {
                'enhanced_items': items,
                'improvements': 0,
                'details': []
            }
        
        # Perform semantic analysis
        enhanced = self._semantic_enhance(items, needs_enhancement)
        
        improvements = len(items) - len(enhanced['items'])
        
        logger.info(f"✨ Enhanced: {len(items)} → {len(enhanced['items'])} items ({improvements} improvements)")
        
        return {
            'enhanced_items': enhanced['items'],
            'improvements': improvements,
            'details': enhanced['details']
        }
    
    def _find_items_needing_enhancement(self, items: List[Dict]) -> List[Dict]:
        """
        Find items that might benefit from spaCy's intelligence
        """
        needs_help = []
        
        for item in items:
            # Check if this looks like it might be combinable
            name = item.get('name', '').lower()
            
            # Unknown ingredients (not in common families)
            if not self._is_known_ingredient(name):
                needs_help.append(item)
            # Very specific preparations that might be combinable
            elif any(prep in name for prep in ['finely', 'coarsely', 'roughly']):
                needs_help.append(item)
        
        return needs_help
    
    def _is_known_ingredient(self, name: str) -> bool:
        """Check if ingredient is in known families"""
        for family, variations in self.ingredient_families.items():
            for variation in variations:
                if variation in name:
                    return True
        return False
    
    def _semantic_enhance(self, items: List[Dict], focus_items: List[Dict]) -> Dict:
        """
        Use spaCy to find semantic similarities
        """
        # Create spaCy docs for all items
        item_docs = [(item, self.nlp(item['name'].lower())) for item in items]
        
        # Find semantic groups
        groups = defaultdict(list)
        used = set()
        improvements = []
        
        for i, (item1, doc1) in enumerate(item_docs):
            if i in used:
                continue
            
            # Extract core ingredient
            core1 = self._extract_core_ingredient(doc1)
            group_key = core1.text
            groups[group_key].append(item1)
            used.add(i)
            
            # Find similar items
            for j, (item2, doc2) in enumerate(item_docs):
                if j <= i or j in used:
                    continue
                
                core2 = self._extract_core_ingredient(doc2)
                
                # Calculate similarity
                similarity = doc1.similarity(doc2)
                
                if similarity > self.similarity_threshold:
                    groups[group_key].append(item2)
                    used.add(j)
                    
                    improvements.append({
                        'items': [item1['name'], item2['name']],
                        'similarity': float(similarity),
                        'action': 'combined'
                    })
        
        # Combine groups
        combined_items = []
        for group_key, group_items in groups.items():
            if len(group_items) == 1:
                combined_items.append(group_items[0])
            else:
                # Combine multiple items
                combined = self._combine_semantic_group(group_items)
                combined_items.append(combined)
        
        return {
            'items': combined_items,
            'details': improvements
        }
    
    def _extract_core_ingredient(self, doc) -> any:
        """
        Extract the core ingredient noun from spaCy doc
        """
        # Find the main noun (usually the ingredient)
        nouns = [token for token in doc if token.pos_ == 'NOUN']
        
        if nouns:
            # Return the last noun (usually the ingredient)
            # e.g., "cherry tomatoes" → "tomatoes"
            return nouns[-1]
        
        # Fallback: return last token
        return doc[-1] if len(doc) > 0 else doc
    
    def _combine_semantic_group(self, items: List[Dict]) -> Dict:
        """
        Combine semantically similar items
        """
        # Use the longest/most descriptive name
        base_name = max(items, key=lambda x: len(x['name']))['name']
        
        # Extract preparations from all items
        preparations = set()
        for item in items:
            doc = self.nlp(item['name'].lower())
            for token in doc:
                if token.text in self.preparation_keywords:
                    preparations.add(token.text)
        
        # Build combined name
        display_name = base_name
        if preparations:
            prep_str = ', '.join(sorted(preparations))
            display_name = f"{base_name} ({prep_str})"
        
        return {
            'id': f"spacy-combined-{items[0]['id']}",
            'name': display_name,
            'checked': any(item.get('checked', False) for item in items),
            '_enhanced': True,
            '_spacy_combined': True,
            '_original_items': items,
            '_backendRef': items[0].get('_backendRef', {})
        }
    
    def merge_multiple_lists(self, lists: List[List[Dict]]) -> Dict:
        """
        Intelligently merge multiple grocery lists
        
        Args:
            lists: List of grocery lists to merge
            
        Returns:
            Dict with merged list and statistics
        """
        logger.info(f"🔄 Merging {len(lists)} grocery lists...")
        
        # Flatten all items
        all_items = []
        for list_items in lists:
            all_items.extend(list_items)
        
        logger.info(f"📊 Total items before merge: {len(all_items)}")
        
        # Use semantic enhancement to merge
        merged = self._semantic_enhance(all_items, all_items)
        
        duplicates_found = len(all_items) - len(merged['items'])
        
        logger.info(f"✅ Merged: {len(all_items)} → {len(merged['items'])} items ({duplicates_found} duplicates removed)")
        
        return {
            'merged_items': merged['items'],
            'stats': {
                'input_lists': len(lists),
                'total_items_before': len(all_items),
                'total_items_after': len(merged['items']),
                'duplicates_found': duplicates_found
            },
            'details': merged['details']
        }
    
    def compare_lists(self, list_a: List[Dict], list_b: List[Dict]) -> Dict:
        """
        Compare two grocery lists semantically
        
        Returns what's unique to each list and what's common
        """
        logger.info(f"🔍 Comparing lists: {len(list_a)} vs {len(list_b)} items")
        
        # Create docs
        docs_a = [(item, self.nlp(item['name'].lower())) for item in list_a]
        docs_b = [(item, self.nlp(item['name'].lower())) for item in list_b]
        
        only_in_a = []
        only_in_b = []
        in_both = []
        
        matched_b = set()
        
        # Find matches
        for item_a, doc_a in docs_a:
            best_match = None
            best_similarity = 0
            best_idx = None
            
            for idx, (item_b, doc_b) in enumerate(docs_b):
                if idx in matched_b:
                    continue
                
                similarity = doc_a.similarity(doc_b)
                if similarity > best_similarity and similarity > self.similarity_threshold:
                    best_match = item_b
                    best_similarity = similarity
                    best_idx = idx
            
            if best_match:
                in_both.append({
                    'item_a': item_a['name'],
                    'item_b': best_match['name'],
                    'similarity': float(best_similarity)
                })
                matched_b.add(best_idx)
            else:
                only_in_a.append(item_a)
        
        # Items in B that weren't matched
        for idx, (item_b, doc_b) in enumerate(docs_b):
            if idx not in matched_b:
                only_in_b.append(item_b)
        
        return {
            'only_in_a': only_in_a,
            'only_in_b': only_in_b,
            'in_both': in_both,
            'stats': {
                'unique_to_a': len(only_in_a),
                'unique_to_b': len(only_in_b),
                'common': len(in_both)
            }
        }
    
    def _load_ingredient_families(self) -> Dict[str, List[str]]:
        """
        Load ingredient families (subset for server-side)
        Keep in sync with JavaScript version
        """
        return {
            'garlic': ['garlic', 'garlic clove', 'garlic cloves', 'minced garlic', 
                       'chopped garlic', 'crushed garlic', 'garlic powder'],
            'onion': ['onion', 'onions', 'yellow onion', 'white onion', 'red onion',
                      'sweet onion', 'diced onion', 'chopped onion'],
            'tomato': ['tomato', 'tomatoes', 'cherry tomatoes', 'roma tomatoes',
                       'diced tomatoes', 'crushed tomatoes', 'tomato paste'],
            'potato': ['potato', 'potatoes', 'russet potato', 'red potato',
                       'sweet potato', 'baby potatoes'],
            'carrot': ['carrot', 'carrots', 'baby carrots'],
            'chicken': ['chicken', 'chicken breast', 'chicken thigh', 'chicken wings'],
            'beef': ['beef', 'ground beef', 'beef chuck', 'sirloin'],
            # Add more as needed...
        }


# Singleton instance
_normalizer = None

def get_normalizer() -> SpaCyIngredientNormalizer:
    """Get or create the normalizer singleton"""
    global _normalizer
    if _normalizer is None:
        _normalizer = SpaCyIngredientNormalizer()
    return _normalizer
