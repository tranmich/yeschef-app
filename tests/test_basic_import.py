#!/usr/bin/env python3
"""
Basic Import System Test - Day 1 Implementation
==============================================

Tests the core import functionality:
- Text recipe import
- Basic API endpoints
- Error handling
- Integration with existing systems

Run this after implementing Day 1 to verify everything works.
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core_systems.recipe_importer import UniversalRecipeImporter, ImportRequest, ImportResult
    print("✅ Successfully imported UniversalRecipeImporter")
except ImportError as e:
    print(f"❌ Failed to import UniversalRecipeImporter: {e}")
    sys.exit(1)

class ImportSystemTester:
    def __init__(self):
        self.base_url = 'http://localhost:5000'  # Adjust if needed
        self.importer = UniversalRecipeImporter()
        
    def test_backend_health(self):
        """Test if backend is running and import system is available"""
        print("\n🏥 Testing Backend Health...")
        try:
            response = requests.get(f'{self.base_url}/api/health', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend is running")
                print(f"   Recipe Import Available: {data.get('capabilities', {}).get('recipe_import', False)}")
                print(f"   Database Connection: {data.get('capabilities', {}).get('database_connection', False)}")
                print(f"   Recipe Count: {data.get('capabilities', {}).get('recipe_count', 'Unknown')}")
                return True
            else:
                print(f"❌ Backend returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to backend: {e}")
            return False
    
    def test_direct_import(self):
        """Test direct UniversalRecipeImporter class"""
        print("\n🧪 Testing Direct Import System...")
        
        test_recipe = """
        Spaghetti Carbonara

        Ingredients:
        - 400g spaghetti
        - 200g pancetta, diced
        - 4 large eggs
        - 100g Parmesan cheese, grated
        - Black pepper
        - Salt

        Instructions:
        1. Cook spaghetti according to package directions
        2. Fry pancetta until crispy
        3. Beat eggs with Parmesan
        4. Combine hot pasta with pancetta
        5. Add egg mixture and toss quickly
        6. Season with pepper and serve
        """
        
        try:
            # Create import request
            request = ImportRequest(
                source_type='text',
                source_data=test_recipe,
                user_id=1
            )
            
            # Process import
            start_time = datetime.now()
            result = self.importer.import_recipe(request)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            print(f"✅ Import completed in {processing_time:.2f}s")
            print(f"   Success: {result.success}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Recipe ID: {result.recipe_id}")
            print(f"   Needs Review: {result.needs_review}")
            print(f"   Extraction Method: {result.extraction_method}")
            
            if result.errors:
                print(f"   Errors: {', '.join(result.errors)}")
            if result.warnings:
                print(f"   Warnings: {', '.join(result.warnings)}")
            
            return result.success
            
        except Exception as e:
            print(f"❌ Direct import failed: {e}")
            return False
    
    def test_api_text_import(self):
        """Test text import via API endpoint"""
        print("\n🌐 Testing API Text Import...")
        
        test_recipe = """
        Simple Pasta Salad
        
        Ingredients:
        - 300g pasta
        - 2 tomatoes, diced
        - 1 cucumber, diced
        - 100g feta cheese
        - Olive oil
        - Basil leaves
        
        Instructions:
        1. Cook pasta and let cool
        2. Mix with vegetables
        3. Add feta and oil
        4. Garnish with basil
        """
        
        try:
            response = requests.post(
                f'{self.base_url}/api/recipes/import/text',
                json={
                    'recipe_text': test_recipe,
                    'user_id': 1
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API import successful")
                print(f"   Success: {data.get('success')}")
                print(f"   Confidence: {data.get('confidence', 0):.2f}")
                print(f"   Recipe ID: {data.get('recipe_id')}")
                print(f"   Processing Time: {data.get('processing_time', 0):.2f}s")
                return True
            else:
                print(f"❌ API returned status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return False
    
    def test_api_url_import(self):
        """Test URL import via API endpoint (should show Day 2 placeholder)"""
        print("\n🔗 Testing API URL Import (Day 2 Preview)...")
        
        try:
            response = requests.post(
                f'{self.base_url}/api/recipes/import/url',
                json={
                    'url': 'https://www.bonappetit.com/recipe/simple-pasta',
                    'user_id': 1
                },
                timeout=10
            )
            
            data = response.json()
            print(f"   Response: {data.get('error', 'Unknown response')}")
            print(f"   Warnings: {data.get('warnings', [])}")
            
            # This should fail for Day 1 with a "coming in Day 2" message
            return 'Day 2' in str(data.get('error', '')) or 'URL import coming' in str(data.get('errors', []))
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        print("\n⚠️ Testing Error Handling...")
        
        # Test empty text
        try:
            request = ImportRequest(
                source_type='text',
                source_data='',
                user_id=1
            )
            result = self.importer.import_recipe(request)
            
            if not result.success and 'too short' in str(result.errors):
                print("✅ Empty text handled correctly")
            else:
                print("❌ Empty text not handled properly")
                return False
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
        
        # Test invalid source type
        try:
            request = ImportRequest(
                source_type='invalid',
                source_data='test',
                user_id=1
            )
            result = self.importer.import_recipe(request)
            
            if not result.success and 'Unsupported' in str(result.errors):
                print("✅ Invalid source type handled correctly")
            else:
                print("❌ Invalid source type not handled properly")
                return False
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 UNIVERSAL RECIPE IMPORT SYSTEM - DAY 1 TESTING")
        print("=" * 55)
        
        tests = [
            ('Backend Health Check', self.test_backend_health),
            ('Direct Import System', self.test_direct_import),
            ('API Text Import', self.test_api_text_import),
            ('API URL Import (Day 2 Preview)', self.test_api_url_import),
            ('Error Handling', self.test_error_handling),
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
        
        print(f"\n📊 TEST RESULTS:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Success Rate: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "   📈 No tests run")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Day 1 implementation is working correctly.")
        else:
            print(f"\n⚠️ {failed} test(s) failed. Check the output above for details.")
        
        return failed == 0

if __name__ == "__main__":
    print("Starting Recipe Import System Test...")
    
    tester = ImportSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Ready to proceed to Day 2 implementation!")
        sys.exit(0)
    else:
        print("\n❌ Please fix the issues above before proceeding.")
        sys.exit(1)
