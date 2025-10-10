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
        
        if GROQ_AVAILABLE:
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                try:
                    self.client = Groq(api_key=api_key)
                    logger.info("✅ Groq client initialized")
                except Exception as e:
                    logger.error(f"❌ Groq initialization failed: {e}")
            else:
                logger.warning("⚠️ GROQ_API_KEY not found in environment")
    
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
        
        # Format items
        items_text = "\n".join([f"- {item.get('name', 'Unknown')}" for item in items])
        
        prompt = f"""Analyze these grocery items and suggest which should be combined:

ITEMS:
{items_text}

RULES:
1. Different cuts of meat should stay separate (chicken breast ≠ chicken thigh)
2. Meat and broth/stock should stay separate (chicken breast ≠ chicken broth)
3. Stock and broth are the same (combine them)
4. Different pepper types should stay separate (black pepper ≠ red pepper flakes ≠ bell pepper)
5. Fresh vs canned/dried are different (fresh tomatoes ≠ canned tomatoes)
6. Same herb in different forms can combine (fresh parsley + dried parsley)
7. Consider quality descriptors (fresh, canned, frozen, dried)

"""
        
        # Add spaCy context if available
        if spacy_metadata:
            prompt += f"""
SPACY ANALYSIS:
{json.dumps(spacy_metadata, indent=2)}

Use this to help understand core ingredients and qualities.

"""
        
        prompt += """
Return JSON with:
{
  "groups": [
    {
      "items": ["item1", "item2"],
      "combined_name": "suggested name",
      "reasoning": "why these should combine"
    }
  ],
  "separate": [
    {
      "item": "item name",
      "reasoning": "why this stays separate"
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
