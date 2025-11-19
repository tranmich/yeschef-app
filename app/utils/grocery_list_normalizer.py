"""
Grocery List Normalizer
=======================
Single point of conversion for all grocery list formats.

STANDARD FORMAT (The One True Schema):
{
    'id': int,
    'name': str,
    'items': [
        {
            'id': str,
            'name': str,          # ← ONLY field for item text
            'checked': bool,
            'quantity': str (optional),
            'unit': str (optional),
            'category': str (optional)
        }
    ],
    'household_id': int (optional),
    'whiteboard_id': int (optional),
    'created_at': str,
    'updated_at': str
}

WHY THIS EXISTS:
- Whiteboard uses: ingredient
- Web uses: name
- Mobile uses: name
- Database legacy used: list_name, items_json
- Recipe gen uses: ingredient_name, display_text

This normalizer converts EVERYTHING to/from the standard format.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GroceryListNormalizer:
    """
    Converts any grocery list format to/from StandardGroceryList.
    
    This is the SINGLE point where format conversion happens.
    All other code should use the standard format.
    """
    
    # Standard field names (enforced)
    STANDARD_LIST_NAME = 'name'
    STANDARD_ITEMS_FIELD = 'items'
    STANDARD_ITEM_NAME_FIELD = 'name'
    
    @staticmethod
    def to_standard(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert ANY format to StandardGroceryList.
        
        Accepts:
        - Whiteboard format (ingredient)
        - Legacy format (list_name, items_json)
        - Web format (sections)
        - Mobile format (already standard)
        
        Returns:
        - StandardGroceryList (name, items array)
        """
        if not raw_data:
            logger.warning("⚠️ Normalizer received empty data")
            return GroceryListNormalizer._empty_standard()
        
        logger.info(f"🔄 Normalizing grocery list data (has {len(raw_data)} fields)")
        
        # Build standard structure
        standard = {
            'id': raw_data.get('id'),
            
            # List name - check all possible fields
            'name': (
                raw_data.get('name') or 
                raw_data.get('list_name') or 
                'Grocery List'
            ),
            
            # Items array (will be populated below)
            'items': [],
            
            # Optional metadata
            'household_id': raw_data.get('household_id') or raw_data.get('hid'),
            'whiteboard_id': raw_data.get('whiteboard_id') or raw_data.get('wid'),
            'meal_plan_id': raw_data.get('meal_plan_id'),
            'widget_position': raw_data.get('widget_position') or raw_data.get('wp'),
            'linked_recipe_ids': raw_data.get('linked_recipe_ids') or raw_data.get('lr'),
            
            # Timestamps
            'created_at': str(raw_data.get('created_at') or raw_data.get('created_date') or ''),
            'updated_at': str(raw_data.get('updated_at') or raw_data.get('updated_date') or '')
        }
        
        # Find items from various possible sources
        items_source = (
            raw_data.get('items') or           # Phase 2/3 standard
            raw_data.get('list_data') or       # Database JSONB
            raw_data.get('items_json') or      # Legacy TEXT
            []
        )
        
        # Parse if it's a JSON string
        if isinstance(items_source, str):
            try:
                items_source = json.loads(items_source)
            except json.JSONDecodeError:
                logger.error(f"❌ Failed to parse items JSON: {items_source[:100]}")
                items_source = []
        
        # Convert items to standard format
        standard['items'] = GroceryListNormalizer._normalize_items(items_source)
        
        logger.info(f"✅ Normalized to standard: {standard['name']} with {len(standard['items'])} items")
        
        return standard
    
    @staticmethod
    def _normalize_items(items_source: Any) -> List[Dict[str, Any]]:
        """
        Convert items from any format to standard item array.
        
        Handles:
        - Flat array: [{name: "milk", checked: false}, ...]
        - Sections: {produce: [...], dairy: [...], ...}
        - Nested: {sections: {produce: [...], ...}}
        """
        normalized_items = []
        
        # Case 1: Already a flat array
        if isinstance(items_source, list):
            for idx, item in enumerate(items_source):
                if isinstance(item, dict):
                    normalized_items.append(GroceryListNormalizer._normalize_single_item(item, idx))
                elif isinstance(item, str):
                    # Plain string array
                    normalized_items.append({
                        'id': f'item-{idx}',
                        'name': item,
                        'checked': False
                    })
        
        # Case 2: Sections format (web)
        elif isinstance(items_source, dict):
            item_idx = 0
            
            # Check for nested sections
            if 'sections' in items_source:
                items_source = items_source['sections']
            
            # Known section names
            section_names = ['produce', 'meat_seafood', 'dairy', 'pantry', 'frozen', 'other', 'bakery']
            
            for section_name in section_names:
                if section_name in items_source:
                    section_items = items_source[section_name]
                    
                    # Web format: {items: [...]}
                    if isinstance(section_items, dict) and 'items' in section_items:
                        section_items = section_items['items']
                    
                    # Convert each item
                    if isinstance(section_items, list):
                        for item in section_items:
                            normalized_items.append(
                                GroceryListNormalizer._normalize_single_item(item, item_idx)
                            )
                            item_idx += 1
        
        logger.info(f"  📋 Normalized {len(normalized_items)} items from source")
        return normalized_items
    
    @staticmethod
    def _normalize_single_item(item: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Normalize a single item to standard format.
        
        Checks ALL possible field names for the item text:
        - name (standard, web, mobile)
        - ingredient (whiteboard)
        - ingredient_name (recipe gen)
        - display_text (backend combiner)
        - text (legacy)
        """
        # Extract item name from any possible field
        item_name = (
            item.get('name') or
            item.get('ingredient') or
            item.get('ingredient_name') or
            item.get('display_text') or
            item.get('text') or
            f'Item {index + 1}'
        )
        
        return {
            'id': item.get('id') or f'item-{index}',
            'name': str(item_name).strip(),
            'checked': bool(item.get('checked', False)),
            'quantity': item.get('quantity'),
            'unit': item.get('unit'),
            'category': item.get('category')
        }
    
    @staticmethod
    def from_standard(standard: Dict[str, Any], target_format: str = 'standard') -> Dict[str, Any]:
        """
        Convert StandardGroceryList to a specific platform format.
        
        During migration, some platforms may still need old formats.
        Once migration is complete, this should only return standard format.
        
        Args:
            standard: StandardGroceryList
            target_format: 'standard', 'database', 'legacy'
        
        Returns:
            Formatted data for target platform
        """
        if target_format == 'database':
            # Database storage format
            return {
                'id': standard.get('id'),
                'name': standard['name'],
                'list_data': standard['items'],  # JSONB
                'household_id': standard.get('household_id'),
                'whiteboard_id': standard.get('whiteboard_id'),
                'meal_plan_id': standard.get('meal_plan_id'),
                'widget_position': standard.get('widget_position'),
                'linked_recipe_ids': standard.get('linked_recipe_ids'),
                'created_at': standard.get('created_at'),
                'updated_at': standard.get('updated_at')
            }
        
        elif target_format == 'legacy':
            # Legacy API format (for backward compatibility during migration)
            return {
                'id': standard.get('id'),
                'list_name': standard['name'],
                'list_data': standard['items'],
                'created_date': standard.get('created_at'),
                'updated_date': standard.get('updated_at')
            }
        
        # Default: return standard format as-is
        return standard
    
    @staticmethod
    def _empty_standard() -> Dict[str, Any]:
        """Return empty standard grocery list"""
        return {
            'id': None,
            'name': 'Grocery List',
            'items': [],
            'household_id': None,
            'whiteboard_id': None,
            'created_at': '',
            'updated_at': ''
        }
    
    @staticmethod
    def validate_standard(data: Dict[str, Any]) -> bool:
        """
        Validate that data conforms to StandardGroceryList schema.
        
        Required fields:
        - name (string)
        - items (array)
        
        Each item must have:
        - name (string)
        - checked (boolean)
        """
        try:
            # Check required top-level fields
            if 'name' not in data or not isinstance(data['name'], str):
                logger.error("❌ Validation failed: 'name' must be a string")
                return False
            
            if 'items' not in data or not isinstance(data['items'], list):
                logger.error("❌ Validation failed: 'items' must be an array")
                return False
            
            # Check each item
            for idx, item in enumerate(data['items']):
                if not isinstance(item, dict):
                    logger.error(f"❌ Validation failed: Item {idx} is not an object")
                    return False
                
                if 'name' not in item or not isinstance(item['name'], str):
                    logger.error(f"❌ Validation failed: Item {idx} missing 'name' string")
                    return False
                
                if 'checked' not in item or not isinstance(item['checked'], bool):
                    logger.error(f"❌ Validation failed: Item {idx} missing 'checked' boolean")
                    return False
            
            logger.info(f"✅ Validation passed: {data['name']} with {len(data['items'])} items")
            return True
            
        except Exception as e:
            logger.error(f"❌ Validation exception: {e}")
            return False


# Convenience functions
def normalize(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Shorthand for to_standard()"""
    return GroceryListNormalizer.to_standard(raw_data)


def validate(data: Dict[str, Any]) -> bool:
    """Shorthand for validate_standard()"""
    return GroceryListNormalizer.validate_standard(data)
