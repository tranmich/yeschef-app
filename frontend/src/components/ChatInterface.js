import React, { useState, useRef, useEffect } from 'react';
import { api } from '../utils/api';
import SessionMemoryManager from '../utils/SessionMemoryManager';
import RecipeDropdown from './RecipeDropdown';
import './ChatInterface.css';

const ChatInterface = ({ sessionMemory, getPantryForAPI, hasPantryItems, pantryItems, setShowPantry, isCompact = false, isExtraCompact = false, onAddToMealPlan }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [hasStartedChat, setHasStartedChat] = useState(false);
    const [showMealPlanPopover, setShowMealPlanPopover] = useState(false);
    const [selectedRecipeForMealPlan, setSelectedRecipeForMealPlan] = useState(null);
    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Chat Message Send Function
    const sendMessage = async () => {
        if (!inputMessage.trim() || isLoading) return;

        // Start chat UI on first message
        if (!hasStartedChat) setHasStartedChat(true);

        const userMessage = inputMessage.trim();
        setInputMessage("");
        setIsLoading(true);

        try {
            // Check for special commands first
            if (userMessage.toLowerCase().includes('reset memory')) {
                sessionMemory.resetUserSession();
                const resetMessage = {
                    type: 'hungie',
                    content: `🔄 Memory reset! I've cleared all the recipes I've shown you before. Now you can search for anything and see all available recipes again! What would you like to cook? 🍴`,
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, resetMessage]);
                setIsLoading(false);
                return;
            }

            // Add user message to chat
            const userMessageObj = {
                type: 'user',
                content: userMessage,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, userMessageObj]);

            console.log('🧠 [' + new Date().toLocaleTimeString() + '] Starting enhanced search for:', userMessage);

            let searchResult;
            let isIntelligentAvailable = false;

            // Get variation strategy for repeat searches
            const variationStrategy = sessionMemory.getRecipeVariationStrategy(userMessage, { context: {} });
            console.log('🔄 Variation Strategy:', variationStrategy);

            // Try intelligent session-aware search first, fallback to standard if unavailable
            try {
                isIntelligentAvailable = await api.isIntelligentSearchAvailable();
                console.log('🧠 Intelligent search available:', isIntelligentAvailable);

                if (isIntelligentAvailable) {
                    // Get pantry data for enhanced search
                    const userPantry = getPantryForAPI();
                    const pantryFirst = hasPantryItems;

                    console.log('🥫 ChatInterface - Pantry Integration:', {
                        pantryItems: userPantry.map(item => item.name),
                        pantryFirst,
                        userMessage
                    });

                    // Use enhanced session-aware search
                    const data = await api.searchRecipesIntelligent(
                        userMessage,
                        sessionMemory.sessionId,
                        sessionMemory.getShownRecipeIds(),
                        5,
                        {
                            user_pantry: userPantry,
                            pantry_first: pantryFirst
                        }
                    );

                    if (data.success) {
                        // Track the new recipes as shown
                        sessionMemory.recordShownRecipes(data.recipes);

                        searchResult = {
                            recipes: data.recipes,
                            hasMore: data.has_more,
                            totalAvailable: data.total_available,
                            shownCount: data.shown_count,
                            metadata: data.search_metadata
                        };
                        console.log('🧠 Enhanced search result:', searchResult);
                    } else {
                        throw new Error(data.error || 'Intelligent search failed');
                    }
                } else {
                    throw new Error('Intelligent search not available');
                }
            } catch (intelligentError) {
                // Fallback to standard search with frontend filtering
                console.log('🔄 Falling back to standard search with frontend filtering. Reason:', intelligentError.message);
                const response = await api.searchRecipes(userMessage);
                const recipes = response.recipes || response.data || [];
                const newRecipes = sessionMemory.filterNewRecipes(recipes);

                searchResult = {
                    recipes: newRecipes,
                    hasMore: false,
                    totalAvailable: recipes.length,
                    shownCount: sessionMemory.shownRecipes.size,
                    metadata: { fallback_search_used: true, isIntelligentAvailable: false }
                };

                // Mark displayed recipes as shown
                const displayedRecipes = newRecipes.slice(0, 5);
                sessionMemory.recordShownRecipes(displayedRecipes);
            }

            if (searchResult.error) {
                throw new Error(searchResult.error);
            }

            // Check if we have new recipes to show
            if (searchResult.recipes.length === 0) {
                // Clean the search term to avoid "recipes recipes" duplication
                const cleanSearchTerm = userMessage.toLowerCase().includes('recipes')
                    ? userMessage.replace(/\s*recipes?\s*$/i, '')
                    : userMessage;

                const noNewRecipesMessage = {
                    type: 'hungie',
                    content: `I've already shown you all the ${cleanSearchTerm} recipes I found! 🤔\n\nI searched through ${searchResult.totalAvailable || 'all available'} recipes.\n\nOptions:\n• Try searching for something different\n• Search for variations (e.g., "spicy ${cleanSearchTerm}" or "healthy ${cleanSearchTerm}")\n• Type "reset memory" to see all recipes again\n\nWhat would you like to explore?`,
                    recipes: [],
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, noNewRecipesMessage]);
            } else {
                // Clean the search term to avoid "recipes recipes" duplication
                const cleanSearchTerm = userMessage.toLowerCase().includes('recipes')
                    ? userMessage.replace(/\s*recipes?\s*$/i, '')
                    : userMessage;

                // Generate intelligent batch summary based on search metadata and recipe analysis
                const batchSummary = renderBatchSummary(searchResult, cleanSearchTerm, hasPantryItems, variationStrategy);

                const aiMessage = {
                    type: 'hungie',
                    content: batchSummary,
                    recipes: searchResult.recipes,
                    timestamp: new Date(),
                    searchMetadata: searchResult.metadata,
                    batchAnalysis: analyzeBatch(searchResult.recipes),
                    variationStrategy: variationStrategy
                };
                setMessages(prev => [...prev, aiMessage]);

                console.log('✅ Enhanced search complete:', {
                    shown: searchResult.recipes.length,
                    totalAvailable: searchResult.totalAvailable,
                    hasMore: searchResult.hasMore,
                    totalEverShown: searchResult.shownCount,
                    usingIntelligentSearch: isIntelligentAvailable
                });
            }

        } catch (error) {
            console.error('❌ Search error details:', error);
            console.error('❌ Error message:', error.message);
            console.error('❌ Error stack:', error.stack);

            const errorMessage = {
                type: 'hungie',
                content: `I'm having trouble finding recipes right now. Error: ${error.message}. Please try again! 🍴`,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    // Helper function to analyze batch of recipes for intelligence summary
    const analyzeBatch = (recipes) => {
        if (!recipes || !Array.isArray(recipes) || recipes.length === 0) {
            return {
                easyCount: 0,
                onePotCount: 0,
                kidFriendlyCount: 0,
                leftoverFriendlyCount: 0,
                avgTimeMin: 0,
                quickCount: 0,
                pantryMatches: [],
                cuisineTypes: new Set(),
                mealRoles: new Set()
            };
        }

        const analysis = {
            easyCount: 0,
            onePotCount: 0,
            kidFriendlyCount: 0,
            leftoverFriendlyCount: 0,
            avgTimeMin: 0,
            quickCount: 0, // ≤30 min
            pantryMatches: [],
            cuisineTypes: new Set(),
            mealRoles: new Set()
        };

        recipes.forEach(recipe => {
            if (recipe.is_easy) analysis.easyCount++;
            if (recipe.is_one_pot) analysis.onePotCount++;
            if (recipe.kid_friendly) analysis.kidFriendlyCount++;
            if (recipe.leftover_friendly) analysis.leftoverFriendlyCount++;
            if (recipe.time_min && recipe.time_min <= 30) analysis.quickCount++;
            if (recipe.meal_role) analysis.mealRoles.add(recipe.meal_role);

            // Extract pantry matches from explanations
            if (recipe.explanations && hasPantryItems) {
                pantryItems.forEach(item => {
                    const itemName = typeof item === 'string' ? item : item.name;
                    if (itemName && recipe.explanations.toLowerCase().includes(itemName.toLowerCase())) {
                        if (!analysis.pantryMatches.includes(itemName)) {
                            analysis.pantryMatches.push(itemName);
                        }
                    }
                });
            }
        });

        // Calculate average time
        const recipesWithTime = recipes.filter(r => r.time_min);
        if (recipesWithTime.length > 0) {
            analysis.avgTimeMin = Math.round(
                recipesWithTime.reduce((sum, r) => sum + r.time_min, 0) / recipesWithTime.length
            );
        }

        return analysis;
    };

    // Helper function to render intelligent batch summary
    const renderBatchSummary = (searchResult, cleanSearchTerm, hasPantryItems, variationStrategy = null) => {
        // Handle both searchResult object and direct recipes array
        let recipes, totalAvailable, hasMore, metadata;
        
        if (Array.isArray(searchResult)) {
            // Direct recipes array (from chat)
            recipes = searchResult;
            totalAvailable = null;
            hasMore = false;
            metadata = null;
        } else {
            // SearchResult object (from search)
            ({ recipes, totalAvailable, hasMore, metadata } = searchResult);
        }

        // Safety check
        if (!recipes || recipes.length === 0) {
            return null;
        }

        const analysis = analyzeBatch(recipes);

        // Additional safety check after analysis
        if (!recipes || !Array.isArray(recipes) || recipes.length === 0) {
            return null;
        }

        let summary = '';

        // Add fallback notice if using standard search
        if (metadata && metadata.fallback_search_used) {
            summary += `🔄 Using standard search (session intelligence temporarily unavailable)\n\n`;
        }

        // Add variation message if this is a repeat search
        if (variationStrategy && variationStrategy.isRepeatSearch && variationStrategy.variationMessage) {
            summary += `🔄 ${variationStrategy.variationMessage}\n\n`;
        }

        summary += `Here are some great ${cleanSearchTerm} recipes I found for you! 🍴\n\n`;

        // Intelligent count summary with analysis
        const intelligentFeatures = [];
        if (analysis.easyCount > 0) intelligentFeatures.push(`${analysis.easyCount} easy`);
        if (analysis.onePotCount > 0) intelligentFeatures.push(`${analysis.onePotCount} one-pot`);
        if (analysis.quickCount > 0) intelligentFeatures.push(`${analysis.quickCount} ≤30 min`);
        if (analysis.kidFriendlyCount > 0) intelligentFeatures.push(`${analysis.kidFriendlyCount} kid-friendly`);

        summary += `📊 Showing ${recipes.length}`;
        if (totalAvailable && totalAvailable > recipes.length) {
            summary += ` of ${totalAvailable}`;
        }

        if (intelligentFeatures.length > 0) {
            summary += ` (${intelligentFeatures.join(', ')})`;
        }

        // Pantry intelligence
        if (hasPantryItems && analysis.pantryMatches.length > 0) {
            summary += `\n🥫 Pantry matched: ${analysis.pantryMatches.slice(0, 3).join(', ')}`;
            if (analysis.pantryMatches.length > 3) {
                summary += ` +${analysis.pantryMatches.length - 3} more`;
            }
        }

        // Time intelligence
        if (analysis.avgTimeMin > 0) {
            summary += `\n⏱️ Average cooking time: ${analysis.avgTimeMin} minutes`;
        }

        // Discovery encouragement
        if (hasMore) {
            summary += `\n\n💡 Search again for more ${cleanSearchTerm} variations!`;
        }

        return summary;
    };

    // Helper function to render recipe badges
    const renderRecipeBadges = (recipe) => {
        const badges = [];

        if (recipe.time_min && recipe.time_min <= 30) {
            badges.push({ text: '≤30 min', type: 'time', color: '#10b981' });
        } else if (recipe.time_min) {
            badges.push({ text: `${recipe.time_min} min`, type: 'time', color: '#6b7280' });
        }

        if (recipe.is_easy) {
            badges.push({ text: 'Easy', type: 'difficulty', color: '#3b82f6' });
        }

        if (recipe.is_one_pot) {
            badges.push({ text: 'One-pot', type: 'equipment', color: '#8b5cf6' });
        }

        if (recipe.kid_friendly) {
            badges.push({ text: 'Kid-friendly', type: 'audience', color: '#f59e0b' });
        }

        if (recipe.leftover_friendly) {
            badges.push({ text: 'Leftover-friendly', type: 'meal-prep', color: '#06b6d4' });
        }

        // Pantry matches
        if (recipe.explanations && hasPantryItems) {
            const matches = pantryItems.filter(item => {
                const itemName = typeof item === 'string' ? item : item.name;
                return itemName && recipe.explanations.toLowerCase().includes(itemName.toLowerCase());
            });
            if (matches.length > 0) {
                const matchNames = matches.map(item => typeof item === 'string' ? item : item.name);
                badges.push({
                    text: `Uses ${matchNames.slice(0, 2).join(', ')}${matchNames.length > 2 ? ` +${matchNames.length - 2}` : ''}`,
                    type: 'pantry',
                    color: '#dc2626'
                });
            }
        }

        return badges;
    };

    // Handle meal plan integration
    const handleAddToMealPlan = (recipe) => {
        setSelectedRecipeForMealPlan(recipe);
        setShowMealPlanPopover(true);
    };

    const handleMealPlanSubmit = async (day, mealType) => {
        if (onAddToMealPlan && selectedRecipeForMealPlan) {
            try {
                const result = await onAddToMealPlan(day, mealType, selectedRecipeForMealPlan);
                if (result.success !== false) {
                    // Show success message
                    const successMessage = {
                        type: 'hungie',
                        content: `✅ Added "${selectedRecipeForMealPlan.title}" to ${day} ${mealType}! You can view your meal plan in the sidebar.`,
                        timestamp: new Date()
                    };
                    setMessages(prev => [...prev, successMessage]);
                }
            } catch (error) {
                console.error('Error adding to meal plan:', error);
            }
        }
        setShowMealPlanPopover(false);
        setSelectedRecipeForMealPlan(null);
    };

    const handleMealPlanCancel = () => {
        setShowMealPlanModal(false);
        setSelectedRecipeForMealPlan(null);
        setSelectedDay('monday');
        setSelectedMeal('dinner');
    };

    // Helper function to check if pantry is sparse and suggest generation
    const checkSparsePantryAndSuggest = (results) => {
        const pantryCount = pantryItems?.length || 0;
        const hasViableRecipes = results && Array.isArray(results) && results.length > 0;

        // Consider pantry sparse if less than 5 items or no viable recipes found
        const isSparsePantry = pantryCount < 5 || !hasViableRecipes;

        if (isSparsePantry) {
            return {
                shouldSuggest: true,
                reason: pantryCount < 5 ? 'limited-ingredients' : 'no-matches',
                pantryCount: pantryCount
            };
        }

        return { shouldSuggest: false };
    };

    // Helper function to render sparse pantry suggestion
    const renderSparsePantrySuggestion = (sparsePantryInfo) => {
        const { reason, pantryCount } = sparsePantryInfo;

        const handleGenerateFromPantry = () => {
            const message = reason === 'limited-ingredients'
                ? `I only have ${pantryCount} ingredients. Can you suggest recipes using what I have and recommend what to buy?`
                : "I couldn't find good matches. Can you suggest recipes using my pantry items and what to buy?";

            handleSendMessage(message);
        };

        return (
            <div className="sparse-pantry-suggestion">
                <div className="suggestion-icon">🛒</div>
                <div className="suggestion-content">
                    <h4>
                        {reason === 'limited-ingredients'
                            ? 'Limited Ingredients Available'
                            : 'No Great Matches Found'}
                    </h4>
                    <p>
                        {reason === 'limited-ingredients'
                            ? `With only ${pantryCount} ingredients, let me suggest recipes and a shopping list.`
                            : 'Let me help you find recipes using your pantry items plus a few additions.'}
                    </p>
                    <button
                        className="generate-pantry-btn"
                        onClick={handleGenerateFromPantry}
                    >
                        Generate from Pantry + Shopping List
                    </button>
                </div>
            </div>
        );
    };

    // Helper function for flexible meal planning (future enhancement)
    const handleFlexibleMealPlan = (recipe, planType = 'standard') => {
        // Future implementation for flexible meal planning blocks
        // This will support:
        // - Custom time blocks (not just breakfast/lunch/dinner)
        // - Multi-day planning
        // - Flexible scheduling (e.g., "sometime this week")
        // - Batch cooking integration

        const flexibleOptions = {
            'custom-time': {
                label: 'Custom Time Block',
                description: 'Plan for specific times or custom blocks'
            },
            'batch-cook': {
                label: 'Batch Cooking',
                description: 'Plan for meal prep and batch cooking'
            },
            'flexible-week': {
                label: 'Flexible Week',
                description: 'Add to weekly rotation without specific day'
            },
            'leftovers': {
                label: 'Leftovers Planning',
                description: 'Plan for multiple meals from one recipe'
            }
        };

        // For now, use standard meal plan functionality
        // Future: Show modal with flexible planning options
        handleAddToMealPlan(recipe);
    };    // Handle action button clicks (refinement searches)
    const handleActionButtonClick = (action, currentQuery) => {
        const actions = {
            'quick': `${currentQuery} quick 30 minutes`,
            'one-pot': `${currentQuery} one pot`,
            'easy': `${currentQuery} easy`,
            'kid-friendly': `${currentQuery} kid friendly`,
            'different-cuisine': `different ${currentQuery} cuisine`,
            'pantry-only': `${currentQuery} using my pantry`
        };

        const newQuery = actions[action] || currentQuery;
        setInputMessage(newQuery);

        // Auto-send after a brief delay
        setTimeout(() => {
            sendMessage();
        }, 100);
    };

    // Handle suggestion chip clicks
    const handleSuggestionClick = (suggestion) => {
        setInputMessage(suggestion);
        // Auto-send the suggestion
        setTimeout(() => {
            sendMessage();
        }, 100);
    };

    // Handle enter key press
    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className={`chat-interface ${isCompact ? 'compact' : ''} ${isExtraCompact ? 'extra-compact' : ''}`}>
            {/* Chat Content */}
            <div className="chat-content">
                {/* Welcome Screen or Chat Messages */}
                {/* Welcome State */}
                {!hasStartedChat && (
                    <div className="welcome-section">
                        <div className="welcome-content">
                            <h1>What are you hungry for?</h1>
                            <p>Ask me anything about cooking! I can help you find recipes, suggest meal ideas, or work with what's in your pantry.</p>

                            <div className="suggestion-chips">
                                <span className="chip" onClick={() => handleSuggestionClick('Quick dinner ideas')}>Quick dinner ideas</span>
                                <span className="chip" onClick={() => handleSuggestionClick('Healthy lunch recipes')}>Healthy lunch recipes</span>
                                <span className="chip" onClick={() => handleSuggestionClick('Dessert for tonight')}>Dessert for tonight</span>
                                <span className="chip" onClick={() => handleSuggestionClick('Use what\'s in my fridge')}>Use what's in my fridge</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Chat Messages */}
                {hasStartedChat && (
                    <div className="chat-container">
                        <div className="chat-box">
                            {messages.map((msg, index) => (
                                <div key={index} className={`chat-message ${msg.type}`} style={{ whiteSpace: 'pre-line', marginBottom: msg.recipes && msg.recipes.length > 0 ? '10px' : undefined }}>
                                    {msg.content || msg.text}

                                    {/* Recipe list with enhanced badges and actions */}
                                    {msg.type === 'hungie' && msg.recipes && msg.recipes.length > 0 && (
                                        <div className="chat-recipe-dropdown">
                                            <div className="recipe-dropdown-list">
                                                <h2>Recipe Suggestions:</h2>

                                                {/* Batch Summary */}
                                                {(() => {
                                                    const userQuery = messages.find(m => m.type === 'user' && messages.indexOf(m) < index)?.content || '';
                                                    return renderBatchSummary(msg.recipes, userQuery, hasPantryItems);
                                                })()}

                                                {/* Action buttons for refinement */}
                                                <div className="recipe-action-buttons">
                                                    <button
                                                        className="action-btn"
                                                        onClick={() => handleActionButtonClick('quick', messages[index - 1]?.content || '')}
                                                        title="Show only quick recipes (≤30 min)"
                                                    >
                                                        ⚡ ≤30 min
                                                    </button>
                                                    <button
                                                        className="action-btn"
                                                        onClick={() => handleActionButtonClick('one-pot', messages[index - 1]?.content || '')}
                                                        title="Show only one-pot recipes"
                                                    >
                                                        🍲 One-pot
                                                    </button>
                                                    <button
                                                        className="action-btn"
                                                        onClick={() => handleActionButtonClick('easy', messages[index - 1]?.content || '')}
                                                        title="Show only easy recipes"
                                                    >
                                                        ✅ Easy
                                                    </button>
                                                    <button
                                                        className="action-btn"
                                                        onClick={() => handleActionButtonClick('different-cuisine', messages[index - 1]?.content || '')}
                                                        title="Try different cuisine variations"
                                                    >
                                                        🌍 Different cuisine
                                                    </button>
                                                    {hasPantryItems && (
                                                        <button
                                                            className="action-btn pantry-btn"
                                                            onClick={() => handleActionButtonClick('pantry-only', messages[index - 1]?.content || '')}
                                                            title="Use only pantry ingredients"
                                                        >
                                                            🥫 Pantry-only
                                                        </button>
                                                    )}
                                                </div>

                                                <ul>
                                                    {msg.recipes.slice(0, 5).map((recipe, rIdx) => {
                                                        const uniqueKey = `${recipe.id || 'recipe'}-${rIdx}`;
                                                        const badges = renderRecipeBadges(recipe);
                                                        return (
                                                            <li key={uniqueKey} className="enhanced-recipe-item">
                                                                <RecipeDropdown recipe={recipe} index={rIdx} />

                                                                {/* Recipe Intelligence Badges */}
                                                                {badges.length > 0 && (
                                                                    <div className="recipe-badges">
                                                                        {badges.map((badge, bIdx) => (
                                                                            <span
                                                                                key={bIdx}
                                                                                className={`recipe-badge badge-${badge.type}`}
                                                                                style={{ backgroundColor: badge.color }}
                                                                                title={badge.text}
                                                                            >
                                                                                {badge.text}
                                                                            </span>
                                                                        ))}
                                                                    </div>
                                                                )}

                                                                {/* Add to Meal Plan Button */}
                                                                <div className="recipe-meal-plan-actions">
                                                                    <button
                                                                        className="add-to-meal-plan-btn"
                                                                        onClick={() => handleAddToMealPlan(recipe)}
                                                                        title="Add to meal plan"
                                                                        disabled={!onAddToMealPlan}
                                                                    >
                                                                        📅 Add to Meal Plan
                                                                    </button>
                                                                </div>
                                                            </li>
                                                        );
                                                    })}
                                                </ul>

                                                {/* Post-result refinement chips */}
                                                <div className="post-result-chips">
                                                    <p className="refinement-prompt">Want to refine your results?</p>
                                                    <div className="refinement-chips">
                                                        <span
                                                            className="refinement-chip"
                                                            onClick={() => handleActionButtonClick('quick', messages.find(m => m.type === 'user' && messages.indexOf(m) < index)?.content || '')}
                                                        >
                                                            ⚡ Only ≤30 min
                                                        </span>
                                                        <span
                                                            className="refinement-chip"
                                                            onClick={() => handleActionButtonClick('easy', messages.find(m => m.type === 'user' && messages.indexOf(m) < index)?.content || '')}
                                                        >
                                                            ✅ Easy only
                                                        </span>
                                                        <span
                                                            className="refinement-chip"
                                                            onClick={() => handleActionButtonClick('different-cuisine', messages.find(m => m.type === 'user' && messages.indexOf(m) < index)?.content || '')}
                                                        >
                                                            🌍 Different cuisine
                                                        </span>
                                                        {hasPantryItems && (
                                                            <span
                                                                className="refinement-chip pantry-chip"
                                                                onClick={() => handleActionButtonClick('pantry-only', messages.find(m => m.type === 'user' && messages.indexOf(m) < index)?.content || '')}
                                                            >
                                                                🥫 Use pantry only
                                                            </span>
                                                        )}
                                                        <span
                                                            className="refinement-chip"
                                                            onClick={() => setInputMessage('show me something completely different')}
                                                        >
                                                            🎲 Surprise me
                                                        </span>
                                                    </div>
                                                </div>

                                                {/* Sparse Pantry Suggestion */}
                                                {(() => {
                                                    const sparsePantryInfo = checkSparsePantryAndSuggest(msg.recipes);
                                                    if (sparsePantryInfo.shouldSuggest && sparsePantryInfo.reason === 'limited-ingredients') {
                                                        return (
                                                            <div className="additional-suggestion">
                                                                {renderSparsePantrySuggestion(sparsePantryInfo)}
                                                            </div>
                                                        );
                                                    }
                                                    return null;
                                                })()}
                                            </div>
                                        </div>
                                    )}

                                    {/* Handle case where no recipes found - show sparse pantry suggestion */}
                                    {msg.type === 'hungie' && (!msg.recipes || msg.recipes.length === 0) && (
                                        <div className="no-results-container">
                                            {(() => {
                                                const sparsePantryInfo = checkSparsePantryAndSuggest([]);
                                                if (sparsePantryInfo.shouldSuggest) {
                                                    return renderSparsePantrySuggestion(sparsePantryInfo);
                                                }
                                                return (
                                                    <div className="no-results">
                                                        <div className="no-results-icon">🔍</div>
                                                        <p>No recipes found matching your criteria.</p>
                                                    </div>
                                                );
                                            })()}
                                        </div>
                                    )}
                                </div>
                            ))}

                            <div ref={messagesEndRef} />
                        </div>
                    </div>
                )}

                {/* Chat Input - Always at bottom */}
                <div className="chat-input-container">
                    {/* Pantry Status Indicator */}
                    {hasPantryItems && (
                        <div className="pantry-status-indicator">
                            🥫 Using your pantry ({pantryItems.length} items) for smarter recipe suggestions
                            <button
                                className="pantry-link"
                                onClick={() => setShowPantry(true)}
                                title="Manage your pantry"
                            >
                                Manage Pantry
                            </button>
                        </div>
                    )}

                    <div className="chat-input-row">
                        <div>
                            <textarea
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                onKeyDown={handleKeyPress}
                                placeholder="Ask me anything about cooking..."
                                disabled={isLoading}
                                rows="1"
                                style={{ resize: 'none', overflow: 'hidden' }}
                            />
                            <button
                                onClick={sendMessage}
                                disabled={isLoading || !inputMessage.trim()}
                                className="send-button"
                            >
                                {isLoading ? '⏳' : '➤'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Meal Plan Popover Modal */}
                {showMealPlanPopover && selectedRecipeForMealPlan && (
                    <div className="meal-plan-modal-overlay" onClick={handleMealPlanCancel}>
                        <div className="meal-plan-modal" onClick={e => e.stopPropagation()}>
                            <div className="modal-header">
                                <h3>Add to Meal Plan</h3>
                                <button className="modal-close" onClick={handleMealPlanCancel}>×</button>
                            </div>
                            <div className="modal-content">
                                <p className="recipe-name">{selectedRecipeForMealPlan.title}</p>
                                <div className="meal-plan-selector">
                                    <div className="day-selector">
                                        <label>Day:</label>
                                        <select id="day-select">
                                            <option value="Monday">Monday</option>
                                            <option value="Tuesday">Tuesday</option>
                                            <option value="Wednesday">Wednesday</option>
                                            <option value="Thursday">Thursday</option>
                                            <option value="Friday">Friday</option>
                                            <option value="Saturday">Saturday</option>
                                            <option value="Sunday">Sunday</option>
                                        </select>
                                    </div>
                                    <div className="meal-selector">
                                        <label>Meal:</label>
                                        <select id="meal-select">
                                            <option value="Breakfast">Breakfast</option>
                                            <option value="Lunch">Lunch</option>
                                            <option value="Dinner">Dinner</option>
                                            <option value="Snack">Snack</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div className="modal-actions">
                                <button className="cancel-btn" onClick={handleMealPlanCancel}>Cancel</button>
                                <button
                                    className="add-btn"
                                    onClick={() => {
                                        const day = document.getElementById('day-select').value;
                                        const meal = document.getElementById('meal-select').value;
                                        handleMealPlanSubmit(day, meal);
                                    }}
                                >
                                    Add to Plan
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Close chat-content div */}
            </div>
        </div>
    );
};

export default ChatInterface;
