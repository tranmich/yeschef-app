"""
🧪 YouTube Recipe Extractor - Test Script
==========================================

Tests the YouTube extractor with real cooking videos
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_systems.youtube_recipe_extractor import YouTubeRecipeExtractor, test_extraction
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Test YouTube recipe extraction"""
    
    print("=" * 80)
    print("🎥 YouTube Recipe Extractor - Test Suite")
    print("=" * 80)
    
    # Get API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("\n❌ ERROR: YOUTUBE_API_KEY not found in environment variables")
        print("\nPlease set your YouTube API key:")
        print("1. Add to .env file: YOUTUBE_API_KEY=your_key_here")
        print("2. Or set environment variable: set YOUTUBE_API_KEY=your_key_here")
        return
    
    print(f"\n✅ YouTube API Key found: {api_key[:10]}...")
    
    # Test URLs - Popular cooking videos
    test_videos = [
        {
            'name': 'Babish - Carbonara',
            'url': 'https://www.youtube.com/watch?v=3AAdKl1UYZs',
            'expected': 'Should extract carbonara recipe with pasta, eggs, cheese, pancetta'
        },
        {
            'name': 'Gordon Ramsay - Scrambled Eggs',
            'url': 'https://www.youtube.com/watch?v=PUP7U5vTMM0',
            'expected': 'Should extract simple scrambled eggs recipe'
        },
        {
            'name': 'Kenji López-Alt - Roast Chicken',
            'url': 'https://www.youtube.com/watch?v=Kw6qlz3bvXk',
            'expected': 'Should extract detailed roast chicken recipe'
        }
    ]
    
    # Test each video
    results = []
    for i, video in enumerate(test_videos, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_videos)}: {video['name']}")
        print(f"URL: {video['url']}")
        print(f"Expected: {video['expected']}")
        print('='*80)
        
        try:
            result = test_extraction(video['url'], api_key)
            results.append({
                'name': video['name'],
                'success': result is not None and result['success'],
                'result': result
            })
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            results.append({
                'name': video['name'],
                'success': False,
                'error': str(e)
            })
        
        print("\n" + "-"*80)
        input("Press Enter to continue to next test...")
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\n✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"\n{status} {result['name']}")
        if not result['success'] and 'error' in result:
            print(f"   Error: {result['error']}")
    
    # Detailed analysis of first successful result
    print("\n" + "="*80)
    print("🔍 DETAILED ANALYSIS OF FIRST SUCCESSFUL EXTRACTION")
    print("="*80)
    
    for result in results:
        if result['success'] and result['result']:
            data = result['result']
            video_data = data['video_data']
            
            print(f"\n📹 VIDEO DETAILS:")
            print(f"   Title: {video_data.title}")
            print(f"   Channel: {video_data.channel}")
            print(f"   Duration: {video_data.duration_formatted}")
            print(f"   Views: {video_data.view_count:,}")
            print(f"   Published: {video_data.published_at}")
            print(f"   Thumbnail: {video_data.thumbnail_url}")
            
            print(f"\n📝 CONTENT ANALYSIS:")
            print(f"   Description length: {len(video_data.description)} characters")
            print(f"   Transcript available: {data['has_transcript']}")
            if data['has_transcript']:
                print(f"   Transcript length: {len(video_data.transcript)} characters")
            print(f"   Combined text length: {len(data['combined_text'])} characters")
            
            if video_data.tags:
                print(f"\n🏷️  TAGS: {', '.join(video_data.tags[:5])}")
            
            print(f"\n📄 DESCRIPTION PREVIEW:")
            print("-" * 80)
            print(video_data.description[:300])
            print("...")
            print("-" * 80)
            
            if data['has_transcript']:
                print(f"\n🎤 TRANSCRIPT PREVIEW:")
                print("-" * 80)
                print(video_data.transcript[:300])
                print("...")
                print("-" * 80)
            
            print(f"\n📋 COMBINED TEXT FOR AI (First 500 chars):")
            print("-" * 80)
            print(data['combined_text'][:500])
            print("...")
            print("-" * 80)
            
            break
    
    print("\n" + "="*80)
    print("✅ Testing complete!")
    print("="*80)


def quick_test():
    """Quick test with a single video"""
    print("🎥 Quick YouTube Extraction Test")
    print("=" * 80)
    
    # Get API key
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        api_key = input("\nEnter your YouTube API key: ").strip()
    
    # Get URL
    url = input("\nEnter YouTube video URL (or press Enter for default): ").strip()
    if not url:
        url = "https://www.youtube.com/watch?v=3AAdKl1UYZs"  # Babish Carbonara
        print(f"Using default: {url}")
    
    # Test
    print("\n" + "-"*80)
    result = test_extraction(url, api_key)
    print("-"*80)
    
    if result and result['success']:
        print("\n✅ Extraction successful!")
        print("\nThis data is now ready to be sent to OpenAI for recipe parsing.")
        print(f"Combined text length: {len(result['combined_text'])} characters")
        
        # Show what would be sent to OpenAI
        print("\n📤 This is what will be sent to OpenAI GPT-4:")
        print("="*80)
        print(result['combined_text'][:1000])
        print("...")
        print("="*80)
    else:
        print("\n❌ Extraction failed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'quick':
        quick_test()
    else:
        main()
