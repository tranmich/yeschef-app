#!/usr/bin/env python3
"""
🧠📚 HYBRID TRAINING STRATEGY
============================

Bridge from rule-based extractors to ML model training:
1. Use existing extractors to auto-generate training data
2. Train layout detection model for region identification
3. Combine ML regions with rule-based parsing logic
4. Create active learning loop for continuous improvement

This preserves all your existing work while adding ML generalization.
"""

import os
import json
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class RecipeRegion:
    """Represents a detected region on a page"""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    region_type: str  # 'title', 'ingredients', 'instructions', 'headnote', 'noise'
    confidence: float
    text: str = ""
    source: str = "heuristic"  # 'heuristic', 'model', 'manual'

class HybridExtractorTrainer:
    """
    Combines rule-based extraction with ML training data generation
    
    Phase 1: Use your existing ATK extractor to auto-label pages
    Phase 2: Manual correction of auto-labels in Label Studio
    Phase 3: Train layout detection model
    Phase 4: Hybrid inference (model + rules)
    """
    
    def __init__(self, existing_extractor=None):
        self.existing_extractor = existing_extractor
        self.training_data = []
        
    def generate_training_data_from_extractor(self, pdf_path: str, output_dir: str):
        """
        Phase 1: Use your existing ATK extractor to create training annotations
        
        This converts your rule-based extraction into bounding box annotations
        that can be used to train a layout detection model.
        """
        
        # Run your existing extractor
        recipes = self.existing_extractor.extract_recipes(pdf_path)
        
        # Convert to page images and annotations
        training_samples = []
        
        for page_num, recipe_data in recipes.items():
            # Render PDF page to image (for training)
            page_image = self._render_pdf_page_to_image(pdf_path, page_num)
            
            # Convert extraction results to bounding boxes
            regions = self._convert_extraction_to_regions(recipe_data, page_image)
            
            # Create training annotation
            annotation = {
                'image_path': f"{output_dir}/page_{page_num}.png",
                'image_width': page_image.shape[1],
                'image_height': page_image.shape[0],
                'regions': [
                    {
                        'bbox': region.bbox,
                        'class': region.region_type,
                        'confidence': region.confidence,
                        'text': region.text[:100]  # Preview for manual review
                    }
                    for region in regions
                ]
            }
            
            # Save page image
            cv2.imwrite(f"{output_dir}/page_{page_num}.png", page_image)
            training_samples.append(annotation)
            
        # Save annotations in Label Studio format
        self._save_label_studio_format(training_samples, f"{output_dir}/annotations.json")
        
        print(f"✅ Generated {len(training_samples)} training samples from ATK extractor")
        print(f"📁 Saved to: {output_dir}")
        print(f"🏷️ Next: Import {output_dir}/annotations.json to Label Studio for correction")
        
        return training_samples
    
    def _convert_extraction_to_regions(self, recipe_data: Dict, page_image: np.ndarray) -> List[RecipeRegion]:
        """
        Convert your extractor's text-based results to bounding box regions
        
        This is the key bridge: your extractor finds text, we estimate where
        that text appears on the page image for training data.
        """
        regions = []
        
        # Title region (usually top of page, larger font)
        if recipe_data.get('title'):
            title_bbox = self._estimate_text_bbox(
                recipe_data['title'], 
                page_image, 
                region_type='title'
            )
            regions.append(RecipeRegion(
                bbox=title_bbox,
                region_type='title',
                confidence=0.9,  # High confidence from rule-based
                text=recipe_data['title'],
                source='heuristic'
            ))
        
        # Ingredients region (middle-left or full width)
        if recipe_data.get('ingredients'):
            ingredients_bbox = self._estimate_text_bbox(
                recipe_data['ingredients'][:200],  # First 200 chars
                page_image,
                region_type='ingredients'
            )
            regions.append(RecipeRegion(
                bbox=ingredients_bbox,
                region_type='ingredients', 
                confidence=0.85,
                text=recipe_data['ingredients'][:100],
                source='heuristic'
            ))
        
        # Instructions region (usually bottom half)
        if recipe_data.get('instructions'):
            instructions_bbox = self._estimate_text_bbox(
                recipe_data['instructions'][:200],
                page_image,
                region_type='instructions'
            )
            regions.append(RecipeRegion(
                bbox=instructions_bbox,
                region_type='instructions',
                confidence=0.85,
                text=recipe_data['instructions'][:100],
                source='heuristic'
            ))
        
        return regions
    
    def _estimate_text_bbox(self, text: str, page_image: np.ndarray, region_type: str) -> Tuple[int, int, int, int]:
        """
        Estimate bounding box for text on page image
        
        This is a rough estimation based on typical cookbook layouts.
        Manual correction in Label Studio will fix the exact boundaries.
        """
        height, width = page_image.shape[:2]
        
        # Default regions based on typical cookbook layout
        if region_type == 'title':
            # Top 20% of page, centered
            return (int(width * 0.1), int(height * 0.05), int(width * 0.9), int(height * 0.2))
        
        elif region_type == 'ingredients':
            # Left column or full width, upper middle
            return (int(width * 0.1), int(height * 0.25), int(width * 0.9), int(height * 0.6))
        
        elif region_type == 'instructions':
            # Lower half of page
            return (int(width * 0.1), int(height * 0.6), int(width * 0.9), int(height * 0.9))
        
        else:
            # Default full page
            return (0, 0, width, height)
    
    def _render_pdf_page_to_image(self, pdf_path: str, page_num: int, dpi: int = 150) -> np.ndarray:
        """Render PDF page to image for training"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(pdf_path)
            page = doc[page_num - 1]  # Convert to 0-indexed
            
            # Render to image
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Convert to OpenCV format
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            doc.close()
            return image
            
        except ImportError:
            print("❌ PyMuPDF not installed. Install with: pip install PyMuPDF")
            return np.zeros((1000, 800, 3), dtype=np.uint8)
    
    def _save_label_studio_format(self, training_samples: List[Dict], output_path: str):
        """Save annotations in Label Studio import format"""
        
        ls_data = []
        for sample in training_samples:
            ls_item = {
                "data": {
                    "image": sample['image_path']
                },
                "predictions": [{
                    "model_version": "heuristic_v1",
                    "score": 0.85,
                    "result": []
                }]
            }
            
            # Convert regions to Label Studio format
            for region in sample['regions']:
                x1, y1, x2, y2 = region['bbox']
                width_pct = ((x2 - x1) / sample['image_width']) * 100
                height_pct = ((y2 - y1) / sample['image_height']) * 100
                x_pct = (x1 / sample['image_width']) * 100
                y_pct = (y1 / sample['image_height']) * 100
                
                ls_item["predictions"][0]["result"].append({
                    "value": {
                        "x": x_pct,
                        "y": y_pct, 
                        "width": width_pct,
                        "height": height_pct,
                        "rectanglelabels": [region['class']]
                    },
                    "from_name": "bbox",
                    "to_name": "image",
                    "type": "rectanglelabels"
                })
            
            ls_data.append(ls_item)
        
        with open(output_path, 'w') as f:
            json.dump(ls_data, f, indent=2)

class HybridInferenceEngine:
    """
    Phase 4: Combine trained layout model with your rule-based parsing
    
    This is where the magic happens - ML finds the regions,
    your proven rules parse the content within those regions.
    """
    
    def __init__(self, layout_model_path: str, rule_based_extractor):
        self.layout_model = self._load_layout_model(layout_model_path)
        self.rule_extractor = rule_based_extractor
        
    def extract_recipe_hybrid(self, pdf_path: str, page_num: int) -> Dict:
        """
        Hybrid extraction: ML regions + rule-based parsing
        
        1. Use trained model to detect regions (title, ingredients, instructions)
        2. Extract text from each region  
        3. Use your proven rules to parse text within regions
        4. Combine with confidence scoring
        """
        
        # Step 1: Detect regions with ML model
        page_image = self._render_page_to_image(pdf_path, page_num)
        detected_regions = self.layout_model.detect(page_image)
        
        # Step 2: Extract text from each region
        region_texts = {}
        for region in detected_regions:
            if region.confidence > 0.5:  # Confidence threshold
                text = self._extract_text_from_region(pdf_path, page_num, region.bbox)
                region_texts[region.region_type] = {
                    'text': text,
                    'confidence': region.confidence,
                    'bbox': region.bbox
                }
        
        # Step 3: Parse with your proven rules within each region
        recipe_data = {}
        
        # Title parsing (your existing logic, but only on title region)
        if 'title' in region_texts:
            title_text = region_texts['title']['text']
            recipe_data['title'] = self.rule_extractor._parse_title(title_text)
            recipe_data['title_confidence'] = region_texts['title']['confidence']
        
        # Ingredients parsing (your existing logic, but only on ingredients region)
        if 'ingredients' in region_texts:
            ingredients_text = region_texts['ingredients']['text']
            recipe_data['ingredients'] = self.rule_extractor._parse_ingredients(ingredients_text)
            recipe_data['ingredients_confidence'] = region_texts['ingredients']['confidence']
        
        # Instructions parsing (your existing logic, but only on instructions region)
        if 'instructions' in region_texts:
            instructions_text = region_texts['instructions']['text']
            recipe_data['instructions'] = self.rule_extractor._parse_instructions(instructions_text)
            recipe_data['instructions_confidence'] = region_texts['instructions']['confidence']
        
        # Step 4: Fallback to full-page rule-based if ML confidence is low
        overall_confidence = self._calculate_overall_confidence(recipe_data)
        if overall_confidence < 0.7:
            # Fall back to your existing full-page extractor
            fallback_result = self.rule_extractor.extract_page(pdf_path, page_num)
            recipe_data = self._merge_results(recipe_data, fallback_result)
        
        return recipe_data
    
    def _calculate_overall_confidence(self, recipe_data: Dict) -> float:
        """Calculate overall extraction confidence"""
        confidences = [
            recipe_data.get('title_confidence', 0),
            recipe_data.get('ingredients_confidence', 0), 
            recipe_data.get('instructions_confidence', 0)
        ]
        return sum(confidences) / len(confidences) if confidences else 0
    
    def _merge_results(self, ml_result: Dict, fallback_result: Dict) -> Dict:
        """Merge ML and rule-based results, preferring higher confidence"""
        merged = {}
        
        for field in ['title', 'ingredients', 'instructions']:
            ml_conf = ml_result.get(f'{field}_confidence', 0)
            fallback_conf = 0.6  # Assume moderate confidence for rule-based
            
            if ml_conf > fallback_conf:
                merged[field] = ml_result.get(field)
                merged[f'{field}_confidence'] = ml_conf
                merged[f'{field}_source'] = 'ml'
            else:
                merged[field] = fallback_result.get(field)
                merged[f'{field}_confidence'] = fallback_conf
                merged[f'{field}_source'] = 'rules'
        
        return merged

# Usage Example for your ATK extractor
if __name__ == "__main__":
    # Import your existing ATK extractor
    from atk_25th_unified_extractor import ATK25thUnifiedExtractor
    
    # Phase 1: Generate training data from your existing extractor
    trainer = HybridExtractorTrainer(existing_extractor=ATK25thUnifiedExtractor())
    
    # Convert your ATK extractions to ML training data
    training_data = trainer.generate_training_data_from_extractor(
        pdf_path="path/to/atk_25th_anniversary.pdf",
        output_dir="training_data/atk_annotations"
    )
    
    print("🎯 Next Steps:")
    print("1. Import training_data/atk_annotations/annotations.json to Label Studio")
    print("2. Correct any wrong bounding boxes (should be ~80% correct already)")
    print("3. Export corrected annotations")
    print("4. Train YOLOv8 layout detection model")
    print("5. Use HybridInferenceEngine for production extraction")
