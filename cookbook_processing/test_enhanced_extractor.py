#!/usr/bin/env python3
"""
Test the enhanced ATK 25th extractor with comprehensive category TOC discovery
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from atk_25th_unified_extractor import ATK25thUnifiedExtractor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_enhanced_extraction():
    """Test the enhanced extractor with comprehensive category scanning"""
    
    pdf_path = r"d:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return
    
    logger.info("🚀 Testing Enhanced ATK 25th Extractor with Comprehensive Category TOC Discovery")
    logger.info("=" * 80)
    
    try:
        # Initialize extractor
        extractor = ATK25thUnifiedExtractor(pdf_path)
        
        # Test current extraction first
        logger.info("📋 Step 1: Current TOC extraction...")
        toc = extractor.extract_toc()
        logger.info(f"✅ Current TOC extraction found: {len(toc)} recipes")
        
        # Run a small extraction to see current results
        logger.info("\n📝 Step 2: Sample extraction with current method...")
        recipes = extractor.extract_recipes(max_recipes=50)
        logger.info(f"✅ Sample extraction completed: {len(recipes)} recipes extracted")
        
        # Show sample results
        if recipes:
            logger.info("\n📄 Sample of extracted recipes:")
            for i, recipe in enumerate(recipes[:10]):
                logger.info(f"  {i+1}. {recipe.get('title', 'No title')} (Page {recipe.get('page', 'Unknown')})")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ Enhanced extractor test completed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_extraction()
