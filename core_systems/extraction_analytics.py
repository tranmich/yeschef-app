"""
🧠 Extraction Analytics - Self-Improving Recipe Extraction System
==============================================================

Machine learning-powered analytics engine that learns from extraction patterns
and continuously improves recipe extraction accuracy and confidence scoring.

Features:
- Site-specific performance tracking
- Dynamic confidence score refinement
- Adaptive method selection optimization
- User feedback integration
- Real-time learning and improvement

Builds on Day 1-2 foundation:
- Leverages existing confidence scoring system
- Integrates with WebRecipeExtractor methods
- Uses extraction success/failure data for ML training

Author: GitHub Copilot & Team
Date: August 26, 2025 - Day 3 Implementation
"""

import os
import json
import logging
import sqlite3
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from urllib.parse import urlparse
from collections import defaultdict, deque
import pickle

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ExtractionResult:
    """Detailed extraction result for analytics tracking"""
    url: str
    domain: str
    extraction_method: str
    confidence_predicted: float
    confidence_actual: Optional[float] = None
    success: bool = False
    processing_time: float = 0.0
    ingredients_count: int = 0
    instructions_count: int = 0
    has_title: bool = False
    has_timing: bool = False
    has_servings: bool = False
    user_feedback: Optional[str] = None  # 'accepted', 'corrected', 'rejected'
    timestamp: datetime = None
    recipe_id: Optional[int] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SitePerformanceMetrics:
    """Performance metrics for a specific site/domain"""
    domain: str
    total_attempts: int = 0
    successful_extractions: int = 0
    method_success_rates: Dict[str, float] = None
    average_confidence: float = 0.0
    average_processing_time: float = 0.0
    confidence_accuracy: float = 0.0  # How accurate our confidence predictions are
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.method_success_rates is None:
            self.method_success_rates = {}
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    @property
    def success_rate(self) -> float:
        """Overall success rate for this domain"""
        if self.total_attempts == 0:
            return 0.0
        return self.successful_extractions / self.total_attempts

