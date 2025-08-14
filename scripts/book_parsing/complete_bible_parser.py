"""
Complete Flavor Bible Parser - Parse the entire document
"""
from fixed_flavor_parser import FixedFlavorParser
import time

def parse_complete_flavor_bible():
    """Parse the entire Flavor Bible document in manageable chunks"""
    
    print("🌟 COMPLETE FLAVOR BIBLE PARSING")
    print("=" * 60)
    print("📚 This will parse the entire 962-page Flavor Bible!")
    print("⏱️  Estimated time: 15-30 minutes")
    print("💾 Results will be saved in chunks for safety")
    print()
    
    parser = FixedFlavorParser()
    
    # Parse in chunks to avoid memory issues and allow progress tracking
    chunks = [
        (1, 100),     # Intro/early content
        (100, 200),   # Early ingredients  
        (200, 400),   # Main ingredient section 1
        (400, 600),   # Main ingredient section 2
        (600, 800),   # Main ingredient section 3
        (800, 962)    # Final ingredients + appendices
    ]
    
    all_results = {}
    total_stats = {
        'total_pages_processed': 0,
        'total_ingredients': 0,
        'total_pairings': 0,
        'chunks_completed': 0,
        'processing_start': time.time()
    }
    
    for chunk_num, (start_page, end_page) in enumerate(chunks, 1):
        print(f"\n🔥 CHUNK {chunk_num}/6: Pages {start_page}-{end_page}")
        print("=" * 50)
        
        chunk_start_time = time.time()
        
        # Parse this chunk
        chunk_results = parser.parse_page_range(start_page, end_page)
        
        # Merge results
        all_results.update(chunk_results)
        
        # Update stats
        chunk_pages = len(chunk_results)
        chunk_ingredients = sum(len(page_data['ingredient_sections']) for page_data in chunk_results.values())
        chunk_pairings = parser.stats['total_pairings'] - total_stats['total_pairings']
        
        total_stats['total_pages_processed'] += chunk_pages
        total_stats['total_ingredients'] += chunk_ingredients
        total_stats['total_pairings'] = parser.stats['total_pairings']
        total_stats['chunks_completed'] += 1
        
        chunk_time = time.time() - chunk_start_time
        
        print(f"✅ CHUNK {chunk_num} COMPLETE!")
        print(f"   📄 Pages with content: {chunk_pages}")
        print(f"   🥕 Ingredients found: {chunk_ingredients}")
        print(f"   ⏱️  Time taken: {chunk_time:.1f} seconds")
        print(f"   📊 Running totals: {total_stats['total_ingredients']} ingredients, {total_stats['total_pairings']} pairings")
        
        # Reset parser stats for next chunk
        parser.stats['total_pairings'] = total_stats['total_pairings']
    
    # Final summary
    total_time = time.time() - total_stats['processing_start']
    
    print(f"\n🎉 COMPLETE FLAVOR BIBLE PARSING FINISHED!")
    print("=" * 60)
    print(f"⏱️  Total processing time: {total_time/60:.1f} minutes")
    print(f"📄 Total pages with content: {total_stats['total_pages_processed']}")
    print(f"🥕 Total ingredients extracted: {total_stats['total_ingredients']}")
    print(f"🔗 Total flavor pairings: {total_stats['total_pairings']}")
    print(f"📈 Average pairings per ingredient: {total_stats['total_pairings']/total_stats['total_ingredients']:.1f}")
    
    # Calculate formatting distribution from final results
    formatting_breakdown = {'bold_caps': 0, 'bold_only': 0, 'caps_only': 0, 'plain_text': 0}
    ingredient_list = []
    
    for page_data in all_results.values():
        for ingredient_name, section in page_data['ingredient_sections'].items():
            ingredient_list.append(ingredient_name)
            for format_type, pairings in section['pairings'].items():
                formatting_breakdown[format_type] += len(pairings)
    
    total_pairings = sum(formatting_breakdown.values())
    
    print(f"\n💪 FINAL FORMATTING BREAKDOWN:")
    print(f"   🟥 Bold+Caps (0.95 - STRONGEST): {formatting_breakdown['bold_caps']} ({formatting_breakdown['bold_caps']/total_pairings*100:.1f}%)")
    print(f"   🟧 Bold only (0.90 - VERY STRONG): {formatting_breakdown['bold_only']} ({formatting_breakdown['bold_only']/total_pairings*100:.1f}%)")
    print(f"   🟨 Caps only (0.85 - STRONG): {formatting_breakdown['caps_only']} ({formatting_breakdown['caps_only']/total_pairings*100:.1f}%)")
    print(f"   🟩 Plain text (0.80 - GOOD): {formatting_breakdown['plain_text']} ({formatting_breakdown['plain_text']/total_pairings*100:.1f}%)")
    
    # Show sample of ingredients found
    unique_ingredients = sorted(set(ingredient_list))
    print(f"\n🌟 INGREDIENTS DISCOVERED ({len(unique_ingredients)} total):")
    print("First 30 ingredients:")
    for i, ingredient in enumerate(unique_ingredients[:30]):
        print(f"   {i+1:2d}. {ingredient}")
    
    if len(unique_ingredients) > 30:
        print(f"   ... and {len(unique_ingredients) - 30} more!")
    
    print(f"\n💾 All results saved in: flavor_bible_data/")
    print(f"🎯 COMPLETE FLAVOR BIBLE PARSING SUCCESS!")
    
    return all_results

if __name__ == "__main__":
    results = parse_complete_flavor_bible()
