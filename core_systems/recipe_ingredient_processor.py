"""
🔄 Recipe Ingredient Processor - Auto-Processing Pipeline for New Recipes
========================================================================

This system handles ingredient processing when recipes are added or updated.
It orchestrates the auto-mapping workflow and manages the review queue for
uncertain mappings.

Part of the Me Hungie Pantry Intelligence System - Day 2 Implementation
"""

import psycopg2
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import os
from dotenv import load_dotenv

from ingredient_intelligence_engine import IngredientIntelligenceEngine, IngredientMapping

load_dotenv()

@dataclass
class ProcessingResult:
    """Result of recipe ingredient processing"""
    recipe_id: int
    total_ingredients: int
    auto_mapped: int
    queued_for_review: int
    failed_mappings: int
    processing_time: float
    success_rate: float

@dataclass
class PendingMapping:
    """Ingredient mapping awaiting human verification"""
    id: int
    recipe_id: int
    raw_text: str
    suggested_canonical_id: Optional[int]
    suggested_canonical_name: Optional[str]
    confidence: float
    alternative_suggestions: List[Tuple[int, str, float]]
    created_at: datetime

class RecipeIngredientProcessor:
    """
    🔄 Handles ingredient processing when recipes are added/updated
    
    This class orchestrates the complete ingredient processing pipeline:
    - Parse raw ingredient lists from new recipes
    - Apply intelligent auto-mapping via IngredientIntelligenceEngine
    - Route based on confidence levels (auto-map vs review queue)
    - Maintain data integrity in recipe_ingredients table
    - Track processing statistics for monitoring
    """
    
    def __init__(self):
        self.db_connection = None
        self.intelligence_engine = IngredientIntelligenceEngine()
        
        # Confidence thresholds for routing decisions
        self.AUTO_MAP_THRESHOLD = 0.85    # High confidence - auto-map
        self.REVIEW_THRESHOLD = 0.60      # Medium confidence - queue for review
        # Below 0.60 = Low confidence - queue with multiple suggestions
    
    def _get_db_connection(self):
        """Get database connection using Railway PostgreSQL"""
        if not self.db_connection:
            try:
                db_url = os.getenv('DATABASE_URL')
                if not db_url:
                    raise Exception("DATABASE_URL environment variable required")
                
                self.db_connection = psycopg2.connect(db_url)
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise
        return self.db_connection
    
    def process_recipe_ingredients(self, recipe_id: int, raw_ingredients: List[str]) -> ProcessingResult:
        """
        🎯 Main entry point for processing new recipe ingredients
        
        This function:
        1. Processes each ingredient through the intelligence engine
        2. Routes based on confidence levels
        3. Updates recipe_ingredients table for high-confidence mappings
        4. Queues uncertain mappings for review
        5. Returns processing statistics
        """
        
        start_time = datetime.now()
        
        total_ingredients = len(raw_ingredients)
        auto_mapped = 0
        queued_for_review = 0
        failed_mappings = 0
        
        print(f"🔄 Processing {total_ingredients} ingredients for recipe {recipe_id}")
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Clear any existing ingredients for this recipe (in case of re-processing)
            cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id,))
            
            for i, raw_ingredient in enumerate(raw_ingredients, 1):
                
                print(f"  📝 {i}/{total_ingredients}: {raw_ingredient[:50]}...")
                
                # Get mapping from intelligence engine
                mapping = self.intelligence_engine.map_ingredient(raw_ingredient)
                
                if mapping.confidence >= self.AUTO_MAP_THRESHOLD:
                    # High confidence - auto-map to recipe_ingredients
                    success = self._auto_map_ingredient(cursor, recipe_id, mapping)
                    if success:
                        auto_mapped += 1
                        print(f"    ✅ Auto-mapped: {mapping.canonical_name} (conf: {mapping.confidence:.2f})")
                    else:
                        failed_mappings += 1
                        print(f"    ❌ Auto-map failed for: {raw_ingredient}")
                
                elif mapping.confidence >= self.REVIEW_THRESHOLD:
                    # Medium confidence - queue for review with suggestion
                    success = self._queue_for_review(cursor, recipe_id, mapping, has_suggestion=True)
                    if success:
                        queued_for_review += 1
                        print(f"    ⚠️  Queued with suggestion: {mapping.canonical_name} (conf: {mapping.confidence:.2f})")
                    else:
                        failed_mappings += 1
                        print(f"    ❌ Queue failed for: {raw_ingredient}")
                
                else:
                    # Low confidence - queue for review with multiple options
                    success = self._queue_for_review(cursor, recipe_id, mapping, has_suggestion=False)
                    if success:
                        queued_for_review += 1
                        print(f"    ❓ Queued for manual review: {raw_ingredient} (conf: {mapping.confidence:.2f})")
                    else:
                        failed_mappings += 1
                        print(f"    ❌ Queue failed for: {raw_ingredient}")
            
            # Commit all changes
            conn.commit()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            success_rate = (auto_mapped / total_ingredients * 100) if total_ingredients > 0 else 0
            
            result = ProcessingResult(
                recipe_id=recipe_id,
                total_ingredients=total_ingredients,
                auto_mapped=auto_mapped,
                queued_for_review=queued_for_review,
                failed_mappings=failed_mappings,
                processing_time=processing_time,
                success_rate=success_rate
            )
            
            # Log the processing result
            self._log_processing_result(cursor, result)
            conn.commit()
            
            print(f"\n🎊 Processing Complete for Recipe {recipe_id}:")
            print(f"   ✅ Auto-mapped: {auto_mapped}/{total_ingredients} ({success_rate:.1f}%)")
            print(f"   ⚠️  Review queue: {queued_for_review}")
            print(f"   ❌ Failed: {failed_mappings}")
            print(f"   ⏱️  Time: {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            print(f"❌ Recipe processing failed: {e}")
            if conn:
                conn.rollback()
            raise
    
    def _auto_map_ingredient(self, cursor, recipe_id: int, mapping: IngredientMapping) -> bool:
        """Insert high-confidence mapping directly into recipe_ingredients"""
        try:
            cursor.execute("""
                INSERT INTO recipe_ingredients 
                (recipe_id, canonical_ingredient_id, amount_numeric, unit, modifiers, raw_text, confidence, verified_manually, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE, NOW())
            """, (
                recipe_id,
                mapping.canonical_id,
                mapping.amount,
                mapping.unit,
                mapping.modifiers,  # Note: this might need to be handled as text array or json
                mapping.raw_text,
                mapping.confidence
            ))
            return True
        except Exception as e:
            print(f"❌ Auto-map insertion failed: {e}")
            return False
    
    def _queue_for_review(self, cursor, recipe_id: int, mapping: IngredientMapping, has_suggestion: bool) -> bool:
        """Queue uncertain mapping for human review"""
        try:
            # Prepare alternative suggestions as JSON
            import json
            suggestions_data = None
            if mapping.suggestions:
                suggestions_data = json.dumps([
                    {
                        'canonical_id': canonical_id,
                        'canonical_name': canonical_name,
                        'confidence': confidence
                    }
                    for canonical_id, canonical_name, confidence in mapping.suggestions
                ])
            
            cursor.execute("""
                INSERT INTO ingredient_review_queue 
                (recipe_id, raw_text, suggested_canonical_id, suggested_canonical_name, 
                 confidence, alternative_suggestions, amount, unit, modifiers, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                recipe_id,
                mapping.raw_text,
                mapping.canonical_id if has_suggestion else None,
                mapping.canonical_name if has_suggestion else None,
                mapping.confidence,
                suggestions_data,
                mapping.amount,
                mapping.unit,
                mapping.modifiers
            ))
            return True
        except Exception as e:
            print(f"❌ Review queue insertion failed: {e}")
            return False
    
    def _log_processing_result(self, cursor, result: ProcessingResult):
        """Log processing statistics for monitoring and analytics"""
        try:
            cursor.execute("""
                INSERT INTO recipe_processing_logs
                (recipe_id, total_ingredients, auto_mapped, queued_for_review, 
                 failed_mappings, processing_time, success_rate, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                result.recipe_id,
                result.total_ingredients,
                result.auto_mapped,
                result.queued_for_review,
                result.failed_mappings,
                result.processing_time,
                result.success_rate
            ))
        except Exception as e:
            print(f"⚠️  Failed to log processing result: {e}")
    
    def reprocess_recipe_ingredients(self, recipe_id: int) -> ProcessingResult:
        """
        🔄 Reprocess ingredients for an existing recipe
        
        Useful when:
        - Intelligence engine has been improved
        - Manual corrections have been made to canonical ingredients
        - Recipe ingredients have been updated
        """
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Get the original raw ingredients for this recipe
            cursor.execute("""
                SELECT DISTINCT raw_text 
                FROM recipe_ingredients 
                WHERE recipe_id = %s
                UNION
                SELECT DISTINCT raw_text
                FROM ingredient_review_queue
                WHERE recipe_id = %s
                ORDER BY raw_text
            """, (recipe_id, recipe_id))
            
            raw_ingredients = [row[0] for row in cursor.fetchall()]
            
            if not raw_ingredients:
                print(f"⚠️  No ingredients found for recipe {recipe_id}")
                return ProcessingResult(
                    recipe_id=recipe_id,
                    total_ingredients=0,
                    auto_mapped=0,
                    queued_for_review=0,
                    failed_mappings=0,
                    processing_time=0.0,
                    success_rate=0.0
                )
            
            print(f"🔄 Reprocessing {len(raw_ingredients)} ingredients for recipe {recipe_id}")
            
            # Clear existing data
            cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id,))
            cursor.execute("DELETE FROM ingredient_review_queue WHERE recipe_id = %s", (recipe_id,))
            conn.commit()
            
            # Process with current intelligence
            return self.process_recipe_ingredients(recipe_id, raw_ingredients)
            
        except Exception as e:
            print(f"❌ Reprocessing failed: {e}")
            raise
    
    def get_processing_statistics(self, days: int = 7) -> Dict:
        """Get processing statistics for the last N days"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as recipes_processed,
                    SUM(total_ingredients) as total_ingredients,
                    SUM(auto_mapped) as total_auto_mapped,
                    SUM(queued_for_review) as total_queued,
                    SUM(failed_mappings) as total_failed,
                    AVG(success_rate) as avg_success_rate,
                    AVG(processing_time) as avg_processing_time
                FROM recipe_processing_logs
                WHERE created_at >= NOW() - INTERVAL '%s days'
            """, (days,))
            
            result = cursor.fetchone()
            if result:
                (recipes, ingredients, auto_mapped, queued, failed, 
                 avg_success, avg_time) = result
                
                return {
                    'period_days': days,
                    'recipes_processed': recipes or 0,
                    'total_ingredients': ingredients or 0,
                    'auto_mapped': auto_mapped or 0,
                    'queued_for_review': queued or 0,
                    'failed_mappings': failed or 0,
                    'overall_success_rate': float(avg_success) if avg_success else 0.0,
                    'average_processing_time': float(avg_time) if avg_time else 0.0,
                    'auto_mapping_rate': (auto_mapped / ingredients * 100) if ingredients else 0.0
                }
            
        except Exception as e:
            print(f"❌ Failed to get processing statistics: {e}")
            
        return {'error': 'Failed to retrieve statistics'}

