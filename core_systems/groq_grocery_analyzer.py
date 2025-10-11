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
        
        # Pattern: number + unit at the start
        # Matches: "9 cups", "2 tbsp", "1.5 tsp", "0.5 cup"
        pattern = r'^([\d\.\/\s]+(?:cup|cups|tablespoon|tablespoons|tbsp|tsp|teaspoon|teaspoons|ounce|ounces|oz|pound|pounds|lb|lbs|gram|grams|g|kg|clove|cloves)?)\s+'
        
        match = re.match(pattern, item_name, re.IGNORECASE)
        if match:
            quantity = match.group(1).strip()
            ingredient = item_name[len(match.group(0)):].strip()
            return (quantity, ingredient)
        
        # Check for "as needed" pattern
        if '(as needed)' in item_name.lower() or 'to taste' in item_name.lower():
            # Remove these descriptors to get clean ingredient
            clean = re.sub(r'\(as needed\)|\(to taste\)|as needed|to taste', '', item_name, flags=re.IGNORECASE).strip()
            return ('as needed', clean)
        
        # No quantity found, return empty quantity
        return ('', item_name)
    
    def _build_analysis_prompt(self, items: List[Dict], spacy_metadata: Optional[Dict]) -> str:
        """Build the prompt for LLM analysis"""
        
        # Parse items into structured format (quantity + ingredient)
        structured_items = []
        for i, item in enumerate(items):
            name = item.get('name', 'Unknown')
            quantity, ingredient = self._parse_quantity(name)
            structured_items.append({
                'index': i + 1,
                'full_name': name,
                'ingredient': ingredient,
                'quantity': quantity
            })
        
        # Format for display
        items_text = "\n".join([
            f"{item['index']}. {item['full_name']}" 
            for item in structured_items
        ])
        
        prompt = f"""Analyze these grocery items and suggest which should be combined.

ITEMS:
{items_text}

When analyzing, focus on the INGREDIENT (ignore quantities). But use full_name when listing items.

UNIVERSAL COMBINING PRINCIPLES:

1. SAME HERB/SPICE IN DIFFERENT FORMS = COMBINE
   Examples: 
   - "fresh parsley" + "dried parsley" + "parsley sprigs" = combine
   - "fresh basil" + "basil leaves" = combine
   - "ground cinnamon" + "cinnamon" = combine

2. SAME LIQUID/STOCK = COMBINE
   Examples:
   - "chicken stock" + "chicken broth" = combine (same thing)
   - "lemon juice" + "juice of 1 lemon" = combine
   But: chicken stock ≠ beef stock (different base)

3. SAME INGREDIENT, DIFFERENT PREPARATION = COMBINE
   Examples:
   - "diced onion" + "sliced onion" = combine
   - "grated cheese" + "shredded cheese" = combine
   - "crushed garlic" + "minced garlic" = combine

4. QUALITY DESCRIPTORS DON'T CHANGE INGREDIENT = COMBINE
   Examples:
   - "extra virgin olive oil" + "olive oil" = combine (same oil)
   - "fresh parsley" + "parsley" = combine (same herb)
   - "organic eggs" + "eggs" = combine (same item)

5. DIFFERENT CUTS OF MEAT = NEVER COMBINE
   Examples:
   - chicken breast ≠ chicken thigh (different cuts)
   - ground beef ≠ beef stew meat (different cuts)
   - pork chops ≠ pork tenderloin (different cuts)

6. MEAT VS BROTH = NEVER COMBINE
   Examples:
   - chicken breast ≠ chicken broth (one is meat, one is liquid)
   - beef steak ≠ beef stock (completely different uses)

7. DIFFERENT SPICE TYPES = NEVER COMBINE
   Examples:
   - black pepper ≠ red pepper flakes (black is table pepper, red is chili)
   - paprika ≠ cayenne (different heat/flavor)
   - cinnamon ≠ nutmeg (different spices)
   But: "black pepper" = "ground black pepper" = "freshly ground pepper" (SAME spice!)

8. DIFFERENT PRODUCE VARIETIES = USUALLY COMBINE
   Examples:
   - "Little Neck clams" + "Manila clams" = combine (both clams)
   - "Roma tomatoes" + "cherry tomatoes" = combine (both tomatoes)

9. FRESH VS CANNED/DRIED = DIFFERENT (DON'T COMBINE)
   Examples:
   - fresh tomatoes ≠ canned tomatoes (different form)
   - fresh herbs ≠ dried herbs (different potency)

CRITICAL RULE: Each item appears in ONLY ONE place!
- If you put an item in a group, DO NOT list it in "separate"
- If you list an item in "separate", DO NOT include it in any group

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
