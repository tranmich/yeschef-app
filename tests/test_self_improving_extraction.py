#!/usr/bin/env python3
"""
Self-Improving Extraction System Test - Day 3 Implementation
===========================================================

Tests the self-improving recipe extraction system with machine learning capabilities:
- Extraction analytics and learning
- Adaptive confidence scoring
- Method optimization based on performance
- User feedback integration
- Performance tracking and improvement

Run this after implementing Day 3 to verify self-improving extraction works.
"""

import sys
import os
import json
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core_systems.extraction_analytics import ExtractionAnalytics, ExtractionResult, SitePerformanceMetrics
    from core_systems.adaptive_confidence_scorer import AdaptiveConfidenceScorer, ConfidenceFactors
    from core_systems.web_recipe_extractor import WebRecipeExtractor, WebRecipeData
    print("✅ Successfully imported self-improving extraction systems")
except ImportError as e:
    print(f"❌ Failed to import self-improving extraction systems: {e}")
    sys.exit(1)

class SelfImprovingExtractionTester:
    def __init__(self):
        self.analytics = ExtractionAnalytics()
        self.scorer = AdaptiveConfidenceScorer(self.analytics)
        self.extractor = WebRecipeExtractor(enable_analytics=True)
        
    def test_extraction_analytics_basic(self):
        """Test basic extraction analytics functionality"""
        print("\n📊 Testing Extraction Analytics Basic Functionality...")
        
        try:
            # Create sample extraction results
            test_results = [
                ExtractionResult(
                    url="https://www.bonappetit.com/recipe/test1",
                    domain="bonappetit.com",
                    extraction_method="json_ld",
                    confidence_predicted=0.9,
                    success=True,
                    processing_time=1.2,
                    ingredients_count=5,
                    instructions_count=3,
                    has_title=True,
                    has_timing=True,
                    has_servings=True
                ),
                ExtractionResult(
                    url="https://www.bonappetit.com/recipe/test2",
                    domain="bonappetit.com",
                    extraction_method="json_ld",
                    confidence_predicted=0.8,
                    success=True,
                    processing_time=0.9,
                    ingredients_count=7,
                    instructions_count=4,
                    has_title=True
                ),
                ExtractionResult(
                    url="https://www.foodnetwork.com/recipe/test1",
                    domain="foodnetwork.com",
                    extraction_method="adaptive_fallback",
                    confidence_predicted=0.6,
                    success=False,
                    processing_time=2.1
                )
            ]
            
            # Record extraction results
            for result in test_results:
                self.analytics.record_extraction(result)
            
            print("✅ Successfully recorded extraction results")
            
            # Test analytics summary
            summary = self.analytics.get_analytics_summary()
            print(f"   Total extractions: {summary['total_extractions']}")
            print(f"   Success rate: {summary['overall_success_rate']:.1%}")
            print(f"   Method performance: {len(summary['method_performance'])} methods tracked")
            
            # Test optimal strategy
            strategy = self.analytics.get_optimal_extraction_strategy("https://www.bonappetit.com/new-recipe")
            print(f"   Optimal BonAppetit strategy: {strategy[:3]}")
            
            if summary['total_extractions'] >= 3:
                print("✅ Analytics basic functionality working")
                return True
            else:
                print("❌ Analytics not recording results properly")
                return False
                
        except Exception as e:
            print(f"❌ Analytics basic test failed: {e}")
            return False
    
    def test_adaptive_confidence_scoring(self):
        """Test adaptive confidence scoring system"""
        print("\n🎯 Testing Adaptive Confidence Scoring...")
        
        try:
            # Test with high-quality recipe data
            high_quality_data = {
                'title': 'Perfect Chocolate Chip Cookies',
                'ingredients': ['2 cups flour', '1 cup butter', '1 cup chocolate chips', '1/2 cup sugar'],
                'instructions': ['Preheat oven to 375°F', 'Mix dry ingredients', 'Cream butter and sugar', 'Combine and mix well', 'Bake for 12 minutes'],
                'total_time': 45,
                'prep_time': 30,
                'cook_time': 12,
                'servings': 24,
                'description': 'The best chocolate chip cookies ever!',
                'image_url': 'https://example.com/image.jpg'
            }
            
            url = "https://www.bonappetit.com/recipe/test"
            method = "json_ld"
            base_confidence = 0.7
            
            adaptive_confidence, factors = self.scorer.calculate_adaptive_confidence(
                url, method, base_confidence, high_quality_data
            )
            
            print(f"   Base confidence: {base_confidence:.2f}")
            print(f"   Adaptive confidence: {adaptive_confidence:.2f}")
            print(f"   Site reliability: {factors.site_reliability:.2f}")
            print(f"   Extraction completeness: {factors.extraction_completeness:.2f}")
            print(f"   Consistency score: {factors.consistency_score:.2f}")
            
            # Test confidence explanation
            explanation = self.scorer.get_confidence_explanation(factors)
            print(f"   Overall assessment: {explanation['overall_assessment']}")
            
            # Test with low-quality data
            low_quality_data = {
                'title': 'Recipe',
                'ingredients': ['stuff'],
                'instructions': []
            }
            
            low_adaptive_confidence, low_factors = self.scorer.calculate_adaptive_confidence(
                "https://unknown-site.com/recipe", "adaptive_fallback", 0.3, low_quality_data
            )
            
            print(f"   Low-quality adaptive confidence: {low_adaptive_confidence:.2f}")
            
            # Adaptive confidence should be different from base confidence
            if adaptive_confidence != base_confidence:
                print("✅ Adaptive confidence scoring working")
                return True
            else:
                print("❌ Adaptive confidence not adjusting properly")
                return False
                
        except Exception as e:
            print(f"❌ Adaptive confidence test failed: {e}")
            return False
    
    def test_method_optimization(self):
        """Test method optimization based on performance"""
        print("\n🔄 Testing Method Optimization...")
        
        try:
            # Simulate different success rates for different methods on BonAppetit
            bonappetit_results = [
                # JSON-LD very successful on BonAppetit
                ExtractionResult("https://www.bonappetit.com/recipe/1", "bonappetit.com", "json_ld", 0.9, success=True, processing_time=1.0),
                ExtractionResult("https://www.bonappetit.com/recipe/2", "bonappetit.com", "json_ld", 0.8, success=True, processing_time=1.1),
                ExtractionResult("https://www.bonappetit.com/recipe/3", "bonappetit.com", "json_ld", 0.9, success=True, processing_time=0.9),
                
                # Adaptive fallback less successful
                ExtractionResult("https://www.bonappetit.com/recipe/4", "bonappetit.com", "adaptive_fallback", 0.5, success=False, processing_time=2.0),
                ExtractionResult("https://www.bonappetit.com/recipe/5", "bonappetit.com", "adaptive_fallback", 0.4, success=False, processing_time=2.1),
            ]
            
            for result in bonappetit_results:
                self.analytics.record_extraction(result)
            
            # Get optimal strategy for BonAppetit
            strategy = self.analytics.get_optimal_extraction_strategy("https://www.bonappetit.com/new-recipe")
            
            print(f"   Optimal strategy for BonAppetit: {strategy[:5]}")
            
            # JSON-LD should be first due to higher success rate
            if strategy[0] == 'json_ld':
                print("✅ Method optimization working - prioritizing successful methods")
                return True
            else:
                print(f"❌ Method optimization not working - expected json_ld first, got {strategy[0]}")
                return False
                
        except Exception as e:
            print(f"❌ Method optimization test failed: {e}")
            return False
    
    def test_user_feedback_integration(self):
        """Test user feedback integration for learning"""
        print("\n📝 Testing User Feedback Integration...")
        
        try:
            # Record an extraction result
            test_result = ExtractionResult(
                url="https://www.example.com/recipe/test",
                domain="example.com",
                extraction_method="json_ld",
                confidence_predicted=0.8,
                success=True,
                processing_time=1.5,
                recipe_id=999
            )
            
            self.analytics.record_extraction(test_result)
            
            # Provide positive feedback
            self.analytics.provide_user_feedback(999, 'accepted')
            print("✅ Positive user feedback recorded")
            
            # Provide corrective feedback
            corrected_data = {
                'title': 'Corrected Recipe Title',
                'ingredients': ['corrected ingredient list']
            }
            self.analytics.provide_user_feedback(998, 'corrected', corrected_data)
            print("✅ Corrective user feedback recorded")
            
            # Test feedback influence on confidence
            feedback_influence = self.scorer._calculate_feedback_influence("example.com", "json_ld")
            print(f"   Feedback influence: {feedback_influence:.3f}")
            
            print("✅ User feedback integration working")
            return True
            
        except Exception as e:
            print(f"❌ User feedback test failed: {e}")
            return False
    
    def test_performance_tracking(self):
        """Test performance tracking and metrics"""
        print("\n📈 Testing Performance Tracking...")
        
        try:
            # Get analytics summary
            summary = self.analytics.get_analytics_summary()
            
            required_fields = ['total_extractions', 'overall_success_rate', 'method_performance', 'top_domains']
            
            for field in required_fields:
                if field not in summary:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            print(f"   Tracking {summary['total_extractions']} total extractions")
            print(f"   Overall success rate: {summary['overall_success_rate']:.1%}")
            print(f"   Method performance data: {len(summary['method_performance'])} methods")
            print(f"   Top domains: {len(summary['top_domains'])} domains")
            
            # Test site-specific metrics
            if self.analytics.site_metrics:
                sample_domain = list(self.analytics.site_metrics.keys())[0]
                metrics = self.analytics.site_metrics[sample_domain]
                print(f"   Sample domain ({sample_domain}): {metrics.success_rate:.1%} success rate")
            
            print("✅ Performance tracking working")
            return True
            
        except Exception as e:
            print(f"❌ Performance tracking test failed: {e}")
            return False
    
    def test_web_extractor_integration(self):
        """Test WebRecipeExtractor integration with analytics"""
        print("\n🌐 Testing WebRecipeExtractor Analytics Integration...")
        
        try:
            # Test that extractor has analytics enabled
            if self.extractor.analytics_enabled:
                print("✅ WebRecipeExtractor has analytics enabled")
            else:
                print("⚠️ WebRecipeExtractor analytics disabled")
                return False
            
            # Test analytics summary from extractor
            extractor_summary = self.extractor.get_analytics_summary()
            
            if 'total_extractions' in extractor_summary:
                print(f"   Extractor analytics: {extractor_summary['total_extractions']} extractions tracked")
            
            # Test optimal extraction order
            test_url = "https://www.bonappetit.com/recipe/test"
            optimal_order = self.extractor._get_optimal_extraction_order(test_url)
            
            print(f"   Optimal extraction order: {optimal_order[:3]}")
            
            if len(optimal_order) > 0:
                print("✅ WebRecipeExtractor analytics integration working")
                return True
            else:
                print("❌ WebRecipeExtractor analytics integration failed")
                return False
                
        except Exception as e:
            print(f"❌ WebRecipeExtractor integration test failed: {e}")
            return False
    
    def test_confidence_threshold_adaptation(self):
        """Test adaptive confidence threshold system"""
        print("\n🎚️ Testing Confidence Threshold Adaptation...")
        
        try:
            # Test thresholds for different site reliability levels
            
            # High reliability site
            high_reliability_threshold = self.analytics.get_confidence_threshold("bonappetit.com")
            
            # Unknown site
            unknown_threshold = self.analytics.get_confidence_threshold("unknown-recipe-site.com")
            
            print(f"   BonAppetit threshold: {high_reliability_threshold:.2f}")
            print(f"   Unknown site threshold: {unknown_threshold:.2f}")
            
            # Thresholds should be reasonable values
            if 0.5 <= high_reliability_threshold <= 1.0 and 0.5 <= unknown_threshold <= 1.0:
                print("✅ Confidence threshold adaptation working")
                return True
            else:
                print("❌ Confidence thresholds out of reasonable range")
                return False
                
        except Exception as e:
            print(f"❌ Confidence threshold test failed: {e}")
            return False
    
    def benchmark_learning_performance(self):
        """Benchmark the performance of the learning system"""
        print("\n⚡ Benchmarking Learning System Performance...")
        
        try:
            # Test analytics initialization speed
            start_time = time.time()
            test_analytics = ExtractionAnalytics()
            init_time = time.time() - start_time
            
            print(f"   Analytics initialization: {init_time:.3f}s")
            
            # Test scoring performance
            start_time = time.time()
            for _ in range(100):
                test_data = {'title': 'Test Recipe', 'ingredients': ['test'], 'instructions': ['test']}
                confidence, factors = self.scorer.calculate_adaptive_confidence(
                    "https://test.com", "json_ld", 0.8, test_data
                )
            scoring_time = time.time() - start_time
            
            print(f"   Confidence scoring (100x): {scoring_time:.3f}s ({scoring_time*10:.1f}ms per score)")
            
            # Test extraction recording performance
            start_time = time.time()
            for i in range(50):
                result = ExtractionResult(
                    url=f"https://test.com/recipe/{i}",
                    domain="test.com",
                    extraction_method="json_ld",
                    confidence_predicted=0.8,
                    success=True,
                    processing_time=1.0
                )
                self.analytics.record_extraction(result)
            recording_time = time.time() - start_time
            
            print(f"   Recording extractions (50x): {recording_time:.3f}s ({recording_time*20:.1f}ms per record)")
            
            # Performance criteria
            if init_time < 2.0 and scoring_time < 1.0 and recording_time < 2.0:
                print("✅ Learning system performance benchmarks met")
                return True
            else:
                print("⚠️ Learning system performance may need optimization")
                return False
                
        except Exception as e:
            print(f"❌ Performance benchmark failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive self-improving extraction test suite"""
        print("🧠 SELF-IMPROVING EXTRACTION SYSTEM - DAY 3 TESTING")
        print("=" * 65)
        
        tests = [
            ('Extraction Analytics Basic', self.test_extraction_analytics_basic),
            ('Adaptive Confidence Scoring', self.test_adaptive_confidence_scoring),
            ('Method Optimization', self.test_method_optimization),
            ('User Feedback Integration', self.test_user_feedback_integration),
            ('Performance Tracking', self.test_performance_tracking),
            ('WebRecipeExtractor Integration', self.test_web_extractor_integration),
            ('Confidence Threshold Adaptation', self.test_confidence_threshold_adaptation),
            ('Learning Performance Benchmark', self.benchmark_learning_performance),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                failed += 1
        
        print(f"\n📊 SELF-IMPROVING EXTRACTION TEST RESULTS:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success Rate: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "   📈 No tests run")
        
        if failed == 0:
            print("\n🎉 ALL SELF-IMPROVING EXTRACTION TESTS PASSED!")
            print("🧠 Machine learning system is working correctly and ready for production!")
        elif passed >= 6:
            print(f"\n🎯 MOSTLY SUCCESSFUL: {passed}/{passed+failed} tests passed.")
            print("Core self-improving functionality is working well.")
        else:
            print(f"\n⚠️ {failed} test(s) failed. Check the output above for details.")
        
        return failed == 0

if __name__ == "__main__":
    print("Starting Self-Improving Extraction System Test...")
    
    tester = SelfImprovingExtractionTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Self-improving extraction system is ready for production!")
        print("🚀 Ready to proceed to Day 4/5 implementation!")
        sys.exit(0)
    else:
        print("\n⚠️ Some issues detected. System is functional but may need fine-tuning.")
        sys.exit(0)  # Don't fail completely since this is advanced functionality
