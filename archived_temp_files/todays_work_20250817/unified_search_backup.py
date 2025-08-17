# BACKUP: Unified Smart Search Function
# This is the cleaned up smart-search route for hungie_server.py

@app.route('/api/smart-search', methods=['POST'])
def smart_search():
    """
    UNIFIED SMART SEARCH - Day 4 Implementation
    Intelligent recipe search with filter support and consolidated logic
    Replaces all scattered search implementations with unified system
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        query = data.get('query', user_message).strip()  # Support both message and query
        session_id = data.get('session_id', 'default')
        
        # NEW: Extract intelligence filters from request (Day 4 enhancement)
        filters = {
            'meal_role': data.get('meal_role'),
            'max_time': data.get('max_time'),
            'is_easy': data.get('is_easy', False),
            'is_one_pot': data.get('is_one_pot', False),
            'kid_friendly': data.get('kid_friendly', False),
            'leftover_friendly': data.get('leftover_friendly', False),
            'pantry_first': data.get('pantry_first', False)
        }
        
        # Get user pantry if available (future enhancement)
        user_pantry = data.get('user_pantry', [])
        exclude_ids = data.get('exclude_ids', [])
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Use unified search engine (consolidated from all scattered functions)
        if not search_engine:
            return jsonify({
                'success': False,
                'error': 'Search engine not available'
            }), 503
        
        # Get session memory if available
        session_memory = None
        if session_manager:
            session_memory = session_manager.get_session_data(session_id)
        
        # UNIFIED SEARCH CALL - replaces all scattered search functions
        search_result = search_engine.unified_intelligent_search(
            query=query,
            session_memory=session_memory,
            user_pantry=user_pantry,
            exclude_ids=exclude_ids,
            limit=limit,
            include_explanations=True
        )
        
        if not search_result['success']:
            return jsonify({
                'success': False,
                'error': search_result.get('error', 'Search failed')
            }), 500
        
        recipes = search_result['recipes']
        filters_applied = search_result['filters_applied']
        search_metadata = search_result['search_metadata']
        
        # Record query in session if available
        if session_manager:
            session_manager.record_query(
                session_id=session_id,
                user_query=query,
                intent="recipe_search",
                context=f"filters: {filters_applied}",
                result_count=len(recipes),
                displayed_count=len(recipes),
                search_phase="unified_search"
            )
        
        # Generate intelligent response based on results
        if recipes:
            # Smart response based on filters applied
            response_parts = [f"Found {len(recipes)} recipes"]
            
            if filters_applied.get('max_time'):
                response_parts.append(f"ready in ≤{filters_applied['max_time']} minutes")
            if filters_applied.get('is_easy'):
                response_parts.append("that are easy to make")
            if filters_applied.get('is_one_pot'):
                response_parts.append("using just one pot")
            if filters_applied.get('kid_friendly'):
                response_parts.append("that are kid-friendly")
            if filters_applied.get('meal_role'):
                response_parts.append(f"perfect for {filters_applied['meal_role']}")
            
            ai_response = " ".join(response_parts) + "! 🍴"
            
            # Generate conversation suggestions if available
            conversation_suggestions = None
            if session_manager:
                try:
                    conversation_suggestions = ConversationSuggestionGenerator.generate_suggestions(
                        query, recipes
                    )
                except:
                    conversation_suggestions = []
            
            # Enhanced response with intelligence metadata
            response_data = {
                'success': True,
                'data': {
                    'response': ai_response,
                    'context': query,
                    'recipes': recipes,
                    'filters_applied': filters_applied,
                    'search_metadata': search_metadata,
                    'session_id': session_id,
                    'total_results': len(recipes),
                    'intelligence_enabled': True  # Day 4 feature flag
                }
            }
            
            # Add conversation suggestions if available
            if conversation_suggestions:
                response_data['data']['conversation_suggestions'] = conversation_suggestions
            
            return jsonify(response_data)
            
        else:
            # No results found - provide helpful suggestions
            ai_response = "I couldn't find recipes matching those criteria. Try adjusting your filters or being more specific about ingredients or cooking style. 🔍"
            
            return jsonify({
                'success': True,
                'data': {
                    'response': ai_response,
                    'context': query,
                    'recipes': [],
                    'filters_applied': filters_applied,
                    'search_metadata': search_metadata,
                    'session_id': session_id,
                    'total_results': 0,
                    'intelligence_enabled': True,
                    'suggestions': [
                        "Try removing some filters",
                        "Search for ingredients you have",
                        "Look for a different meal type",
                        "Ask for general recipe ideas"
                    ]
                }
            })
            
    except Exception as e:
        logger.error(f"Unified smart search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
