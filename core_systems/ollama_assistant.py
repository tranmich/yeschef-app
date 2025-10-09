"""
Ollama LLM Integration for Smart Grocery Combining
Uses local Llama 3.2 model for food context understanding
"""
import json
import logging
from typing import List, Dict, Optional
import requests

logger = logging.getLogger(__name__)

class OllamaGroceryAssistant:
    """
    Uses local Ollama (Llama 3.2) for intelligent grocery combining decisions
    """
    
    def __init__(self, model="llama3.2:3b", base_url="http://localhost:11434"):
        """
        Initialize Ollama assistant
        
        Args:
            model: Ollama model to use (default: llama3.2:3b)
            base_url: Ollama API endpoint
        """
        self.model = model
        self.base_url = base_url
        self.available = self._check_availability()
        
        if self.available:
            logger.info(f"✅ Ollama available with model: {model}")
        else:
            logger.warning(f"⚠️ Ollama not available - will use fallback logic")
    
    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.ok:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                return self.model in model_names
            return False
        except Exception as e:
            logger.debug(f"Ollama check failed: {e}")
            return False
    
    def should_combine(self, item1: Dict, item2: Dict) -> Dict:
        """
        Ask LLM if two items should be combined
        
        Args:
            item1: First grocery item {'name': '...', 'core': '...'}
            item2: Second grocery item {'name': '...', 'core': '...'}
            
        Returns:
            {
                'should_combine': bool,
                'reason': str,
                'combined_name': str (if should_combine=True)
            }
        """
        if not self.available:
            return {
                'should_combine': False,
                'reason': 'Ollama not available',
                'llm_used': False
            }
        
        prompt = f"""You are a grocery shopping assistant. Analyze these two items:

Item 1: "{item1['name']}"
Item 2: "{item2['name']}"

Should these be combined into one grocery list item?

Consider:
1. Are they the SAME ingredient? (e.g., "tomatoes" and "roma tomatoes" = YES)
2. Are they DIFFERENT forms? (e.g., "fresh tomatoes" vs "canned tomatoes" = NO)
3. Are they DIFFERENT uses? (e.g., "chicken breast" vs "chicken broth" = NO)
4. Are they DIFFERENT types? (e.g., "black pepper" vs "red pepper" = NO)

Respond ONLY in JSON format:
{{
    "should_combine": true/false,
    "reason": "brief explanation",
    "combined_name": "name if combining" or null
}}"""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=10
            )
            
            if response.ok:
                result = response.json()
                llm_response = json.loads(result['response'])
                llm_response['llm_used'] = True
                
                logger.info(f"🤖 LLM: {item1['name']} + {item2['name']} = "
                           f"{'COMBINE' if llm_response['should_combine'] else 'SEPARATE'}")
                
                return llm_response
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return {'should_combine': False, 'reason': 'API error', 'llm_used': False}
                
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return {'should_combine': False, 'reason': str(e), 'llm_used': False}
    
    def analyze_ambiguous_group(self, items: List[Dict]) -> Dict:
        """
        Analyze a group of items with the same base ingredient
        Ask LLM which should combine and which should separate
        
        Args:
            items: List of grocery items with same base ingredient
                   [{'name': '...', 'core': '...', 'id': '...'}, ...]
        
        Returns:
            {
                'groups': [
                    {'items': [item_ids], 'name': 'combined name'},
                    ...
                ],
                'reason': 'explanation'
            }
        """
        if not self.available or len(items) < 2:
            return {
                'groups': [[item['id'] for item in items]],
                'reason': 'No LLM or single item',
                'llm_used': False
            }
        
        # Format items for LLM
        item_list = "\n".join([f"{i+1}. {item['name']}" for i, item in enumerate(items)])
        
        prompt = f"""You are a grocery shopping assistant. These items share a base ingredient:

{item_list}

Group these items for a grocery list. Items should be SEPARATE if they are:
- Different forms (fresh vs canned)
- Different cuts (chicken breast vs chicken thigh)
- Different uses (tomatoes vs tomato sauce)
- Different types (black pepper vs red pepper)

Items should be COMBINED if they are:
- Same ingredient with minor variations
- Same form and use

Respond ONLY in JSON format:
{{
    "groups": [
        {{"items": [1, 2], "name": "combined name", "reason": "why combined"}},
        {{"items": [3], "name": "item name", "reason": "why separate"}}
    ],
    "explanation": "brief overall explanation"
}}"""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=15
            )
            
            if response.ok:
                result = response.json()
                llm_response = json.loads(result['response'])
                
                # Convert item indices to IDs
                groups_with_ids = []
                for group in llm_response['groups']:
                    item_ids = [items[idx-1]['id'] for idx in group['items']]
                    groups_with_ids.append({
                        'items': item_ids,
                        'name': group['name'],
                        'reason': group.get('reason', '')
                    })
                
                logger.info(f"🤖 LLM grouped {len(items)} items into {len(groups_with_ids)} groups")
                
                return {
                    'groups': groups_with_ids,
                    'explanation': llm_response.get('explanation', ''),
                    'llm_used': True
                }
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return {
                    'groups': [[item['id'] for item in items]],
                    'reason': 'API error',
                    'llm_used': False
                }
                
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return {
                'groups': [[item['id'] for item in items]],
                'reason': str(e),
                'llm_used': False
            }
    
    def explain_combination(self, items: List[str]) -> str:
        """
        Get LLM explanation of why items were combined or separated
        Useful for user-facing messages
        
        Args:
            items: List of item names
            
        Returns:
            Explanation string
        """
        if not self.available:
            return "Combined based on ingredient matching"
        
        item_list = ", ".join(items)
        
        prompt = f"""Briefly explain (one sentence) why these grocery items are grouped together:

{item_list}

Keep it simple and user-friendly."""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=5
            )
            
            if response.ok:
                result = response.json()
                return result['response'].strip()
            else:
                return "Combined based on similar ingredients"
                
        except Exception as e:
            logger.error(f"Ollama explanation failed: {e}")
            return "Combined based on ingredient matching"


# Singleton instance
_ollama_assistant = None

def get_ollama_assistant() -> OllamaGroceryAssistant:
    """Get or create Ollama assistant singleton"""
    global _ollama_assistant
    if _ollama_assistant is None:
        _ollama_assistant = OllamaGroceryAssistant()
    return _ollama_assistant


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    assistant = get_ollama_assistant()
    
    if assistant.available:
        # Test 1: Should these combine?
        print("\n🧪 Test 1: Chicken Thighs vs Chicken Broth")
        result = assistant.should_combine(
            {'name': '2 Chicken Thighs', 'core': 'thigh'},
            {'name': '1 cup Chicken Broth', 'core': 'broth'}
        )
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Test 2: Group analysis
        print("\n🧪 Test 2: Multiple chicken items")
        items = [
            {'id': '1', 'name': '2 Bone-In Chicken Thighs', 'core': 'thigh'},
            {'id': '2', 'name': '2 Chicken Breasts', 'core': 'breast'},
            {'id': '3', 'name': '9 cups Chicken Stock', 'core': 'stock'},
            {'id': '4', 'name': '0.5 cup Chicken Broth', 'core': 'broth'}
        ]
        result = assistant.analyze_ambiguous_group(items)
        print(f"Result: {json.dumps(result, indent=2)}")
    else:
        print("❌ Ollama not available. Please install and run Ollama with llama3.2:3b")
