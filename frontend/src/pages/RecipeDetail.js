import React, { useState, useRef, useEffect } from 'react';
import { DndContext, closestCenter, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import CompactHeader from '../components/CompactHeader';
import SidebarNavigation from '../components/SidebarNavigation';
import MealPlannerView from '../components/MealPlannerView';
import RecipeDropdown from '../components/RecipeDropdown';
import './RecipeDetail.css';
import { api } from '../utils/api';

const RecipeDetail = () => {
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
  const [hasStartedChat, setHasStartedChat] = useState(false);

  // NEW: Meal Planner State
  const [showMealPlanner, setShowMealPlanner] = useState(false);

  // NEW: Drag and Drop State
  const [draggedRecipe, setDraggedRecipe] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  // Configure drag sensors with distance threshold
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 10, // Require 10px movement before starting drag
      },
    })
  );

  // NEW: Meal Plan State
  const [mealPlan, setMealPlan] = useState({
    monday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    tuesday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    wednesday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    thursday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    friday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    saturday: { breakfast: [], lunch: [], dinner: [], snacks: [] },
    sunday: { breakfast: [], lunch: [], dinner: [], snacks: [] }
  });

  // NEW: Drag handlers
  const handleDragStart = (event) => {
    // Get recipe directly from the drag data instead of searching by ID
    const recipe = event.active.data.current?.recipe;
    setDraggedRecipe(recipe);
    setIsDragging(true);
  };

  const handleDragEnd = (event) => {
    const { over } = event;
    
    // Only add recipe if there's a valid drop target AND dragged recipe
    if (over && draggedRecipe) {
      // Parse the drop zone ID
      const dropZoneId = over.id;
      const [day, mealType] = dropZoneId.split('-');

      if (day && mealType && mealPlan[day] && mealPlan[day][mealType] !== undefined) {
        // Add recipe to meal plan
        setMealPlan(prev => ({
          ...prev,
          [day]: {
            ...prev[day],
            [mealType]: [...prev[day][mealType], draggedRecipe]
          }
        }));
      }
    }
    
    // Reset drag state
    setDraggedRecipe(null);
    setIsDragging(false);
  };

  const handleDragCancel = () => {
    // Reset drag state if drag is cancelled
    setDraggedRecipe(null);
    setIsDragging(false);
  };

  // --- Chat Scroll ---
  const scrollToBottom = () => {
    // Don't scroll if user is dragging
    if (isDragging) {
      return;
    }
    
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ 
        behavior: "smooth",
        block: "end"
      });
    }, 100);
  };

  // Track message count to only scroll on actual new messages
  const [lastMessageCount, setLastMessageCount] = useState(0);

  useEffect(() => {
    // Only scroll if we have new messages (not just re-renders) and not dragging
    if (messages.length > lastMessageCount && !isDragging) {
      scrollToBottom();
      setLastMessageCount(messages.length);
    } else if (messages.length !== lastMessageCount) {
      setLastMessageCount(messages.length);
    }
  }, [messages]); // Removed lastMessageCount to prevent infinite loops

  useEffect(() => {
    // Only scroll when loading finishes (new content arrived) and not currently dragging
    if (!isLoading && !isDragging && messages.length > 0) {
      scrollToBottom();
    }
  }, [isLoading]); // Removed isDragging from dependencies to prevent scroll on drag end

  // Toggle meal planner visibility
  const toggleMealPlanner = () => {
    setShowMealPlanner(!showMealPlanner);
  };

  // --- Chat Message Send Function ---
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Start chat UI on first message
    if (!hasStartedChat) setHasStartedChat(true);

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);

    try {
      // Search for recipes using the correct API method
      const response = await api.searchRecipes(userMessage);
      
      // Extract recipes from the correct response structure
      const recipes = response.data || response.recipes || [];
      
      // Add AI response with recipes
      const aiMessage = {
        type: 'hungie',
        content: `Here are some great ${userMessage} recipes I found for you! 🍴`,
        recipes: recipes,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error('Search error:', error);
      const errorMessage = {
        type: 'hungie',
        content: "I'm having trouble finding recipes right now. Please try again! 🍴",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
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
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <div className="app-container">
        {/* Compact Header */}
        <CompactHeader />
        
        {/* Main Content Area */}
        <div className="main-content">
          {/* Sidebar Navigation - Always visible */}
          <SidebarNavigation 
            showMealPlanner={showMealPlanner}
            onToggleMealPlanner={toggleMealPlanner}
            onFeatureSelect={(feature) => {
              // Handle future feature navigation
              console.log('Feature selected:', feature);
            }}
          />
          
          {/* Chat Area */}
          <div className={`chat-area ${showMealPlanner ? 'with-meal-planner' : ''}`}>
            <div className="chat-container">
              {/* Empty State - ChatGPT Style */}
              {!hasStartedChat && (
                <div className="empty-chat-state">
                  <div className="empty-state-content">
                    <div className="empty-state-icon">🍽️</div>
                    <h3>What would you like to cook today?</h3>
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
                <div className="chat-box">
                  {messages.map((msg, index) => (
                    <div key={index} className={`chat-message ${msg.type}`} style={{ whiteSpace: 'pre-line', marginBottom: msg.recipes && msg.recipes.length > 0 ? '10px' : undefined }}>
                      {msg.content || msg.text}
                      
                      {/* Recipe list with RecipeDropdown components */}
                      {msg.type === 'hungie' && msg.recipes && msg.recipes.length > 0 && (
                        <div className="chat-recipe-dropdown" style={{ marginTop: '8px' }}>
                          <div className="recipe-dropdown-list" style={{ border: '1px solid #d1d5db', borderRadius: '6px', background: '#fff', padding: '10px', marginTop: '4px' }}>
                            {msg.recipes.slice(0, 5).map((recipe, rIdx) => {
                              const uniqueKey = `${recipe.id || 'recipe'}-${rIdx}`;
                              return (
                                <RecipeDropdown key={uniqueKey} recipe={recipe} index={rIdx} />
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {/* Chat Input - Always at bottom */}
            <div className="chat-input-container">
              <div className="chat-input">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Tell me what you're craving..."
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                >
                  {isLoading ? "🔄" : "🍴"}
                </button>
              </div>
            </div>
          </div>
          
          {/* Meal Planner Sidebar - Notion-inspired */}
          <div className={`meal-planner-sidebar ${showMealPlanner ? 'visible' : ''}`}>
            {/* Resize Handle */}
            <div className="meal-planner-resize-handle"></div>
            
            {/* Close Button */}
            <button 
              className="meal-planner-close"
              onClick={toggleMealPlanner}
              title="Close meal planner"
            >
              ✕
            </button>
            
            <MealPlannerView 
              searchResults={[]} // No separate search results - drag from chat
              isVisible={showMealPlanner}
              isCompactMode={true} // New prop for sidebar mode
              chatRecipes={messages.flatMap(m => m.recipes || [])} // Pass chat recipes
              mealPlan={mealPlan} // Pass meal plan state
              setMealPlan={setMealPlan} // Pass meal plan setter
            />
          </div>
        </div>
      </div>
    </DndContext>
  );
};

export default RecipeDetail;
