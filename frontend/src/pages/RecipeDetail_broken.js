import React, { useState, useRef, useEffect } from 'react';
import { DndContext, closestCenter, DragOverlay } from '@dnd-kit/core';
import Debug from '../components/Debug';
import MealPlannerView from '../components/MealPlannerView';
import RecipeDropdown from '../components/RecipeDropdown';
import './RecipeDetail.css';
import { api } from '../utils/api';
import { analyzeUserQuery } from '../utils/IntentClassifier';
import { buildSmartQuery, executeSmartSearch, generateNoResultsMessage } from '../utils/SmartQueryBuilder';
import SessionMemoryManager from '../utils/SessionMemoryManager';

const RecipeDetail = () => {
  // --- Session Memory ---
  const [sessionMemory] = useState(() => new SessionMemoryManager());
  
  // --- Chat State ---
  const [messages, setMessages] = useState([
    {
      type: 'hungie',
      content: "Hello there! 👋 I'm Hungie, your personal chef assistant! What are you craving today? Tell me about your situation - are you looking for something quick, budget-friendly, healthy, or just want to try something new? Yes, Chef! 🍴",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  // --- Existing recipe detail state ---
  const [recipes, setRecipes] = useState([]);
  const [expandedRecipe, setExpandedRecipe] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [selectedRecipes, setSelectedRecipes] = useState([]);
  const [hasStartedChat, setHasStartedChat] = useState(false);
  const [isFormattingRecipe, setIsFormattingRecipe] = useState(false);
  const [formattedRecipes, setFormattedRecipes] = useState(new Map());
  const [suggestedItems, setSuggestedItems] = useState(new Set());
  const [lastRequestType, setLastRequestType] = useState(null);
  const [recipeAnalyses, setRecipeAnalyses] = useState(new Map());
  const [suggestedRecipes, setSuggestedRecipes] = useState([]);
  
  // NEW: Conversation flow state for enhanced chat experience
  const [conversationSuggestions, setConversationSuggestions] = useState([]);
  const [currentRecipeTypes, setCurrentRecipeTypes] = useState([]);
  const [detectedIngredients, setDetectedIngredients] = useState([]);
  const [conversationContext, setConversationContext] = useState({
    mainIngredient: null,
    preferredTypes: [],
    exploredCuisines: [],
    chatPhase: 'initial' // initial, exploring, refining, deciding
  });

  // NEW: Meal Planner State
  const [showMealPlanner, setShowMealPlanner] = useState(false);
  const [mealPlannerSearchResults, setMealPlannerSearchResults] = useState([]);

  // NEW: Drag and Drop State
  const [draggedRecipe, setDraggedRecipe] = useState(null);

  // --- Chat Scroll ---
  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ 
        behavior: "smooth",
        block: "end"
      });
    }, 100);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Additional scroll trigger when loading state changes
  useEffect(() => {
    if (!isLoading) {
      scrollToBottom();
    }
  }, [isLoading]);

  // Update meal planner search results when recipes change
  useEffect(() => {
    if (recipes.length > 0) {
      setMealPlannerSearchResults(recipes);
    }
  }, [recipes]);

  // Toggle meal planner visibility
  const toggleMealPlanner = () => {
    setShowMealPlanner(!showMealPlanner);
  };

  // --- Intent-based Success Messages ---
  const getIntentSuccessMessage = (queryAnalysis, recipeCount, searchPhase, variationStrategy = null) => {
    const { intent, context } = queryAnalysis;
    const { INTENT_TYPES } = require('../utils/IntentClassifier');
    
    // Handle variation messages
    if (variationStrategy && variationStrategy.isRepeatSearch) {
      if (variationStrategy.variationMessage) {
        return `${variationStrategy.variationMessage} Found ${recipeCount} new options! 🍴`;
      }
      return `I found ${recipeCount} different variations for you! 🍴`;
    }
    
    let message = `I found ${recipeCount} delicious recipes for you!`;
    
    switch (intent) {
      case INTENT_TYPES.COMPLETE_MEAL:
        if (context.mealType === 'side dishes' || context.mealType === 'side dish') {
          message = `Here are ${recipeCount} fantastic side dish options that would pair perfectly with your main course!`;
        } else if (context.mealType === 'appetizers' || context.mealType === 'appetizer') {
          message = `Perfect! I found ${recipeCount} appetizers that will get your meal started right!`;
        }
        break;
      case INTENT_TYPES.MEAL_PLANNING:
        message = `Great! I've got ${recipeCount} meal ideas that should work perfectly for your situation!`;
        break;
      case INTENT_TYPES.OCCASION_BASED:
        if (context.occasion) {
          message = `Excellent! Here are ${recipeCount} recipes perfect for ${context.occasion}!`;
        }
        break;
      case INTENT_TYPES.DIETARY_FILTERING:
        if (context.dietaryNeeds?.length > 0) {
          message = `Found ${recipeCount} delicious ${context.dietaryNeeds.join(' ')} recipes just for you!`;
        }
        break;
    }
    
    // Add search phase info for debugging (in development)
    if (searchPhase && searchPhase !== 'primary') {
      console.log(`🔍 Success achieved with ${searchPhase} search strategy`);
    }
    
    return `${message} 🍴`;
  };

  // --- Chat Send Message ---

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Start chat UI on first message
    if (!hasStartedChat) setHasStartedChat(true);

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);

    // Don't add user message to chat - only show AI responses

    try {
      // Build context for the AI
      const context = buildUserContext(userMessage, messages, suggestedItems);
      
      // Create conversational prompt
      const { prompt, requestType } = await createConversationalPrompt(userMessage, context);
      setLastRequestType(requestType);

      console.log('🤖 Sending to AI:', { prompt: prompt.substring(0, 200) + '...', requestType });

      // Send to AI chat system
      const response = await api.smartSearch(prompt, context.chatHistory);
      
      console.log('🤖 AI Response:', response);

      let aiMessage = {
        type: 'hungie',
        content: response.data?.response || response.chat_response || "I'm having trouble understanding that request. Can you try rephrasing it?",
        timestamp: new Date(),
        responseType: requestType
      };

      // For search requests, also try to find actual recipes
      if (requestType === 'search' && response.recipes && response.recipes.length > 0) {
        // Enhance recipes with AI formatting
        const enhancedRecipes = await Promise.all(
          response.recipes.slice(0, 5).map(async (recipe) => {
            try {
              return await formatRecipeWithAI(recipe);
            } catch (e) {
              console.error('Error formatting recipe:', e);
              return recipe;
            }
          })
        );

        aiMessage.recipes = enhancedRecipes;
        setRecipes(enhancedRecipes);
        setSuggestedRecipes(enhancedRecipes);
        
        // NEW: Generate conversation suggestions for AI response path
        if (response.recipe_types) {
          setCurrentRecipeTypes(response.recipe_types);
          generateConversationSuggestions(response.recipe_types, response.detected_ingredients, userMessage);
        }
        
        // Track detected ingredients for progressive discovery
        if (response.detected_ingredients) {
          setDetectedIngredients(prev => [...new Set([...prev, ...response.detected_ingredients])]);
        }
        
        // Update conversation context
        updateConversationContext(userMessage, response);
      } else if (requestType === 'search') {
        // If no recipes in AI response, use intelligent search system with session memory
        try {
          console.log('🧠 Using intelligent search system for:', userMessage);
          
          // Analyze user query with intent classification
          const queryAnalysis = analyzeUserQuery(userMessage);
          console.log('🧠 Query Analysis:', queryAnalysis);
          
          // Build smart query based on analysis and session memory
          const smartQuery = await buildSmartQuery(queryAnalysis, sessionMemory);
          console.log('🧠 Smart Query:', smartQuery);
          
          // Execute multi-phase intelligent search with session memory
          const searchResults = await executeSmartSearch(smartQuery, api.searchRecipes, sessionMemory);
          console.log('🧠 Search Results:', searchResults);
          
          if (searchResults.recipes && searchResults.recipes.length > 0) {
            // Deduplicate recipes by ID first, then by title
            const uniqueRecipes = [];
            const seenIds = new Set();
            const seenTitles = new Set();
            
            for (const recipe of searchResults.recipes) {
              const recipeId = recipe.id;
              const normalizedTitle = recipe.title?.toLowerCase().trim();
              
              // Skip if we've seen this exact ID before
              if (recipeId && seenIds.has(recipeId)) {
                continue;
              }
              
              // Skip if we've seen this exact title before
              if (normalizedTitle && seenTitles.has(normalizedTitle)) {
                continue;
              }
              
              // Add to our tracking sets
              if (recipeId) seenIds.add(recipeId);
              if (normalizedTitle) seenTitles.add(normalizedTitle);
              
              uniqueRecipes.push(recipe);
            }
            
            console.log(`🔍 Deduplication: ${searchResults.recipes.length} → ${uniqueRecipes.length} recipes`);
            
            // Only take the first 5 recipes for display
            const recipesToDisplay = uniqueRecipes.slice(0, 5);
            
            const enhancedRecipes = await Promise.all(
              recipesToDisplay.map(async (recipe) => {
                try {
                  return await formatRecipeWithAI(recipe);
                } catch (e) {
                  console.error('Error formatting recipe:', e);
                  return recipe;
                }
              })
            );

            aiMessage.recipes = enhancedRecipes;
            setRecipes(enhancedRecipes);
            setSuggestedRecipes(enhancedRecipes);
            
            // Record this search in session memory with ONLY displayed recipes
            sessionMemory.recordQuery(userMessage, queryAnalysis, searchResults, enhancedRecipes);
            
            // Generate context-aware success message with variation info
            const intentMessage = getIntentSuccessMessage(queryAnalysis, enhancedRecipes.length, searchResults.searchPhase, smartQuery.variationStrategy);
            aiMessage.content += `\n\n${intentMessage}`;
            
            // NEW: Generate conversation suggestions based on search results
            if (searchResults.recipe_types) {
              setCurrentRecipeTypes(searchResults.recipe_types);
              generateConversationSuggestions(searchResults.recipe_types, searchResults.detected_ingredients, userMessage);
            }
            
            // Track detected ingredients for progressive discovery
            if (searchResults.detected_ingredients) {
              setDetectedIngredients(prev => [...new Set([...prev, ...searchResults.detected_ingredients])]);
            }
            
            // Update conversation context
            updateConversationContext(userMessage, searchResults);
          } else {
            // Record query even for no results (but with empty displayed recipes)
            sessionMemory.recordQuery(userMessage, queryAnalysis, searchResults, []);
            
            // Generate intelligent no-results message with session context
            const noResultsMessage = generateNoResultsMessage(queryAnalysis, searchResults, sessionMemory);
            aiMessage.content += `\n\n${noResultsMessage}`;
          }
        } catch (searchError) {
          console.error('Intelligent search failed:', searchError);
          // Fallback to simple message
          aiMessage.content += `\n\nI'm having trouble searching right now. Try asking for specific ingredients like 'chicken', 'beef', or 'pasta'! 🍴`;
        }
      }

      setMessages(prev => [...prev, aiMessage]);
      
      // Force scroll to bottom after state update
      setTimeout(() => {
        scrollToBottom();
      }, 100);

    } catch (error) {
      console.error('Chat error:', error);
      
      // Fallback: try intelligent search directly
      try {
        console.log('🧠 Fallback: Using intelligent search system');
        
        // Analyze user query with intent classification
        const queryAnalysis = analyzeUserQuery(userMessage);
        console.log('🧠 Fallback Query Analysis:', queryAnalysis);
        
        // Build smart query based on analysis and session memory
        const smartQuery = await buildSmartQuery(queryAnalysis, sessionMemory);
        
        // Execute multi-phase intelligent search with session memory
        const searchResults = await executeSmartSearch(smartQuery, api.searchRecipes, sessionMemory);
        
        if (searchResults.recipes && searchResults.recipes.length > 0) {
          // Deduplicate recipes by ID first, then by title
          const uniqueRecipes = [];
          const seenIds = new Set();
          const seenTitles = new Set();
          
          for (const recipe of searchResults.recipes) {
            const recipeId = recipe.id;
            const normalizedTitle = recipe.title?.toLowerCase().trim();
            
            // Skip if we've seen this exact ID before
            if (recipeId && seenIds.has(recipeId)) {
              continue;
            }
            
            // Skip if we've seen this exact title before
            if (normalizedTitle && seenTitles.has(normalizedTitle)) {
              continue;
            }
            
            // Add to our tracking sets
            if (recipeId) seenIds.add(recipeId);
            if (normalizedTitle) seenTitles.add(normalizedTitle);
            
            uniqueRecipes.push(recipe);
          }
          
          console.log(`🔍 Deduplication: ${searchResults.recipes.length} → ${uniqueRecipes.length} recipes`);
          
          // Only take the first 5 recipes for display
          const recipesToDisplay = uniqueRecipes.slice(0, 5);
          
          const enhancedRecipes = await Promise.all(
            recipesToDisplay.map(async (recipe) => {
              try {
                return await formatRecipeWithAI(recipe);
              } catch (e) {
                console.error('Error formatting recipe:', e);
                return recipe;
              }
            })
          );

          // Record this search in session memory with ONLY displayed recipes
          sessionMemory.recordQuery(userMessage, queryAnalysis, searchResults, enhancedRecipes);

          const intentMessage = getIntentSuccessMessage(queryAnalysis, enhancedRecipes.length, searchResults.searchPhase, smartQuery.variationStrategy);
          const fallbackMessage = {
            type: "hungie",
            content: `${intentMessage} 🍳`,
            timestamp: new Date(),
            recipes: enhancedRecipes,
            responseType: 'search'
          };
          
          setMessages(prev => [...prev, fallbackMessage]);
          setRecipes(enhancedRecipes);
          setSuggestedRecipes(enhancedRecipes);
          
          // NEW: Generate conversation suggestions for fallback results
          if (searchResults.recipe_types) {
            setCurrentRecipeTypes(searchResults.recipe_types);
            generateConversationSuggestions(searchResults.recipe_types, searchResults.detected_ingredients, userMessage);
          }
          
          // Track detected ingredients for progressive discovery
          if (searchResults.detected_ingredients) {
            setDetectedIngredients(prev => [...new Set([...prev, ...searchResults.detected_ingredients])]);
          }
          
          // Update conversation context
          updateConversationContext(userMessage, searchResults);
        } else {
          // Record query even for no results (but with empty displayed recipes)
          sessionMemory.recordQuery(userMessage, queryAnalysis, searchResults, []);
          
          // Generate intelligent no-results message with session context
          const noResultsMessage = generateNoResultsMessage(queryAnalysis, searchResults, sessionMemory);
          const fallbackMessage = {
            type: "hungie",
            content: noResultsMessage,
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, fallbackMessage]);
        }
      } catch (fallbackError) {
        console.error('All search methods failed:', fallbackError);
        const fallbackMessage = {
          type: "hungie",
          content: "Oops! I'm having some technical difficulties, but I'm still eager to help! 😅 What are you looking to cook today? Yes, Chef! 🍴",
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, fallbackMessage]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // AI Chef Inspection - formats recipe before serving
  const formatRecipeWithAI = async (recipe) => {
    const recipeId = recipe.id;
    
    // Check if we already have a formatted version
    if (formattedRecipes.has(recipeId)) {
      return formattedRecipes.get(recipeId);
    }
    
    // Check if the recipe needs formatting (has messy data)
    const needsFormatting = (
      (recipe.ingredients && typeof recipe.ingredients === 'string' && 
       (recipe.ingredients.includes('INGREDIENTS') || recipe.ingredients.includes('DIRECTIONS') ||
        recipe.ingredients.match(/\b(In large bowl|Whisk|Stir|Pour)\b/i) ||
        recipe.ingredients.length > 1500)) ||
      (recipe.instructions && typeof recipe.instructions === 'string' && 
       (recipe.instructions.includes('INGREDIENTS') || 
        recipe.instructions.match(/\b(cups?|tbsp|tsp|oz|lbs)\s+\w+/i) ||
        recipe.instructions.length > 2500))
    );
    
    if (!needsFormatting) {
      // Recipe is already clean, cache it and return
      setFormattedRecipes(prev => new Map(prev.set(recipeId, recipe)));
      return recipe;
    }
    
    try {
      setIsFormattingRecipe(true);
      // AI Chef Inspection - clean up the recipe
      const response = await api.formatRecipe({
        title: recipe.title,
        ingredients: recipe.ingredients,
        instructions: recipe.instructions
      });
      // Parse the AI response to extract formatted ingredients and instructions
      let formattedIngredients = recipe.ingredients;
      let formattedInstructions = recipe.instructions;
      if (response && response.chat_response) {
        const aiResponse = response.chat_response;
        console.log('AI Response:', aiResponse); // Debug log
        // Extract ingredients section - look for INGREDIENTS: header
        const ingredientsMatch = aiResponse.match(/INGREDIENTS?:?\s*\n(.*?)(?:\n\s*INSTRUCTIONS?:|$)/is);
        if (ingredientsMatch) {
          const extractedIngredients = ingredientsMatch[1].trim()
            .split('\n')
            .filter(line => line.trim() && !line.match(/^(ingredients?|instructions?|directions?):?\s*$/i))
            .map(line => line.replace(/^[\-\*•]\s*/, '').trim())
            .filter(line => line.length > 2);
          // Only use AI ingredients if we got a reasonable number and they have measurements
          if (extractedIngredients.length >= 3 && 
              extractedIngredients.some(ing => ing.match(/\d+/) || ing.includes('cup') || ing.includes('tbsp') || ing.includes('tsp'))) {
            formattedIngredients = extractedIngredients;
            console.log('Using AI-formatted ingredients:', extractedIngredients);
          } else {
            console.log('AI ingredients failed validation, using original');
          }
        }
        // Extract instructions section - look for INSTRUCTIONS: header
        const instructionsMatch = aiResponse.match(/INSTRUCTIONS?:?\s*\n(.*?)$/is);
        if (instructionsMatch) {
          const extractedInstructions = instructionsMatch[1].trim()
            .split('\n')
            .filter(line => line.trim() && !line.match(/^(ingredients?|instructions?|directions?):?\s*$/i))
            .map((line, index) => line.replace(/^\d+\.\s*/, '').trim())
            .filter(line => line.length > 15);
          // Only use AI instructions if we got reasonable content
          if (extractedInstructions.length >= 2) {
            formattedInstructions = extractedInstructions;
            console.log('Using AI-formatted instructions:', extractedInstructions);
          } else {
            console.log('AI instructions failed validation, using original');
          }
        }
      }
      const formattedRecipe = {
        ...recipe,
        ingredients: formattedIngredients,
        instructions: formattedInstructions,
        formatted_by_ai: true
      };
      // Cache the formatted recipe
      setFormattedRecipes(prev => new Map(prev.set(recipeId, formattedRecipe)));
      return formattedRecipe;
    } catch (error) {
      console.error('AI formatting failed:', error);
      // Fallback to original recipe
      setFormattedRecipes(prev => new Map(prev.set(recipeId, recipe)));
      return recipe;
    } finally {
      setIsFormattingRecipe(false);
    }
  };

  // Recipe analysis function
  const analyzeRecipe = async (recipeId) => {
    if (recipeAnalyses.has(recipeId)) {
      return recipeAnalyses.get(recipeId);
    }

    try {
      const analysis = await api.analyzeRecipe(recipeId);
      if (analysis.success) {
        setRecipeAnalyses(prev => new Map(prev.set(recipeId, analysis.data)));
        return analysis.data;
      }
    } catch (error) {
      console.error('Error analyzing recipe:', error);
    }
    return null;
  };

  // Toggle suggestion status for ingredients/instructions
  const toggleSuggestion = (type, content, recipeId) => {
    const itemKey = `${recipeId}-${type}-${content.substring(0, 50)}`;
    setSuggestedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemKey)) {
        newSet.delete(itemKey);
      } else {
        newSet.add(itemKey);
      }
      return newSet;
    });
  };

  // Build rich user context for conversational AI
  const buildUserContext = (currentInput, chatHistory, selectedItems) => {
    // Extract selected ingredients with their recipe context
    const selectedIngredients = Array.from(selectedItems)
      .filter(key => key.includes('-ingredient-'))
      .map(key => {
        const parts = key.split('-ingredient-');
        if (parts.length === 2) {
          const recipeId = parts[0];
          const ingredient = parts[1] ? parts[1].substring(0, 50) : '';
          
          // Find the recipe this ingredient belongs to
          const recipe = recipes.find(r => r.id === recipeId || r.id === parseInt(recipeId));
          const recipeTitle = recipe ? recipe.title : `Recipe ${recipeId}`;
          
          return {
            ingredient: ingredient,
            recipeId: recipeId,
            recipeTitle: recipeTitle,
            recipe: recipe
          };
        }
        return null;
      })
      .filter(item => item && item.ingredient.length > 0);

    const selectedRecipes = Array.from(selectedItems)
      .filter(key => key.includes('recipe-'))
      .map(key => {
        const recipeId = key.replace('recipe-', '');
        // Find recipe title from current recipes state
        const recipe = recipes.find(r => r.id === recipeId || r.id === parseInt(recipeId));
        return recipe ? recipe.title : `Recipe ${recipeId}`;
      });

    // Analyze chat history for dietary preferences and cooking patterns
    const chatText = chatHistory.map(msg => (msg.content || msg.text || '').toLowerCase()).join(' ');
    const dietaryPreferences = [];
    
    if (chatText.includes('vegetarian') || chatText.includes('veggie')) dietaryPreferences.push('vegetarian');
    if (chatText.includes('vegan')) dietaryPreferences.push('vegan');
    if (chatText.includes('gluten-free') || chatText.includes('gluten free')) dietaryPreferences.push('gluten-free');
    if (chatText.includes('dairy-free') || chatText.includes('dairy free')) dietaryPreferences.push('dairy-free');
    if (chatText.includes('keto') || chatText.includes('ketogenic')) dietaryPreferences.push('keto');
    if (chatText.includes('paleo')) dietaryPreferences.push('paleo');
    if (chatText.includes('low carb') || chatText.includes('low-carb')) dietaryPreferences.push('low-carb');

    // Detect cooking time preferences
    const timePreferences = [];
    if (chatText.includes('quick') || chatText.includes('fast') || chatText.includes('30 min')) timePreferences.push('quick');
    if (chatText.includes('slow') || chatText.includes('long') || chatText.includes('weekend')) timePreferences.push('slow-cooking');

    // Detect mood/occasion
    const moodContext = [];
    if (chatText.includes('cozy') || chatText.includes('comfort')) moodContext.push('comfort food');
    if (chatText.includes('healthy') || chatText.includes('light')) moodContext.push('healthy');
    if (chatText.includes('party') || chatText.includes('entertaining')) moodContext.push('entertaining');
    if (chatText.includes('romantic') || chatText.includes('date')) moodContext.push('romantic');

    return {
      chatHistory: chatHistory.map(msg => `${msg.type}: ${msg.content || msg.text || ''}`).join('\n'),
      selectedIngredients,
      selectedRecipes,
      dietaryPreferences,
      timePreferences,
      moodContext,
      currentInput
    };
  };

  // Let AI classify the request type instead of hardcoded patterns
  const classifyRequestWithAI = async (userInput, context) => {
    const classificationPrompt = `CLASSIFICATION TASK: Analyze the user request and respond with ONLY one word.

User request: "${userInput}"

RESPOND WITH ONLY ONE OF THESE WORDS:
- recipe_search (if user wants to find recipes/dishes to cook)
- ingredient_advice (if user wants substitutions/alternatives for ingredients)  
- cooking_advice (if user wants cooking tips/techniques/general guidance)

Examples:
"I want to make chicken" → recipe_search
"I don't eat butter, what can I use instead?" → ingredient_advice
"How can I make this more exciting?" → cooking_advice
"What's a good recipe for dinner?" → recipe_search
"I'm allergic to nuts, what can I substitute?" → ingredient_advice
"Any tips for better flavor?" → cooking_advice
"How do I make food taste better?" → cooking_advice

RESPOND WITH ONLY THE CATEGORY NAME. NO OTHER TEXT.`;

    // List of common food/ingredient words
    const foodWords = [
      'chicken','beef','pork','fish','salmon','shrimp','tofu','egg','eggs','cheese','pasta','noodle','noodles','rice','potato','potatoes','carrot','carrots','broccoli','beans','lentil','lentils','soup','stew','curry','sandwich','salad','bacon','steak','burger','turkey','lamb','duck','sausage','mushroom','mushrooms','onion','garlic','tomato','tomatoes','pepper','peppers','zucchini','squash','spinach','kale','quinoa','oats','oatmeal','pancake','waffle','pizza','pie','cake','cookie','cookies','brownie','brownies','dessert','breakfast','lunch','dinner','snack','snacks','meal','meals','dish','dishes','recipe','recipes','bake','baked','roast','roasted','grill','grilled','fry','fried','stir fry','stir-fry','casserole','wrap','wraps','taco','tacos','enchilada','enchiladas','burrito','burritos','salsa','guacamole','hummus','falafel','shawarma','sushi','ramen','pho','bibimbap','kimchi','cabbage','coleslaw','lasagna','spaghetti','macaroni','cheddar','mozzarella','parmesan','brie','gouda','swiss','provolone','ricotta','cream','yogurt','milk','butter','bread','roll','rolls','bagel','bagels','croissant','croissants','toast','muffin','muffins','scone','scones','biscuit','biscuits','jam','jelly','honey','syrup','maple','granola','bar','bars','nut','nuts','almond','almonds','walnut','walnuts','pecan','pecans','cashew','cashews','peanut','peanuts','hazelnut','hazelnuts','pistachio','pistachios','seed','seeds','chia','flax','sunflower','pumpkin','sesame','coconut','apple','apples','banana','bananas','orange','oranges','lemon','lemons','lime','limes','grape','grapes','pear','pears','peach','peaches','plum','plums','cherry','cherries','berry','berries','strawberry','strawberries','blueberry','blueberries','raspberry','raspberries','blackberry','blackberries','melon','melons','watermelon','cantaloupe','honeydew','pineapple','kiwi','mango','mangoes','papaya','pomegranate','apricot','apricots','fig','figs','date','dates','raisin','raisins','currant','currants','passionfruit','guava','starfruit','dragonfruit','lychee','jackfruit','durian','olive','olives','avocado','avocados','artichoke','artichokes','asparagus','beet','beets','bok choy','brussels sprout','brussels sprouts','cauliflower','celery','chard','collard','corn','cucumber','eggplant','endive','fennel','leek','lettuce','okra','parsnip','pea','peas','radish','radishes','rutabaga','turnip','turnips','watercress','yam','yams','zucchini','herb','herbs','spice','spices','basil','cilantro','parsley','dill','oregano','rosemary','sage','thyme','mint','chive','chives','tarragon','marjoram','bay leaf','bay leaves','coriander','cumin','curry','paprika','turmeric','saffron','cinnamon','clove','cloves','nutmeg','allspice','anise','cardamom','caraway','fennel','ginger','mace','mustard','peppercorn','sumac','vanilla','wasabi','zaatar','zest','zests','zatar','sambal','sriracha','tabasco','tamari','teriyaki','vinegar','worcestershire','yuzu','zest','zests','zatar','sambal','sriracha','tabasco','tamari','teriyaki','vinegar','worcestershire','yuzu'
    ];

    try {
      const response = await api.smartSearch(classificationPrompt, { skipRecipeSearch: true }, { skipRecipeSearch: true });
      const classification = response?.chat_response?.toLowerCase?.().trim() || '';
      
      // Enhanced debugging
      console.log('🤖 AI Classification Debug:', {
        originalInput: userInput,
        classificationPrompt: classificationPrompt.substring(0, 200) + '...',
        aiResponse: response?.chat_response,
        extractedClassification: classification,
        contains_ingredient_advice: classification.includes('ingredient_advice'),
        contains_cooking_advice: classification.includes('cooking_advice'),
        contains_recipe_search: classification.includes('recipe_search')
      });
      
      // More precise matching
      if (classification === 'ingredient_advice' || classification.includes('ingredient_advice')) return 'advice';
      if (classification === 'cooking_advice' || classification.includes('cooking_advice')) return 'advice';
      if (classification === 'recipe_search' || classification.includes('recipe_search')) return 'search';

      // If the AI returns something unexpected, fallback to keyword logic below
    } catch (error) {
      console.error('AI classification failed, using fallback logic:', error);
    }

    // Fallback to improved keyword detection
    const inputLower = userInput.toLowerCase();
    // Advice keywords
    if (
      inputLower.includes('substitute') ||
      inputLower.includes("don't eat") ||
      inputLower.includes('allergic') ||
      inputLower.includes('alternative') ||
      inputLower.includes('better') ||
      inputLower.includes('flavor') ||
      inputLower.includes('taste') ||
      inputLower.includes('tips') ||
      inputLower.includes('how do i')
    ) {
      return 'advice';
    }

    // If the input contains a food word, treat as recipe search
    if (foodWords.some(word => inputLower.includes(word))) {
      return 'search';
    }

    // Default fallback
    return 'search';
  };

  // Create conversational prompt for the AI
  const createConversationalPrompt = async (userInput, context) => {
    // Let AI determine the request type
    const requestType = await classifyRequestWithAI(userInput, context);
    
    if (requestType === 'advice') {
      let advicePrompt = `You are Hungie, a creative and enthusiastic personal chef assistant. The user is asking for cooking advice, ingredient substitutions, or culinary guidance - NOT recipe searches.

IMPORTANT: Do NOT search for or suggest new recipes. Instead, provide specific advice, tips, and guidance.

User's request: "${userInput}"

Context about the user:`;

      if (context.selectedRecipes.length > 0) {
        advicePrompt += `\n- They're currently interested in: ${context.selectedRecipes.join(', ')}`;
      }

      if (context.selectedIngredients.length > 0) {
        const ingredientContext = context.selectedIngredients.map(item => 
          `${item.ingredient} (from "${item.recipeTitle}")`
        ).join(', ');
        advicePrompt += `\n- Selected ingredients: ${ingredientContext}`;
      }

      if (context.dietaryPreferences.length > 0) {
        advicePrompt += `\n- Dietary preferences: ${context.dietaryPreferences.join(', ')}`;
      }

      if (context.chatHistory) {
        const recentChat = context.chatHistory.split('\n').slice(-6).join('\n');
        advicePrompt += `\n- Recent conversation: ${recentChat}`;
      }

      advicePrompt += `\n\nPlease provide helpful cooking advice such as:
- Ingredient substitutions and alternatives
- Cooking techniques and tips
- Flavor enhancement suggestions
- Kitchen hacks and shortcuts
- Creative modifications to existing dishes

Respond conversationally with specific, actionable advice. Be enthusiastic and explain WHY your suggestions work!`;

      return { prompt: advicePrompt, requestType: 'advice' };
    } else {
      // This is a recipe search request
      let recipePrompt = `You are Hungie, a friendly and enthusiastic personal chef assistant. The user is looking for recipe suggestions.

IMPORTANT: Do NOT invent or create new recipes. Focus on providing conversational responses about recipes that will be found from the database search.

User's request: "${userInput}"

Context about the user:`;

      if (context.selectedIngredients.length > 0) {
        const ingredientContext = context.selectedIngredients.map(item => 
          `${item.ingredient} (from "${item.recipeTitle}")`
        ).join(', ');
        recipePrompt += `\n- They have these ingredients available: ${ingredientContext}`;
      }

      if (context.selectedRecipes.length > 0) {
        recipePrompt += `\n- They've shown interest in these recipes: ${context.selectedRecipes.join(', ')}`;
      }

      if (context.dietaryPreferences.length > 0) {
        recipePrompt += `\n- Dietary preferences: ${context.dietaryPreferences.join(', ')}`;
      }

      if (context.timePreferences.length > 0) {
        recipePrompt += `\n- Cooking time preference: ${context.timePreferences.join(', ')}`;
      }

      if (context.moodContext.length > 0) {
        recipePrompt += `\n- Cooking mood/occasion: ${context.moodContext.join(', ')}`;
      }

      if (context.chatHistory) {
        const recentChat = context.chatHistory.split('\n').slice(-4).join('\n');
        recipePrompt += `\n- Previous conversation: ${recentChat}`;
      }

      recipePrompt += `\n\nPlease respond conversationally about their request. Be enthusiastic and helpful, but follow these STRICT rules:

CRITICAL: Do NOT mention specific recipe names or invent recipes. Instead:
- Acknowledge their request warmly
- Describe the type of recipes you'll look for
- Mention general characteristics (quick, healthy, etc.)
- Let them know you're searching for actual recipes
- Keep it brief and conversational

EXAMPLE: "Great choice! I'll find some delicious beef recipes for you. Looking for options that are both quick and healthy... let me search our database!"

Do NOT use numbered lists or mention specific recipe names that don't exist in our database.`;

      return { prompt: recipePrompt, requestType: 'search' };
    }
  };
  const formatIngredients = (ingredients) => {
    if (!ingredients) return [];
    
    let ingredientList = [];
    
    // Handle different input types
    if (Array.isArray(ingredients)) {
      // Already an array - process each item
      ingredientList = ingredients.map(item => {
        if (typeof item === 'object' && item !== null) {
          // If it's an object, try to extract meaningful text
          return item.text || item.name || item.ingredient || JSON.stringify(item);
        }
        return String(item);
      });
    } else if (typeof ingredients === 'string') {
      try {
        // Try to parse as JSON first
        const parsed = JSON.parse(ingredients);
        if (Array.isArray(parsed)) {
          ingredientList = parsed.map(item => {
            if (typeof item === 'object' && item !== null) {
              return item.text || item.name || item.ingredient || String(item);
            }
            return String(item);
          });
        } else {
          // If not JSON, split by newlines
          ingredientList = ingredients.split(/\n+/).filter(line => line.trim().length > 0);
        }
      } catch (e) {
        // If JSON parsing fails, split by newlines and clean up
        let rawText = ingredients
          .replace(/INGREDIENTS/gi, '') // Remove section headers
          .replace(/DIRECTIONS/gi, '') // Remove direction headers that got mixed in
          .replace(/In large bowl,.*$/gi, '') // Remove instruction text that got mixed in
          .replace(/In saucepan,.*$/gi, '') // Remove instruction text
          .replace(/Turn out onto.*$/gi, '') // Remove instruction text
          .replace(/Cover loosely.*$/gi, '') // Remove instruction text
          .replace(/\b(Whisk|Stir|Pour|Divide|Remove)\b.*$/gim, '') // Remove sentences starting with cooking verbs
        
        ingredientList = rawText.split(/\n+/).filter(line => {
          const trimmed = line.trim();
          // Filter out empty lines and lines that look like instructions
          return trimmed.length > 0 && 
                 !trimmed.match(/^(In|Whisk|Stir|Pour|Divide|Remove|Turn|Cover|Let|Sprinkle)/i) &&
                 !trimmed.match(/minutes\.?\s*$/i) &&
                 !trimmed.match(/until\s+/i);
        });
      }
    } else if (Array.isArray(ingredients)) {
      ingredientList = ingredients;
    }
    
    // Smart combining logic for fragmented ingredients
    const combinedIngredients = [];
    let currentIngredient = '';
    
    for (let i = 0; i < ingredientList.length; i++) {
      const item = String(ingredientList[i]).trim();
      
      // Skip empty items and instruction-like content
      if (!item || 
          item.match(/^(In|Whisk|Stir|Pour|Divide|Remove|Turn|Cover|Let|Sprinkle)/i) ||
          item.match(/minutes\.?\s*$/i) ||
          item.match(/until\s+/i) ||
          item.length < 3) continue;
      
      // More precise patterns for detecting new ingredients
      const startsWithMeasurement = /^(\d+\/?\d*|\d*\.?\d+|½|¼|¾|⅓|⅔|⅛|⅜|⅝|⅞)\s*(cups?|tbsp|tsp|tablespoons?|teaspoons?|g|kg|lbs?|pounds?|oz|ounces?|ml|l|liters?|gallons?|quarts?|pints?|each|whole|large|medium|small|cloves?|slices?|pieces?|inch|inches|cm|mm|pkg|packages?)/i.test(item);
      const startsWithCount = /^(\d+\/?\d*|\d*\.?\d+|½|¼|¾|⅓|⅔|⅛|⅜|⅝|⅞)\s+/i.test(item);
      const isParenthetical = /^\([^)]*\)$/.test(item);
      const isConnector = /^(and|or)\s+/i.test(item);
      const endsIncomplete = /(\([\d\-\/\s]*$|[\d\-\/\s]+$|,\s*$)/i.test(currentIngredient);
      const continuesIncomplete = /^([\d\-\/\s\)]+|cm|mm|inch|inches)/i.test(item);
      
      // Check if this looks like a measurement fragment that got split
      const isMeasurementFragment = /^(cups?|tbsp|tsp|tablespoons?|teaspoons?|g|kg|lbs?|pounds?|oz|ounces?|ml|l|liters?|each|whole|large|medium|small|cloves?)$/i.test(item);
      
      // Check if this is likely a continuation of a food item (not a measurement)
      const isFoodContinuation = /^(chocolate|butter|cream|sugar|flour|oil|milk|cheese|meat|chicken|beef|pork|fish|salmon|bread|rice|pasta|noodles|sauce|dressing|vinegar|honey|vanilla|cinnamon|salt|pepper|herbs?|spices?|nuts?|almonds?|walnuts?|pecans?)([,\s].*)?$/i.test(item);
      
      if (currentIngredient === '') {
        // Starting a new ingredient
        currentIngredient = item;
      } else if (isMeasurementFragment && !currentIngredient.match(/\b(cups?|tbsp|tsp|tablespoons?|teaspoons?|g|kg|lbs?|pounds?|oz|ounces?|ml|l|liters?)\b/i)) {
        // This is a measurement unit that belongs to the previous ingredient
        currentIngredient += ' ' + item;
      } else if (isFoodContinuation && currentIngredient.match(/\d+/)) {
        // This looks like the food part of an ingredient that got split - if current ingredient has any number, combine
        currentIngredient += ' ' + item;
      } else if (endsIncomplete && continuesIncomplete) {
        // Previous ingredient has incomplete measurement, continue it
        currentIngredient += ' ' + item;
      } else if (currentIngredient.endsWith(',') && !startsWithMeasurement && !startsWithCount) {
        // Previous ingredient ended with a comma, this is likely a continuation
        currentIngredient += ' ' + item;
      } else if (item.length <= 15 && !startsWithMeasurement && !startsWithCount && currentIngredient.match(/\d+/)) {
        // If this is a short word/phrase and doesn't start with measurement, and current ingredient has a number, combine it
        currentIngredient += ' ' + item;
      } else if ((startsWithMeasurement || startsWithCount) && !isConnector) {
        // This definitely looks like a new ingredient with measurement
        if (currentIngredient.length > 0) {
          combinedIngredients.push(currentIngredient.replace(/^[•\-*]\s*/, ''));
        }
        currentIngredient = item;
      } else if (isParenthetical) {
        // Parenthetical info belongs to previous ingredient
        currentIngredient += ' ' + item;
      } else {
        // Check if this might be a continuation
        const prevItem = currentIngredient.toLowerCase();
        const currentItem = item.toLowerCase();
        
        // If the previous ingredient doesn't end with a complete word and this doesn't start with a measurement, combine
        if (!startsWithMeasurement && !startsWithCount && (
          prevItem.endsWith('each') || 
          prevItem.endsWith('ground') || 
          prevItem.endsWith('and') ||
          prevItem.endsWith('or') ||
          prevItem.endsWith('square') ||
          prevItem.endsWith('(6-inch/') ||
          prevItem.endsWith('spring roll') ||
          prevItem.endsWith('roll') ||
          prevItem.endsWith('finely') ||
          prevItem.endsWith('coarsely') ||
          prevItem.endsWith('roughly') ||
          prevItem.endsWith('thinly') ||
          prevItem.endsWith('thickly') ||
          currentItem.startsWith('and') ||
          currentItem.startsWith('or') ||
          currentItem.startsWith('grated') ||
          currentItem.startsWith('minced') ||
          currentItem.startsWith('fresh') ||
          currentItem.startsWith('chopped') ||
          currentItem.startsWith('diced') ||
          currentItem.startsWith('sliced') ||
          currentItem.startsWith('wrappers') ||
          currentItem.startsWith('sheets') ||
          currentItem.startsWith('slices') ||
          currentItem.startsWith('pieces') ||
          currentItem.match(/^\d+\s*cm/) ||
          // Check if current item is just a food type/descriptor without measurement
          (currentItem.match(/^(wrappers?|sheets?|slices?|pieces?|leaves?|strips?|rounds?|halves?|quarters?|diced?|chopped?|minced?|sliced?|flour|sugar|salt|milk|butter|water|oil|eggs?)$/))
        )) {
          currentIngredient += ' ' + item;
        } else {
          // This looks like a new ingredient
          if (currentIngredient.length > 0) {
            combinedIngredients.push(currentIngredient.replace(/^[•\-*]\s*/, ''));
          }
          currentIngredient = item;
        }
      }
    }
    
    // Add the last ingredient
    if (currentIngredient) {
      combinedIngredients.push(currentIngredient.replace(/^[•\-*]\s*/, ''));
    }
    
    // Clean up page references and extra spaces from all ingredients
    const finalIngredients = combinedIngredients.map(ingredient => 
      ingredient
        .replace(/\(see tip,?\s*page\s*\d+\)/gi, '') // Remove page references like "(see tip, page 27)"
        .replace(/\(see\s*page\s*\d+\)/gi, '') // Remove simple page references like "(see page 27)"
        .replace(/\(tip,?\s*page\s*\d+\)/gi, '') // Remove tip references like "(tip, page 27)"
        .replace(/\s+/g, ' ') // Clean up extra spaces
        .trim()
    );
    
    // Remove duplicates
    const uniqueIngredients = [];
    const seen = new Set();
    
    for (const ingredient of finalIngredients) {
      if (!ingredient || ingredient.length < 3) continue;
      
      const duplicateKey = ingredient.substring(0, 50).toLowerCase();
      if (!seen.has(duplicateKey)) {
        seen.add(duplicateKey);
        uniqueIngredients.push(ingredient);
      }
    }
    
    return uniqueIngredients;
  };

  // Function to format instructions as numbered steps
  const formatInstructions = (instructions) => {
    if (!instructions) return [];
    
    let instructionList = [];
    
    console.log('🔍 Debug instructions input:', { type: typeof instructions, value: instructions });
    
    // Handle different input types
    if (Array.isArray(instructions)) {
      // Already an array - process each item
      instructionList = instructions.map(item => {
        if (typeof item === 'object' && item !== null) {
          // If it's an object, try to extract meaningful text
          return item.text || item.instruction || item.step || JSON.stringify(item);
        }
        return String(item);
      });
    } else if (typeof instructions === 'string') {
      try {
        // Try to parse as JSON first
        const parsed = JSON.parse(instructions);
        if (Array.isArray(parsed)) {
          instructionList = parsed.map(item => {
            if (typeof item === 'object' && item !== null) {
              return item.text || item.instruction || item.step || String(item);
            }
            return String(item);
          });
        } else {
          // If not JSON, split by newlines and clean up
          let rawText = instructions
            .replace(/DIRECTIONS/gi, '') // Remove section headers
            .replace(/INGREDIENTS/gi, '') // Remove ingredient headers that got mixed in
          
          instructionList = rawText.split(/\n+/).filter(line => line.trim().length > 0);
        }
      } catch (e) {
        // If JSON parsing fails, handle as text with numbered steps
        let rawText = instructions
          .replace(/DIRECTIONS/gi, '') // Remove section headers
          .replace(/INGREDIENTS/gi, '') // Remove ingredient headers that got mixed in
          .replace(/Editor's note:.*?→/gi, '') // Remove editor's notes
          .replace(/Recipe by.*?\./gi, '') // Remove recipe attribution
          .replace(/Photo by.*?\./gi, '') // Remove photo credits
          .replace(/Adapted from.*?\./gi, '') // Remove adaptation credits
          .replace(/Originally published.*?\./gi, '') // Remove publication info
          .replace(/First printed.*?\./gi, '') // Remove first printed info
          .replace(/This recipe.*?was first.*?\./gi, '') // Remove recipe history
          .replace(/Head this way for more.*?→/gi, '') // Remove promotional links
          .replace(/\bDecember\s+\d+\s*\d*\s*\d*\s*\d*\b/gi, '') // Remove date fragments
          .replace(/\b\d\s+0\s+\d\b/gi, '') // Remove spaced number fragments like "2 0 2"
        
        // First try to split by numbered steps (1., 2., etc.)
        const numberedSteps = rawText.split(/(?=\d+\.)/).filter(step => step.trim().length > 0);
        
        if (numberedSteps.length > 1) {
          instructionList = numberedSteps;
        } else {
          // Fallback to newline splitting
          instructionList = rawText.split(/\n+/).filter(line => line.trim().length > 0);
        }
      }
    } else if (Array.isArray(instructions)) {
      instructionList = instructions;
    }
    
    // Clean and combine instruction fragments
    const cleanedInstructions = [];
    let currentInstruction = '';
    
    // If we have what looks like a single long instruction with embedded numbers,
    // try to split it properly first
    if (instructionList.length === 1 && instructionList[0].includes('2.') && instructionList[0].includes('3.')) {
      const longText = instructionList[0];
      // Split by step numbers but keep the numbers
      const steps = longText.split(/(?=\d+\.)/).filter(step => step.trim());
      instructionList = steps;
    }
    
    for (let i = 0; i < instructionList.length; i++) {
      const line = String(instructionList[i]).trim();
      
      // Skip lines that look like ingredients (start with measurements)
      if (line.match(/^(\d+\/?\d*|\d*\.?\d+|½|¼|¾|⅓|⅔|⅛|⅜|⅝|⅞)\s*(cups?|tbsp|tsp|tablespoons?|teaspoons?|g|kg|lbs?|pounds?|oz|ounces?|ml|l|liters?|pkg)/i)) {
        continue;
      }
      
      // Skip editor's notes and similar content immediately
      if (line.toLowerCase().includes("editor's note") ||
          line.toLowerCase().includes("head this way") ||
          line.toLowerCase().includes("→") ||
          line.toLowerCase().includes("refer to") ||
          line.toLowerCase().includes("see page") ||
          line.toLowerCase().includes("see tip") ||
          line.toLowerCase().includes("first printed") ||
          line.toLowerCase().includes("originally published") ||
          line.toLowerCase().includes("recipe by") ||
          line.toLowerCase().includes("adapted from") ||
          line.toLowerCase().includes("photo by") ||
          line.toLowerCase().includes("styling by") ||
          line.toLowerCase().includes("food styling") ||
          line.toLowerCase().includes("prop styling") ||
          line.toLowerCase().includes("recipe appears in") ||
          line.toLowerCase().includes("for more") ||
          line.toLowerCase().includes("check out") ||
          line.toLowerCase().includes("visit") ||
          line.toLowerCase().includes("browse") ||
          line.toLowerCase().includes("subscribe") ||
          line.toLowerCase().includes("follow us") ||
          line.toLowerCase().match(/\b\d{4}\b/) && (line.toLowerCase().includes("december") || line.toLowerCase().includes("january") || line.toLowerCase().includes("february") || line.toLowerCase().includes("march") || line.toLowerCase().includes("april") || line.toLowerCase().includes("may") || line.toLowerCase().includes("june") || line.toLowerCase().includes("july") || line.toLowerCase().includes("august") || line.toLowerCase().includes("september") || line.toLowerCase().includes("october") || line.toLowerCase().includes("november"))) {
        continue;
      }
      
      // Skip very short fragments unless they end a sentence
      if (line.length < 10 && !line.endsWith('.') && !line.endsWith('minutes')) {
        if (currentInstruction) {
          currentInstruction += ' ' + line;
        }
        continue;
      }
      
      // If this looks like a new numbered step, finish the previous one
      if (line.match(/^\d+\./) && currentInstruction) {
        cleanedInstructions.push(currentInstruction);
        currentInstruction = line;
      }
      // If this looks like a continuation of the previous instruction
      else if (currentInstruction && !line.match(/^(In|Whisk|Stir|Pour|Divide|Remove|Turn|Cover|Let|Sprinkle)/i) && 
          !currentInstruction.match(/\.\s*$/)) {
        currentInstruction += ' ' + line;
      } else {
        // Start a new instruction
        if (currentInstruction) {
          cleanedInstructions.push(currentInstruction);
        }
        currentInstruction = line;
      }
    }
    
    // Add the last instruction
    if (currentInstruction) {
      cleanedInstructions.push(currentInstruction);
    }
    
    // Remove duplicates and very similar instructions
    const uniqueInstructions = [];
    const seen = new Set();
    
    for (const instruction of cleanedInstructions) {
      const normalizedInstruction = String(instruction).trim()
        .replace(/^\d+\.\s*/, '') // Remove numbering
        .replace(/\(see tip,?\s*page\s*\d+\)/gi, '') // Remove page references
        .replace(/\(see\s*page\s*\d+\)/gi, '') // Remove simple page references
        .replace(/\(tip,?\s*page\s*\d+\)/gi, '') // Remove tip references
        .replace(/Editor's note:.*?→/gi, '') // Remove editor's notes
        .replace(/Head this way for more.*?→/gi, '') // Remove link text
        .replace(/Recipe by.*?\./gi, '') // Remove recipe attribution
        .replace(/Photo by.*?\./gi, '') // Remove photo credits
        .replace(/Adapted from.*?\./gi, '') // Remove adaptation credits
        .replace(/Originally published.*?\./gi, '') // Remove publication info
        .replace(/First printed.*?\./gi, '') // Remove first printed info
        .replace(/This recipe.*?was first.*?\./gi, '') // Remove recipe history
        .replace(/\bDecember\s+\d+\s*\d*\s*\d*\s*\d*\b/gi, '') // Remove date fragments
        .replace(/\b\d\s+0\s+\d\b/gi, '') // Remove spaced number fragments like "2 0 2"
        .replace(/\s+/g, ' ') // Clean up extra spaces
        .trim();
      
      // Skip if empty or too short
      if (!normalizedInstruction || normalizedInstruction.length < 15) continue;
      
      // Skip editor's notes and similar content with more comprehensive filtering
      const lowerInstruction = normalizedInstruction.toLowerCase();
      if (lowerInstruction.includes("editor's note") ||
          lowerInstruction.includes("head this way") ||
          lowerInstruction.includes("→") ||
          lowerInstruction.includes("refer to") ||
          lowerInstruction.includes("see page") ||
          lowerInstruction.includes("see tip") ||
          lowerInstruction.includes("first printed") ||
          lowerInstruction.includes("originally published") ||
          lowerInstruction.includes("recipe by") ||
          lowerInstruction.includes("adapted from") ||
          lowerInstruction.includes("photo by") ||
          lowerInstruction.includes("styling by") ||
          lowerInstruction.includes("food styling") ||
          lowerInstruction.includes("prop styling") ||
          lowerInstruction.includes("recipe appears in") ||
          lowerInstruction.includes("for more") ||
          lowerInstruction.includes("check out") ||
          lowerInstruction.includes("visit") ||
          lowerInstruction.includes("browse") ||
          lowerInstruction.includes("subscribe") ||
          lowerInstruction.includes("follow us") ||
          lowerInstruction.includes("get the recipe") ||
          lowerInstruction.includes("full recipe") ||
          lowerInstruction.includes("complete recipe") ||
          lowerInstruction.includes("recipe notes") ||
          lowerInstruction.includes("cook's note") ||
          lowerInstruction.includes("chef's note") ||
          lowerInstruction.includes("tip:") ||
          lowerInstruction.includes("note:") ||
          lowerInstruction.includes("variation:") ||
          lowerInstruction.includes("substitution:") ||
          // Skip lines that are just dates or publication info
          (lowerInstruction.match(/\b\d{4}\b/) && (lowerInstruction.includes("december") || lowerInstruction.includes("january") || lowerInstruction.includes("february") || lowerInstruction.includes("march") || lowerInstruction.includes("april") || lowerInstruction.includes("may") || lowerInstruction.includes("june") || lowerInstruction.includes("july") || lowerInstruction.includes("august") || lowerInstruction.includes("september") || lowerInstruction.includes("october") || lowerInstruction.includes("november"))) ||
          // Skip lines that are just numbers or fragments
          lowerInstruction.match(/^[\d\s\.]+$/) ||
          // Skip lines that are just "2 0 2" or similar fragments
          lowerInstruction.match(/^[\d\s]{1,10}$/)) {
        continue;
      }
      
      // Create a more robust key for duplicate detection
      // Use first meaningful words instead of just character count
      const words = normalizedInstruction.toLowerCase().split(/\s+/).slice(0, 10);
      const duplicateKey = words.join(' ');
      
      if (!seen.has(duplicateKey)) {
        seen.add(duplicateKey);
        uniqueInstructions.push(normalizedInstruction);
      }
    }
    
    return uniqueInstructions.filter(instruction => instruction.length > 10); // Filter out very short fragments
  };

  // Checkbox handler for recipe selection
  const handleRecipeCheckbox = (recipeId) => {
    const isCurrentlySelected = selectedRecipes.includes(recipeId);
    const newSelection = isCurrentlySelected
      ? selectedRecipes.filter(id => id !== recipeId)
      : [...selectedRecipes, recipeId];
    
    setSelectedRecipes(newSelection);
    
    // Track recipe interaction in session memory
    sessionMemory.recordRecipeInteraction(recipeId, {
      action: isCurrentlySelected ? 'unselect' : 'select',
      timestamp: Date.now()
    });
  };

  // Dropdown handler for recipe details
  const handleRecipeDropdown = async (recipe) => {
    if (expandedRecipe && expandedRecipe.id === recipe.id) {
      setExpandedRecipe(null);
    } else {
      // Track recipe interaction in session memory
      sessionMemory.recordRecipeInteraction(recipe.id, {
        action: 'view_details',
        title: recipe.title,
        timestamp: Date.now()
      });
      
      // Format recipe with AI before showing
      const formattedRecipe = await formatRecipeWithAI(recipe);
      setExpandedRecipe(formattedRecipe);
    }
  };

  // NEW: Conversation flow enhancement functions
  const generateConversationSuggestions = (recipeTypes, detectedIngredients, userMessage) => {
    const suggestions = [];
    const messageText = userMessage.toLowerCase();
    
    // Progressive discovery based on recipe types
    if (recipeTypes && recipeTypes.length > 0) {
      // Suggest related types
      if (recipeTypes.includes('quick') && !conversationContext.preferredTypes.includes('easy')) {
        suggestions.push({
          type: 'explore_type',
          text: 'Show me easy recipes too',
          context: 'easy recipes',
          icon: '⚡'
        });
      }
      
      if (recipeTypes.includes('one_pot') && !messageText.includes('cleanup')) {
        suggestions.push({
          type: 'explore_benefit',
          text: 'What about minimal cleanup meals?',
          context: 'easy cleanup one pot meals',
          icon: '🍲'
        });
      }
      
      if (recipeTypes.includes('challenging') && !conversationContext.preferredTypes.includes('quick')) {
        suggestions.push({
          type: 'explore_alternative',
          text: 'Show me quicker versions',
          context: 'quick versions of challenging recipes',
          icon: '🏃‍♂️'
        });
      }
    }
    
    // Ingredient-based suggestions
    if (detectedIngredients && detectedIngredients.length > 0) {
      const mainIngredient = detectedIngredients[0];
      
      // Suggest complementary ingredients
      const complementaryPairs = {
        'sweet potato': ['black beans', 'spinach', 'feta cheese'],
        'chicken': ['herbs', 'lemon', 'garlic'],
        'pasta': ['tomatoes', 'basil', 'parmesan'],
        'rice': ['vegetables', 'soy sauce', 'ginger']
      };
      
      if (complementaryPairs[mainIngredient]) {
        complementaryPairs[mainIngredient].forEach(complement => {
          if (!detectedIngredients.includes(complement)) {
            suggestions.push({
              type: 'ingredient_combo',
              text: `Try ${mainIngredient} with ${complement}`,
              context: `${mainIngredient} ${complement} recipes`,
              icon: '🥗'
            });
          }
        });
      }
      
      // Suggest cuisine exploration
      if (!conversationContext.exploredCuisines.includes('mediterranean') && 
          (mainIngredient.includes('tomato') || mainIngredient.includes('olive'))) {
        suggestions.push({
          type: 'cuisine_explore',
          text: 'Explore Mediterranean flavors',
          context: `mediterranean ${mainIngredient} recipes`,
          icon: '🌿'
        });
      }
    }
    
    // Contextual suggestions based on chat phase
    if (conversationContext.chatPhase === 'initial' && suggestions.length > 0) {
      suggestions.push({
        type: 'cooking_style',
        text: 'What cooking style do you prefer?',
        context: 'cooking styles and techniques',
        icon: '👨‍🍳'
      });
    }
    
    // Limit to 4 suggestions to avoid overwhelming
    setConversationSuggestions(suggestions.slice(0, 4));
  };
  
  const updateConversationContext = (userMessage, searchData) => {
    const messageText = userMessage.toLowerCase();
    
    setConversationContext(prev => {
      const newContext = { ...prev };
      
      // Update main ingredient
      if (searchData.detected_ingredients && searchData.detected_ingredients.length > 0) {
        newContext.mainIngredient = searchData.detected_ingredients[0];
      }
      
      // Track preferred types
      if (searchData.recipe_types) {
        newContext.preferredTypes = [...new Set([...prev.preferredTypes, ...searchData.recipe_types])];
      }
      
      // Update chat phase
      if (messageText.includes('quick') || messageText.includes('easy')) {
        newContext.chatPhase = 'exploring';
      } else if (messageText.includes('decide') || messageText.includes('choose')) {
        newContext.chatPhase = 'deciding';
      } else if (prev.chatPhase === 'initial') {
        newContext.chatPhase = 'exploring';
      }
      
      return newContext;
    });
  };
  
  const handleSuggestionClick = async (suggestion) => {
    setInputMessage(suggestion.context);
    
    // Update conversation context based on suggestion
    if (suggestion.type === 'explore_type') {
      setConversationContext(prev => ({
        ...prev,
        preferredTypes: [...prev.preferredTypes, 'easy'],
        chatPhase: 'refining'
      }));
    }
    
    // Trigger search with suggestion
    setTimeout(() => {
      sendMessage();
    }, 100);
  };

  // Drag and Drop Handlers
  const handleDragStart = (event) => {
    const { active } = event;
    
    // Find the recipe being dragged
    let recipe = null;
    
    // Check if it's from chat messages
    for (const msg of messages) {
      if (msg.recipes) {
        recipe = msg.recipes.find(r => active.id === `chat-recipe-${r.id || r.name}`);
        if (recipe) break;
      }
    }
    
    setDraggedRecipe(recipe);
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;
    
    if (over && draggedRecipe) {
      // The meal planner will handle the drop logic
      // We just need to clear our drag state
      setDraggedRecipe(null);
    } else {
      setDraggedRecipe(null);
    }
  };

  return (
    <DndContext
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <Debug />
      <div className={`main-app ${showMealPlanner ? 'with-meal-planner' : ''}`}>
        <div className={`chat-home ${hasStartedChat ? 'chat-started' : 'landing'}`}>
          <div className="chat-container">
        {!hasStartedChat && (
          <div className="landing-header">
            <h1>Welcome to Hungie! 🍴</h1>
            <p>Your personal chef assistant ready to help you discover amazing recipes</p>
          </div>
        )}
        {hasStartedChat && (
          <>
            <div className="chat-box">
              {messages.map((msg, index) => {
                return (
                  <div key={index} className={`chat-message ${msg.type}`} style={{ whiteSpace: 'pre-line', marginBottom: msg.recipes && msg.recipes.length > 0 ? '10px' : undefined }}>
                    {msg.content || msg.text}
                    {/* Always visible recipe list */}
                    {msg.type === 'hungie' && msg.recipes && msg.recipes.length > 0 && (
                      <div className="chat-recipe-dropdown" style={{ marginTop: '8px' }}>
                        <div className="recipe-dropdown-list" style={{ border: '1px solid #d1d5db', borderRadius: '6px', background: '#fff', padding: '10px', marginTop: '4px' }}>
                            {msg.recipes.slice(0, 5).map((recipe, rIdx) => {
                              const uniqueKey = `${recipe.id || 'recipe'}-${rIdx}`;
                              return (
                                <RecipeDropdown key={uniqueKey} recipe={recipe} />
                              );
                            })}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
              
              {/* Conversation Suggestions */} 
                                  padding: '16px',
                                  cursor: 'pointer',
                                  transition: 'all 0.2s ease',
                                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                }}
                                onMouseEnter={(e) => {
                                  e.target.style.borderColor = '#3b82f6';
                                  e.target.style.boxShadow = '0 4px 12px rgba(59,130,246,0.15)';
                                }}
                                onMouseLeave={(e) => {
                                  e.target.style.borderColor = '#e5e7eb';
                                  e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                                }}
                                >
                                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                                    <h4 style={{ 
                                      margin: '0', 
                                      color: '#1f2937', 
                                      fontSize: '16px', 
                                      fontWeight: '600',
                                      lineHeight: '1.4',
                                      flex: 1,
                                      paddingRight: '8px'
                                    }}>{recipe.title}</h4>
                                    <input
                                      type="checkbox"
                                      checked={selectedRecipes.includes(recipe.id)}
                                      onChange={() => handleRecipeCheckbox(recipe.id)}
                                      style={{ marginLeft: '8px', transform: 'scale(1.1)' }}
                                      title="Select recipe for cooking"
                                    />
                                  </div>
                                  
                                  {recipe.description && (
                                    <p style={{ 
                                      color: '#6b7280', 
                                      fontSize: '14px', 
                                      lineHeight: '1.5', 
                                      margin: '0 0 12px 0',
                                      display: '-webkit-box',
                                      WebkitLineClamp: 2,
                                      WebkitBoxOrient: 'vertical',
                                      overflow: 'hidden'
                                    }}>
                                      {recipe.description}
                                    </p>
                                  )}

                                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto' }}>
                                    <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#6b7280' }}>
                                      {recipe.total_time && (
                                        <span>⏱️ {recipe.total_time}</span>
                                      )}
                                      {recipe.servings && (
                                        <span>👥 {recipe.servings}</span>
                                      )}
                                    </div>
                                    <button
                                      className="recipe-details-btn"
                                      style={{ 
                                        background: isExpanded ? '#ef4444' : '#3b82f6', 
                                        color: 'white', 
                                        border: 'none', 
                                        borderRadius: '6px', 
                                        padding: '6px 12px', 
                                        fontSize: '12px',
                                        fontWeight: '600', 
                                        cursor: 'pointer',
                                        transition: 'background 0.2s ease'
                                      }}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleRecipeDropdown(recipe);
                                      }}
                                      title={`${isExpanded ? 'Hide' : 'Show'} recipe details`}
                                    >
                                      {isExpanded ? '❌ Hide' : '👁️ Details'}
                                    </button>
                                  </div>
                                  
                                  {isExpanded && (
                                    <div className="inline-recipe-details" style={{ 
                                      marginTop: '16px', 
                                      paddingTop: '16px',
                                      borderTop: '1px solid #e5e7eb',
                                      background: '#f9fafb', 
                                      margin: '16px -16px -16px -16px',
                                      padding: '16px',
                                      borderRadius: '0 0 12px 12px'
                                    }}>
                                      {isFormattingRecipe && (
                                        <div className="ai-formatting-indicator" style={{
                                          background: 'linear-gradient(135deg, #667eea, #764ba2)',
                                          color: 'white',
                                          padding: '12px',
                                          borderRadius: '8px',
                                          marginBottom: '16px',
                                          display: 'flex',
                                          alignItems: 'center',
                                          gap: '8px'
                                        }}>
                                          <div className="typing-indicator">
                                            <span></span>
                                            <span></span>
                                            <span></span>
                                          </div>
                                          👨‍🍳 Chef is inspecting and formatting this recipe...
                                        </div>
                                      )}
                                      
                                      {expandedRecipe.formatted_by_ai && (
                                        <div className="ai-formatted-badge" style={{
                                          background: '#10b981',
                                          color: 'white',
                                          padding: '8px 12px',
                                          borderRadius: '6px',
                                          fontSize: '12px',
                                          fontWeight: '600',
                                          marginBottom: '16px',
                                          display: 'inline-block'
                                        }}>
                                          ✨ Recipe formatted by AI Chef
                                        </div>
                                      )}
                                      
                                      {/* Recipe Analysis Section */}
                                      <div className="recipe-analysis-section">
                                        <button
                                          className="analyze-btn"
                                          onClick={async () => {
                                            const analysis = await analyzeRecipe(expandedRecipe.id);
                                            if (analysis) {
                                              setExpandedRecipe(prev => ({ ...prev, analysis }));
                                            }
                                          }}
                                          style={{ 
                                            background: '#10b981', 
                                            color: 'white', 
                                            border: 'none', 
                                            padding: '8px 16px', 
                                            borderRadius: '6px', 
                                            marginBottom: '16px',
                                            cursor: 'pointer',
                                            fontWeight: '600'
                                          }}
                                        >
                                          🧠 Analyze Recipe
                                        </button>
                                        
                                        {(expandedRecipe.analysis || recipeAnalyses.get(expandedRecipe.id)) && (
                                          <div className="analysis-results" style={{ 
                                            background: '#f0f9ff', 
                                            border: '1px solid #0ea5e9', 
                                            borderRadius: '8px', 
                                            padding: '16px', 
                                            marginBottom: '16px' 
                                          }}>
                                            {(() => {
                                              const analysis = expandedRecipe.analysis || recipeAnalyses.get(expandedRecipe.id);
                                              return (
                                                <>
                                                  <h5 style={{ margin: '0 0 12px 0', color: '#0c4a6e' }}>🧠 Recipe Analysis</h5>
                                                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '12px' }}>
                                                    <div><strong>Difficulty:</strong> {analysis.difficulty}</div>
                                                    <div><strong>Type:</strong> {analysis.recipe_type}</div>
                                                    <div><strong>Prep Time:</strong> {analysis.estimated_prep_time}</div>
                                                    <div><strong>Cook Time:</strong> {analysis.estimated_cook_time}</div>
                                                  </div>
                                                  {analysis.cooking_methods && analysis.cooking_methods.length > 0 && (
                                                    <div style={{ marginBottom: '12px' }}>
                                                      <strong>Cooking Methods:</strong> {analysis.cooking_methods.join(', ')}
                                                    </div>
                                                  )}
                                                  {analysis.cooking_tips && analysis.cooking_tips.length > 0 && (
                                                    <div>
                                                      <strong>Cooking Tips:</strong>
                                                      <ul style={{ margin: '8px 0 0 20px' }}>
                                                        {analysis.cooking_tips.map((tip, index) => (
                                                          <li key={index} style={{ marginBottom: '4px' }}>{tip}</li>
                                                        ))}
                                                      </ul>
                                                    </div>
                                                  )}
                                                </>
                                              );
                                            })()}
                                          </div>
                                        )}
                                      </div>
                                      
                                      <div className="recipe-meta" style={{ marginBottom: '16px' }}>
                                        {expandedRecipe.total_time && <p style={{ margin: '4px 0' }}><strong>⏱️ Total Time:</strong> {expandedRecipe.total_time}</p>}
                                        {expandedRecipe.servings && <p style={{ margin: '4px 0' }}><strong>👥 Servings:</strong> {expandedRecipe.servings}</p>}
                                        {expandedRecipe.description && <p style={{ margin: '4px 0' }}><strong>📝 Description:</strong> {expandedRecipe.description}</p>}
                                      </div>

                                      {expandedRecipe.ingredients && (
                                        <div className="recipe-ingredients" style={{ marginBottom: '16px' }}>
                                          <h4 style={{ color: '#1f2937', marginBottom: '8px' }}>🥘 Ingredients</h4>
                                          <ul className="ingredients-list" style={{ listStyle: 'none', padding: 0 }}>
                                            {formatIngredients(expandedRecipe.ingredients).map((ingredient, index) => {
                                              const itemKey = `${expandedRecipe.id}-ingredient-${ingredient.substring(0, 50)}`;
                                              const isSuggested = suggestedItems.has(itemKey);
                                              return (
                                                <li key={index} className="ingredient-item" style={{ marginBottom: '8px', display: 'flex', alignItems: 'flex-start' }}>
                                                  <input
                                                    type="checkbox"
                                                    className="suggestion-checkbox"
                                                    checked={isSuggested}
                                                    onChange={() => toggleSuggestion('ingredient', ingredient, expandedRecipe.id)}
                                                    title="Mark as suggested/needed"
                                                    style={{ marginRight: '8px', marginTop: '2px' }}
                                                  />
                                                  <span className={`ingredient-text ${isSuggested ? 'suggested' : ''}`} style={{ 
                                                    textDecoration: isSuggested ? 'line-through' : 'none',
                                                    color: isSuggested ? '#6b7280' : '#1f2937'
                                                  }}>
                                                    {ingredient}
                                                  </span>
                                                </li>
                                              );
                                            })}
                                          </ul>
                                        </div>
                                      )}

                                      {expandedRecipe.instructions && (
                                        <div className="recipe-instructions">
                                          <h4 style={{ color: '#1f2937', marginBottom: '8px' }}>👨‍🍳 Instructions</h4>
                                          <ol className="instructions-list" style={{ paddingLeft: '20px' }}>
                                            {formatInstructions(expandedRecipe.instructions).map((instruction, index) => {
                                              const itemKey = `${expandedRecipe.id}-instruction-${instruction.substring(0, 50)}`;
                                              const isSuggested = suggestedItems.has(itemKey);
                                              return (
                                                <li key={index} className="instruction-item" style={{ marginBottom: '12px' }}>
                                                  <div className="instruction-content" style={{ display: 'flex', alignItems: 'flex-start' }}>
                                                    <input
                                                      type="checkbox"
                                                      className="suggestion-checkbox"
                                                      checked={isSuggested}
                                                      onChange={() => toggleSuggestion('instruction', instruction, expandedRecipe.id)}
                                                      title="Mark as completed/noted"
                                                      style={{ marginRight: '8px', marginTop: '2px' }}
                                                    />
                                                    <span className={`instruction-text ${isSuggested ? 'suggested' : ''}`} style={{ 
                                                      textDecoration: isSuggested ? 'line-through' : 'none',
                                                      color: isSuggested ? '#6b7280' : '#1f2937'
                                                    }}>
                                                      {instruction}
                                                    </span>
                                                  </div>
                                                </li>
                                              );
                                            })}
                                          </ol>
                                        </div>
                                      )}

                                      {expandedRecipe.url && (
                                        <div className="recipe-url" style={{ marginTop: '16px' }}>
                                          <a 
                                            href={expandedRecipe.url} 
                                            target="_blank" 
                                            rel="noopener noreferrer"
                                            style={{ 
                                              color: '#3b82f6', 
                                              textDecoration: 'none',
                                              fontWeight: '600'
                                            }}
                                          >
                                            🔗 View Original Recipe
                                          </a>
                                        </div>
                                      )}
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                  </div>
                );
              })}
              
              {/* Conversation Suggestions */}
              {conversationSuggestions.length > 0 && !isLoading && (
                <div style={{
                  margin: '16px 0',
                  padding: '12px',
                  background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
                  borderRadius: '12px',
                  border: '1px solid #cbd5e1'
                }}>
                  <div style={{
                    fontSize: '13px',
                    color: '#64748b',
                    marginBottom: '10px',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    💡 <span>Try asking:</span>
                  </div>
                  <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '8px'
                  }}>
                    {conversationSuggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion)}
                        style={{
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white',
                          border: 'none',
                          borderRadius: '20px',
                          padding: '8px 14px',
                          fontSize: '12px',
                          fontWeight: '500',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          transition: 'all 0.2s ease',
                          boxShadow: '0 2px 4px rgba(102, 126, 234, 0.3)',
                          maxWidth: '200px',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.transform = 'translateY(-1px) scale(1.02)';
                          e.target.style.boxShadow = '0 4px 8px rgba(102, 126, 234, 0.4)';
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.transform = 'translateY(0) scale(1)';
                          e.target.style.boxShadow = '0 2px 4px rgba(102, 126, 234, 0.3)';
                        }}
                      >
                        <span style={{ fontSize: '14px' }}>{suggestion.icon}</span>
                        <span>{suggestion.text}</span>
                      </button>
                    ))}
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: '#94a3b8',
                    marginTop: '8px',
                    fontStyle: 'italic'
                  }}>
                    Click a suggestion to explore new recipe ideas
                  </div>
                </div>
              )}
              
              {isLoading && (
                <div className="chat-message bot loading-message">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  Hungie is thinking... 🤔
                </div>
              )}
              {/* Scroll target for auto-scroll */}
              <div ref={messagesEndRef} />
            </div>
            {/* Expanded recipe details now shown inline in dropdown, not as overlay */}
            {!isLoading && recipes.length === 0 && messages.length > 0 && lastRequestType === 'search' && (
              <div className="no-recipes-message">
                <p>🤔 No recipes found for your request. Try a different search term!</p>
              </div>
            )}
          </>
        )}
        <div className={`chat-input ${hasStartedChat ? 'chat-mode' : 'landing-mode'}`}>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={hasStartedChat ? "Type your message..." : "What are you in the mood for?"}
            disabled={isLoading}
          />
          <button onClick={sendMessage} disabled={isLoading}>Send</button>
          {hasStartedChat && (
            <button 
              onClick={toggleMealPlanner}
              className={`meal-planner-toggle ${showMealPlanner ? 'active' : ''}`}
              title="Toggle Meal Planner"
            >
              🍽️ {showMealPlanner ? 'Hide' : 'Meal Plan'}
            </button>
          )}
        </div>
        
        {/* Session Debug Info */}
        {hasStartedChat && (
          <div style={{ textAlign: 'center', margin: '10px 0' }}>
            <button
              onClick={() => {
                try {
                  console.log('SessionMemory object:', sessionMemory);
                  console.log('Available methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(sessionMemory)));
                  
                  const summary = sessionMemory.getSessionSummary();
                  const recommendations = sessionMemory.getPersonalizedRecommendations ? 
                    sessionMemory.getPersonalizedRecommendations() : 
                    { error: 'Method not available' };
                    
                  console.log('Session Summary:', summary);
                  console.log('Personalized Recommendations:', recommendations);
                  
                  alert(`Session Stats:\n• Queries: ${summary.stats.totalQueries}\n• Recipes Viewed: ${summary.stats.recipesViewed}\n• Unique Recipes Shown: ${summary.uniqueRecipesShown}\n\nCheck console for full details!`);
                } catch (error) {
                  console.error('Debug button error:', error);
                  alert(`Error: ${error.message}\nCheck console for details.`);
                }
              }}
              style={{
                background: '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '15px',
                padding: '5px 12px',
                fontSize: '12px',
                cursor: 'pointer'
              }}
            >
              🔍 Session Debug
            </button>
          </div>
        )}
        </div>
      </div>
      
      {/* Side-by-side layout when meal planner is active */}
      {showMealPlanner && (
        <div className="meal-planner-sidebar">
          <MealPlannerView 
            searchResults={[]} // No separate search results - drag from chat
            isVisible={true}
            isCompactMode={true} // New prop for sidebar mode
          />
        </div>
      )}
      </div>
      
      {/* Drag Overlay */}
      <DragOverlay>
        {draggedRecipe && (
          <div className="recipe-drag-preview">
            <strong>{draggedRecipe.name || draggedRecipe.title}</strong>
          </div>
        )}
      </DragOverlay>
    </DndContext>
  );
};

export default RecipeDetail;

