"""
🤖 AI Recipe Parser
===================

Uses OpenAI GPT-4 to parse YouTube video content into structured recipe format.
Works with the YouTubeRecipeExtractor to convert extracted text into YesChef recipes.

Author: GitHub Copilot
Date: October 2, 2025
"""

import os
import json
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

# OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ openai package not installed. Install with: pip install openai")

load_dotenv()
logger = logging.getLogger(__name__)


class AIRecipeParser:
    """
    Parse recipe content from text using OpenAI GPT-4
    
    Takes raw text (from YouTube videos, web pages, etc.) and converts it
    into structured recipe format suitable for YesChef database.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Recipe Parser
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter")
        
        # Set API key
        openai.api_key = self.api_key
        logger.info("✅ AI Recipe Parser initialized with OpenAI GPT-4")
    
    def parse_youtube_recipe(self, combined_text: str, video_data: Dict, source_url: str) -> Optional[Dict]:
        """
        Parse recipe from YouTube video content
        
        Args:
            combined_text: Combined text from video (title + description + transcript)
            video_data: Video metadata dict
            source_url: Original YouTube URL
            
        Returns:
            Dict with structured recipe data or None if parsing fails
        """
        logger.info(f"🤖 Starting AI recipe parsing for: {video_data.get('title', 'Unknown')}")
        logger.info(f"   Input text length: {len(combined_text)} characters")
        
        # Create parsing prompt
        prompt = self._create_youtube_parsing_prompt(combined_text, video_data, source_url)
        
        try:
            # Call OpenAI GPT-4
            logger.info("📡 Calling OpenAI GPT-4...")
            
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",  # or "gpt-4" if you don't have turbo access
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert recipe extraction system. You analyze cooking video content and extract structured recipe data. Always return valid JSON only, no markdown or explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},  # Force JSON response
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=2000  # Enough for detailed recipes
            )
            
            # Parse response
            recipe_json = response.choices[0].message.content
            recipe_data = json.loads(recipe_json)
            
            # Add source information
            recipe_data['source'] = 'YouTube'
            recipe_data['source_url'] = source_url
            recipe_data['source_title'] = video_data.get('title', '')
            recipe_data['source_channel'] = video_data.get('channel', '')
            recipe_data['thumbnail_url'] = video_data.get('thumbnail_url', '')
            
            logger.info(f"✅ Successfully parsed recipe: {recipe_data.get('title', 'Unknown')}")
            logger.info(f"   Ingredients: {len(recipe_data.get('ingredients', []))}")
            logger.info(f"   Instructions: {len(recipe_data.get('instructions', []))}")
            
            return recipe_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ AI parsing failed: {e}")
            return None
    
    def _create_youtube_parsing_prompt(self, combined_text: str, video_data: Dict, source_url: str) -> str:
        """
        Create the prompt for OpenAI to parse YouTube recipe content
        
        Args:
            combined_text: Combined video content
            video_data: Video metadata
            source_url: YouTube URL
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
Extract recipe information from this YouTube cooking video content and format it as JSON.

VIDEO INFORMATION:
- Title: {video_data.get('title', 'Unknown')}
- Channel: {video_data.get('channel', 'Unknown')}
- Duration: {video_data.get('duration_formatted', 'Unknown')}
- URL: {source_url}

VIDEO CONTENT:
{combined_text}

EXTRACTION INSTRUCTIONS:
Extract and return recipe data in this EXACT JSON format:

{{
  "title": "Recipe name from video",
  "description": "Brief 1-2 sentence description of the recipe",
  "servings": "number or range (e.g., '4', '4-6')",
  "prep_time": "preparation time in minutes (number only, or null if not mentioned)",
  "cook_time": "cooking time in minutes (number only, or null if not mentioned)",
  "total_time": "total time in minutes (number only, or null if not mentioned)",
  "difficulty": "easy, medium, or hard (estimate based on steps)",
  "ingredients": [
    "ingredient with quantity (e.g., '2 cups all-purpose flour')",
    "ingredient with quantity (e.g., '1 tablespoon olive oil')",
    "ingredient with quantity (e.g., '1 teaspoon salt')"
  ],
  "instructions": [
    "Detailed instruction with times/temps if mentioned",
    "Another detailed instruction with techniques",
    "Continue with remaining instructions in chronological order"
  ],
  "tips": [
    "Optional cooking tip or variation",
    "Storage instructions",
    "Serving suggestions"
  ],
  "tags": ["tag1", "tag2", "tag3"],
  "cuisine": "cuisine type (e.g., Italian, Mexican, American)",
  "category": "meal category (e.g., dinner, dessert, breakfast)"
}}

