"""
Quick diagnostic to check YouTube integration status
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

def check_youtube_integration():
    print("="*80)
    print("🔍 YOUTUBE INTEGRATION DIAGNOSTIC")
    print("="*80)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"   YOUTUBE_API_KEY: {'✅ SET' if youtube_key else '❌ MISSING'}")
    if youtube_key:
        print(f"      Value: {youtube_key[:15]}...")
    
    print(f"   OPENAI_API_KEY: {'✅ SET' if openai_key else '❌ MISSING'}")
    if openai_key:
        print(f"      Value: {openai_key[:20]}...")
    
    # Try to import and initialize YouTube extractor
    print("\n📦 Package Imports:")
    try:
        from googleapiclient.discovery import build
        print("   ✅ google-api-python-client installed")
    except ImportError as e:
        print(f"   ❌ google-api-python-client NOT installed: {e}")
        return
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        print("   ✅ youtube-transcript-api installed")
    except ImportError as e:
        print(f"   ❌ youtube-transcript-api NOT installed: {e}")
        return
    
    try:
        import openai
        print("   ✅ openai installed")
    except ImportError as e:
        print(f"   ❌ openai NOT installed: {e}")
        return
    
    # Try to initialize YouTube extractor
    print("\n🎥 YouTube Extractor Initialization:")
    try:
        from core_systems.youtube_recipe_extractor import YouTubeRecipeExtractor
        print("   ✅ YouTubeRecipeExtractor class loaded")
        
        extractor = YouTubeRecipeExtractor(api_key=youtube_key)
        print("   ✅ YouTubeRecipeExtractor initialized successfully!")
        
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Try to initialize UniversalRecipeImporter
    print("\n🚀 UniversalRecipeImporter Initialization:")
    try:
        from core_systems.recipe_importer import UniversalRecipeImporter
        print("   ✅ UniversalRecipeImporter class loaded")
        
        importer = UniversalRecipeImporter()
        print("   ✅ UniversalRecipeImporter initialized")
        
        if importer.youtube_extractor:
            print("   ✅ YouTube extractor is available in importer!")
        else:
            print("   ❌ YouTube extractor is NOT available in importer")
            
    except Exception as e:
        print(f"   ❌ Failed to initialize importer: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test URL detection
    print("\n🔍 URL Detection Test:")
    test_urls = [
        "https://youtube.com/watch?v=abc123",
        "https://youtu.be/abc123",
        "https://youtu.be/afM7gVxT-Q8?si=BM5gb-bafQlW9jTP",
        "https://www.allrecipes.com/recipe/123/test"
    ]
    
    for url in test_urls:
        is_youtube = importer._is_youtube_url(url)
        print(f"   {url}")
        print(f"   → {'🎥 YouTube' if is_youtube else '🌐 Regular web'}")
    
    print("\n" + "="*80)
    print("✅ DIAGNOSTIC COMPLETE")
    print("="*80)
    
    if not importer.youtube_extractor:
        print("\n⚠️  PROBLEM IDENTIFIED:")
        print("   YouTube extractor is not initialized in the UniversalRecipeImporter")
        print("   Check Flask server logs for initialization errors")
        print("   Make sure YOUTUBE_API_KEY is set in Railway environment variables")
    else:
        print("\n✅ YouTube integration appears to be working!")
        print("   The issue might be in the import flow logic")

if __name__ == "__main__":
    check_youtube_integration()
