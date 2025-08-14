"""
BonAppétit Visual Recipe Analyzer
Analyzes the visual structure of BonAppétit recipe pages to improve parsing accuracy
Similar to the PDF book visual analyzer but for web pages
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class BonAppetitVisualAnalyzer:
    """Visual analyzer for BonAppétit recipe pages"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        self.analysis_results = []
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def analyze_recipe_structure(self, recipe_url: str) -> Dict[str, Any]:
        """Analyze the visual structure of a BonAppétit recipe page"""
        if not self.driver:
            self.setup_driver()
            
        print(f"🔍 Analyzing recipe structure: {recipe_url}")
        
        try:
            # Navigate to recipe page
            self.driver.get(recipe_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).wait(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            
            # Wait a bit more for dynamic content
            time.sleep(3)
            
            # Take screenshot for visual reference
            screenshot_data = self.driver.get_screenshot_as_base64()
            
            # Analyze different sections
            analysis = {
                'url': recipe_url,
                'title': self._analyze_title_section(),
                'ingredients': self._analyze_ingredients_section(),
                'instructions': self._analyze_instructions_section(),
                'metadata': self._analyze_metadata_section(),
                'visual_structure': self._analyze_visual_structure(),
                'screenshot': screenshot_data,
                'timestamp': time.time()
            }
            
            self.analysis_results.append(analysis)
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing {recipe_url}: {e}")
            return {'error': str(e), 'url': recipe_url}
            
    def _analyze_title_section(self) -> Dict[str, Any]:
        """Analyze recipe title and header area"""
        title_data = {}
        
        # Find title element
        title_selectors = [
            'h1[data-testid="recipe-title"]',
            'h1.recipe-title',
            'h1',
            '.recipe-header h1',
            '[data-testid="recipe-header"] h1'
        ]
        
        for selector in title_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                title_data['selector'] = selector
                title_data['text'] = element.text
                title_data['location'] = element.location
                title_data['size'] = element.size
                title_data['tag_name'] = element.tag_name
                title_data['classes'] = element.get_attribute('class')
                title_data['data_testid'] = element.get_attribute('data-testid')
                break
            except:
                continue
                
        return title_data
        
    def _analyze_ingredients_section(self) -> Dict[str, Any]:
        """Analyze ingredients section structure"""
        ingredients_data = {
            'container': None,
            'items': [],
            'selectors_tried': []
        }
        
        # Try different container selectors
        container_selectors = [
            '[data-testid="IngredientList"]',
            '[data-testid="recipe-ingredients"]',
            '.recipe-ingredients',
            '.ingredients-section',
            '.ingredients',
            'section[aria-label*="Ingredients"]',
            '.recipe-body .ingredients'
        ]
        
        for selector in container_selectors:
            ingredients_data['selectors_tried'].append(selector)
            try:
                container = self.driver.find_element(By.CSS_SELECTOR, selector)
                ingredients_data['container'] = {
                    'selector': selector,
                    'location': container.location,
                    'size': container.size,
                    'classes': container.get_attribute('class'),
                    'data_testid': container.get_attribute('data-testid')
                }
                
                # Find ingredient items within container
                item_selectors = ['li', '.ingredient', '.ingredient-item', 'p']
                for item_selector in item_selectors:
                    try:
                        items = container.find_elements(By.CSS_SELECTOR, item_selector)
                        if items:
                            ingredients_data['items'] = []
                            for i, item in enumerate(items[:10]):  # Limit to first 10
                                item_data = {
                                    'index': i,
                                    'selector': f"{selector} {item_selector}",
                                    'text': item.text.strip(),
                                    'location': item.location,
                                    'size': item.size,
                                    'tag_name': item.tag_name,
                                    'classes': item.get_attribute('class')
                                }
                                ingredients_data['items'].append(item_data)
                            break
                    except:
                        continue
                break
            except:
                continue
                
        return ingredients_data
        
    def _analyze_instructions_section(self) -> Dict[str, Any]:
        """Analyze instructions/directions section structure"""
        instructions_data = {
            'container': None,
            'items': [],
            'selectors_tried': []
        }
        
        # Try different container selectors
        container_selectors = [
            '[data-testid="InstructionList"]',
            '[data-testid="recipe-instructions"]',
            '.recipe-instructions',
            '.instructions-section',
            '.instructions',
            '.directions',
            'section[aria-label*="Instructions"]',
            'section[aria-label*="Directions"]',
            '.recipe-body .instructions'
        ]
        
        for selector in container_selectors:
            instructions_data['selectors_tried'].append(selector)
            try:
                container = self.driver.find_element(By.CSS_SELECTOR, selector)
                instructions_data['container'] = {
                    'selector': selector,
                    'location': container.location,
                    'size': container.size,
                    'classes': container.get_attribute('class'),
                    'data_testid': container.get_attribute('data-testid')
                }
                
                # Find instruction items within container
                item_selectors = ['li', '.instruction', '.instruction-item', '.step', 'p', 'div']
                for item_selector in item_selectors:
                    try:
                        items = container.find_elements(By.CSS_SELECTOR, item_selector)
                        if items:
                            instructions_data['items'] = []
                            for i, item in enumerate(items[:10]):  # Limit to first 10
                                text = item.text.strip()
                                if text and len(text) > 10:  # Only count substantial text
                                    item_data = {
                                        'index': i,
                                        'selector': f"{selector} {item_selector}",
                                        'text': text[:100] + ('...' if len(text) > 100 else ''),
                                        'full_text_length': len(text),
                                        'location': item.location,
                                        'size': item.size,
                                        'tag_name': item.tag_name,
                                        'classes': item.get_attribute('class')
                                    }
                                    instructions_data['items'].append(item_data)
                            break
                    except:
                        continue
                break
            except:
                continue
                
        return instructions_data
        
    def _analyze_metadata_section(self) -> Dict[str, Any]:
        """Analyze recipe metadata (prep time, cook time, etc.)"""
        metadata_data = {
            'prep_time': None,
            'cook_time': None,
            'total_time': None,
            'servings': None,
            'yield': None,
            'difficulty': None,
            'selectors_found': []
        }
        
        # Common metadata selectors
        metadata_selectors = {
            'prep_time': [
                '[data-testid="prep-time"]',
                '.prep-time',
                '[aria-label*="prep"]',
                '.recipe-meta .prep'
            ],
            'cook_time': [
                '[data-testid="cook-time"]',
                '.cook-time',
                '[aria-label*="cook"]',
                '.recipe-meta .cook'
            ],
            'total_time': [
                '[data-testid="total-time"]',
                '.total-time',
                '[aria-label*="total"]',
                '.recipe-meta .total'
            ],
            'servings': [
                '[data-testid="servings"]',
                '.servings',
                '[aria-label*="serves"]',
                '.recipe-meta .servings'
            ],
            'yield': [
                '[data-testid="yield"]',
                '.yield',
                '[aria-label*="yield"]',
                '.recipe-meta .yield'
            ]
        }
        
        for meta_type, selectors in metadata_selectors.items():
            for selector in selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    metadata_data[meta_type] = {
                        'selector': selector,
                        'text': element.text.strip(),
                        'location': element.location,
                        'size': element.size,
                        'classes': element.get_attribute('class'),
                        'data_testid': element.get_attribute('data-testid')
                    }
                    metadata_data['selectors_found'].append(selector)
                    break
                except:
                    continue
                    
        return metadata_data
        
    def _analyze_visual_structure(self) -> Dict[str, Any]:
        """Analyze overall page structure and layout"""
        structure_data = {
            'page_layout': {},
            'main_content_area': None,
            'navigation': None,
            'json_ld_scripts': []
        }
        
        # Analyze main content area
        main_selectors = [
            'main',
            '.recipe-main',
            '.recipe-content',
            '.main-content',
            '[role="main"]',
            '.recipe-page'
        ]
        
        for selector in main_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                structure_data['main_content_area'] = {
                    'selector': selector,
                    'location': element.location,
                    'size': element.size,
                    'classes': element.get_attribute('class')
                }
                break
            except:
                continue
                
        # Find JSON-LD structured data
        try:
            scripts = self.driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
            for i, script in enumerate(scripts):
                try:
                    content = script.get_attribute('innerHTML')
                    if content and 'Recipe' in content:
                        structure_data['json_ld_scripts'].append({
                            'index': i,
                            'contains_recipe': True,
                            'content_preview': content[:200] + ('...' if len(content) > 200 else '')
                        })
                except:
                    continue
        except:
            pass
            
        # Analyze page dimensions
        structure_data['page_layout'] = {
            'window_size': self.driver.get_window_size(),
            'page_height': self.driver.execute_script("return document.body.scrollHeight"),
            'viewport_height': self.driver.execute_script("return window.innerHeight")
        }
        
        return structure_data
        
    def analyze_multiple_recipes(self, recipe_urls: List[str], save_results: bool = True) -> List[Dict[str, Any]]:
        """Analyze multiple BonAppétit recipes to find patterns"""
        print(f"🔍 Analyzing {len(recipe_urls)} BonAppétit recipes for visual patterns...")
        
        all_results = []
        
        for i, url in enumerate(recipe_urls, 1):
            print(f"📄 Analyzing recipe {i}/{len(recipe_urls)}: {url.split('/')[-1]}")
            result = self.analyze_recipe_structure(url)
            all_results.append(result)
            
            # Small delay between requests
            time.sleep(2)
            
        if save_results:
            self.save_analysis_results(all_results)
            
        # Generate pattern analysis
        patterns = self._analyze_patterns(all_results)
        
        print(f"✅ Visual analysis complete! Found patterns across {len(all_results)} recipes")
        return all_results, patterns
        
    def _analyze_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns across multiple recipe analyses"""
        patterns = {
            'most_reliable_selectors': {
                'title': {},
                'ingredients': {},
                'instructions': {},
                'metadata': {}
            },
            'consistency_scores': {},
            'recommendations': []
        }
        
        # Count successful selectors
        successful_selectors = {
            'title': {},
            'ingredients_container': {},
            'ingredients_items': {},
            'instructions_container': {},
            'instructions_items': {}
        }
        
        valid_results = [r for r in results if 'error' not in r]
        
        if not valid_results:
            return patterns
            
        # Analyze title selectors
        for result in valid_results:
            if result['title'].get('selector'):
                selector = result['title']['selector']
                successful_selectors['title'][selector] = successful_selectors['title'].get(selector, 0) + 1
                
        # Analyze ingredients selectors
        for result in valid_results:
            ingredients = result['ingredients']
            if ingredients.get('container', {}).get('selector'):
                selector = ingredients['container']['selector']
                successful_selectors['ingredients_container'][selector] = successful_selectors['ingredients_container'].get(selector, 0) + 1
                
            if ingredients.get('items') and len(ingredients['items']) > 0:
                # Extract base selector from first item
                first_item_selector = ingredients['items'][0].get('selector', '')
                if ' ' in first_item_selector:
                    base_selector = first_item_selector.split(' ')[0]
                    item_selector = ' '.join(first_item_selector.split(' ')[1:])
                    full_selector = f"{base_selector} {item_selector}"
                    successful_selectors['ingredients_items'][full_selector] = successful_selectors['ingredients_items'].get(full_selector, 0) + 1
                    
        # Analyze instructions selectors
        for result in valid_results:
            instructions = result['instructions']
            if instructions.get('container', {}).get('selector'):
                selector = instructions['container']['selector']
                successful_selectors['instructions_container'][selector] = successful_selectors['instructions_container'].get(selector, 0) + 1
                
            if instructions.get('items') and len(instructions['items']) > 0:
                # Extract base selector from first item
                first_item_selector = instructions['items'][0].get('selector', '')
                if ' ' in first_item_selector:
                    base_selector = first_item_selector.split(' ')[0]
                    item_selector = ' '.join(first_item_selector.split(' ')[1:])
                    full_selector = f"{base_selector} {item_selector}"
                    successful_selectors['instructions_items'][full_selector] = successful_selectors['instructions_items'].get(full_selector, 0) + 1
        
        # Find most reliable selectors (those that work on most pages)
        total_recipes = len(valid_results)
        
        for selector_type, selectors in successful_selectors.items():
            if selectors:
                best_selector = max(selectors.items(), key=lambda x: x[1])
                success_rate = best_selector[1] / total_recipes
                patterns['most_reliable_selectors'][selector_type.replace('_container', '').replace('_items', '')] = {
                    'selector': best_selector[0],
                    'success_count': best_selector[1],
                    'success_rate': success_rate,
                    'confidence': 'high' if success_rate >= 0.8 else 'medium' if success_rate >= 0.6 else 'low'
                }
                
        # Generate recommendations
        recommendations = []
        
        # Check for data-testid patterns
        testid_count = sum(1 for r in valid_results 
                          if r['ingredients'].get('container', {}).get('data_testid') 
                          or r['instructions'].get('container', {}).get('data_testid'))
        
        if testid_count / total_recipes >= 0.7:
            recommendations.append("✅ BonAppétit uses consistent data-testid attributes - prioritize these selectors")
            
        # Check for JSON-LD availability
        jsonld_count = sum(1 for r in valid_results 
                          if r['visual_structure'].get('json_ld_scripts'))
        
        if jsonld_count / total_recipes >= 0.8:
            recommendations.append("✅ JSON-LD structured data is widely available - use as primary extraction method")
            
        patterns['recommendations'] = recommendations
        patterns['analysis_summary'] = {
            'total_recipes_analyzed': total_recipes,
            'successful_analyses': len(valid_results),
            'json_ld_availability': jsonld_count / total_recipes if total_recipes > 0 else 0
        }
        
        return patterns
        
    def save_analysis_results(self, results: List[Dict[str, Any]], filename: str = None):
        """Save analysis results to JSON file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"bonappetit_visual_analysis_{timestamp}.json"
            
        # Remove screenshot data for JSON saving (too large)
        clean_results = []
        for result in results:
            clean_result = result.copy()
            if 'screenshot' in clean_result:
                clean_result['has_screenshot'] = True
                del clean_result['screenshot']
            clean_results.append(clean_result)
            
        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Analysis results saved to: {output_path}")
        
    def save_screenshots(self, results: List[Dict[str, Any]], folder: str = "bonappetit_screenshots"):
        """Save screenshots from analysis results"""
        screenshot_folder = Path(folder)
        screenshot_folder.mkdir(exist_ok=True)
        
        for i, result in enumerate(results):
            if 'screenshot' in result and result['screenshot']:
                url = result.get('url', f'recipe_{i}')
                filename = url.split('/')[-1] or f'recipe_{i}'
                screenshot_path = screenshot_folder / f"{filename}.png"
                
                # Decode base64 screenshot
                screenshot_data = base64.b64decode(result['screenshot'])
                with open(screenshot_path, 'wb') as f:
                    f.write(screenshot_data)
                    
        print(f"📸 Screenshots saved to: {screenshot_folder}")
        
    def generate_optimized_selectors(self, patterns: Dict[str, Any]) -> Dict[str, str]:
        """Generate optimized selectors based on pattern analysis"""
        optimized = {}
        
        for section, data in patterns['most_reliable_selectors'].items():
            if data and data.get('confidence') in ['high', 'medium']:
                optimized[section] = data['selector']
                
        return optimized
        
    def cleanup(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()

def test_bonappetit_visual_analysis():
    """Test the visual analyzer with some sample BonAppétit recipes"""
    
    # Sample BonAppétit recipe URLs for testing
    test_urls = [
        "https://www.bonappetit.com/recipe/simple-tomato-salad",
        "https://www.bonappetit.com/recipe/weeknight-chicken-and-rice",
        "https://www.bonappetit.com/recipe/brown-butter-chocolate-chip-cookies",
        "https://www.bonappetit.com/recipe/classic-caesar-salad",
        "https://www.bonappetit.com/recipe/perfect-roast-chicken"
    ]
    
    analyzer = BonAppetitVisualAnalyzer(headless=False)  # Set to True for headless mode
    
    try:
        results, patterns = analyzer.analyze_multiple_recipes(test_urls[:2])  # Test with first 2 recipes
        
        # Print pattern analysis
        print("\n🎯 PATTERN ANALYSIS RESULTS:")
        print("=" * 50)
        
        for section, data in patterns['most_reliable_selectors'].items():
            if data:
                print(f"\n📍 {section.upper()}:")
                print(f"   Best Selector: {data['selector']}")
                print(f"   Success Rate: {data['success_rate']:.1%}")
                print(f"   Confidence: {data['confidence']}")
                
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in patterns['recommendations']:
            print(f"   {rec}")
            
        # Generate optimized selectors
        optimized = analyzer.generate_optimized_selectors(patterns)
        print(f"\n🎯 OPTIMIZED SELECTORS FOR CHROME EXTENSION:")
        for section, selector in optimized.items():
            print(f"   {section}: '{selector}'")
            
    finally:
        analyzer.cleanup()

if __name__ == "__main__":
    test_bonappetit_visual_analysis()
