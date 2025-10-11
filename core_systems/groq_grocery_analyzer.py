"""
Groq LLM Integration for Smart Grocery Combining
Uses Groq's fast LLM API for intelligent ingredient analysis
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
    logger.info("✅ Groq SDK imported successfully")
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("⚠️ Groq SDK not available - install with: pip install groq")

class GroqGroceryAnalyzer:
    """
    Uses Groq's LLM to intelligently analyze grocery items for combining
    """
    
    def __init__(self):
        self.client = None
        self.model = "llama-3.1-8b-instant"  # Fast & free tier!
        
        logger.info("🔧 Initializing Groq analyzer...")
        logger.info(f"   GROQ_AVAILABLE: {GROQ_AVAILABLE}")
        
        if GROQ_AVAILABLE:
            api_key = os.getenv('GROQ_API_KEY')
            logger.info(f"   API key present: {bool(api_key)}")
            if api_key:
                logger.info(f"   API key starts with: {api_key[:10]}...")
                try:
                    self.client = Groq(api_key=api_key)
                    logger.info("✅ Groq client initialized successfully!")
                except Exception as e:
                    logger.error(f"❌ Groq initialization failed: {e}")
            else:
                logger.warning("⚠️ GROQ_API_KEY not found in environment variables")
                logger.info(f"   Available env vars: {list(os.environ.keys())[:10]}...")
    
    def is_available(self) -> bool:
        """Check if Groq is available and configured"""
        return self.client is not None
    
    def analyze_combining(self, items: List[Dict], spacy_metadata: Optional[Dict] = None) -> Dict:
        """
        Analyze items with LLM to determine smart combining
        
        Args:
            items: List of grocery items with names
            spacy_metadata: Optional spaCy analysis results
            
        Returns:
            Dict with combining suggestions and reasoning
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Groq not available',
                'fallback': 'Using spaCy only'
            }
        
        try:
            # Build prompt with context
            prompt = self._build_analysis_prompt(items, spacy_metadata)
            
            logger.info(f"🤖 Analyzing {len(items)} items with Groq...")
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a grocery shopping assistant. Analyze ingredients and suggest which items should be combined in a grocery list. Focus on food context, avoiding combining items with different uses (e.g., chicken breast vs chicken broth)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            logger.info(f"✅ Groq analysis complete")
            
            return {
                'success': True,
                'analysis': result,
                'model': self.model,
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            logger.error(f"❌ Groq analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback': 'Using spaCy only'
            }
    
    def _parse_quantity(self, item_name: str) -> tuple:
        """
        Parse quantity from item name
        Returns: (quantity, ingredient_name)
        
        Examples:
            "9 cups Chicken Stock" -> ("9 cups", "Chicken Stock")
            "2 tablespoons Olive Oil" -> ("2 tablespoons", "Olive Oil")
            "Salt (as needed)" -> ("as needed", "Salt")
        """
        import re
        
        # First, remove "noise" phrases that don't affect the ingredient
        # These are instructions/suggestions, not part of the ingredient name
        noise_phrases = [
            r'\(as needed\)',
            r'\(to taste\)',
            r'\(to season\)',
            r'\(as desired\)',
            r'\(as required\)',
            r'\(optional\)',
            r'\(if desired\)',
            r'\(if needed\)',
            r'\(for serving\)',
            r'\(for garnish\)',
            r'\(for topping\)',
            r'\(for drizzling\)',
            r'\(for sprinkling\)',
            r'\(for dusting\)',
            r'as needed',
            r'to taste',
            r'to season',
            r'as desired',
            r'optional'
        ]
        
        cleaned_name = item_name
        for phrase in noise_phrases:
            cleaned_name = re.sub(phrase, '', cleaned_name, flags=re.IGNORECASE)
        
        # Clean up extra spaces and parentheses
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name)  # Multiple spaces -> single
        cleaned_name = re.sub(r'\(\s*\)', '', cleaned_name)  # Empty parentheses
        cleaned_name = cleaned_name.strip()
        
        # Pattern: number + unit at the start
        # Matches: "9 cups", "2 tbsp", "1.5 tsp", "0.5 cup"
        pattern = r'^([\d\.\/\s]+(?:cup|cups|tablespoon|tablespoons|tbsp|tsp|teaspoon|teaspoons|ounce|ounces|oz|pound|pounds|lb|lbs|gram|grams|g|kg|clove|cloves)?)\s+'
        
        match = re.match(pattern, cleaned_name, re.IGNORECASE)
        if match:
            quantity = match.group(1).strip()
            ingredient = cleaned_name[len(match.group(0)):].strip()
            return (quantity, ingredient)
        
        # Check if original item had "as needed" pattern (before cleaning)
        if re.search(r'(as needed|to taste|optional)', item_name, re.IGNORECASE):
            return ('as needed', cleaned_name)
        
        # No quantity found, return empty quantity
        return ('', cleaned_name)
    
    def _build_analysis_prompt(self, items: List[Dict], spacy_metadata: Optional[Dict]) -> str:
        """Build the prompt for LLM analysis"""
        
        # Parse items into structured format (quantity + ingredient)
        structured_items = []
        logger.info("\n📋 ===== ITEMS SENT TO GROQ =====")
        for i, item in enumerate(items):
            name = item.get('name', 'Unknown')
            quantity, ingredient = self._parse_quantity(name)
            structured_items.append({
                'index': i + 1,
                'full_name': name,
                'ingredient': ingredient,
                'quantity': quantity
            })
            logger.info(f"   {i+1}. '{name}' → '{ingredient}'")
        logger.info("=================================\n")
        
        # Format for display - show ONLY ingredient names (cleaned) to Groq
        items_text = "\n".join([
            f"{item['index']}. {item['ingredient']}"  # Only send cleaned ingredient
            for item in structured_items
        ])
        
        prompt = f"""Analyze these grocery items using CATEGORY-BASED intelligence.

ITEMS (cleaned ingredient names without quantities):
{items_text}

IMPORTANT: When listing items in groups, use these EXACT ingredient names from the list above!

🗂️ INGREDIENT CATEGORIES - Understand these to make smart decisions:

CATEGORY 1: STOCKS & BROTHS
- chicken stock, beef stock, vegetable broth, fish stock
✅ "chicken stock" + "chicken broth" = SAME ingredient, COMBINE
❌ "chicken stock" + "beef stock" = DIFFERENT ingredients, SEPARATE

CATEGORY 2: COOKING LIQUIDS (all different!)
- water, wine, beer, sake
❌ water ≠ wine ≠ beer (completely different liquids!)

CATEGORY 3: ACIDS (all different!)
- lemon juice, lime juice, vinegar types, orange juice
❌ lemon juice ≠ lime juice ≠ vinegar (different acids!)
✅ "lemon juice" + "juice of 1 lemon" = SAME thing, COMBINE

CATEGORY 4: OILS & FATS
- olive oil, vegetable oil, sesame oil, butter
✅ "olive oil" + "extra virgin olive oil" = SAME oil, COMBINE
❌ "olive oil" + "sesame oil" = DIFFERENT oils, SEPARATE

CATEGORY 5: FRESH HERBS (each is unique flavor!)
- parsley, cilantro, basil, dill, mint, thyme, rosemary
✅ "fresh parsley" + "dried parsley" + "parsley sprigs" = SAME herb, COMBINE
❌ parsley ≠ cilantro ≠ basil (different herbs!)

CATEGORY 6: GROUND SPICES (each is different!)
- black pepper, red pepper flakes, cumin, paprika, cayenne
✅ "black pepper" + "ground black pepper" + "freshly ground pepper" = SAME spice, COMBINE
❌ black pepper ≠ red pepper flakes (completely different spices!)
❌ paprika ≠ cayenne ≠ cumin (all different!)

CATEGORY 7: CONDIMENTS (all different!)
- ketchup, mustard, mayo, soy sauce, hot sauce
❌ ketchup ≠ mustard ≠ mayo (all different condiments!)

CATEGORY 8: BRINED/PICKLED (all different!)
- capers, olives, pickles, pickled jalapeños
❌ capers ≠ olives ≠ pickles (all different!)

CATEGORY 9: CHEESE TYPES (each is different!)
- parmesan, cheddar, mozzarella, feta
✅ "parmesan" + "grated parmesan" + "parmesan cheese" = SAME cheese, COMBINE
❌ parmesan ≠ cheddar ≠ mozzarella (different cheeses!)

CATEGORY 10: PROTEINS (never auto-combine!)
- chicken breast, chicken thigh, ground beef, salmon
❌ chicken breast ≠ chicken thigh (different cuts, different cooking!)
❌ ground beef ≠ beef stew meat (different preparations!)
❌ chicken breast ≠ chicken stock (meat ≠ liquid!)

CATEGORY 11: AROMATICS
- onions, garlic, shallots, leeks, ginger
✅ "diced onion" + "sliced onion" = SAME ingredient, COMBINE
❌ onions ≠ shallots ≠ garlic (different flavors!)

CATEGORY 12: FRESH VEGETABLES
- tomatoes, peppers, carrots, broccoli
✅ "Roma tomatoes" + "cherry tomatoes" = both tomatoes, CAN combine
❌ fresh tomatoes ≠ canned tomatoes (different form!)

🎯 THE GOLDEN RULE:
Within any category: SAME ingredient (different form/prep) = COMBINE
Within any category: DIFFERENT ingredients = SEPARATE (even if same category!)

CRITICAL: Each item appears in ONLY ONE place - either in a group OR in separate, NEVER both!
"""
        
        # Add spaCy context if available
        if spacy_metadata:
            prompt += f"""
SPACY ANALYSIS:
{json.dumps(spacy_metadata, indent=2)}

Use this to understand cores and qualities.

"""
        
        prompt += """
Return JSON with this EXACT format:
{
  "groups": [
    {
      "items": ["item1", "item2"],
      "combined_name": "generic name WITHOUT quantities",
      "reasoning": "why combine"
    }
  ],
  "separate": [
    {
      "item": "item name",
      "reasoning": "why separate"
    }
  ]
}

FOR combined_name:
- Use GENERIC names that show combination (e.g., "Chicken Stock/Broth", "Parmesan Cheese")
- NEVER include quantities (the system adds them automatically)
- Show what's combined (e.g., "Stock/Broth", "Olive Oil", "Parsley", "Salt & Pepper")

Good examples: "Chicken Stock/Broth", "Parmesan Cheese", "Parsley", "Olive Oil", "Salt & Pepper"
Bad examples: "Chicken Stock", "9 cups Chicken Stock", "2 pounds clams"

REMEMBER: Each item appears in ONLY ONE place - either in a group OR in separate, NEVER both!
"""
        
        # Add spaCy context if available
        if spacy_metadata:
            prompt += f"""

ADDITIONAL CONTEXT (spaCy analysis):
{json.dumps(spacy_metadata, indent=2)[:1000]}...

Use this to understand core ingredients.
"""
        
        prompt += """

Return JSON format:
{
  "groups": [
    {
      "items": ["exact item name 1", "exact item name 2"],
      "combined_name": "readable combined name",
      "reasoning": "brief reason"
    }
  ],
  "separate": [
    {
      "item": "exact item name",
      "reasoning": "brief reason why separate"
    }
  ]
}
"""
        
        return prompt
    
    def quick_check(self, item1: str, item2: str) -> Dict:
        """
        Quick check if two items should combine
        Used for on-the-fly decisions
        """
        if not self.is_available():
            return {'should_combine': None, 'reason': 'Groq not available'}
        
        try:
            prompt = f"""Should these two grocery items be combined into one line?

Item 1: {item1}
Item 2: {item2}

Answer with JSON:
{{
  "should_combine": true/false,
  "reason": "brief explanation"
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a grocery shopping assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"❌ Quick check failed: {e}")
            return {'should_combine': None, 'reason': str(e)}


# Global instance
_groq_analyzer = None

def get_groq_analyzer() -> GroqGroceryAnalyzer:
    """Get or create the global Groq analyzer instance"""
    global _groq_analyzer
    if _groq_analyzer is None:
        _groq_analyzer = GroqGroceryAnalyzer()
    return _groq_analyzer
