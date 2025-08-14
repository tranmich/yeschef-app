import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import RecipeCard from './RecipeCard';
import RecipeDropdown from './RecipeDropdown';
import { api } from '../utils/api';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      type: 'hungie',
      content: "Hello there! 👋 I'm Hungie, your personal chef assistant! What are you craving today? Tell me about your situation - are you looking for something quick, budget-friendly, healthy, or just want to try something new? Yes, Chef! 🍴",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedRecipes, setSuggestedRecipes] = useState([]);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {

    console.log('🟠 DEBUG: sendMessage called. inputMessage:', inputMessage, 'isLoading:', isLoading);
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Add user message to chat
    const newUserMessage = {
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newUserMessage]);

    try {
      // Get conversation context (last few messages)
      const context = messages.slice(-4).map(msg => 
        `${msg.type}: ${msg.content}`
      ).join('\n');

      const data = await api.smartSearch(userMessage, context);
      // Support both top-level and nested fullResponse for recipes/chat_response
      const recipes = data.recipes || (data.fullResponse && data.fullResponse.recipes) || [];
      const chat_response = data.chat_response || (data.fullResponse && data.fullResponse.chat_response) || '';
      const substitutions = data.substitutions || (data.fullResponse && data.fullResponse.substitutions) || null;
      const responseType = data.type || (data.fullResponse && data.fullResponse.type) || 'recipe_search';

      const hungieMessage = {
        type: 'hungie',
        content: chat_response,
        timestamp: new Date(),
        recipes,
        substitutions,
        responseType
      };
      console.log('🟢 DEBUG: Built hungieMessage:', hungieMessage);

      setMessages(prev => {
        const updated = [...prev, hungieMessage];
        console.log('🟢 DEBUG: Updated messages array:', updated);
        return updated;
      });
      setSuggestedRecipes(recipes);

    } catch (error) {
      console.error('🔴 DEBUG: Error in sendMessage:', error);
      
      // Fallback response
      const fallbackMessage = {
        type: 'hungie',
        content: "Oops! Something went wrong, but I'm still here to help! 😅 What are you looking to cook today? Yes, Chef! 🍴",
        timestamp: new Date()
      };

      setMessages(prev => [...prev, fallbackMessage]);
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

  const handleRecipeClick = (recipe) => {
    navigate(`/recipe/${recipe.id}`);
  };

  const quickPrompts = [
    "I need something quick for dinner",
    "What can I make with chicken?",
    "I'm on a budget, help me out",
    "Something healthy and delicious",
    "Kid-friendly recipes please",
    "I want to try something new"
  ];

  const handleQuickPrompt = (prompt) => {
    setInputMessage(prompt);
  };

  return (
    <div className="chat-container">
      <div style={{color: 'red', fontWeight: 'bold', fontSize: '18px', margin: '10px 0'}}>DEBUG: Chat.js is rendering!</div>
      <div className="chat-header">
        <h2>🍴 Chat with Hungie</h2>
        <p>Your personal chef assistant is here to help!</p>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            <div className="message-avatar">
              {message.type === 'hungie' ? '👨‍🍳' : '👤'}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              {message.recipes && message.recipes.length > 0 && (
                <div className="message-recipes">
                  <h4>Here are some great options for you:</h4>
                  {console.log('🔍 DEBUG: Rendering recipes for message:', message.recipes)}
                  <div className="recipe-suggestions">
                    {message.recipes.map((recipe, idx) => (
                      <RecipeDropdown key={idx} recipe={recipe} />
                    ))}
                  </div>
                </div>
              )}
              
              {message.substitutions && (
                <div className="message-substitutions">
                  <h4>🔄 Ingredient Substitutions:</h4>
                  {Object.entries(message.substitutions).map(([ingredient, subs]) => (
                    <div key={ingredient} className="substitution-group">
                      <h5 className="ingredient-name">For {ingredient}:</h5>
                      <div className="substitution-options">
                        {subs.map((sub, idx) => (
                          <div key={idx} className="substitution-option">
                            <div className="sub-header">
                              <strong>{sub.substitute}</strong>
                              <span className="sub-ratio">({sub.ratio})</span>
                            </div>
                            <p className="sub-notes">{sub.notes}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <div className="message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message hungie">
            <div className="message-avatar">👨‍🍳</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 1 && (
        <div className="quick-prompts">
          <p>Try asking Hungie:</p>
          <div className="prompt-buttons">
            {quickPrompts.map((prompt, index) => (
              <button
                key={index}
                className="prompt-button"
                onClick={() => handleQuickPrompt(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="chat-input">
        <div className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Hungie anything... 'What should I cook tonight?' or 'I need something quick and healthy'"
            rows={2}
            disabled={isLoading}
          />
          <button 
            onClick={sendMessage} 
            disabled={!inputMessage.trim() || isLoading}
            className="send-button"
          >
            {isLoading ? '...' : '🚀'}
          </button>
        </div>
        <p className="input-hint">
          💡 Try being specific: "I have 20 minutes and chicken" or "Cheap comfort food for tonight"
        </p>
      </div>
    </div>
  );
};

export default Chat;
