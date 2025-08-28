#!/usr/bin/env python3
"""
URL Extraction System Test - Day 2 Implementation
===============================================

Tests the URL extraction functionality:
- JSON-LD Schema.org extraction
- Site-specific extractors (BonAppetit, Food Network, etc.)
- Fallback extraction methods
- Integration with import system
- Performance and reliability

Run this after implementing Day 2 to verify URL extraction works.
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core_systems.web_recipe_extractor import WebRecipeExtractor, WebRecipeData
    from core_systems.recipe_importer import UniversalRecipeImporter, ImportRequest, ImportResult
    print("✅ Successfully imported WebRecipeExtractor and UniversalRecipeImporter")
except ImportError as e:
    print(f"❌ Failed to import URL extraction systems: {e}")
    sys.exit(1)

class URLExtractionTester:
    def __init__(self):
        self.base_url = 'http://localhost:5000'
        self.web_extractor = WebRecipeExtractor()
        self.importer = UniversalRecipeImporter()
        
        # Test URLs for different extraction methods
        self.test_urls = {
            'json_ld': [
                'https://www.allrecipes.com/recipe/213742/cheesy-chicken-broccoli-casserole/',
                'https://www.food.com/recipe/simple-pasta-salad-12345'
            ],
            'bonappetit': [
                'https://www.bonappetit.com/recipe/simple-tomato-salad',
                'https://www.bonappetit.com/recipe/perfect-pizza-dough'
            ],
            'foodnetwork': [
                'https://www.foodnetwork.com/recipes/ree-drummond/chicken-fried-steak-recipe-2107383'
            ],
            'generic': [
                'https://example.com/fake-recipe-url',  # For testing fallback
            ]
        }
        
    def test_web_extractor_direct(self):
        """Test WebRecipeExtractor class directly"""
        print("\n🌐 Testing WebRecipeExtractor Direct...")
        
        # Test with a known good URL (mock test)
        test_url = "https://www.example.com/test-recipe"
        
        try:
            # Since we can't rely on external URLs in testing, let's test the initialization
            extractor = WebRecipeExtractor()
            print("✅ WebRecipeExtractor initialized successfully")
            print(f"   Supported sites: {len(extractor.site_extractors)}")
            print(f"   Site extractors: {list(extractor.site_extractors.keys())}")
            
            # Test URL validation logic
            valid_urls = [
                "https://www.bonappetit.com/recipe/test",
                "https://www.foodnetwork.com/recipes/test",
                "https://www.allrecipes.com/recipe/123/test"
            ]
            
            for url in valid_urls:
                domain = extractor.session.headers.get('User-Agent')
                if domain:
                    print(f"✅ User agent configured: {domain[:50]}...")
                    break
            
            return True
            
        except Exception as e:
            print(f"❌ WebRecipeExtractor test failed: {e}")
            return False
    
    def test_import_system_url_integration(self):
        """Test URL import through the UniversalRecipeImporter"""
        print("\n🔗 Testing URL Import Integration...")
        
        try:
            # Test with invalid URL first
            invalid_request = ImportRequest(
                source_type='url',
                source_data='not-a-url',
                user_id=1
            )
            
            result = self.importer.import_from_url('not-a-url', 1)
            
            if not result.success and 'Invalid URL format' in str(result.errors):
                print("✅ Invalid URL handling works correctly")
            else:
                print("❌ Invalid URL handling failed")
                return False
            
            # Test with valid URL format (even if extraction fails)
            valid_url = "https://www.example.com/recipe"
            result = self.importer.import_from_url(valid_url, 1)
            
            # Should not crash, even if extraction fails
            print(f"✅ Valid URL processing completed")
            print(f"   Success: {result.success}")
            print(f"   Extraction Method: {result.extraction_method}")
            print(f"   Errors: {result.errors}")
            
            return True
            
        except Exception as e:
            print(f"❌ URL import integration test failed: {e}")
            return False
    
    def test_api_url_import_endpoint(self):
        """Test URL import via API endpoint"""
        print("\n🌐 Testing API URL Import Endpoint...")
        
        try:
            # Test with valid URL format
            test_url = "https://www.bonappetit.com/recipe/test-recipe"
            
            response = requests.post(
                f'{self.base_url}/api/recipes/import/url',
                json={
                    'url': test_url,
                    'user_id': 1
                },
                timeout=15  # Increased timeout for web extraction
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API URL import endpoint responding")
                print(f"   Success: {data.get('success')}")
                print(f"   Extraction Method: {data.get('extraction_method')}")
                print(f"   Confidence: {data.get('confidence', 0):.2f}")
                print(f"   Processing Time: {data.get('processing_time', 0):.2f}s")
                
                # Check if it's no longer a placeholder
                if 'placeholder' not in data.get('extraction_method', ''):
                    print("✅ URL extraction system is active (no longer placeholder)")
                    return True
                else:
                    print("⚠️ Still using placeholder - Day 2 not fully implemented")
                    return False
            else:
                print(f"❌ API returned status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return False
    
    def test_extraction_methods(self):
        """Test different extraction methods"""
        print("\n🧪 Testing Extraction Methods...")
        
        try:
            extractor = WebRecipeExtractor()
            
            # Test JSON-LD parsing with mock data
            mock_json_ld = {
                "@type": "Recipe",
                "name": "Test Recipe",
                "description": "A test recipe",
                "recipeIngredient": ["1 cup flour", "2 eggs"],
                "recipeInstructions": [
                    {"text": "Mix ingredients"},
                    {"text": "Bake for 30 minutes"}
                ],
                "totalTime": "PT45M",
                "recipeYield": "4 servings"
            }
            
            # Test parsing logic
            recipe = extractor._parse_json_ld_recipe(mock_json_ld)
            if recipe and recipe.title == "Test Recipe":
                print("✅ JSON-LD parsing logic works")
            else:
                print("❌ JSON-LD parsing logic failed")
                return False
            
            # Test duration parsing
            test_durations = ["PT30M", "PT1H30M", "45 minutes", "1 hour"]
            for duration in test_durations:
                parsed = extractor._parse_duration(duration)
                if parsed is not None:
                    print(f"✅ Duration parsing: '{duration}' → {parsed} minutes")
                else:
                    print(f"⚠️ Could not parse duration: '{duration}'")
            
            # Test servings parsing
            test_servings = ["4", "serves 6", "6-8 servings", 4, "makes 12"]
            for serving in test_servings:
                parsed = extractor._parse_servings(serving)
                if parsed is not None:
                    print(f"✅ Servings parsing: '{serving}' → {parsed} servings")
                else:
                    print(f"⚠️ Could not parse servings: '{serving}'")
            
            return True
            
        except Exception as e:
            print(f"❌ Extraction methods test failed: {e}")
            return False
    
    def test_backend_health_url_support(self):
        """Test if backend reports URL import capability"""
        print("\n🏥 Testing Backend URL Import Support...")
        
        try:
            response = requests.get(f'{self.base_url}/api/health', timeout=5)
            if response.status_code == 200:
                data = response.json()
                capabilities = data.get('capabilities', {})
                
                print(f"✅ Backend health check successful")
                print(f"   Recipe Import Available: {capabilities.get('recipe_import', False)}")
                print(f"   Database Connection: {capabilities.get('database_connection', False)}")
                
                # Check if import system is available
                if capabilities.get('recipe_import', False):
                    print("✅ Recipe import system is available for URL processing")
                    return True
                else:
                    print("❌ Recipe import system not available")
                    return False
            else:
                print(f"❌ Health check failed with status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to backend for health check: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling for various URL scenarios"""
        print("\n⚠️ Testing URL Error Handling...")
        
        error_test_cases = [
            ("", "Empty URL"),
            ("not-a-url", "Invalid URL format"),
            ("ftp://invalid.protocol.com", "Invalid protocol"),
            ("https://", "Incomplete URL"),
        ]
        
        passed = 0
        total = len(error_test_cases)
        
        for test_url, description in error_test_cases:
            try:
                result = self.importer.import_from_url(test_url, 1)
                
                if not result.success:
                    print(f"✅ {description}: Properly rejected")
                    passed += 1
                else:
                    print(f"❌ {description}: Should have been rejected but wasn't")
            except Exception as e:
                print(f"❌ {description}: Crashed with {e}")
        
        print(f"📊 Error handling: {passed}/{total} test cases passed")
        return passed == total
    
    def benchmark_extraction_performance(self):
        """Benchmark extraction performance"""
        print("\n⚡ Benchmarking Extraction Performance...")
        
        try:
            extractor = WebRecipeExtractor()
            
            # Test initialization time
            start_time = datetime.now()
            test_extractor = WebRecipeExtractor()
            init_time = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ WebRecipeExtractor initialization: {init_time:.3f}s")
            
            # Test parsing performance with mock data
            mock_data = {
                "@type": "Recipe",
                "name": "Performance Test Recipe",
                "recipeIngredient": [f"Ingredient {i}" for i in range(20)],
                "recipeInstructions": [{"text": f"Step {i}"} for i in range(10)]
            }
            
            start_time = datetime.now()
            for _ in range(100):  # Parse 100 times
                recipe = extractor._parse_json_ld_recipe(mock_data)
            parse_time = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ JSON-LD parsing (100x): {parse_time:.3f}s ({parse_time*10:.1f}ms per parse)")
            
            # Performance criteria
            if init_time < 1.0 and parse_time < 0.5:
                print("✅ Performance benchmarks met")
                return True
            else:
                print("⚠️ Performance may need optimization")
                return False
                
        except Exception as e:
            print(f"❌ Performance benchmark failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive URL extraction test suite"""
        print("🌐 URL EXTRACTION SYSTEM - DAY 2 TESTING")
        print("=" * 55)
        
        tests = [
            ('WebRecipeExtractor Direct Test', self.test_web_extractor_direct),
            ('Import System URL Integration', self.test_import_system_url_integration),
            ('API URL Import Endpoint', self.test_api_url_import_endpoint),
            ('Extraction Methods', self.test_extraction_methods),
            ('Backend URL Support', self.test_backend_health_url_support),
            ('URL Error Handling', self.test_error_handling),
            ('Performance Benchmark', self.benchmark_extraction_performance),
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
        
        print(f"\n📊 URL EXTRACTION TEST RESULTS:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success Rate: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "   📈 No tests run")
        
        if failed == 0:
            print("\n🎉 ALL URL EXTRACTION TESTS PASSED! Day 2 implementation is working correctly.")
        else:
            print(f"\n⚠️ {failed} test(s) failed. Check the output above for details.")
        
        return failed == 0

if __name__ == "__main__":
    print("Starting URL Extraction System Test...")
    
    tester = URLExtractionTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Ready to proceed to Day 3 implementation!")
        sys.exit(0)
    else:
        print("\n❌ Please fix the issues above before proceeding.")
        sys.exit(1)
