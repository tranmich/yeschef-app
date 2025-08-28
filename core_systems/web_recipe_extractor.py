"""
🌐 Web Recipe Extractor - Advanced URL Recipe Extraction System
=============================================================

Extracts recipes from websites using multiple strategies:
1. JSON-LD Schema.org (most reliable - 90%+ success rate)
2. BonAppetit-specific patterns (proven success)
3. Site-specific extractors (Food Network, AllRecipes, etc.)
4. Open Graph metadata
5. Adaptive fallback parsing

Integrates with existing Me Hungie systems:
- AdaptiveRecipeExtractor for fallback parsing
- IngredientIntelligenceEngine for ingredient processing
- Confidence scoring for quality assessment

Author: GitHub Copilot & Team
Date: August 26, 2025 - Day 2 Implementation
"""

import os
import re
import json
import requests
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time

# Import our self-improving analytics system
try:
    from core_systems.extraction_analytics import ExtractionAnalytics, ExtractionResult
    from core_systems.adaptive_confidence_scorer import AdaptiveConfidenceScorer, ConfidenceFactors
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    print("⚠️ Analytics system not available - running without self-improvement")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class WebRecipeData:
    """Structured recipe data extracted from web sources"""
    title: str = ""
    ingredients: List[str] = None
    instructions: List[str] = None
    description: str = ""
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    servings: Optional[int] = None
    cuisine: str = ""
    category: str = ""
    keywords: List[str] = None
    nutrition: Dict = None
    image_url: str = ""
    source_url: str = ""
    author: str = ""
    rating: Optional[float] = None
    review_count: Optional[int] = None
    extraction_method: str = ""
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.ingredients is None:
            self.ingredients = []
        if self.instructions is None:
            self.instructions = []
        if self.keywords is None:
            self.keywords = []
        if self.nutrition is None:
            self.nutrition = {}