class MappingReviewQueue:
    """
    📝 Simple admin interface for reviewing uncertain ingredient mappings
    
    This class provides functions for:
    - Retrieving pending mappings that need human verification
    - Processing verification decisions
    - Batch operations for efficiency
    - Learning integration with the intelligence engine
    """
    
    def __init__(self):
        self.db_connection = None
        self.intelligence_engine = IngredientIntelligenceEngine()
    
    def _get_db_connection(self):
        """Get database connection using Railway PostgreSQL"""
        if not self.db_connection:
            try:
                db_url = os.getenv('DATABASE_URL')
                if not db_url:
                    raise Exception("DATABASE_URL environment variable required")
                
                self.db_connection = psycopg2.connect(db_url)
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise
        return self.db_connection
    
    def get_pending_reviews(self, limit: int = 20) -> List[PendingMapping]:
        """Get the next batch of ingredients awaiting verification"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, recipe_id, raw_text, suggested_canonical_id, 
                    suggested_canonical_name, confidence, alternative_suggestions, created_at
                FROM ingredient_review_queue
                ORDER BY created_at ASC
                LIMIT %s
            """, (limit,))
            
            pending_mappings = []
            for row in cursor.fetchall():
                (id, recipe_id, raw_text, suggested_id, suggested_name, 
                 confidence, alternatives, created_at) = row
                
                # Parse alternative suggestions
                alt_suggestions = []
                if alternatives:
                    for alt in alternatives:
                        alt_suggestions.append((
                            alt['canonical_id'],
                            alt['canonical_name'],
                            alt['confidence']
                        ))
                
                pending_mappings.append(PendingMapping(
                    id=id,
                    recipe_id=recipe_id,
                    raw_text=raw_text,
                    suggested_canonical_id=suggested_id,
                    suggested_canonical_name=suggested_name,
                    confidence=confidence,
                    alternative_suggestions=alt_suggestions,
                    created_at=created_at
                ))
            
            return pending_mappings
            
        except Exception as e:
            print(f"❌ Failed to get pending reviews: {e}")
            return []
    
    def verify_mapping(self, pending_id: int, verified_canonical_id: int, 
                      amount: Optional[float] = None, unit: Optional[str] = None, 
                      modifiers: Optional[List[str]] = None) -> bool:
        """
        ✅ Process human verification and move to recipe_ingredients
        
        This function:
        1. Moves the verified mapping to recipe_ingredients table
        2. Removes from review queue
        3. Triggers learning in the intelligence engine
        4. Returns success status
        """
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Get the pending mapping details
            cursor.execute("""
                SELECT recipe_id, raw_text, suggested_canonical_id, confidence
                FROM ingredient_review_queue
                WHERE id = %s
            """, (pending_id,))
            
            result = cursor.fetchone()
            if not result:
                print(f"❌ Pending mapping {pending_id} not found")
                return False
            
            recipe_id, raw_text, suggested_id, confidence = result
            
            # Insert into recipe_ingredients
            cursor.execute("""
                INSERT INTO recipe_ingredients 
                (recipe_id, canonical_ingredient_id, amount, unit, modifiers, 
                 raw_text, confidence, verified_manually, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, NOW())
            """, (
                recipe_id,
                verified_canonical_id,
                amount,
                unit,
                modifiers,
                raw_text,
                confidence
            ))
            
            # Remove from review queue
            cursor.execute("DELETE FROM ingredient_review_queue WHERE id = %s", (pending_id,))
            
            # Commit the database changes
            conn.commit()
            
            # Trigger learning in the intelligence engine
            from .ingredient_intelligence_engine import IngredientMapping
            
            mock_mapping = IngredientMapping(
                raw_text=raw_text,
                canonical_id=suggested_id,
                canonical_name=None,  # Will be looked up by learning function
                confidence=confidence
            )
            
            self.intelligence_engine.learn_from_verification(mock_mapping, verified_canonical_id)
            
            print(f"✅ Verified mapping: '{raw_text}' → canonical_id {verified_canonical_id}")
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            if conn:
                conn.rollback()
            return False
    
    def batch_verify_mappings(self, verifications: List[Tuple[int, int]]) -> Dict[str, int]:
        """
        ⚡ Batch process multiple verifications for efficiency
        
        verifications: List of (pending_id, verified_canonical_id) tuples
        Returns: Dictionary with success/failure counts
        """
        
        successful = 0
        failed = 0
        
        for pending_id, canonical_id in verifications:
            if self.verify_mapping(pending_id, canonical_id):
                successful += 1
            else:
                failed += 1
        
        return {
            'successful': successful,
            'failed': failed,
            'total': len(verifications)
        }
    
    def get_queue_statistics(self) -> Dict:
        """Get current review queue statistics"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_pending,
                    COUNT(CASE WHEN suggested_canonical_id IS NOT NULL THEN 1 END) as with_suggestions,
                    COUNT(CASE WHEN suggested_canonical_id IS NULL THEN 1 END) as without_suggestions,
                    AVG(confidence) as avg_confidence,
                    MIN(created_at) as oldest_pending
                FROM ingredient_review_queue
            """)
            
            result = cursor.fetchone()
            if result:
                total, with_sugg, without_sugg, avg_conf, oldest = result
                return {
                    'total_pending': total or 0,
                    'with_suggestions': with_sugg or 0,
                    'without_suggestions': without_sugg or 0,
                    'average_confidence': float(avg_conf) if avg_conf else 0.0,
                    'oldest_pending': oldest.isoformat() if oldest else None
                }
            
        except Exception as e:
            print(f"❌ Failed to get queue statistics: {e}")
            
        return {'error': 'Failed to retrieve statistics'}

