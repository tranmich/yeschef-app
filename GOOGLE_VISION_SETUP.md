# Google Cloud Vision API Setup Guide

## Step 1: Get Google Cloud Credentials

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable the Vision API:
   - Go to "APIs & Services" → "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"

4. Create service account credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name it (e.g., "yeschef-ocr")
   - Grant role: "Cloud Vision API User"
   - Click "Done"

5. Create key:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON"
   - Download the JSON file

## Step 2: Set up Credentials

### Option A: Environment Variable (Recommended for development)
```bash
# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your-credentials.json"

# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-credentials.json"
```

### Option B: Add to .env file
```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-credentials.json
```

### Option C: For Production (Railway)
1. Go to Railway project settings
2. Add environment variable:
   - Key: `GOOGLE_CLOUD_CREDENTIALS_JSON`
   - Value: Paste entire JSON content
3. Update code to load from environment variable

## Step 3: Install Package

```bash
# Activate your virtual environment
cd "D:\Mik\Downloads\Me Hungie"
venv\Scripts\activate

# Install Google Cloud Vision
pip install google-cloud-vision
```

## Step 4: Test OCR

```python
# Test script
from ocr_processor import get_ocr_processor

processor = get_ocr_processor()
if processor.is_available():
    print("✅ Google Vision API is ready!")
else:
    print("❌ Google Vision API not available")
```

## Pricing (Very Affordable!)

- **Free tier**: 1,000 OCR requests per month
- **After free tier**: $1.50 per 1,000 images
- **Example**: 100 users × 10 recipes/month = 1,000 images = FREE or $1.50

## Alternative: Tesseract (Free but Lower Quality)

If you want a completely free solution:

```bash
# Install Tesseract
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr

# Install Python wrapper
pip install pytesseract
```

The code will automatically use Tesseract as fallback if Google Vision is not available.

## Recommended: Use Google Vision

- Much better accuracy (95%+ vs 85%)
- Handles columns and layout better
- Free tier covers development and early users
- Only $1.50 per 1,000 images after that

## Next Steps

1. Set up Google Cloud credentials
2. Test OCR with sample recipe image
3. Adjust confidence thresholds if needed
4. Deploy to production with credentials
