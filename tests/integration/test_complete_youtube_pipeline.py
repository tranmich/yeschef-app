"""
🎯 Complete YouTube to Recipe Pipeline Test
============================================

Tests the full pipeline:
1. YouTube URL → Video extraction (YouTubeRecipeExtractor)
2. Video content → AI parsing (AIRecipeParser)
3. Display final recipe ready for database

Author: GitHub Copilot
Date: October 2, 2025
"""

import sys
import os
from dotenv import load_dotenv

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
load_dotenv()

from core_systems.youtube_recipe_extractor import YouTubeRecipeExtractor
from core_systems.ai_recipe_parser import AIRecipeParser

def test_complete_pipeline(url: str):
    """
    Test the complete YouTube → Recipe pipeline
    
    Args:
        url: YouTube video URL
    """
    print("="*80)
    print("🎯 COMPLETE YOUTUBE TO RECIPE PIPELINE TEST")
    print("="*80)
    
    # Get API keys
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not youtube_key:
        print("\n❌ ERROR: YOUTUBE_API_KEY not found")
        return
    
    if not openai_key:
        print("\n❌ ERROR: OPENAI_API_KEY not found")
        return
    
    print(f"\n✅ YouTube API Key: {youtube_key[:15]}...")
    print(f"✅ OpenAI API Key: {openai_key[:20]}...")
    
    try:
        # STEP 1: Extract YouTube video content
        print("\n" + "="*80)
        print("STEP 1: EXTRACTING YOUTUBE VIDEO CONTENT")
        print("="*80)
        print(f"\n📹 URL: {url}")
        
        extractor = YouTubeRecipeExtractor(api_key=youtube_key)
        extraction_result = extractor.extract_recipe_content(url)
        
        if not extraction_result['success']:
            print(f"\n❌ Extraction failed: {extraction_result['error']}")
            return
        
        video_data = extraction_result['video_data']
        combined_text = extraction_result['combined_text']
        
        print(f"\n✅ Extraction successful!")
        print(f"   Title: {video_data.title}")
        print(f"   Channel: {video_data.channel}")
        print(f"   Duration: {video_data.duration_formatted}")
        print(f"   Transcript: {'✅ Available' if extraction_result['has_transcript'] else '❌ Not available'}")
        print(f"   Combined text: {len(combined_text)} characters")
        
        # STEP 2: Parse recipe with AI
        print("\n" + "="*80)
        print("STEP 2: PARSING RECIPE WITH AI (GPT-4)")
        print("="*80)
        
        parser = AIRecipeParser(api_key=openai_key)
        
        # Estimate cost
        cost = parser.estimate_cost(len(combined_text))
        print(f"\n💰 Estimated cost: ${cost['estimated_cost_usd']:.4f}")
        print(f"   Input: ~{cost['estimated_input_tokens']} tokens (${cost['input_cost']:.4f})")
        print(f"   Output: ~{cost['estimated_output_tokens']} tokens (${cost['output_cost']:.4f})")
        
        print(f"\n🤖 Calling OpenAI GPT-4...")
        print("   (This may take 10-30 seconds...)")
        
        recipe_data = parser.parse_youtube_recipe(
            combined_text=combined_text,
            video_data=video_data.to_dict(),
            source_url=url
        )
        
        if not recipe_data:
            print("\n❌ Recipe parsing failed")
            return
        
        # STEP 3: Display final recipe
        print("\n" + "="*80)
        print("STEP 3: FINAL RECIPE (READY FOR DATABASE)")
        print("="*80)
        
        print(f"\n📋 RECIPE DETAILS:")
        print(f"   Title: {recipe_data['title']}")
        print(f"   Description: {recipe_data.get('description', 'N/A')}")
        print(f"   Servings: {recipe_data.get('servings', 'N/A')}")
        print(f"   Difficulty: {recipe_data.get('difficulty', 'N/A')}")
        print(f"   Prep Time: {recipe_data.get('prep_time', 'N/A')} min")
        print(f"   Cook Time: {recipe_data.get('cook_time', 'N/A')} min")
        print(f"   Total Time: {recipe_data.get('total_time', 'N/A')} min")
        print(f"   Cuisine: {recipe_data.get('cuisine', 'N/A')}")
        print(f"   Category: {recipe_data.get('category', 'N/A')}")
        
        ingredients = recipe_data.get('ingredients', [])
        print(f"\n🥘 INGREDIENTS ({len(ingredients)}):")
        for i, ing in enumerate(ingredients, 1):
            print(f"   {i:2d}. {ing}")
        
        instructions = recipe_data.get('instructions', [])
        print(f"\n👨‍🍳 INSTRUCTIONS ({len(instructions)} steps):")
        for i, inst in enumerate(instructions, 1):
            print(f"\n   Step {i}:")
            print(f"   {inst}")
        
        tips = recipe_data.get('tips', [])
        if tips:
            print(f"\n💡 TIPS & NOTES ({len(tips)}):")
            for i, tip in enumerate(tips, 1):
                print(f"   {i}. {tip}")
        
        tags = recipe_data.get('tags', [])
        if tags:
            print(f"\n🏷️  TAGS: {', '.join(tags)}")
        
        print(f"\n📺 SOURCE INFORMATION:")
        print(f"   Source: {recipe_data['source']}")
        print(f"   Channel: {recipe_data['source_channel']}")
        print(f"   Video URL: {recipe_data['source_url']}")
        print(f"   Thumbnail: {recipe_data.get('thumbnail_url', 'N/A')}")
        
        # Success summary
        print("\n" + "="*80)
        print("🎉 PIPELINE COMPLETE - RECIPE READY!")
        print("="*80)
        
        print(f"\n✅ Successfully converted YouTube video to YesChef recipe!")
        print(f"   Video: '{video_data.title}'")
        print(f"   Recipe: '{recipe_data['title']}'")
        print(f"   Ingredients: {len(ingredients)}")
        print(f"   Steps: {len(instructions)}")
        print(f"   Processing cost: ~${cost['estimated_cost_usd']:.4f}")
        
        print(f"\n📤 NEXT STEPS:")
        print("   1. This recipe data is ready to save to PostgreSQL")
        print("   2. Mobile app will receive this in RecipeImportReviewScreen")
        print("   3. User can edit/customize before final save")
        
        return recipe_data
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def quick_test():
    """Quick test with user input"""
    print("🎯 YouTube to Recipe Pipeline - Quick Test")
    print("="*80)
    
    url = input("\nEnter YouTube cooking video URL (or press Enter for default): ").strip()
    if not url:
        # Default to a popular cooking video
        url = "https://www.youtube.com/watch?v=CfchYxh7Q9g"  # Ground Beef recipe
        print(f"Using default: {url}")
    
    print("\n" + "-"*80)
    result = test_complete_pipeline(url)
    print("-"*80)
    
    if result:
        save = input("\n💾 Would you like to see the JSON output? (y/n): ").strip().lower()
        if save == 'y':
            import json
            print("\n" + "="*80)
            print("JSON OUTPUT (for database):")
            print("="*80)
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    quick_test()