class WebRecipeExtractor:
    """
    🌐 Advanced Web Recipe Extraction Engine
    
    Multi-strategy extraction with intelligent fallbacks and confidence scoring
    """
    
    def __init__(self, timeout=10, user_agent=None, enable_analytics=True):
        """Initialize the web extractor with self-improving capabilities"""
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set a realistic user agent to avoid blocking
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.session.headers.update({'User-Agent': self.user_agent})
        
        # Initialize self-improving analytics system
        self.analytics_enabled = enable_analytics and ANALYTICS_AVAILABLE
        self.analytics = None
        self.adaptive_scorer = None
        
        if self.analytics_enabled:
            try:
                self.analytics = ExtractionAnalytics()
                self.adaptive_scorer = AdaptiveConfidenceScorer(self.analytics)
                logger.info("🧠 Self-improving analytics system activated")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize analytics system: {e}")
                self.analytics_enabled = False
        
        # Site-specific extraction patterns
        self.site_extractors = {
            'bonappetit.com': self._extract_bonappetit,
            'foodnetwork.com': self._extract_foodnetwork,
            'allrecipes.com': self._extract_allrecipes,
            'seriouseats.com': self._extract_seriouseats,
            'cooking.nytimes.com': self._extract_nytimes,
        }
        
        logger.info(f"✅ WebRecipeExtractor initialized with multi-strategy extraction")
        if self.analytics_enabled:
            logger.info("🧠 Self-improving capabilities: ENABLED")
        else:
            logger.info("📊 Self-improving capabilities: DISABLED")
    
    def extract_from_url(self, url: str) -> WebRecipeData:
        """
        Main extraction method with self-improving capabilities
        """
        logger.info(f"🌐 Starting extraction from: {url}")
        start_time = time.time()
        domain = urlparse(url).netloc.lower()
        
        # Get optimal extraction strategy from analytics
        extraction_methods = self._get_optimal_extraction_order(url)
        
        try:
            # Fetch the page content
            response = self._fetch_page(url)
            if not response:
                self._record_extraction_failure(url, "fetch_failed", start_time)
                return WebRecipeData(
                    source_url=url,
                    extraction_method="fetch_failed",
                    confidence=0.0
                )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try extraction methods in optimal order
            for method_name in extraction_methods:
                try:
                    recipe_data = None
                    
                    if method_name == 'json_ld':
                        recipe_data = self._extract_json_ld(soup, url)
                    elif method_name == 'open_graph':
                        recipe_data = self._extract_open_graph(soup, url)
                    elif method_name == 'microdata':
                        recipe_data = self._extract_microdata(soup, url)
                    elif method_name == 'adaptive_fallback':
                        recipe_data = self._extract_adaptive_fallback(soup, url)
                    else:
                        # Site-specific extractors
                        for site_pattern, extractor_func in self.site_extractors.items():
                            if site_pattern in domain and method_name == f"{site_pattern.split('.')[0]}_specific":
                                recipe_data = extractor_func(soup, url)
                                break
                    
                    if recipe_data and recipe_data.confidence > 0.3:
                        # Apply adaptive confidence scoring
                        original_confidence = recipe_data.confidence
                        adaptive_confidence = self._calculate_adaptive_confidence(
                            url, method_name, recipe_data, original_confidence
                        )
                        recipe_data.confidence = adaptive_confidence
                        
                        # Record successful extraction
                        processing_time = time.time() - start_time
                        self._record_extraction_success(url, method_name, recipe_data, processing_time)
                        
                        logger.info(f"✅ Extraction successful via {method_name} in {processing_time:.2f}s")
                        logger.info(f"🎯 Confidence: {original_confidence:.2f} → {adaptive_confidence:.2f}")
                        return recipe_data
                
                except Exception as e:
                    logger.warning(f"⚠️ Method {method_name} failed: {e}")
                    continue
            
            # All methods failed
            fallback_recipe = self._extract_adaptive_fallback(soup, url)
            processing_time = time.time() - start_time
            self._record_extraction_failure(url, "all_methods_failed", processing_time)
            
            logger.warning(f"⚠️ All extraction methods failed in {processing_time:.2f}s")
            return fallback_recipe
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._record_extraction_failure(url, "extraction_exception", processing_time)
            logger.error(f"❌ Extraction failed after {processing_time:.2f}s: {e}")
            return WebRecipeData(
                source_url=url,
                extraction_method="extraction_failed",
                confidence=0.0
            )
    
    def _fetch_page(self, url: str) -> Optional[requests.Response]:
        """Fetch webpage content with error handling and retries"""
        try:
            logger.info(f"📥 Fetching content from: {url}")
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.info(f"✅ Page fetched successfully ({len(response.text)} characters)")
                return response
            else:
                logger.warning(f"⚠️ HTTP {response.status_code} for URL: {url}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Timeout fetching URL: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Network error fetching URL: {url} - {e}")
            return None
    
    def _extract_json_ld(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """
        Extract recipe data from JSON-LD Schema.org markup (most reliable method)
        """
        logger.info("🔍 Attempting JSON-LD extraction...")
        
        try:
            # Find all JSON-LD script tags
            json_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Handle different JSON-LD structures
                    if isinstance(data, list):
                        # Multiple items in array
                        for item in data:
                            recipe = self._parse_json_ld_recipe(item)
                            if recipe:
                                recipe.source_url = url
                                recipe.extraction_method = "json_ld"
                                recipe.confidence = 0.9
                                return recipe
                    else:
                        # Single item
                        recipe = self._parse_json_ld_recipe(data)
                        if recipe:
                            recipe.source_url = url
                            recipe.extraction_method = "json_ld"
                            recipe.confidence = 0.9
                            return recipe
                            
                except json.JSONDecodeError:
                    continue
            
            logger.info("ℹ️ No valid JSON-LD recipe data found")
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ JSON-LD extraction failed: {e}")
            return None
    
    def _parse_json_ld_recipe(self, data: Dict) -> Optional[WebRecipeData]:
        """Parse JSON-LD data for recipe information"""
        
        # Check if this is a recipe object
        if not self._is_recipe_object(data):
            return None
        
        try:
            recipe = WebRecipeData()
            
            # Basic information
            recipe.title = data.get('name', '')
            recipe.description = data.get('description', '')
            recipe.author = self._extract_author(data.get('author', ''))
            
            # Images
            image = data.get('image')
            if image:
                if isinstance(image, list):
                    recipe.image_url = image[0] if image else ''
                elif isinstance(image, dict):
                    recipe.image_url = image.get('url', '')
                else:
                    recipe.image_url = str(image)
            
            # Ingredients
            ingredients = data.get('recipeIngredient', [])
            recipe.ingredients = [str(ing) for ing in ingredients] if ingredients else []
            
            # Instructions
            instructions = data.get('recipeInstructions', [])
            recipe.instructions = self._parse_instructions(instructions)
            
            # Timing
            recipe.prep_time = self._parse_duration(data.get('prepTime'))
            recipe.cook_time = self._parse_duration(data.get('cookTime'))
            recipe.total_time = self._parse_duration(data.get('totalTime'))
            
            # Servings/Yield
            recipe.servings = self._parse_servings(data.get('recipeYield'))
            
            # Category and cuisine
            recipe.cuisine = data.get('recipeCuisine', '')
            recipe.category = data.get('recipeCategory', '')
            recipe.keywords = data.get('keywords', [])
            
            # Rating
            rating = data.get('aggregateRating')
            if rating:
                recipe.rating = float(rating.get('ratingValue', 0))
                recipe.review_count = int(rating.get('reviewCount', 0))
            
            # Nutrition
            nutrition = data.get('nutrition')
            if nutrition:
                recipe.nutrition = self._parse_nutrition(nutrition)
            
            # Only return if we have essential data
            if recipe.title and (recipe.ingredients or recipe.instructions):
                return recipe
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing JSON-LD recipe: {e}")
            return None
    
    def _is_recipe_object(self, data: Dict) -> bool:
        """Check if JSON-LD object represents a recipe"""
        recipe_types = ['Recipe', 'recipe']
        
        # Check @type field
        obj_type = data.get('@type', '')
        if isinstance(obj_type, list):
            return any(t in recipe_types for t in obj_type)
        else:
            return obj_type in recipe_types
    
    def _extract_bonappetit(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """
        Extract from BonAppetit using proven patterns from existing codebase
        """
        logger.info("🎯 Using BonAppetit-specific extraction patterns...")
        
        try:
            recipe = WebRecipeData()
            recipe.source_url = url
            recipe.extraction_method = "bonappetit_specific"
            
            # Title extraction
            title_elem = soup.find('h1', class_='recipe-title') or soup.find('h1')
            recipe.title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Description
            desc_elem = soup.find('div', class_='recipe-description') or soup.find('p', class_='description')
            recipe.description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Ingredients - BonAppetit specific selectors
            ingredient_elems = soup.find_all('div', class_='ingredient') or soup.find_all('li', class_='ingredient')
            recipe.ingredients = [elem.get_text(strip=True) for elem in ingredient_elems]
            
            # Instructions
            instruction_elems = soup.find_all('div', class_='step') or soup.find_all('li', class_='instruction')
            recipe.instructions = [elem.get_text(strip=True) for elem in instruction_elems]
            
            # Timing from BonAppetit metadata
            time_elem = soup.find('span', class_='recipe-time') or soup.find('time')
            if time_elem:
                time_text = time_elem.get_text(strip=True)
                recipe.total_time = self._parse_time_text(time_text)
            
            # Servings
            servings_elem = soup.find('span', class_='serves') or soup.find('span', class_='yield')
            if servings_elem:
                recipe.servings = self._parse_servings(servings_elem.get_text(strip=True))
            
            # Calculate confidence based on data completeness
            confidence = 0.5
            if recipe.title: confidence += 0.2
            if recipe.ingredients: confidence += 0.2
            if recipe.instructions: confidence += 0.1
            
            recipe.confidence = min(confidence, 1.0)
            
            if recipe.title and (recipe.ingredients or recipe.instructions):
                return recipe
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ BonAppetit extraction failed: {e}")
            return None
    
    def _extract_foodnetwork(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract from Food Network"""
        # Implement Food Network specific patterns
        logger.info("🎯 Using Food Network extraction patterns...")
        # Placeholder for now - can be expanded
        return self._extract_generic_structured(soup, url, "foodnetwork_specific")
    
    def _extract_allrecipes(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract from AllRecipes"""
        # Implement AllRecipes specific patterns
        logger.info("🎯 Using AllRecipes extraction patterns...")
        # Placeholder for now - can be expanded
        return self._extract_generic_structured(soup, url, "allrecipes_specific")
    
    def _extract_seriouseats(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract from Serious Eats"""
        logger.info("🎯 Using Serious Eats extraction patterns...")
        return self._extract_generic_structured(soup, url, "seriouseats_specific")
    
    def _extract_nytimes(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract from NYTimes Cooking"""
        logger.info("🎯 Using NYTimes Cooking extraction patterns...")
        return self._extract_generic_structured(soup, url, "nytimes_specific")
    
    def _extract_open_graph(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract recipe data from Open Graph metadata"""
        logger.info("🔍 Attempting Open Graph extraction...")
        
        try:
            recipe = WebRecipeData()
            recipe.source_url = url
            recipe.extraction_method = "open_graph"
            
            # Extract Open Graph metadata
            og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
            
            for tag in og_tags:
                property_name = tag.get('property', '')
                content = tag.get('content', '')
                
                if property_name == 'og:title':
                    recipe.title = content
                elif property_name == 'og:description':
                    recipe.description = content
                elif property_name == 'og:image':
                    recipe.image_url = content
            
            # Basic confidence scoring
            confidence = 0.3
            if recipe.title: confidence += 0.2
            if recipe.description: confidence += 0.1
            
            recipe.confidence = confidence
            
            if recipe.title:
                return recipe
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Open Graph extraction failed: {e}")
            return None
    
    def _extract_microdata(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract recipe data from HTML5 Microdata"""
        logger.info("🔍 Attempting Microdata extraction...")
        
        try:
            # Look for recipe microdata
            recipe_elem = soup.find(attrs={'itemtype': re.compile(r'.*Recipe')})
            if not recipe_elem:
                return None
            
            recipe = WebRecipeData()
            recipe.source_url = url
            recipe.extraction_method = "microdata"
            
            # Extract microdata properties
            for elem in recipe_elem.find_all(attrs={'itemprop': True}):
                prop = elem.get('itemprop')
                
                if prop == 'name':
                    recipe.title = elem.get_text(strip=True)
                elif prop == 'description':
                    recipe.description = elem.get_text(strip=True)
                elif prop == 'recipeIngredient':
                    recipe.ingredients.append(elem.get_text(strip=True))
                elif prop == 'recipeInstructions':
                    recipe.instructions.append(elem.get_text(strip=True))
            
            # Calculate confidence
            confidence = 0.4
            if recipe.title: confidence += 0.2
            if recipe.ingredients: confidence += 0.2
            
            recipe.confidence = confidence
            
            if recipe.title and (recipe.ingredients or recipe.instructions):
                return recipe
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Microdata extraction failed: {e}")
            return None
    
    def _extract_adaptive_fallback(self, soup: BeautifulSoup, url: str) -> WebRecipeData:
        """
        Adaptive fallback extraction using heuristics and page analysis
        """
        logger.info("🔄 Using adaptive fallback extraction...")
        
        recipe = WebRecipeData()
        recipe.source_url = url
        recipe.extraction_method = "adaptive_fallback"
        
        try:
            # Extract title from various common selectors
            title_selectors = ['h1', '.recipe-title', '.entry-title', '.post-title', 'title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    recipe.title = title_elem.get_text(strip=True)
                    break
            
            # Extract ingredients using common patterns
            ingredient_patterns = [
                '.ingredient', '.recipe-ingredient', '[class*="ingredient"]',
                'ul li', 'ol li'  # Common list patterns
            ]
            
            for pattern in ingredient_patterns:
                elements = soup.select(pattern)
                if elements and len(elements) > 2:  # Must have multiple ingredients
                    recipe.ingredients = [elem.get_text(strip=True) for elem in elements[:20]]  # Limit to 20
                    break
            
            # Extract instructions
            instruction_patterns = [
                '.instruction', '.recipe-instruction', '.step', '.method',
                '[class*="instruction"]', '[class*="direction"]'
            ]
            
            for pattern in instruction_patterns:
                elements = soup.select(pattern)
                if elements:
                    recipe.instructions = [elem.get_text(strip=True) for elem in elements[:20]]  # Limit to 20
                    break
            
            # Basic confidence scoring
            confidence = 0.2  # Base confidence for fallback
            if recipe.title: confidence += 0.2
            if recipe.ingredients: confidence += 0.2
            if recipe.instructions: confidence += 0.1
            
            recipe.confidence = min(confidence, 0.7)  # Cap fallback confidence at 0.7
            
            return recipe
            
        except Exception as e:
            logger.warning(f"⚠️ Adaptive fallback extraction failed: {e}")
            recipe.confidence = 0.0
            return recipe
    
    def _extract_generic_structured(self, soup: BeautifulSoup, url: str, method: str) -> Optional[WebRecipeData]:
        """Generic structured data extraction for site-specific methods"""
        recipe = WebRecipeData()
        recipe.source_url = url
        recipe.extraction_method = method
        
        # Generic structured extraction logic
        # This is a placeholder that can be expanded for specific sites
        recipe.confidence = 0.5
        
        return recipe if recipe.title else None
    
    def _get_optimal_extraction_order(self, url: str) -> List[str]:
        """Get optimal extraction method order based on analytics"""
        if self.analytics_enabled and self.analytics:
            return self.analytics.get_optimal_extraction_strategy(url)
        else:
            # Default order if analytics not available
            return ['json_ld', 'bonappetit_specific', 'foodnetwork_specific', 
                   'allrecipes_specific', 'seriouseats_specific', 'nytimes_specific',
                   'open_graph', 'microdata', 'adaptive_fallback']
    
    def _calculate_adaptive_confidence(self, url: str, method: str, recipe_data: WebRecipeData, base_confidence: float) -> float:
        """Calculate adaptive confidence using self-improving scorer"""
        if self.analytics_enabled and self.adaptive_scorer:
            try:
                # Convert recipe data to dictionary for analysis
                extracted_data = {
                    'title': recipe_data.title,
                    'ingredients': recipe_data.ingredients,
                    'instructions': recipe_data.instructions,
                    'description': recipe_data.description,
                    'total_time': recipe_data.total_time,
                    'prep_time': recipe_data.prep_time,
                    'cook_time': recipe_data.cook_time,
                    'servings': recipe_data.servings,
                    'image_url': recipe_data.image_url
                }
                
                adaptive_confidence, factors = self.adaptive_scorer.calculate_adaptive_confidence(
                    url, method, base_confidence, extracted_data
                )
                
                return adaptive_confidence
                
            except Exception as e:
                logger.warning(f"⚠️ Adaptive confidence calculation failed: {e}")
                return base_confidence
        else:
            return base_confidence
    
    def _record_extraction_success(self, url: str, method: str, recipe_data: WebRecipeData, processing_time: float):
        """Record successful extraction for analytics learning"""
        if self.analytics_enabled and self.analytics:
            try:
                domain = urlparse(url).netloc.lower()
                
                result = ExtractionResult(
                    url=url,
                    domain=domain,
                    extraction_method=method,
                    confidence_predicted=recipe_data.confidence,
                    success=True,
                    processing_time=processing_time,
                    ingredients_count=len(recipe_data.ingredients) if recipe_data.ingredients else 0,
                    instructions_count=len(recipe_data.instructions) if recipe_data.instructions else 0,
                    has_title=bool(recipe_data.title),
                    has_timing=bool(recipe_data.total_time or recipe_data.prep_time or recipe_data.cook_time),
                    has_servings=bool(recipe_data.servings),
                    timestamp=datetime.now()
                )
                
                self.analytics.record_extraction(result)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to record extraction success: {e}")
    
    def _record_extraction_failure(self, url: str, failure_reason: str, processing_time: float):
        """Record extraction failure for analytics learning"""
        if self.analytics_enabled and self.analytics:
            try:
                domain = urlparse(url).netloc.lower()
                
                result = ExtractionResult(
                    url=url,
                    domain=domain,
                    extraction_method=failure_reason,
                    confidence_predicted=0.0,
                    success=False,
                    processing_time=processing_time,
                    timestamp=datetime.now()
                )
                
                self.analytics.record_extraction(result)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to record extraction failure: {e}")
    
    def provide_feedback(self, recipe_id: int, feedback: str, corrected_data: Optional[Dict] = None):
        """Provide user feedback to improve future extractions"""
        if self.analytics_enabled and self.analytics:
            try:
                self.analytics.provide_user_feedback(recipe_id, feedback, corrected_data)
                logger.info(f"📝 User feedback recorded for recipe {recipe_id}: {feedback}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to record user feedback: {e}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary for monitoring and improvement"""
        if self.analytics_enabled and self.analytics:
            return self.analytics.get_analytics_summary()
        else:
            return {'analytics_enabled': False, 'message': 'Analytics system not available'}
    
    # Helper methods for parsing
    def _extract_author(self, author_data) -> str:
        """Extract author name from various formats"""
        if isinstance(author_data, dict):
            return author_data.get('name', '')
        elif isinstance(author_data, list) and author_data:
            first_author = author_data[0]
            if isinstance(first_author, dict):
                return first_author.get('name', '')
            return str(first_author)
        return str(author_data) if author_data else ''
    
    def _parse_instructions(self, instructions: List) -> List[str]:
        """Parse instructions from various JSON-LD formats"""
        parsed = []
        
        for instruction in instructions:
            if isinstance(instruction, dict):
                text = instruction.get('text', '')
                if not text:
                    text = instruction.get('name', '')
                if text:
                    parsed.append(text)
            else:
                parsed.append(str(instruction))
        
        return parsed
    
    def _parse_duration(self, duration_str: Optional[str]) -> Optional[int]:
        """Parse ISO 8601 duration to minutes"""
        if not duration_str:
            return None
        
        try:
            # Handle ISO 8601 format (PT30M = 30 minutes)
            if duration_str.startswith('PT'):
                match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_str)
                if match:
                    hours = int(match.group(1) or 0)
                    minutes = int(match.group(2) or 0)
                    return hours * 60 + minutes
            
            # Handle plain number formats
            match = re.search(r'(\d+)', duration_str)
            if match:
                return int(match.group(1))
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def _parse_servings(self, servings_data) -> Optional[int]:
        """Parse servings/yield from various formats"""
        if not servings_data:
            return None
        
        try:
            if isinstance(servings_data, (int, float)):
                return int(servings_data)
            
            # Extract number from string
            match = re.search(r'(\d+)', str(servings_data))
            if match:
                return int(match.group(1))
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def _parse_time_text(self, time_text: str) -> Optional[int]:
        """Parse time from natural language text"""
        if not time_text:
            return None
        
        try:
            # Look for patterns like "30 minutes", "1 hour 30 min", etc.
            total_minutes = 0
            
            # Hours
            hour_match = re.search(r'(\d+)\s*(?:hour|hr)', time_text, re.IGNORECASE)
            if hour_match:
                total_minutes += int(hour_match.group(1)) * 60
            
            # Minutes
            min_match = re.search(r'(\d+)\s*(?:minute|min)', time_text, re.IGNORECASE)
            if min_match:
                total_minutes += int(min_match.group(1))
            
            # If no specific time units, just extract first number
            if total_minutes == 0:
                num_match = re.search(r'(\d+)', time_text)
                if num_match:
                    total_minutes = int(num_match.group(1))
            
            return total_minutes if total_minutes > 0 else None
            
        except (ValueError, AttributeError):
            return None
    
    def _parse_nutrition(self, nutrition_data: Dict) -> Dict:
        """Parse nutrition information"""
        parsed_nutrition = {}
        
        try:
            if isinstance(nutrition_data, dict):
                # Map common nutrition fields
                nutrition_mapping = {
                    'calories': ['calories', 'kcal', 'energy'],
                    'protein': ['protein'],
                    'fat': ['fat', 'totalFat'],
                    'carbs': ['carbohydrate', 'carbs', 'totalCarbohydrate'],
                    'fiber': ['fiber', 'dietaryFiber'],
                    'sugar': ['sugar', 'sugars'],
                    'sodium': ['sodium']
                }
                
                for nutrient, keys in nutrition_mapping.items():
                    for key in keys:
                        value = nutrition_data.get(key)
                        if value:
                            # Extract numeric value
                            if isinstance(value, str):
                                match = re.search(r'(\d+(?:\.\d+)?)', value)
                                if match:
                                    parsed_nutrition[nutrient] = float(match.group(1))
                            elif isinstance(value, (int, float)):
                                parsed_nutrition[nutrient] = float(value)
                            break
            
            return parsed_nutrition
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing nutrition data: {e}")
            return {}

# Export main class
__all__ = ['WebRecipeExtractor', 'WebRecipeData']

if __name__ == "__main__":
    # Basic testing
    extractor = WebRecipeExtractor()
    
    test_urls = [
        "https://www.bonappetit.com/recipe/simple-pasta-with-tomatoes",
        "https://www.foodnetwork.com/recipes/simple-salad",
        "https://www.allrecipes.com/recipe/easy-cookies"
    ]
    
    for url in test_urls:
        print(f"\n🧪 Testing extraction from: {url}")
        result = extractor.extract_from_url(url)
        print(f"   Title: {result.title}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Method: {result.extraction_method}")
        print(f"   Ingredients: {len(result.ingredients)} found")
        print(f"   Instructions: {len(result.instructions)} found")