CRITICAL RULES:
1. Extract ALL ingredients mentioned with their EXACT quantities
2. Preserve measurements exactly (cups, tablespoons, grams, ounces, etc.)
3. Keep instruction steps in chronological order
4. Include cooking times, temperatures, and techniques in instructions
5. DO NOT include step numbers like "Step 1:", "Step 2:" - just the instruction text
6. If prep_time, cook_time, or total_time aren't mentioned, set to null
7. Estimate difficulty: easy (< 5 steps), medium (5-10 steps), hard (10+ steps or complex techniques)
8. Extract any tips, variations, or serving suggestions mentioned
9. Add relevant tags (cooking methods, main ingredients, dietary info)
10. Identify cuisine and category based on recipe characteristics
11. Return ONLY valid JSON, no markdown formatting or explanations
12. If information is unclear, use your best judgment based on recipe context

Focus on accuracy and completeness. This recipe will be reviewed by the user before saving.
"""
        return prompt
    
    def parse_generic_recipe(self, text: str, source: str = "text", source_url: Optional[str] = None) -> Optional[Dict]:
        """
        Parse recipe from generic text (not specifically YouTube)
        
        Args:
            text: Recipe text to parse
            source: Source type (e.g., "text", "webpage", "manual")
            source_url: Optional source URL
            
        Returns:
            Dict with structured recipe data or None if parsing fails
        """
        logger.info(f"🤖 Parsing recipe from {source}")
        logger.info(f"   Input text length: {len(text)} characters")
        
        prompt = f"""
Extract recipe information from this text and format it as JSON.

SOURCE: {source}
{f"URL: {source_url}" if source_url else ""}

RECIPE TEXT:
{text}

Extract and return recipe data in this EXACT JSON format:

{{
  "title": "Recipe name",
  "description": "Brief description",
  "servings": "number or range",
  "prep_time": "prep time in minutes (number only, or null)",
  "cook_time": "cook time in minutes (number only, or null)",
  "total_time": "total time in minutes (number only, or null)",
  "difficulty": "easy, medium, or hard",
  "ingredients": ["ingredient with quantity", ...],
  "instructions": ["First instruction without step number", "Second instruction", ...],
  "tips": ["tip 1", ...],
  "tags": ["tag1", "tag2", ...],
  "cuisine": "cuisine type",
  "category": "meal category"
}}

RULES:
- Extract ALL ingredients with exact quantities
- Keep instruction steps in order
- Include times and temperatures in instructions
- Set prep_time, cook_time, total_time to null if not mentioned
- Return ONLY valid JSON, no markdown or explanations

