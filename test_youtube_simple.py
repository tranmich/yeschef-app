"""
Quick test of YouTube Recipe Extractor
"""
import os
import sys
from dotenv import load_dotenv

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
load_dotenv()

from core_systems.youtube_recipe_extractor import YouTubeRecipeExtractor

def main():
    print("="*80)
    print("🎥 YouTube Recipe Extractor - Quick Test")
    print("="*80)
    
    # Check API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("\n❌ ERROR: YOUTUBE_API_KEY not found in environment")
        return
    
    print(f"\n✅ API Key loaded: {api_key[:15]}...")
    
    # Test URL - Popular cooking video
    url = input("\nEnter YouTube URL (or press Enter for default): ").strip()
    if not url:
        url = "https://www.youtube.com/watch?v=3AAdKl1UYZs"  # Babish Carbonara
        print(f"Using default: {url}")
    
    print("\n" + "-"*80)
    print("🔄 Extracting video content...")
    print("-"*80)
    
    try:
        # Initialize extractor
        extractor = YouTubeRecipeExtractor(api_key=api_key)
        print("✅ YouTube extractor initialized")
        
        # Extract content
        result = extractor.extract_recipe_content(url)
        
        if result['success']:
            print("\n" + "="*80)
            print("✅ EXTRACTION SUCCESSFUL!")
            print("="*80)
            
            video_data = result['video_data']
            
            print(f"\n📹 VIDEO INFORMATION:")
            print(f"   Title: {video_data.title}")
            print(f"   Channel: {video_data.channel}")
            print(f"   Duration: {video_data.duration_formatted}")
            print(f"   Views: {video_data.view_count:,}")
            print(f"   Published: {video_data.published_at}")
            
            print(f"\n📝 CONTENT EXTRACTION:")
            print(f"   Description length: {len(video_data.description)} characters")
            print(f"   Transcript available: {'✅ YES' if result['has_transcript'] else '❌ NO'}")
            if result['has_transcript']:
                print(f"   Transcript length: {len(video_data.transcript)} characters")
            print(f"   Combined text: {len(result['combined_text'])} characters")
            
            if video_data.tags:
                print(f"\n🏷️  TAGS: {', '.join(video_data.tags[:8])}")
            
            print(f"\n📄 DESCRIPTION PREVIEW (first 400 chars):")
            print("-" * 80)
            print(video_data.description[:400])
            if len(video_data.description) > 400:
                print("...")
            print("-" * 80)
            
            if result['has_transcript']:
                print(f"\n🎤 TRANSCRIPT PREVIEW (first 400 chars):")
                print("-" * 80)
                print(video_data.transcript[:400])
                if len(video_data.transcript) > 400:
                    print("...")
                print("-" * 80)
            
            print(f"\n📋 COMBINED TEXT FOR AI PARSING:")
            print("="*80)
            print("This is what will be sent to OpenAI GPT-4 for recipe extraction:")
            print("="*80)
            print(result['combined_text'][:800])
            if len(result['combined_text']) > 800:
                print("\n... (truncated for display)")
            print("="*80)
            
            print(f"\n✅ Total text ready for AI: {len(result['combined_text'])} characters")
            print("   This will cost approximately $0.01-0.03 to parse with GPT-4")
            
            print("\n" + "="*80)
            print("🎉 YouTube extraction is working perfectly!")
            print("="*80)
            print("\nNext steps:")
            print("1. This extracted text will be sent to OpenAI")
            print("2. GPT-4 will parse it into structured recipe format")
            print("3. Result will be saved to your database")
            print("4. User can review and edit in mobile app")
            
        else:
            print(f"\n❌ EXTRACTION FAILED")
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