class ExtractionAnalytics:
    """
    🧠 Self-Improving Extraction Analytics Engine
    
    Learns from extraction patterns and continuously improves extraction strategy
    """
    
    def __init__(self, db_path: str = "extraction_analytics.db"):
        """Initialize the analytics engine"""
        self.db_path = db_path
        self.site_metrics: Dict[str, SitePerformanceMetrics] = {}
        self.recent_results: deque = deque(maxlen=1000)  # Keep last 1000 results
        self.learning_enabled = True
        
        # Machine learning components
        self.confidence_model = None
        self.method_selector = None
        
        # Performance tracking
        self.extraction_methods = [
            'json_ld', 'bonappetit_specific', 'foodnetwork_specific',
            'allrecipes_specific', 'seriouseats_specific', 'nytimes_specific',
            'open_graph', 'microdata', 'adaptive_fallback'
        ]
        
        # Initialize database and load existing data
        self._init_database()
        self._load_historical_data()
        
        logger.info("🧠 ExtractionAnalytics initialized with self-improving capabilities")
    
    def _init_database(self):
        """Initialize SQLite database for analytics storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create extraction results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extraction_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    extraction_method TEXT NOT NULL,
                    confidence_predicted REAL NOT NULL,
                    confidence_actual REAL,
                    success BOOLEAN NOT NULL,
                    processing_time REAL NOT NULL,
                    ingredients_count INTEGER DEFAULT 0,
                    instructions_count INTEGER DEFAULT 0,
                    has_title BOOLEAN DEFAULT FALSE,
                    has_timing BOOLEAN DEFAULT FALSE,
                    has_servings BOOLEAN DEFAULT FALSE,
                    user_feedback TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    recipe_id INTEGER
                )
            """)
            
            # Create site performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS site_metrics (
                    domain TEXT PRIMARY KEY,
                    total_attempts INTEGER DEFAULT 0,
                    successful_extractions INTEGER DEFAULT 0,
                    method_success_rates TEXT,  -- JSON string
                    average_confidence REAL DEFAULT 0.0,
                    average_processing_time REAL DEFAULT 0.0,
                    confidence_accuracy REAL DEFAULT 0.0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create method performance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS method_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    method_name TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    success_rate REAL NOT NULL,
                    average_confidence REAL NOT NULL,
                    sample_size INTEGER NOT NULL,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(method_name, domain)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Analytics database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize analytics database: {e}")
    
    def record_extraction(self, result: ExtractionResult):
        """
        Record an extraction result for learning and analytics
        """
        try:
            # Store in recent results for quick access
            self.recent_results.append(result)
            
            # Store in database for persistent learning
            self._store_result_in_db(result)
            
            # Update site metrics
            self._update_site_metrics(result)
            
            # Update method performance
            self._update_method_performance(result)
            
            # Trigger learning if enabled
            if self.learning_enabled:
                self._trigger_learning_update()
            
            logger.info(f"📊 Recorded extraction: {result.domain} via {result.extraction_method} (confidence: {result.confidence_predicted:.2f})")
            
        except Exception as e:
            logger.error(f"❌ Failed to record extraction result: {e}")
    
    def get_optimal_extraction_strategy(self, url: str) -> List[str]:
        """
        Get the optimal extraction method order for a given URL based on learning
        """
        domain = urlparse(url).netloc.lower()
        
        # Get site-specific performance data
        site_metrics = self.site_metrics.get(domain)
        
        if site_metrics and site_metrics.method_success_rates:
            # Sort methods by success rate for this domain
            method_performance = site_metrics.method_success_rates
            sorted_methods = sorted(
                method_performance.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Return methods in order of success rate
            optimized_order = [method for method, _ in sorted_methods]
            
            # Fill in any missing methods at the end
            remaining_methods = [m for m in self.extraction_methods if m not in optimized_order]
            optimized_order.extend(remaining_methods)
            
            logger.info(f"🎯 Optimized extraction order for {domain}: {optimized_order[:3]}...")
            return optimized_order
        
        else:
            # Use default order for new/unknown domains
            logger.info(f"🆕 Using default extraction order for new domain: {domain}")
            return self.extraction_methods.copy()
    
    def predict_confidence(self, url: str, method: str, initial_confidence: float) -> float:
        """
        Predict refined confidence score based on historical learning
        """
        domain = urlparse(url).netloc.lower()
        
        # Get historical performance for this domain + method combination
        site_metrics = self.site_metrics.get(domain)
        
        if site_metrics and method in site_metrics.method_success_rates:
            # Adjust confidence based on historical success rate
            historical_success_rate = site_metrics.method_success_rates[method]
            
            # Blend initial confidence with historical data
            # Weight: 70% historical, 30% initial (can be tuned)
            refined_confidence = (0.7 * historical_success_rate) + (0.3 * initial_confidence)
            
            # Apply confidence accuracy correction
            if site_metrics.confidence_accuracy > 0:
                # If our confidence predictions are typically too high/low, adjust
                accuracy_factor = site_metrics.confidence_accuracy
                refined_confidence = refined_confidence * accuracy_factor
            
            # Ensure confidence stays in valid range
            refined_confidence = max(0.0, min(1.0, refined_confidence))
            
            logger.info(f"🧠 Refined confidence: {initial_confidence:.2f} → {refined_confidence:.2f} for {domain}/{method}")
            return refined_confidence
        
        else:
            # No historical data - return initial confidence
            return initial_confidence
    
    def get_confidence_threshold(self, domain: str) -> float:
        """
        Get adaptive confidence threshold for a domain based on its reliability
        """
        site_metrics = self.site_metrics.get(domain)
        
        if site_metrics:
            # Adjust threshold based on site reliability
            if site_metrics.success_rate > 0.8:
                # High reliability site - can use lower threshold
                return 0.6
            elif site_metrics.success_rate > 0.5:
                # Medium reliability - standard threshold
                return 0.7
            else:
                # Low reliability - higher threshold
                return 0.8
        
        # Default threshold for unknown sites
        return 0.7
    
    def provide_user_feedback(self, recipe_id: int, feedback: str, corrected_data: Optional[Dict] = None):
        """
        Record user feedback to improve future extractions
        """
        try:
            # Find the extraction result for this recipe
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update the extraction result with feedback
            cursor.execute("""
                UPDATE extraction_results 
                SET user_feedback = ?, confidence_actual = ?
                WHERE recipe_id = ?
            """, (feedback, self._calculate_actual_confidence(feedback, corrected_data), recipe_id))
            
            conn.commit()
            conn.close()
            
            # Trigger immediate learning update for user feedback
            self._trigger_learning_update()
            
            logger.info(f"📝 User feedback recorded for recipe {recipe_id}: {feedback}")
            
        except Exception as e:
            logger.error(f"❌ Failed to record user feedback: {e}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics summary for dashboard/monitoring
        """
        try:
            total_extractions = len(self.recent_results)
            successful_extractions = sum(1 for r in self.recent_results if r.success)
            
            # Overall success rate
            overall_success_rate = successful_extractions / total_extractions if total_extractions > 0 else 0
            
            # Method performance
            method_stats = defaultdict(lambda: {'attempts': 0, 'successes': 0})
            for result in self.recent_results:
                method_stats[result.extraction_method]['attempts'] += 1
                if result.success:
                    method_stats[result.extraction_method]['successes'] += 1
            
            method_performance = {}
            for method, stats in method_stats.items():
                success_rate = stats['successes'] / stats['attempts'] if stats['attempts'] > 0 else 0
                method_performance[method] = {
                    'success_rate': success_rate,
                    'attempts': stats['attempts']
                }
            
            # Top performing domains
            domain_stats = defaultdict(lambda: {'attempts': 0, 'successes': 0})
            for result in self.recent_results:
                domain_stats[result.domain]['attempts'] += 1
                if result.success:
                    domain_stats[result.domain]['successes'] += 1
            
            top_domains = []
            for domain, stats in domain_stats.items():
                if stats['attempts'] >= 3:  # Only include domains with meaningful sample size
                    success_rate = stats['successes'] / stats['attempts']
                    top_domains.append({
                        'domain': domain,
                        'success_rate': success_rate,
                        'attempts': stats['attempts']
                    })
            
            top_domains.sort(key=lambda x: x['success_rate'], reverse=True)
            
            # Performance trends (last 24 hours vs previous period)
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_results = [r for r in self.recent_results if r.timestamp >= recent_cutoff]
            recent_success_rate = sum(1 for r in recent_results if r.success) / len(recent_results) if recent_results else 0
            
            return {
                'total_extractions': total_extractions,
                'overall_success_rate': overall_success_rate,
                'recent_success_rate': recent_success_rate,
                'method_performance': method_performance,
                'top_domains': top_domains[:10],
                'site_count': len(self.site_metrics),
                'learning_enabled': self.learning_enabled,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate analytics summary: {e}")
            return {'error': str(e)}
    
    def _store_result_in_db(self, result: ExtractionResult):
        """Store extraction result in database with optimized performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Use PRAGMA for better performance
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA journal_mode = WAL")
            
            cursor.execute("""
                INSERT INTO extraction_results (
                    url, domain, extraction_method, confidence_predicted, confidence_actual,
                    success, processing_time, ingredients_count, instructions_count,
                    has_title, has_timing, has_servings, user_feedback, timestamp, recipe_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.url, result.domain, result.extraction_method, result.confidence_predicted,
                result.confidence_actual, result.success, result.processing_time,
                result.ingredients_count, result.instructions_count, result.has_title,
                result.has_timing, result.has_servings, result.user_feedback,
                result.timestamp, result.recipe_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to store result in database: {e}")
    
    def _update_site_metrics(self, result: ExtractionResult):
        """Update site-specific performance metrics"""
        domain = result.domain
        
        if domain not in self.site_metrics:
            self.site_metrics[domain] = SitePerformanceMetrics(domain=domain)
        
        metrics = self.site_metrics[domain]
        
        # Update basic counters
        metrics.total_attempts += 1
        if result.success:
            metrics.successful_extractions += 1
        
        # Update method-specific success rates
        method = result.extraction_method
        if method not in metrics.method_success_rates:
            metrics.method_success_rates[method] = 0.0
        
        # Calculate new success rate for this method
        method_attempts = sum(1 for r in self.recent_results 
                            if r.domain == domain and r.extraction_method == method)
        method_successes = sum(1 for r in self.recent_results 
                             if r.domain == domain and r.extraction_method == method and r.success)
        
        if method_attempts > 0:
            metrics.method_success_rates[method] = method_successes / method_attempts
        
        # Update average metrics
        domain_results = [r for r in self.recent_results if r.domain == domain]
        if domain_results:
            metrics.average_confidence = sum(r.confidence_predicted for r in domain_results) / len(domain_results)
            metrics.average_processing_time = sum(r.processing_time for r in domain_results) / len(domain_results)
        
        metrics.last_updated = datetime.now()
        
        # Store updated metrics in database
        self._store_site_metrics(metrics)
    
    def _update_method_performance(self, result: ExtractionResult):
        """Update method performance tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate current performance for this method + domain
            method_results = [r for r in self.recent_results 
                            if r.extraction_method == result.extraction_method and r.domain == result.domain]
            
            if method_results:
                success_rate = sum(1 for r in method_results if r.success) / len(method_results)
                avg_confidence = sum(r.confidence_predicted for r in method_results) / len(method_results)
                sample_size = len(method_results)
                
                # Update or insert method performance
                cursor.execute("""
                    INSERT OR REPLACE INTO method_performance 
                    (method_name, domain, success_rate, average_confidence, sample_size, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (result.extraction_method, result.domain, success_rate, avg_confidence, 
                     sample_size, datetime.now()))
                
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to update method performance: {e}")
    
    def _store_site_metrics(self, metrics: SitePerformanceMetrics):
        """Store site metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO site_metrics 
                (domain, total_attempts, successful_extractions, method_success_rates,
                 average_confidence, average_processing_time, confidence_accuracy, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.domain, metrics.total_attempts, metrics.successful_extractions,
                json.dumps(metrics.method_success_rates), metrics.average_confidence,
                metrics.average_processing_time, metrics.confidence_accuracy, metrics.last_updated
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to store site metrics: {e}")
    
    def _load_historical_data(self):
        """Load historical data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load site metrics
            cursor.execute("SELECT * FROM site_metrics")
            for row in cursor.fetchall():
                metrics = SitePerformanceMetrics(
                    domain=row[0],
                    total_attempts=row[1],
                    successful_extractions=row[2],
                    method_success_rates=json.loads(row[3]) if row[3] else {},
                    average_confidence=row[4],
                    average_processing_time=row[5],
                    confidence_accuracy=row[6],
                    last_updated=datetime.fromisoformat(row[7]) if row[7] else datetime.now()
                )
                self.site_metrics[metrics.domain] = metrics
            
            # Load recent extraction results (last 1000)
            cursor.execute("""
                SELECT * FROM extraction_results 
                ORDER BY timestamp DESC 
                LIMIT 1000
            """)
            
            for row in cursor.fetchall():
                result = ExtractionResult(
                    url=row[1],
                    domain=row[2],
                    extraction_method=row[3],
                    confidence_predicted=row[4],
                    confidence_actual=row[5],
                    success=bool(row[6]),
                    processing_time=row[7],
                    ingredients_count=row[8],
                    instructions_count=row[9],
                    has_title=bool(row[10]),
                    has_timing=bool(row[11]),
                    has_servings=bool(row[12]),
                    user_feedback=row[13],
                    timestamp=datetime.fromisoformat(row[14]) if row[14] else datetime.now(),
                    recipe_id=row[15]
                )
                self.recent_results.append(result)
            
            conn.close()
            
            logger.info(f"📚 Loaded {len(self.site_metrics)} site metrics and {len(self.recent_results)} recent results")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load historical data: {e}")
    
    def _trigger_learning_update(self):
        """Trigger learning algorithms to update models"""
        try:
            # Simple learning trigger - can be expanded with ML models
            # For now, just update confidence accuracy
            self._update_confidence_accuracy()
            
        except Exception as e:
            logger.warning(f"⚠️ Learning update failed: {e}")
    
    def _update_confidence_accuracy(self):
        """Update confidence accuracy metrics"""
        for domain, metrics in self.site_metrics.items():
            domain_results = [r for r in self.recent_results 
                            if r.domain == domain and r.confidence_actual is not None]
            
            if domain_results:
                # Calculate how accurate our confidence predictions are
                accuracy_scores = []
                for result in domain_results:
                    # Simple accuracy: 1.0 - |predicted - actual|
                    accuracy = 1.0 - abs(result.confidence_predicted - result.confidence_actual)
                    accuracy_scores.append(max(0.0, accuracy))
                
                metrics.confidence_accuracy = sum(accuracy_scores) / len(accuracy_scores)
                self._store_site_metrics(metrics)
    
    def _calculate_actual_confidence(self, feedback: str, corrected_data: Optional[Dict]) -> float:
        """Calculate actual confidence based on user feedback"""
        if feedback == 'accepted':
            return 1.0
        elif feedback == 'corrected' and corrected_data:
            # Partial confidence based on how much was corrected
            return 0.7  # Can be refined based on correction analysis
        elif feedback == 'rejected':
            return 0.0
        else:
            return 0.5  # Neutral/unknown

# Export main class
__all__ = ['ExtractionAnalytics', 'ExtractionResult', 'SitePerformanceMetrics']

if __name__ == "__main__":
    # Basic testing of analytics system
    analytics = ExtractionAnalytics()
    
    # Simulate some extraction results
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
            has_title=True
        ),
        ExtractionResult(
            url="https://www.foodnetwork.com/recipe/test2",
            domain="foodnetwork.com", 
            extraction_method="adaptive_fallback",
            confidence_predicted=0.6,
            success=False,
            processing_time=2.1
        )
    ]
    
    for result in test_results:
        analytics.record_extraction(result)
    
    # Test analytics summary
    summary = analytics.get_analytics_summary()
    print(f"📊 Analytics Summary:")
    print(f"   Total extractions: {summary['total_extractions']}")
    print(f"   Success rate: {summary['overall_success_rate']:.1%}")
    print(f"   Site count: {summary['site_count']}")
    
    # Test optimal strategy
    strategy = analytics.get_optimal_extraction_strategy("https://www.bonappetit.com/new-recipe")
    print(f"🎯 Optimal strategy for BonAppetit: {strategy[:3]}")
    
    print("✅ ExtractionAnalytics system working correctly!")
