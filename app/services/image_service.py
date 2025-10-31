"""
Image Service
Handles recipe image download, optimization, and storage
NO external services required - 100% self-contained
"""

import os
import io
import logging
import requests
from typing import Optional
from PIL import Image

logger = logging.getLogger(__name__)

# Configuration
IMAGE_STORAGE_PATH = os.path.join('data', 'recipe_images')
MAX_IMAGE_WIDTH = 800
MAX_IMAGE_HEIGHT = 600
WEBP_QUALITY = 85
DOWNLOAD_TIMEOUT = 10


class ImageService:
    """
    Recipe image optimization service
    
    Features:
    - Downloads images from recipe websites
    - Resizes to optimal dimensions (800×600 max)
    - Converts to WebP format (80-95% size reduction)
    - Stores locally on server
    - No external APIs or services needed
    """
    
    def __init__(self):
        """Initialize image service and ensure storage directory exists"""
        self._ensure_storage_directory()
        
    def _ensure_storage_directory(self):
        """Create image storage directory if it doesn't exist"""
        try:
            os.makedirs(IMAGE_STORAGE_PATH, exist_ok=True)
            logger.info(f"✅ Image storage ready: {IMAGE_STORAGE_PATH}")
        except Exception as e:
            logger.error(f"❌ Failed to create image storage directory: {e}")
            raise
    
    def download_and_optimize(self, image_url: str, recipe_id: int) -> Optional[str]:
        """
        Download image from URL, optimize, and save locally
        
        Args:
            image_url: Original image URL from recipe website
            recipe_id: Recipe ID for filename generation
            
        Returns:
            Local image path (e.g., "/api/v2/images/recipe_123.webp") or None if failed
            
        Process:
            1. Download original image (may be 2-5 MB)
            2. Resize to max 800×600 (maintains aspect ratio)
            3. Convert to WebP format (superior compression)
            4. Save to local storage (typically 80-100 KB)
            5. Return local API path
        """
        if not image_url:
            logger.warning("⚠️ No image URL provided")
            return None
            
        try:
            logger.info(f"📥 Downloading image from: {image_url[:100]}...")
            
            # Download image with timeout
            response = requests.get(
                image_url, 
                timeout=DOWNLOAD_TIMEOUT,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            response.raise_for_status()
            
            original_size = len(response.content)
            logger.info(f"📦 Downloaded {original_size / 1024:.1f} KB")
            
            # Open image with Pillow
            img = Image.open(io.BytesIO(response.content))
            original_dimensions = img.size
            logger.info(f"📐 Original dimensions: {original_dimensions[0]}×{original_dimensions[1]}")
            
            # Resize to max dimensions (maintains aspect ratio)
            img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT), Image.LANCZOS)
            new_dimensions = img.size
            logger.info(f"📐 Resized to: {new_dimensions[0]}×{new_dimensions[1]}")
            
            # Convert to RGB if needed (WebP requirement)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA' or img.mode == 'LA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
                logger.info("🎨 Converted to RGB")
            
            # Save as WebP with compression
            filename = f"recipe_{recipe_id}.webp"
            filepath = os.path.join(IMAGE_STORAGE_PATH, filename)
            
            # Save with high-quality WebP compression
            img.save(filepath, 'WebP', quality=WEBP_QUALITY, method=6)
            
            optimized_size = os.path.getsize(filepath)
            reduction_percent = ((original_size - optimized_size) / original_size) * 100
            
            logger.info(f"✅ Image optimized:")
            logger.info(f"   Size: {original_size / 1024:.1f} KB → {optimized_size / 1024:.1f} KB")
            logger.info(f"   Reduction: {reduction_percent:.1f}%")
            logger.info(f"   Saved to: {filename}")
            
            # Return API path
            return f"/api/v2/images/{filename}"
            
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ Image download timeout: {image_url[:100]}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Image download failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Image optimization failed: {e}")
            return None
    
    def get_image_path(self, filename: str) -> Optional[str]:
        """
        Get full filesystem path for an image
        
        Args:
            filename: Image filename (e.g., "recipe_123.webp")
            
        Returns:
            Full filesystem path or None if doesn't exist
        """
        filepath = os.path.join(IMAGE_STORAGE_PATH, filename)
        if os.path.exists(filepath):
            return filepath
        return None
    
    def delete_image(self, recipe_id: int) -> bool:
        """
        Delete recipe image from storage
        
        Args:
            recipe_id: Recipe ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            filename = f"recipe_{recipe_id}.webp"
            filepath = os.path.join(IMAGE_STORAGE_PATH, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"🗑️ Deleted image: {filename}")
                return True
            else:
                logger.warning(f"⚠️ Image not found: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to delete image: {e}")
            return False


# Singleton instance
_image_service = None

def get_image_service() -> ImageService:
    """Get or create ImageService singleton instance"""
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service