# Convenience function for testing the processor
def test_recipe_processing():
    """Test the recipe ingredient processor with sample data"""
    
    processor = RecipeIngredientProcessor()
    
    # Sample recipe ingredients
    test_ingredients = [
        "2 cups all-purpose flour",
        "1 cup granulated sugar", 
        "1/2 cup unsalted butter, softened",
        "2 large eggs",
        "1 tsp vanilla extract",
        "1/2 tsp baking soda",
        "1/4 tsp salt",
        "1 cup chocolate chips"
    ]
    
    print("🧪 Testing Recipe Ingredient Processor:")
    print("=" * 50)
    
    # Process with a real recipe ID
    test_recipe_id = 7  # Use a real recipe ID from the database
    
    try:
        result = processor.process_recipe_ingredients(test_recipe_id, test_ingredients)
        
        print(f"\n📊 Processing Results:")
        print(f"   Recipe ID: {result.recipe_id}")
        print(f"   Total Ingredients: {result.total_ingredients}")
        print(f"   Auto-mapped: {result.auto_mapped}")
        print(f"   Queued for Review: {result.queued_for_review}")
        print(f"   Failed: {result.failed_mappings}")
        print(f"   Success Rate: {result.success_rate:.1f}%")
        print(f"   Processing Time: {result.processing_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_recipe_processing()
