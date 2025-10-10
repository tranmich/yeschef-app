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
    
    def _build_analysis_prompt(self, items: List[Dict], spacy_metadata: Optional[Dict]) -> str:
        """Build the prompt for LLM analysis"""
        
        # Format items with IDs for tracking
        items_text = "\n".join([f"{i+1}. {item.get('name', 'Unknown')}" for i, item in enumerate(items)])
        
        prompt = f"""You are a grocery shopping assistant. Analyze these items and determine which should be combined into single grocery list entries.

GROCERY ITEMS ({len(items)} total):
{items_text}

COMBINING RULES:

✅ SHOULD COMBINE:
- Same ingredient, same quality: "2 cups flour" + "1 cup flour" = "3 cups flour"
- Stock and broth are interchangeable: "chicken stock" + "chicken broth" = "chicken stock/broth"
- Same herb, same preparation: "1 tbsp chopped parsley" + "2 tbsp chopped parsley" = "3 tbsp chopped parsley"
- Plain salt entries: "salt to taste" + "salt (as needed)" = "salt to taste"
- Same olive oil without quality difference: "olive oil" + "extra virgin olive oil" (if no quality specified) = "olive oil"

❌ MUST STAY SEPARATE - BE VERY STRICT ABOUT THESE:
- **Different cuts of meat:** "chicken breast" ≠ "chicken thigh" ≠ "chicken wings"
- **Different forms of herbs:** "chopped parsley" ≠ "parsley sprigs" ≠ "parsley leaves" ≠ "garnish parsley"
- **CRITICAL: Different pepper types:** "black pepper" ≠ "red pepper flakes" ≠ "white pepper" ≠ "cayenne"
  * Black pepper = regular table pepper
  * Red pepper flakes = crushed red chilies (SPICY!)
  * These are COMPLETELY DIFFERENT and must stay separate!
- **Different forms of produce:** "fresh tomatoes" ≠ "canned tomatoes" ≠ "sun-dried tomatoes"
- **Items with different uses:** meat ≠ broth (even if same animal)
- **"Salt and Pepper" combos:** Keep "Salt And Pepper To Taste" separate from plain "Salt" or plain "Pepper"

⚠️ BE PRECISE:
- "2 tbsp vinegar" + "3 tbsp vinegar" = COMBINE (same ingredient, can add quantities)
- "6 tbsp butter" is ONE item, not a duplicate
- Don't say "duplicate" unless items are EXACTLY the same
- Don't mix herbs with non-herbs (parsley ≠ lemon juice!)
- When in doubt about form/quality, keep separate

Return JSON with TWO keys:
- "groups": Array of items to combine (only include if 2+ items should merge)
- "separate": Array of items that should stay separate

Only list items in ONE place (either "groups" OR "separate", not both).
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
