"""
OCR Recipe Processor
Google Vision API integration for recipe card scanning

Features:
- Multi-image processing
- Layout-aware text extraction
- Column detection
- Confidence scoring
- Text cleaning and combining

Created: October 7, 2025
Phase 3: OCR Import System
"""

import os
import io
import logging
from typing import List, Dict, Tuple, Optional
from PIL import Image

# Google Vision API
try:
    from google.cloud import vision
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    print("⚠️ Google Vision API not installed. OCR features will be limited.")

logger = logging.getLogger(__name__)

class OCRRecipeProcessor:
    """Process recipe images using Google Vision API"""
    
    def __init__(self):
        """Initialize OCR processor"""
        if VISION_AVAILABLE:
            # Initialize Vision API client
            # Uses GOOGLE_APPLICATION_CREDENTIALS environment variable
            try:
                self.client = vision.ImageAnnotatorClient()
                logger.info("✅ Google Vision API client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Vision API: {e}")
                self.client = None
        else:
            self.client = None
            logger.warning("⚠️ Google Vision API not available")
    
    def is_available(self) -> bool:
        """Check if OCR processing is available"""
        return self.client is not None
    
    def process_images(self, image_files: List[bytes]) -> Dict:
        """
        Process multiple recipe images and extract text
        
        Args:
            image_files: List of image file contents (bytes)
            
        Returns:
            Dictionary with extracted text and metadata
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Google Vision API not available'
            }
        
        try:
            logger.info(f"📸 Processing {len(image_files)} images...")
            
            all_text_blocks = []
            total_confidence = 0
            images_processed = 0
            
            for idx, image_content in enumerate(image_files):
                logger.info(f"Processing image {idx + 1}/{len(image_files)}...")
                
                result = self._extract_text_from_image(image_content)
                
                if result['success']:
                    all_text_blocks.append({
                        'page_number': idx + 1,
                        'text': result['text'],
                        'confidence': result['confidence']
                    })
                    total_confidence += result['confidence']
                    images_processed += 1
                else:
                    logger.warning(f"Failed to process image {idx + 1}: {result.get('error')}")
            
            if images_processed == 0:
                return {
                    'success': False,
                    'error': 'Failed to extract text from any images'
                }
            
            # Combine text from all pages
            combined_text = self._combine_text_blocks(all_text_blocks)
            avg_confidence = total_confidence / images_processed
            
            logger.info(f"✅ OCR complete: {images_processed}/{len(image_files)} images processed")
            logger.info(f"📝 Extracted {len(combined_text)} characters")
            logger.info(f"🎯 Average confidence: {avg_confidence:.2%}")
            
            return {
                'success': True,
                'text': combined_text,
                'confidence': avg_confidence,
                'pages_processed': images_processed,
                'total_pages': len(image_files),
                'text_blocks': all_text_blocks
            }
            
        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            return {
                'success': False,
                'error': f'OCR processing failed: {str(e)}'
            }
    
    def _extract_text_from_image(self, image_content: bytes) -> Dict:
        """
        Extract text from a single image using Google Vision API
        
        Args:
            image_content: Image file content (bytes)
            
        Returns:
            Dictionary with text and confidence
        """
        try:
            # Create Vision API image object
            image = vision.Image(content=image_content)
            
            # Perform document text detection (best for recipes)
            # This preserves layout and reading order
            response = self.client.document_text_detection(image=image)
            
            if response.error.message:
                raise Exception(response.error.message)
            
            # Get full text annotation (includes layout)
            document = response.full_text_annotation
            
            if not document.text:
                return {
                    'success': False,
                    'error': 'No text detected in image'
                }
            
            # Calculate average confidence from all words
            total_confidence = 0
            word_count = 0
            
            for page in document.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            total_confidence += word.confidence
                            word_count += 1
            
            avg_confidence = total_confidence / word_count if word_count > 0 else 0
            
            # Clean up text
            cleaned_text = self._clean_text(document.text)
            
            return {
                'success': True,
                'text': cleaned_text,
                'confidence': avg_confidence,
                'word_count': word_count
            }
            
        except Exception as e:
            logger.error(f"Vision API error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]  # Remove empty lines
        
        # Join with single newlines
        cleaned = '\n'.join(lines)
        
        return cleaned
    
    def _combine_text_blocks(self, text_blocks: List[Dict]) -> str:
        """
        Combine text from multiple pages intelligently
        
        Args:
            text_blocks: List of text blocks from different pages
            
        Returns:
            Combined text string
        """
        # Sort by page number
        sorted_blocks = sorted(text_blocks, key=lambda x: x['page_number'])
        
        # Combine with page separators
        combined_parts = []
        for block in sorted_blocks:
            combined_parts.append(f"=== Page {block['page_number']} ===\n")
            combined_parts.append(block['text'])
            combined_parts.append("\n\n")
        
        combined = ''.join(combined_parts).strip()
        
        return combined
    
    def validate_recipe_text(self, text: str) -> Dict:
        """
        Validate if extracted text looks like a recipe
        
        Args:
            text: Extracted text
            
        Returns:
            Dictionary with validation results
        """
        text_lower = text.lower()
        
        # Check for recipe indicators
        has_ingredients = any(word in text_lower for word in [
            'ingredients', 'cups', 'tablespoon', 'teaspoon', 'oz', 'lb',
            'grams', 'ml', 'flour', 'sugar', 'salt', 'butter', 'eggs'
        ])
        
        has_instructions = any(word in text_lower for word in [
            'instructions', 'directions', 'steps', 'method',
            'mix', 'stir', 'bake', 'cook', 'heat', 'add', 'combine',
            'preheat', 'pour', 'blend', 'whisk'
        ])
        
        # Check text length (recipes should have substantial text)
        has_content = len(text.strip()) > 50
        
        is_likely_recipe = has_ingredients and has_instructions and has_content
        
        return {
            'is_likely_recipe': is_likely_recipe,
            'has_ingredients': has_ingredients,
            'has_instructions': has_instructions,
            'has_content': has_content,
            'text_length': len(text),
            'confidence_multiplier': 1.0 if is_likely_recipe else 0.5
        }


# Fallback OCR using Tesseract (if Google Vision not available)
class TesseractOCRProcessor:
    """Fallback OCR processor using Tesseract"""
    
    def __init__(self):
        try:
            import pytesseract
            self.available = True
            logger.info("✅ Tesseract OCR available as fallback")
        except ImportError:
            self.available = False
            logger.warning("⚠️ Tesseract OCR not available")
    
    def is_available(self) -> bool:
        return self.available
    
    def process_images(self, image_files: List[bytes]) -> Dict:
        """Process images with Tesseract"""
        if not self.available:
            return {
                'success': False,
                'error': 'Tesseract not available'
            }
        
        try:
            import pytesseract
            from PIL import Image
            import io
            
            all_text = []
            
            for idx, image_content in enumerate(image_files):
                # Load image
                image = Image.open(io.BytesIO(image_content))
                
                # Extract text
                text = pytesseract.image_to_string(image)
                all_text.append(text)
            
            combined_text = '\n\n=== PAGE BREAK ===\n\n'.join(all_text)
            
            return {
                'success': True,
                'text': combined_text,
                'confidence': 0.7,  # Tesseract typically lower confidence
                'pages_processed': len(image_files),
                'total_pages': len(image_files)
            }
            
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Factory function to get best available OCR processor
def get_ocr_processor():
    """Get the best available OCR processor"""
    
    # Try Google Vision first (most accurate)
    processor = OCRRecipeProcessor()
    if processor.is_available():
        logger.info("✅ Using Google Vision API for OCR")
        return processor
    
    # Fallback to Tesseract
    fallback = TesseractOCRProcessor()
    if fallback.is_available():
        logger.info("⚠️ Using Tesseract OCR as fallback")
        return fallback
    
    # No OCR available
    logger.error("❌ No OCR processor available")
    return None