Focus on accuracy. This recipe will be reviewed before saving.
"""
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert recipe extraction system. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )
            
            recipe_json = response.choices[0].message.content
            recipe_data = json.loads(recipe_json)
            
            # Add source information
            recipe_data['source'] = source
            if source_url:
                recipe_data['source_url'] = source_url
            
            logger.info(f"✅ Successfully parsed recipe: {recipe_data.get('title', 'Unknown')}")
            return recipe_data
            
        except Exception as e:
            logger.error(f"❌ AI parsing failed: {e}")
            return None
    
    def estimate_cost(self, text_length: int) -> Dict[str, float]:
        """
        Estimate OpenAI API cost for parsing
        
        Args:
            text_length: Length of text to parse in characters
            
        Returns:
            Dict with cost estimates
        """
        # Rough token estimation (1 token ≈ 4 characters)
        estimated_input_tokens = text_length // 4
        estimated_output_tokens = 500  # Typical recipe response
        
        # GPT-4 Turbo pricing (as of Oct 2024)
        input_cost_per_1k = 0.01  # $0.01 per 1K input tokens
        output_cost_per_1k = 0.03  # $0.03 per 1K output tokens
        
        input_cost = (estimated_input_tokens / 1000) * input_cost_per_1k
        output_cost = (estimated_output_tokens / 1000) * output_cost_per_1k
        total_cost = input_cost + output_cost
        
        return {
            'estimated_input_tokens': estimated_input_tokens,
            'estimated_output_tokens': estimated_output_tokens,
            'estimated_cost_usd': round(total_cost, 4),
            'input_cost': round(input_cost, 4),
            'output_cost': round(output_cost, 4)
        }


# Convenience function for testing
def test_parse_youtube_recipe(combined_text: str, video_data: Dict, source_url: str):
    """
    Test AI recipe parsing
    
    Args:
        combined_text: Combined video content
        video_data: Video metadata
        source_url: YouTube URL
    """
    try:
        parser = AIRecipeParser()
        
        # Estimate cost
        cost = parser.estimate_cost(len(combined_text))
        print(f"\n💰 Estimated cost: ${cost['estimated_cost_usd']:.4f}")
        print(f"   Input tokens: ~{cost['estimated_input_tokens']}")
        print(f"   Output tokens: ~{cost['estimated_output_tokens']}")
        
        # Parse recipe
        print(f"\n🤖 Parsing recipe...")
        recipe_data = parser.parse_youtube_recipe(combined_text, video_data, source_url)
        
        if recipe_data:
            print("\n" + "="*80)
            print("✅ RECIPE PARSING SUCCESSFUL!")
            print("="*80)
            
            print(f"\n📋 RECIPE: {recipe_data['title']}")
            print(f"   Description: {recipe_data.get('description', 'N/A')}")
            print(f"   Servings: {recipe_data.get('servings', 'N/A')}")
            print(f"   Difficulty: {recipe_data.get('difficulty', 'N/A')}")
            print(f"   Prep time: {recipe_data.get('prep_time', 'N/A')} min")
            print(f"   Cook time: {recipe_data.get('cook_time', 'N/A')} min")
            
            print(f"\n🥘 INGREDIENTS ({len(recipe_data.get('ingredients', []))}):")
            for i, ing in enumerate(recipe_data.get('ingredients', [])[:10], 1):
                print(f"   {i}. {ing}")
            if len(recipe_data.get('ingredients', [])) > 10:
                print(f"   ... and {len(recipe_data['ingredients']) - 10} more")
            
            print(f"\n👨‍🍳 INSTRUCTIONS ({len(recipe_data.get('instructions', []))}):")
            for i, inst in enumerate(recipe_data.get('instructions', [])[:5], 1):
                print(f"   {i}. {inst[:100]}{'...' if len(inst) > 100 else ''}")
            if len(recipe_data.get('instructions', [])) > 5:
                print(f"   ... and {len(recipe_data['instructions']) - 5} more steps")
            
            if recipe_data.get('tips'):
                print(f"\n💡 TIPS:")
                for tip in recipe_data.get('tips', [])[:3]:
                    print(f"   • {tip}")
            
            if recipe_data.get('tags'):
                print(f"\n🏷️  TAGS: {', '.join(recipe_data.get('tags', []))}")
            
            print(f"\n📺 SOURCE:")
            print(f"   Channel: {recipe_data.get('source_channel', 'N/A')}")
            print(f"   URL: {recipe_data.get('source_url', 'N/A')}")
            
            print("\n" + "="*80)
            print("🎉 Recipe is ready to save to YesChef database!")
            print("="*80)
            
            return recipe_data
        else:
            print("\n❌ Recipe parsing failed")
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("🤖 AI Recipe Parser - Test Mode")
    print("="*80)
    print("\nThis module parses recipe content using OpenAI GPT-4")
    print("\nTo test, use:")
    print("  from ai_recipe_parser import AIRecipeParser")
    print("  parser = AIRecipeParser()")
    print("  recipe = parser.parse_youtube_recipe(text, video_data, url)")
