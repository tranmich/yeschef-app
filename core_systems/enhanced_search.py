"""
Enhanced Search System using Recipe Analysis
Integrates with the recipe analyzer to provide intelligent suggestions
"""
import sqlite3
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

class EnhancedSearchEngine:
    """Search engine that leverages recipe analysis for better results"""
    
    def __init__(self, db_path: str = "hungie.db"):
        self.db_path = Path(db_path)
        
    def smart_search_with_analysis(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Enhanced search using analysis data"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Extract keywords from query
        keywords = self._extract_keywords(query)
        
        # Classify search intent
        search_intent = self._classify_search_intent(query)
        
        # Get recipes with analysis data
        recipes = self._search_with_analysis_filters(cursor, keywords, search_intent, limit)
        
        # Score and rank results
        scored_recipes = self._score_recipes(recipes, keywords, search_intent)
        
        conn.close()
        return scored_recipes[:limit]
        
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from search query"""
        import re
        
        # Enhanced stopwords
        stopwords = {
            'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'she', 'it', 'they', 'them',
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'is', 'am', 'are', 'was', 'were', 'be', 
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 
            'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'something', 
            'anything', 'everything', 'nothing', 'what', 'which', 'who', 'when', 'where', 
            'why', 'how', 'need', 'want', 'like', 'show', 'get', 'give', 'tell', 'ask', 
            'find', 'help', 'make', 'please'
        }
        
        # Extract words and clean them
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        return keywords
        
    def _classify_search_intent(self, query: str) -> Dict[str, Any]:
        """Classify the intent behind the search query"""
        query_lower = query.lower()
        
        intent = {
            'cuisine_preference': None,
            'time_constraint': None,
            'skill_level': None,
            'dietary_restriction': None,
            'meal_type': None,
            'occasion': None,
            'temperature': None,
            'heat_preference': None
        }
        
        # Cuisine preferences
        cuisines = ['italian', 'asian', 'mexican', 'french', 'indian', 'mediterranean']
        for cuisine in cuisines:
            if cuisine in query_lower:
                intent['cuisine_preference'] = cuisine
                break
                
        # Time constraints
        if any(word in query_lower for word in ['quick', 'fast', '15 min', '30 min', 'hurry']):
            intent['time_constraint'] = 'quick'
        elif any(word in query_lower for word in ['slow', 'long', 'weekend', 'leisurely']):
            intent['time_constraint'] = 'long'
            
        # Skill level
        if any(word in query_lower for word in ['easy', 'simple', 'beginner']):
            intent['skill_level'] = 'beginner'
        elif any(word in query_lower for word in ['advanced', 'complex', 'challenging']):
            intent['skill_level'] = 'advanced'
            
        # Dietary restrictions
        dietary_terms = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'paleo']
        for diet in dietary_terms:
            if diet.replace('-', ' ') in query_lower or diet.replace('-', '') in query_lower:
                intent['dietary_restriction'] = diet
                break
                
        # Meal type
        if any(word in query_lower for word in ['breakfast', 'morning']):
            intent['meal_type'] = 'breakfast'
        elif any(word in query_lower for word in ['lunch', 'midday']):
            intent['meal_type'] = 'lunch'
        elif any(word in query_lower for word in ['dinner', 'evening', 'supper']):
            intent['meal_type'] = 'dinner'
        elif any(word in query_lower for word in ['dessert', 'sweet']):
            intent['meal_type'] = 'dessert'
        elif any(word in query_lower for word in ['snack', 'appetizer']):
            intent['meal_type'] = 'snack'
            
        # Occasion
        if any(word in query_lower for word in ['party', 'entertaining', 'guests']):
            intent['occasion'] = 'entertaining'
        elif any(word in query_lower for word in ['comfort', 'cozy']):
            intent['occasion'] = 'comfort'
        elif any(word in query_lower for word in ['healthy', 'light']):
            intent['occasion'] = 'healthy'
            
        # Temperature preference
        if any(word in query_lower for word in ['cold', 'chilled', 'refreshing']):
            intent['temperature'] = 'cold'
        elif any(word in query_lower for word in ['hot', 'warm', 'hearty']):
            intent['temperature'] = 'hot'
            
        # Heat/spice preference
        if any(word in query_lower for word in ['spicy', 'hot', 'fiery']):
            intent['heat_preference'] = 'high'
        elif any(word in query_lower for word in ['mild', 'gentle']):
            intent['heat_preference'] = 'low'
            
        return intent
        
    def _search_with_analysis_filters(self, cursor, keywords: List[str], 
                                    intent: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Search recipes using analysis data for filtering"""
        
        # Build the query with analysis filters
        base_query = """
            SELECT DISTINCT r.id, r.title, r.description, r.hands_on_time, r.total_time, 
                   r.servings, r.url, r.date_saved,
                   ra.cuisine_type, ra.skill_level, ra.time_category, ra.primary_tastes,
                   ra.heat_level, ra.meal_type, ra.social_context, ra.dietary_tags,
                   ra.flavor_intensity, ra.main_protein, ra.cost_estimate
            FROM recipes r
            LEFT JOIN recipe_analysis ra ON r.id = ra.recipe_id
        """
        
        where_conditions = []
        params = []
        
        # Apply intent-based filters
        if intent['cuisine_preference']:
            where_conditions.append("ra.cuisine_type = ?")
            params.append(intent['cuisine_preference'])
            
        if intent['time_constraint']:
            where_conditions.append("ra.time_category = ?")
            params.append(intent['time_constraint'])
            
        if intent['skill_level']:
            where_conditions.append("ra.skill_level = ?")
            params.append(intent['skill_level'])
            
        if intent['meal_type']:
            where_conditions.append("ra.meal_type = ?")
            params.append(intent['meal_type'])
            
        if intent['heat_preference']:
            if intent['heat_preference'] == 'high':
                where_conditions.append("ra.heat_level >= 5")
            elif intent['heat_preference'] == 'low':
                where_conditions.append("ra.heat_level <= 2")
                
        # Apply dietary restrictions
        if intent['dietary_restriction']:
            where_conditions.append("ra.dietary_tags LIKE ?")
            params.append(f'%{intent["dietary_restriction"]}%')
            
        # Apply keyword filters
        if keywords:
            keyword_conditions = []
            for keyword in keywords[:3]:  # Limit to first 3 keywords for performance
                keyword_pattern = f'%{keyword}%'
                keyword_conditions.append("""
                    (LOWER(r.title) LIKE ? OR 
                     LOWER(r.description) LIKE ? OR 
                     LOWER(r.ingredients) LIKE ? OR 
                     LOWER(r.instructions) LIKE ?)
                """)
                params.extend([keyword_pattern, keyword_pattern, keyword_pattern, keyword_pattern])
                
            if keyword_conditions:
                where_conditions.append(f"({' OR '.join(keyword_conditions)})")
                
        # Combine conditions
        if where_conditions:
            base_query += " WHERE " + " AND ".join(where_conditions)
            
        base_query += f" ORDER BY r.date_saved DESC LIMIT {limit * 2}"  # Get more to allow for scoring
        
        cursor.execute(base_query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    def _score_recipes(self, recipes: List[Dict[str, Any]], keywords: List[str], 
                      intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score and rank recipes based on relevance"""
        
        for recipe in recipes:
            score = 0
            
            # Base score for having analysis data
            if recipe.get('cuisine_type'):
                score += 10
                
            # Keyword matching scores
            recipe_text = f"{recipe.get('title', '')} {recipe.get('description', '')}".lower()
            for keyword in keywords:
                if keyword in recipe_text:
                    score += 15  # High weight for title/description matches
                    
            # Intent matching bonuses
            if intent['cuisine_preference'] and recipe.get('cuisine_type') == intent['cuisine_preference']:
                score += 20
                
            if intent['time_constraint'] and recipe.get('time_category') == intent['time_constraint']:
                score += 15
                
            if intent['skill_level'] and recipe.get('skill_level') == intent['skill_level']:
                score += 10
                
            if intent['meal_type'] and recipe.get('meal_type') == intent['meal_type']:
                score += 15
                
            # Heat preference matching
            if intent['heat_preference'] and recipe.get('heat_level') is not None:
                heat_level = recipe['heat_level']
                if intent['heat_preference'] == 'high' and heat_level >= 5:
                    score += 10
                elif intent['heat_preference'] == 'low' and heat_level <= 2:
                    score += 10
                    
            # Dietary restriction matching
            if intent['dietary_restriction'] and recipe.get('dietary_tags'):
                try:
                    dietary_tags = json.loads(recipe['dietary_tags']) if isinstance(recipe['dietary_tags'], str) else recipe['dietary_tags']
                    if intent['dietary_restriction'] in dietary_tags:
                        score += 25  # High bonus for dietary matches
                except:
                    pass
                    
            recipe['relevance_score'] = score
            
        # Sort by score (highest first)
        return sorted(recipes, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
    def get_recipe_suggestions(self, recipe_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get suggestions based on a specific recipe's analysis"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get the analysis for the target recipe
        cursor.execute("SELECT * FROM recipe_analysis WHERE recipe_id = ?", (recipe_id,))
        target_analysis = cursor.fetchone()
        
        if not target_analysis:
            # Fallback to basic search if no analysis
            cursor.execute("""
                SELECT r.id, r.title, r.description, r.total_time, r.servings, r.url
                FROM recipes r WHERE r.id != ? ORDER BY r.date_saved DESC LIMIT ?
            """, (recipe_id, limit))
            conn.close()
            return [dict(row) for row in cursor.fetchall()]
            
        # Find similar recipes based on analysis
        similar_query = """
            SELECT r.id, r.title, r.description, r.total_time, r.servings, r.url,
                   ra.cuisine_type, ra.skill_level, ra.time_category, ra.primary_tastes,
                   ra.heat_level, ra.meal_type, ra.main_protein
            FROM recipes r
            JOIN recipe_analysis ra ON r.id = ra.recipe_id
            WHERE r.id != ?
        """
        
        cursor.execute(similar_query, (recipe_id,))
        candidates = [dict(row) for row in cursor.fetchall()]
        
        # Score similarity
        target_dict = dict(target_analysis)
        for candidate in candidates:
            similarity_score = self._calculate_similarity(target_dict, candidate)
            candidate['similarity_score'] = similarity_score
            
        # Sort by similarity and return top results
        candidates.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        conn.close()
        return candidates[:limit]
        
    def _calculate_similarity(self, target: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """Calculate similarity score between two recipes"""
        score = 0.0
        
        # Cuisine similarity (high weight)
        if target.get('cuisine_type') == candidate.get('cuisine_type'):
            score += 30
            
        # Skill level similarity
        if target.get('skill_level') == candidate.get('skill_level'):
            score += 20
            
        # Time category similarity
        if target.get('time_category') == candidate.get('time_category'):
            score += 15
            
        # Meal type similarity
        if target.get('meal_type') == candidate.get('meal_type'):
            score += 25
            
        # Heat level similarity (within 2 points)
        if target.get('heat_level') is not None and candidate.get('heat_level') is not None:
            heat_diff = abs(target['heat_level'] - candidate['heat_level'])
            if heat_diff <= 2:
                score += max(0, 10 - heat_diff * 3)
                
        # Main protein similarity
        if target.get('main_protein') and target.get('main_protein') == candidate.get('main_protein'):
            score += 15
            
        # Taste similarity
        try:
            target_tastes = json.loads(target.get('primary_tastes', '[]')) if isinstance(target.get('primary_tastes'), str) else target.get('primary_tastes', [])
            candidate_tastes = json.loads(candidate.get('primary_tastes', '[]')) if isinstance(candidate.get('primary_tastes'), str) else candidate.get('primary_tastes', [])
            
            if target_tastes and candidate_tastes:
                common_tastes = set(target_tastes) & set(candidate_tastes)
                score += len(common_tastes) * 5
        except:
            pass
            
        return score
        
    def get_personalized_suggestions(self, user_preferences: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Get personalized suggestions based on user preferences"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query based on preferences
        query = """
            SELECT r.id, r.title, r.description, r.total_time, r.servings, r.url,
                   ra.cuisine_type, ra.skill_level, ra.time_category, ra.meal_type,
                   ra.heat_level, ra.cost_estimate, ra.dietary_tags
            FROM recipes r
            JOIN recipe_analysis ra ON r.id = ra.recipe_id
            WHERE 1=1
        """
        
        params = []
        
        # Apply preference filters
        if user_preferences.get('favorite_cuisines'):
            placeholders = ','.join(['?' for _ in user_preferences['favorite_cuisines']])
            query += f" AND ra.cuisine_type IN ({placeholders})"
            params.extend(user_preferences['favorite_cuisines'])
            
        if user_preferences.get('max_skill_level'):
            skill_levels = ['beginner', 'intermediate', 'advanced', 'professional']
            max_index = skill_levels.index(user_preferences['max_skill_level'])
            allowed_skills = skill_levels[:max_index + 1]
            placeholders = ','.join(['?' for _ in allowed_skills])
            query += f" AND ra.skill_level IN ({placeholders})"
            params.extend(allowed_skills)
            
        if user_preferences.get('dietary_restrictions'):
            for restriction in user_preferences['dietary_restrictions']:
                query += " AND ra.dietary_tags LIKE ?"
                params.append(f'%{restriction}%')
                
        if user_preferences.get('max_heat_level'):
            query += " AND ra.heat_level <= ?"
            params.append(user_preferences['max_heat_level'])
            
        query += " ORDER BY r.date_saved DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results

if __name__ == "__main__":
    # Test the enhanced search
    search_engine = EnhancedSearchEngine()
    
    # Test search
    results = search_engine.smart_search_with_analysis("spicy asian dinner", limit=5)
    print("Search Results:")
    for result in results:
        print(f"- {result['title']} (Score: {result.get('relevance_score', 0)})")
