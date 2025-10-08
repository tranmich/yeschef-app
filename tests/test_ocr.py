"""
Test OCR Processor
Quick test to verify Google Vision API is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_processor import get_ocr_processor

def test_ocr_availability():
    """Test if OCR processor is available and configured"""
    print("=" * 60)
    print("🔍 Testing OCR Processor Configuration")
    print("=" * 60)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    google_creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    google_creds_json = os.getenv('GOOGLE_CLOUD_CREDENTIALS')
    
    if google_creds_file:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS: {google_creds_file}")
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS: Not set")
    
    if google_creds_json:
        print(f"✅ GOOGLE_CLOUD_CREDENTIALS: Set ({len(google_creds_json)} characters)")
    else:
        print("❌ GOOGLE_CLOUD_CREDENTIALS: Not set")
    
    # Test processor
    print("\n🔧 Testing OCR Processor:")
    processor = get_ocr_processor()
    
    if processor and processor.is_available():
        print("✅ Google Vision API is READY!")
        print("\n🎉 SUCCESS! Your OCR system is configured correctly!")
        print("\nYou can now:")
        print("  1. Start your backend server (python hungie_server.py)")
        print("  2. Use the mobile app to scan recipe cards")
        print("  3. Photos will be processed with OCR automatically!")
        return True
    else:
        print("❌ Google Vision API is NOT available")
        print("\n📝 Troubleshooting:")
        print("  1. Make sure you have set up Google Cloud credentials")
        print("  2. For local dev: Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("  3. For Railway: Set GOOGLE_CLOUD_CREDENTIALS with JSON content")
        print("  4. See GOOGLE_VISION_SETUP.md for detailed instructions")
        return False

if __name__ == '__main__':
    success = test_ocr_availability()
    sys.exit(0 if success else 1)
