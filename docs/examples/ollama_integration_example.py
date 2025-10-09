"""
Example of how Ollama integrates with existing grocery list generation
Similar to how spaCy currently works
"""

from flask import Flask, jsonify, request
from core_systems.spacy_ingredient_normalizer import get_normalizer
from core_systems.ollama_grocery_advisor import OllamaGroceryAdvisor

app = Flask(__name__)

# Initialize both systems
spacy_normalizer = get_normalizer()
ollama_advisor = OllamaGroceryAdvisor()

@app.route('/api/meal-plans/<plan_id>/generate-grocery-list', methods=['POST'])
def generate_grocery_list(plan_id):
    """
    Generate grocery list from meal plan
    Mobile app calls this ONE endpoint - doesn't know about spaCy or Ollama!
    """
    
    # 1. Get meal plan recipes
    meal_plan = get_meal_plan(plan_id)
    recipes = meal_plan.recipes
    
    # 2. Extract all ingredients from recipes
    all_ingredients = []
    for recipe in recipes:
        all_ingredients.extend(recipe.ingredients)
    
    print(f"📥 Extracted {len(all_ingredients)} ingredients from {len(recipes)} recipes")
    
    # 3. 🧠 TIER 1: spaCy analysis (FAST - 1-2 seconds)
    print("🧠 Running spaCy analysis...")
    spacy_metadata = spacy_normalizer.extract_metadata(all_ingredients)
    print(f"✅ spaCy analyzed {len(spacy_metadata)} items")
    
    # 4. 🤖 TIER 2: LLM refinement for ambiguous cases (SMART - 2-3 seconds)
    print("🤖 Running LLM analysis for ambiguous cases...")
    ambiguous_items = find_ambiguous_cases(all_ingredients, spacy_metadata)
    
    if ambiguous_items:
        print(f"🤔 Found {len(ambiguous_items)} ambiguous cases, asking LLM...")
        llm_decisions = ollama_advisor.analyze_combining(
            ambiguous_items,
            spacy_metadata
        )
        print(f"✅ LLM provided guidance on {len(llm_decisions)} cases")
    else:
        print("✅ No ambiguous cases, spaCy metadata is sufficient")
        llm_decisions = {}
    
    # 5. Combine ingredients with LLM guidance
    print("🔄 Combining ingredients...")
    combined_items = combine_with_guidance(
        all_ingredients,
        spacy_metadata,
        llm_decisions
    )
    print(f"✅ Combined: {len(all_ingredients)} → {len(combined_items)} items")
    
    # 6. Save to database
    grocery_list = create_grocery_list(
        user_id=current_user.id,
        meal_plan_id=plan_id,
        items=combined_items
    )
    
    # 7. Return to mobile app
    return jsonify({
        'success': True,
        'grocery_list': grocery_list,
        'stats': {
            'original_count': len(all_ingredients),
            'combined_count': len(combined_items),
            'reduction': len(all_ingredients) - len(combined_items),
            'used_llm': len(llm_decisions) > 0
        }
    })


def find_ambiguous_cases(ingredients, spacy_metadata):
    """
    Find cases where spaCy isn't confident
    These are the ONLY cases we'll ask LLM about
    """
    ambiguous = []
    
    # Group by base ingredient
    groups = {}
    for item in ingredients:
        item_id = item.get('id')
        core = spacy_metadata.get(item_id, {}).get('core_ingredient')
        
        if core not in groups:
            groups[core] = []
        groups[core].append(item)
    
    # Find groups with potential ambiguity
    for core, items in groups.items():
        if len(items) > 1:
            # Multiple items with same core - might be ambiguous
            # Example: "chicken thighs", "chicken broth" both have "chicken" related
            if has_mixed_types(items):
                ambiguous.extend(items)
    
    return ambiguous


def has_mixed_types(items):
    """
    Check if items are different types (meat vs liquid, vegetable vs seasoning, etc.)
    """
    # Check if items have very different contexts
    types = set()
    for item in items:
        name = item['name'].lower()
        
        # Detect type
        if any(word in name for word in ['broth', 'stock', 'juice', 'water', 'milk']):
            types.add('liquid')
        elif any(word in name for word in ['breast', 'thigh', 'wing', 'leg', 'meat']):
            types.add('meat')
        elif any(word in name for word in ['pepper', 'salt', 'garlic', 'onion']):
            types.add('seasoning')
        else:
            types.add('other')
    
    # If multiple types, it's ambiguous
    return len(types) > 1


def combine_with_guidance(ingredients, spacy_metadata, llm_decisions):
    """
    Combine ingredients using spaCy + LLM guidance
    """
    combined = []
    processed = set()
    
    for item in ingredients:
        if item['id'] in processed:
            continue
        
        # Check if LLM has specific guidance
        llm_guidance = llm_decisions.get(item['id'])
        
        if llm_guidance and llm_guidance['action'] == 'combine_with':
            # LLM says combine with specific items
            combine_ids = llm_guidance['combine_with_ids']
            items_to_combine = [item] + [i for i in ingredients if i['id'] in combine_ids]
            
            # Combine them
            combined_item = merge_items(items_to_combine)
            combined.append(combined_item)
            
            # Mark as processed
            for i in items_to_combine:
                processed.add(i['id'])
        
        elif llm_guidance and llm_guidance['action'] == 'keep_separate':
            # LLM says keep separate
            combined.append(item)
            processed.add(item['id'])
        
        else:
            # No LLM guidance, use spaCy logic
            # (existing combining logic)
            similar = find_similar_items(item, ingredients, spacy_metadata)
            
            if similar:
                items_to_combine = [item] + similar
                combined_item = merge_items(items_to_combine)
                combined.append(combined_item)
                
                for i in items_to_combine:
                    processed.add(i['id'])
            else:
                combined.append(item)
                processed.add(item['id'])
    
    return combined


# Helper functions (simplified)
def merge_items(items):
    """Merge multiple items into one"""
    # Combine quantities, preserve details, etc.
    pass

def find_similar_items(item, all_items, metadata):
    """Find items that should combine (using spaCy)"""
    pass

def get_meal_plan(plan_id):
    """Get meal plan from database"""
    pass

def create_grocery_list(user_id, meal_plan_id, items):
    """Save grocery list to database"""
    pass
