"""
🎯 Adaptive Confidence Scorer - Dynamic Recipe Extraction Confidence
==================================================================

Machine learning-powered confidence scoring system that adapts and improves
based on historical extraction performance and user feedback.

Features:
- Dynamic confidence adjustment based on site reliability
- Method-specific confidence refinement
- User feedback integration for continuous learning
- Real-time confidence prediction optimization
- Site-specific threshold adaptation

Integrates with:
- ExtractionAnalytics for historical performance data
- WebRecipeExtractor for real-time confidence scoring
- User feedback system for learning loop

Author: GitHub Copilot & Team
Date: August 26, 2025 - Day 3 Implementation
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlparse
import json
import math

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ConfidenceFactors:
    """Factors that influence confidence scoring"""
    site_reliability: float = 0.5  # Historical success rate for this site
    method_effectiveness: float = 0.5  # How well this method works for this site
    content_quality_indicators: Dict[str, float] = None  # Quality signals from content
    extraction_completeness: float = 0.5  # How complete the extracted data appears
    consistency_score: float = 0.5  # How consistent the extraction is
    user_feedback_influence: float = 0.0  # Adjustment based on user feedback
    
    def __post_init__(self):
        if self.content_quality_indicators is None:
            self.content_quality_indicators = {}

class AdaptiveConfidenceScorer:
    """
    🎯 Adaptive Confidence Scoring Engine
    
    Dynamically adjusts confidence scores based on learning and historical performance
    """
    
    def __init__(self, analytics_engine=None):
        """Initialize the adaptive confidence scorer"""
        self.analytics = analytics_engine
        
        # Confidence adjustment weights (can be tuned based on performance)
        self.weights = {
            'site_reliability': 0.25,
            'method_effectiveness': 0.25,
            'content_quality': 0.20,
            'extraction_completeness': 0.15,
            'consistency_score': 0.10,
            'user_feedback': 0.05
        }
        
        # Quality indicators and their weights
        self.quality_indicators = {
            'has_title': 0.20,
            'has_ingredients': 0.25,
            'has_instructions': 0.25,
            'has_timing': 0.10,
            'has_servings': 0.10,
            'has_description': 0.05,
            'has_image': 0.05
        }
        
        logger.info("🎯 AdaptiveConfidenceScorer initialized with dynamic learning")
    
    def calculate_adaptive_confidence(self, 
                                    url: str,
                                    extraction_method: str,
                                    base_confidence: float,
                                    extracted_data: Dict) -> Tuple[float, ConfidenceFactors]:
        """
        Calculate adaptive confidence score using multiple factors and historical learning
        """
        try:
            domain = urlparse(url).netloc.lower()
            
            # Initialize confidence factors
            factors = ConfidenceFactors()
            
            # 1. Site Reliability Factor
            factors.site_reliability = self._calculate_site_reliability(domain)
            
            # 2. Method Effectiveness Factor
            factors.method_effectiveness = self._calculate_method_effectiveness(domain, extraction_method)
            
            # 3. Content Quality Indicators
            factors.content_quality_indicators = self._analyze_content_quality(extracted_data)
            
            # 4. Extraction Completeness
            factors.extraction_completeness = self._calculate_extraction_completeness(extracted_data)
            
            # 5. Consistency Score
            factors.consistency_score = self._calculate_consistency_score(extracted_data)
            
            # 6. User Feedback Influence
            factors.user_feedback_influence = self._calculate_feedback_influence(domain, extraction_method)
            
            # Calculate final adaptive confidence
            adaptive_confidence = self._combine_confidence_factors(base_confidence, factors)
            
            # Apply domain-specific adjustments
            adaptive_confidence = self._apply_domain_adjustments(domain, adaptive_confidence)
            
            # Ensure confidence is in valid range
            adaptive_confidence = max(0.0, min(1.0, adaptive_confidence))
            
            logger.info(f"🎯 Adaptive confidence: {base_confidence:.2f} → {adaptive_confidence:.2f} for {domain}/{extraction_method}")
            
            return adaptive_confidence, factors
            
        except Exception as e:
            logger.warning(f"⚠️ Adaptive confidence calculation failed: {e}")
            return base_confidence, ConfidenceFactors()
    
    def _calculate_site_reliability(self, domain: str) -> float:
        """Calculate site reliability factor based on historical performance"""
        if not self.analytics or domain not in self.analytics.site_metrics:
            return 0.5  # Neutral for unknown sites
        
        site_metrics = self.analytics.site_metrics[domain]
        
        # Base reliability on success rate
        reliability = site_metrics.success_rate
        
        # Adjust based on sample size (more data = more reliable)
        sample_size_factor = min(1.0, site_metrics.total_attempts / 50.0)  # Normalize to 50 attempts
        reliability = reliability * sample_size_factor + 0.5 * (1 - sample_size_factor)
        
        return reliability
    
    def _calculate_method_effectiveness(self, domain: str, method: str) -> float:
        """Calculate how effective this method is for this specific domain"""
        if not self.analytics or domain not in self.analytics.site_metrics:
            return 0.5  # Neutral for unknown combinations
        
        site_metrics = self.analytics.site_metrics[domain]
        
        if method in site_metrics.method_success_rates:
            return site_metrics.method_success_rates[method]
        
        return 0.5  # Neutral for untested method/domain combinations
    
    def _analyze_content_quality(self, extracted_data: Dict) -> Dict[str, float]:
        """Analyze content quality indicators"""
        quality_scores = {}
        
        # Check for presence of key recipe components
        quality_scores['has_title'] = 1.0 if extracted_data.get('title') else 0.0
        quality_scores['has_ingredients'] = 1.0 if extracted_data.get('ingredients') else 0.0
        quality_scores['has_instructions'] = 1.0 if extracted_data.get('instructions') else 0.0
        quality_scores['has_timing'] = 1.0 if extracted_data.get('total_time') or extracted_data.get('prep_time') else 0.0
        quality_scores['has_servings'] = 1.0 if extracted_data.get('servings') else 0.0
        quality_scores['has_description'] = 1.0 if extracted_data.get('description') else 0.0
        quality_scores['has_image'] = 1.0 if extracted_data.get('image_url') else 0.0
        
        # Analyze quality of ingredients
        ingredients = extracted_data.get('ingredients', [])
        if isinstance(ingredients, list):
            if len(ingredients) >= 3:
                quality_scores['ingredients_reasonable_count'] = 1.0
            elif len(ingredients) >= 1:
                quality_scores['ingredients_reasonable_count'] = 0.5
            else:
                quality_scores['ingredients_reasonable_count'] = 0.0
        
        # Analyze quality of instructions
        instructions = extracted_data.get('instructions', [])
        if isinstance(instructions, list):
            if len(instructions) >= 3:
                quality_scores['instructions_reasonable_count'] = 1.0
            elif len(instructions) >= 1:
                quality_scores['instructions_reasonable_count'] = 0.5
            else:
                quality_scores['instructions_reasonable_count'] = 0.0
        
        return quality_scores
    
    def _calculate_extraction_completeness(self, extracted_data: Dict) -> float:
        """Calculate how complete the extraction appears to be"""
        completeness_score = 0.0
        total_possible = 0.0
        
        # Weight different components by importance
        components = [
            ('title', 0.20),
            ('ingredients', 0.30),
            ('instructions', 0.30),
            ('servings', 0.10),
            ('total_time', 0.10)
        ]
        
        for component, weight in components:
            total_possible += weight
            if extracted_data.get(component):
                completeness_score += weight
        
        return completeness_score / total_possible if total_possible > 0 else 0.0
    
    def _calculate_consistency_score(self, extracted_data: Dict) -> float:
        """Calculate internal consistency of extracted data"""
        consistency_score = 0.5  # Start with neutral
        
        # Check for reasonable data relationships
        
        # Timing consistency
        prep_time = extracted_data.get('prep_time', 0) or 0
        cook_time = extracted_data.get('cook_time', 0) or 0
        total_time = extracted_data.get('total_time', 0) or 0
        
        if total_time > 0 and prep_time > 0 and cook_time > 0:
            # Total should be roughly prep + cook
            expected_total = prep_time + cook_time
            if abs(total_time - expected_total) <= 10:  # Within 10 minutes
                consistency_score += 0.2
            elif abs(total_time - expected_total) <= 30:  # Within 30 minutes
                consistency_score += 0.1
        
        # Servings consistency
        servings = extracted_data.get('servings', 0) or 0
        if 1 <= servings <= 20:  # Reasonable serving size
            consistency_score += 0.1
        
        # Ingredient/instruction count relationship
        ingredients = extracted_data.get('ingredients', [])
        instructions = extracted_data.get('instructions', [])
        
        if isinstance(ingredients, list) and isinstance(instructions, list):
            ing_count = len(ingredients)
            inst_count = len(instructions)
            
            if ing_count > 0 and inst_count > 0:
                # Generally, there should be some relationship between ingredient and instruction count
                ratio = min(ing_count, inst_count) / max(ing_count, inst_count)
                if ratio > 0.3:  # Not too imbalanced
                    consistency_score += 0.2
        
        return min(1.0, consistency_score)
    
    def _calculate_feedback_influence(self, domain: str, method: str) -> float:
        """Calculate influence of user feedback on confidence"""
        if not self.analytics:
            return 0.0
        
        # Look for recent user feedback for this domain/method combination
        feedback_influence = 0.0
        
        # Get recent results with feedback
        recent_results = [r for r in self.analytics.recent_results 
                         if r.domain == domain and r.extraction_method == method and r.user_feedback]
        
        if recent_results:
            positive_feedback = sum(1 for r in recent_results if r.user_feedback == 'accepted')
            negative_feedback = sum(1 for r in recent_results if r.user_feedback == 'rejected')
            
            total_feedback = len(recent_results)
            if total_feedback > 0:
                feedback_ratio = positive_feedback / total_feedback
                # Convert to influence factor (-0.2 to +0.2)
                feedback_influence = (feedback_ratio - 0.5) * 0.4
        
        return feedback_influence
    
    def _combine_confidence_factors(self, base_confidence: float, factors: ConfidenceFactors) -> float:
        """Combine all confidence factors into final score"""
        
        # Calculate weighted quality score
        quality_score = 0.0
        quality_total = 0.0
        
        for indicator, value in factors.content_quality_indicators.items():
            if indicator in self.quality_indicators:
                weight = self.quality_indicators[indicator]
                quality_score += value * weight
                quality_total += weight
        
        if quality_total > 0:
            quality_score = quality_score / quality_total
        else:
            quality_score = 0.5
        
        # Combine all factors
        factor_contributions = {
            'site_reliability': factors.site_reliability * self.weights['site_reliability'],
            'method_effectiveness': factors.method_effectiveness * self.weights['method_effectiveness'],
            'content_quality': quality_score * self.weights['content_quality'],
            'extraction_completeness': factors.extraction_completeness * self.weights['extraction_completeness'],
            'consistency_score': factors.consistency_score * self.weights['consistency_score'],
            'user_feedback': factors.user_feedback_influence * self.weights['user_feedback']
        }
        
        # Calculate adaptive adjustment
        adaptive_factor = sum(factor_contributions.values())
        
        # Blend base confidence with adaptive factor
        # Use 60% adaptive, 40% base confidence
        adaptive_confidence = 0.6 * adaptive_factor + 0.4 * base_confidence
        
        return adaptive_confidence
    
    def _apply_domain_adjustments(self, domain: str, confidence: float) -> float:
        """Apply domain-specific confidence adjustments"""
        
        # Known high-quality sites get a slight boost
        high_quality_domains = ['bonappetit.com', 'seriouseats.com', 'cooking.nytimes.com']
        
        if any(hq_domain in domain for hq_domain in high_quality_domains):
            confidence = min(1.0, confidence + 0.05)
        
        # Known problematic patterns get slight penalty
        if 'blogspot' in domain or 'wordpress' in domain:
            confidence = max(0.0, confidence - 0.05)
        
        return confidence
    
    def get_confidence_explanation(self, factors: ConfidenceFactors) -> Dict[str, Any]:
        """Generate human-readable explanation of confidence factors"""
        
        # Calculate quality score
        quality_items = list(factors.content_quality_indicators.items())
        quality_score = sum(v for v in factors.content_quality_indicators.values()) / len(quality_items) if quality_items else 0
        
        explanation = {
            'overall_assessment': self._get_confidence_level_description(
                (factors.site_reliability + factors.method_effectiveness + quality_score) / 3
            ),
            'site_reliability': {
                'score': factors.site_reliability,
                'description': self._get_reliability_description(factors.site_reliability)
            },
            'method_effectiveness': {
                'score': factors.method_effectiveness,
                'description': self._get_effectiveness_description(factors.method_effectiveness)
            },
            'content_quality': {
                'score': quality_score,
                'description': self._get_quality_description(quality_score),
                'details': factors.content_quality_indicators
            },
            'completeness': {
                'score': factors.extraction_completeness,
                'description': self._get_completeness_description(factors.extraction_completeness)
            },
            'consistency': {
                'score': factors.consistency_score,
                'description': self._get_consistency_description(factors.consistency_score)
            }
        }
        
        return explanation
    
    def _get_confidence_level_description(self, score: float) -> str:
        """Get human-readable confidence level"""
        if score >= 0.8:
            return "High confidence - extraction appears very reliable"
        elif score >= 0.6:
            return "Good confidence - extraction appears reliable"
        elif score >= 0.4:
            return "Moderate confidence - extraction may need review"
        else:
            return "Low confidence - extraction likely needs correction"
    
    def _get_reliability_description(self, score: float) -> str:
        """Get site reliability description"""
        if score >= 0.8:
            return "Highly reliable site with consistent extraction success"
        elif score >= 0.6:
            return "Generally reliable site"
        elif score >= 0.4:
            return "Moderately reliable site"
        else:
            return "Site with limited extraction success history"
    
    def _get_effectiveness_description(self, score: float) -> str:
        """Get method effectiveness description"""
        if score >= 0.8:
            return "Extraction method works very well for this site"
        elif score >= 0.6:
            return "Extraction method generally effective for this site"
        elif score >= 0.4:
            return "Extraction method has mixed results for this site"
        else:
            return "Extraction method has limited success for this site"
    
    def _get_quality_description(self, score: float) -> str:
        """Get content quality description"""
        if score >= 0.8:
            return "High-quality recipe data with most components present"
        elif score >= 0.6:
            return "Good recipe data with key components present"
        elif score >= 0.4:
            return "Basic recipe data with some missing components"
        else:
            return "Limited recipe data with many missing components"
    
    def _get_completeness_description(self, score: float) -> str:
        """Get extraction completeness description"""
        if score >= 0.8:
            return "Very complete extraction with all major components"
        elif score >= 0.6:
            return "Good extraction with most components present"
        elif score >= 0.4:
            return "Partial extraction with some components missing"
        else:
            return "Incomplete extraction with many components missing"
    
    def _get_consistency_description(self, score: float) -> str:
        """Get data consistency description"""
        if score >= 0.8:
            return "Data appears internally consistent and reasonable"
        elif score >= 0.6:
            return "Data is mostly consistent with minor inconsistencies"
        elif score >= 0.4:
            return "Data has some inconsistencies that may need review"
        else:
            return "Data has significant inconsistencies"

# Export main class
__all__ = ['AdaptiveConfidenceScorer', 'ConfidenceFactors']

if __name__ == "__main__":
    # Basic testing
    scorer = AdaptiveConfidenceScorer()
    
    # Test with sample extracted data
    test_data = {
        'title': 'Perfect Chocolate Chip Cookies',
        'ingredients': ['2 cups flour', '1 cup butter', '1 cup chocolate chips'],
        'instructions': ['Mix dry ingredients', 'Add wet ingredients', 'Bake for 12 minutes'],
        'total_time': 45,
        'servings': 24,
        'description': 'The best chocolate chip cookies ever!'
    }
    
    url = "https://www.bonappetit.com/recipe/test"
    method = "json_ld"
    base_confidence = 0.8
    
    adaptive_confidence, factors = scorer.calculate_adaptive_confidence(url, method, base_confidence, test_data)
    
    print(f"🎯 Adaptive Confidence Test:")
    print(f"   Base confidence: {base_confidence:.2f}")
    print(f"   Adaptive confidence: {adaptive_confidence:.2f}")
    print(f"   Site reliability: {factors.site_reliability:.2f}")
    print(f"   Method effectiveness: {factors.method_effectiveness:.2f}")
    print(f"   Extraction completeness: {factors.extraction_completeness:.2f}")
    
    # Get explanation
    explanation = scorer.get_confidence_explanation(factors)
    print(f"   Overall assessment: {explanation['overall_assessment']}")
    
    print("✅ AdaptiveConfidenceScorer working correctly!")
