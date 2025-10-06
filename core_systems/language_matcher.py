"""
Language Matcher for Voice Recording
Maps user input to Whisper language codes with cultural context

Created: October 6, 2025
Phase 1: Smart language selection
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Comprehensive language database with cultural context
LANGUAGE_DATABASE = [
    # Format: { id, displayName, whisperCode, culture, keywords, region, commonTerms }
    
    # English
    {
        'id': 'en',
        'displayName': 'English',
        'whisperCode': 'en',
        'culture': 'English',
        'keywords': ['english', 'american', 'british', 'usa', 'uk'],
        'region': 'International',
        'commonTerms': []
    },
    
    # Filipino/Tagalog
    {
        'id': 'fil-tl',
        'displayName': 'Filipino (Tagalog)',
        'whisperCode': 'tl',
        'culture': 'Filipino',
        'keywords': ['filipino', 'tagalog', 'philippines', 'pilipino', 'pinoy'],
        'region': 'Philippines',
        'commonTerms': ['adobo', 'sinigang', 'lumpia', 'patis', 'bagoong', 'pancit']
    },
    
    # Spanish/Mexican
    {
        'id': 'es-mx',
        'displayName': 'Spanish (Mexican)',
        'whisperCode': 'es',
        'culture': 'Mexican',
        'keywords': ['mexican', 'español', 'mexico', 'mexicano', 'spanish'],
        'region': 'Mexico',
        'commonTerms': ['masa', 'tortilla', 'salsa', 'chile', 'mole', 'tamales']
    },
    
    # Spanish/Puerto Rican
    {
        'id': 'es-pr',
        'displayName': 'Spanish (Puerto Rican)',
        'whisperCode': 'es',
        'culture': 'Puerto Rican',
        'keywords': ['puerto rican', 'boricua', 'puerto rico', 'spanish'],
        'region': 'Puerto Rico',
        'commonTerms': ['mofongo', 'pasteles', 'sofrito', 'recaito', 'pernil']
    },
    
    # Chinese/Mandarin
    {
        'id': 'zh-cn',
        'displayName': 'Chinese (Mandarin)',
        'whisperCode': 'zh',
        'culture': 'Chinese',
        'keywords': ['chinese', 'mandarin', 'china', '中文', 'zhongwen'],
        'region': 'China',
        'commonTerms': ['wok', 'dim sum', 'soy sauce', 'ginger', 'dumpling']
    },
    
    # Italian
    {
        'id': 'it',
        'displayName': 'Italian',
        'whisperCode': 'it',
        'culture': 'Italian',
        'keywords': ['italian', 'italiano', 'italy', 'italia'],
        'region': 'Italy',
        'commonTerms': ['pasta', 'risotto', 'parmigiano', 'prosciutto', 'basil']
    },
    
    # Vietnamese
    {
        'id': 'vi',
        'displayName': 'Vietnamese',
        'whisperCode': 'vi',
        'culture': 'Vietnamese',
        'keywords': ['vietnamese', 'vietnam', 'tiếng việt', 'viet'],
        'region': 'Vietnam',
        'commonTerms': ['pho', 'banh mi', 'fish sauce', 'nuoc mam', 'spring rolls']
    },
    
    # Korean
    {
        'id': 'ko',
        'displayName': 'Korean',
        'whisperCode': 'ko',
        'culture': 'Korean',
        'keywords': ['korean', 'korea', '한국어', 'hangul', 'hanguk'],
        'region': 'Korea',
        'commonTerms': ['kimchi', 'gochujang', 'bibimbap', 'bulgogi', 'banchan']
    },
    
    # Japanese
    {
        'id': 'ja',
        'displayName': 'Japanese',
        'whisperCode': 'ja',
        'culture': 'Japanese',
        'keywords': ['japanese', 'japan', '日本語', 'nihongo', 'nippon'],
        'region': 'Japan',
        'commonTerms': ['sushi', 'miso', 'dashi', 'sake', 'tempura', 'ramen']
    },
    
    # Thai
    {
        'id': 'th',
        'displayName': 'Thai',
        'whisperCode': 'th',
        'culture': 'Thai',
        'keywords': ['thai', 'thailand', 'ไทย'],
        'region': 'Thailand',
        'commonTerms': ['pad thai', 'curry', 'lemongrass', 'fish sauce', 'basil']
    },
    
    # Indian (Hindi)
    {
        'id': 'hi',
        'displayName': 'Indian (Hindi)',
        'whisperCode': 'hi',
        'culture': 'Indian',
        'keywords': ['indian', 'hindi', 'india', 'हिन्दी', 'bharat'],
        'region': 'India',
        'commonTerms': ['curry', 'masala', 'tandoor', 'ghee', 'naan', 'chai']
    },
    
    # Greek
    {
        'id': 'el',
        'displayName': 'Greek',
        'whisperCode': 'el',
        'culture': 'Greek',
        'keywords': ['greek', 'greece', 'ελληνικά', 'hellenic'],
        'region': 'Greece',
        'commonTerms': ['feta', 'olive oil', 'tzatziki', 'moussaka', 'gyro']
    },
    
    # Middle Eastern/Arabic
    {
        'id': 'ar',
        'displayName': 'Arabic (Middle Eastern)',
        'whisperCode': 'ar',
        'culture': 'Middle Eastern',
        'keywords': ['arabic', 'middle eastern', 'العربية', 'arab', 'arabian'],
        'region': 'Middle East',
        'commonTerms': ['hummus', 'tahini', 'za\'atar', 'shawarma', 'falafel']
    },
    
    # French
    {
        'id': 'fr',
        'displayName': 'French',
        'whisperCode': 'fr',
        'culture': 'French',
        'keywords': ['french', 'france', 'français', 'francais'],
        'region': 'France',
        'commonTerms': ['baguette', 'croissant', 'sauce', 'butter', 'wine']
    },
    
    # German
    {
        'id': 'de',
        'displayName': 'German',
        'whisperCode': 'de',
        'culture': 'German',
        'keywords': ['german', 'germany', 'deutsch', 'deutschland'],
        'region': 'Germany',
        'commonTerms': ['schnitzel', 'sauerkraut', 'bratwurst', 'pretzel', 'beer']
    },
    
    # Portuguese
    {
        'id': 'pt',
        'displayName': 'Portuguese',
        'whisperCode': 'pt',
        'culture': 'Portuguese',
        'keywords': ['portuguese', 'portugal', 'português', 'brazil', 'brasileiro'],
        'region': 'Portugal/Brazil',
        'commonTerms': ['feijoada', 'pastel', 'bacalhau', 'pão', 'brigadeiro']
    },
    
    # Russian
    {
        'id': 'ru',
        'displayName': 'Russian',
        'whisperCode': 'ru',
        'culture': 'Russian',
        'keywords': ['russian', 'russia', 'русский', 'rossiya'],
        'region': 'Russia',
        'commonTerms': ['borscht', 'pelmeni', 'vodka', 'caviar', 'blini']
    },
    
    # Turkish
    {
        'id': 'tr',
        'displayName': 'Turkish',
        'whisperCode': 'tr',
        'culture': 'Turkish',
        'keywords': ['turkish', 'turkey', 'türkçe', 'turkiye'],
        'region': 'Turkey',
        'commonTerms': ['kebab', 'baklava', 'dolma', 'yogurt', 'pide']
    },
    
    # Polish
    {
        'id': 'pl',
        'displayName': 'Polish',
        'whisperCode': 'pl',
        'culture': 'Polish',
        'keywords': ['polish', 'poland', 'polski', 'polska'],
        'region': 'Poland',
        'commonTerms': ['pierogi', 'kielbasa', 'bigos', 'golabki', 'zurek']
    }
]


class LanguageMatcher:
    """
    Smart language matching with fuzzy search
    Maps user input to Whisper-compatible language codes
    """
    
    def __init__(self):
        self.languages = LANGUAGE_DATABASE
        logger.info(f"✅ LanguageMatcher initialized with {len(self.languages)} languages")
    
    def search(self, query: str) -> List[Dict]:
        """
        Fuzzy search through language database
        Returns matching results in order of relevance
        
        Args:
            query: User search string
        
        Returns:
            List of matching language dicts with scores
        """
        if not query or not query.strip():
            # Return popular languages if empty query
            return self.get_popular_languages()
        
        lowerQuery = query.lower().strip()
        
        # Score each language
        scored = []
        for lang in self.languages:
            score = 0
            
            # Exact match on display name (highest priority)
            if lang['displayName'].lower() == lowerQuery:
                score += 100
            
            # Starts with query (high priority)
            if lang['displayName'].lower().startswith(lowerQuery):
                score += 50
            
            # Contains query in display name
            if lowerQuery in lang['displayName'].lower():
                score += 30
            
            # Match on culture
            if lowerQuery in lang['culture'].lower():
                score += 40
            
            # Match on keywords
            for keyword in lang['keywords']:
                if lowerQuery in keyword:
                    score += 20
                if keyword.startswith(lowerQuery):
                    score += 10
            
            # Match on common terms (user might type a dish name)
            for term in lang['commonTerms']:
                if lowerQuery in term.lower():
                    score += 10
            
            if score > 0:
                scored.append({**lang, 'score': score})
        
        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 10 matches
        return scored[:10]
    
    def get_popular_languages(self) -> List[Dict]:
        """
        Return most commonly used languages for recipes
        
        Returns:
            List of popular language dicts
        """
        popular_codes = ['en', 'es', 'zh', 'it', 'ja', 'fr', 'ko', 'th', 'vi', 'hi', 'tl', 'ar']
        
        return [
            {**lang, 'score': 100} 
            for lang in self.languages 
            if lang['whisperCode'] in popular_codes
        ]
    
    def get_whisper_config(self, language_id: str) -> Dict:
        """
        Get Whisper API configuration for selected language
        
        Args:
            language_id: Language ID from database
        
        Returns:
            {
                'language': 'en',
                'culturalContext': {
                    'culture': 'English',
                    'region': 'International',
                    'commonTerms': [...]
                }
            }
        """
        lang = next((l for l in self.languages if l['id'] == language_id), None)
        
        if not lang:
            # Default to English
            logger.warning(f"⚠️ Language {language_id} not found, defaulting to English")
            lang = next((l for l in self.languages if l['id'] == 'en'), self.languages[0])
        
        return {
            'language': lang['whisperCode'],
            'culturalContext': {
                'culture': lang['culture'],
                'region': lang['region'],
                'commonTerms': lang['commonTerms']
            }
        }
    
    def get_all_languages(self) -> List[Dict]:
        """Get all available languages"""
        return self.languages
    
    def get_language_by_code(self, whisper_code: str) -> Optional[Dict]:
        """
        Find language by Whisper code
        
        Args:
            whisper_code: Whisper API language code (e.g., 'en', 'es')
        
        Returns:
            Language dict or None
        """
        return next((l for l in self.languages if l['whisperCode'] == whisper_code), None)


# Test function
def test_language_matcher():
    """Test language matcher"""
    matcher = LanguageMatcher()
    
    # Test searches
    test_queries = [
        "filipino",
        "mexican",
        "adobo",  # Should match Filipino via commonTerms
        "pasta",  # Should match Italian
        "kimchi",  # Should match Korean
        ""  # Should return popular languages
    ]
    
    print("🧪 Testing LanguageMatcher\n")
    
    for query in test_queries:
        results = matcher.search(query)
        print(f"Query: '{query}'")
        print(f"Results: {len(results)}")
        for r in results[:3]:
            print(f"  - {r['displayName']} ({r['whisperCode']}) - Score: {r['score']}")
        print()


if __name__ == '__main__':
    test_language_matcher()
