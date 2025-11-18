import React, { useState, useEffect } from 'react';
import SocialRecipeView from './SocialRecipeView';
import './CommunityBrowser.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

function CommunityBrowser() {
  const [communityRecipes, setCommunityRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [showRecipeView, setShowRecipeView] = useState(false);

  // Categories for filtering
  const categories = [
    { id: 'all', name: 'All Recipes', count: 0 },
    { id: 'breakfast', name: 'Breakfast', count: 0 },
    { id: 'lunch', name: 'Lunch', count: 0 },
    { id: 'dinner', name: 'Dinner', count: 0 },
    { id: 'dessert', name: 'Desserts', count: 0 },
    { id: 'vegetarian', name: 'Vegetarian', count: 0 },
    { id: 'quick', name: 'Quick Meals', count: 0 }
  ];

  // Load real community recipes from backend
  useEffect(() => {
    loadCommunityRecipes();
  }, []);

  const loadCommunityRecipes = async () => {
    setLoading(true);
    setError('');
    
    try {
      console.log('🔍 Fetching community recipes from v2:', `${API_BASE_URL}/api/v2/community/recipes`);
      
      const response = await fetch(`${API_BASE_URL}/api/v2/community/recipes?limit=50&sort=recent`, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      console.log('✅ Community recipes loaded (v2):', data);
      
      // Handle v2 response structure: data.data.recipes or data.recipes
      const recipes = data.data?.recipes || data.recipes || [];
      
      if (data.success && recipes.length > 0) {
        // Transform backend data to match frontend expectations
        const transformedRecipes = recipes.map(recipe => ({
          id: recipe.id,
          title: recipe.title || recipe.community_title,
          description: recipe.description || recipe.community_description || 'No description available',
          author: recipe.shared_by || recipe.user || 'Anonymous',
          authorInitials: getInitials(recipe.shared_by || recipe.user),
          category: detectCategory(recipe.title, recipe.description),
          prepTime: recipe.prep_time || 'Unknown',
          cookTime: recipe.cook_time || 'Unknown',
          difficulty: recipe.difficulty || 'Medium',
          likes: recipe.likes || 0,
          saves: 0, // TODO: Add saves count when implemented
          views: 0, // TODO: Add views count when implemented
          rating: 4.5, // TODO: Add real ratings when implemented
          reviews: 0, // TODO: Add reviews count when implemented
          image: recipe.image || recipe.community_icon || generateRecipeImage(recipe.title),
          tags: recipe.tags || [],
          createdAt: formatTimeAgo(recipe.shared_at),
          ingredients: recipe.ingredients,
          instructions: recipe.instructions,
          servings: recipe.servings
        }));
        
        setCommunityRecipes(transformedRecipes);
      } else {
        // If no recipes or API returns empty, show friendly message
        setCommunityRecipes([]);
      }
    } catch (error) {
      console.error('❌ Error loading community recipes:', error);
      setError('Failed to load community recipes. Using sample data.');
      
      // Fallback to mock data on error
      loadMockRecipes();
    } finally {
      setLoading(false);
    }
  };

  const loadMockRecipes = () => {
    // Fallback mock data if API fails
    const mockRecipes = [
      {
        id: 9999,
        title: "Community Features Coming Soon!",
        description: "Share your recipes with the community and discover amazing dishes from other users.",
        author: "YesChef Team",
        authorInitials: "YC",
        category: "all",
        prepTime: "N/A",
        cookTime: "N/A",
        difficulty: "Easy",
        likes: 0,
        saves: 0,
        views: 0,
        rating: 5.0,
        reviews: 0,
        image: "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=400",
        tags: ["community", "sharing"],
        createdAt: "Just now"
      }
    ];
    setCommunityRecipes(mockRecipes);
  };

  // Helper functions
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  const detectCategory = (title, description) => {
    const text = `${title} ${description}`.toLowerCase();
    if (text.includes('breakfast') || text.includes('pancake') || text.includes('egg')) return 'breakfast';
    if (text.includes('lunch') || text.includes('sandwich') || text.includes('salad')) return 'lunch';
    if (text.includes('dinner') || text.includes('pasta') || text.includes('chicken')) return 'dinner';
    if (text.includes('dessert') || text.includes('cake') || text.includes('cookie')) return 'dessert';
    if (text.includes('vegetarian') || text.includes('vegan')) return 'vegetarian';
    if (text.includes('quick') || text.includes('easy') || text.includes('15 min')) return 'quick';
    return 'all';
  };

  const formatTimeAgo = (dateString) => {
    if (!dateString) return 'Recently';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
  };

  const generateRecipeImage = (title) => {
    // Unsplash food images based on title keywords
    const keywords = {
      'cookie': 'photo-1499636136210-6f4ee915583e',
      'pasta': 'photo-1621996346565-e3dbc646d9a9',
      'salad': 'photo-1512621776951-a57141f2eefd',
      'chicken': 'photo-1598103442097-8b74394b95c6',
      'default': 'photo-1556910103-1c02745aae4d'
    };
    
    const keyword = Object.keys(keywords).find(k => title.toLowerCase().includes(k)) || 'default';
    return `https://images.unsplash.com/${keywords[keyword]}?w=400`;
  };

  // Filter recipes based on search and category
  const filteredRecipes = communityRecipes.filter(recipe => {
    const matchesSearch = searchQuery === '' || 
      recipe.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recipe.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recipe.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recipe.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || recipe.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const handleLikeRecipe = async (recipe) => {
    try {
      console.log('Liking recipe:', recipe.id);
      setCommunityRecipes(prev => prev.map(r => 
        r.id === recipe.id 
          ? { ...r, likes: r.likes + 1 }
          : r
      ));
      setSuccess(`Liked "${recipe.title}"!`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError('Failed to like recipe');
    }
  };

  const handleSaveRecipe = async (recipe) => {
    try {
      console.log('Saving recipe:', recipe.id);
      setCommunityRecipes(prev => prev.map(r => 
        r.id === recipe.id 
          ? { ...r, saves: r.saves + 1 }
          : r
      ));
      setSuccess(`"${recipe.title}" saved to your collection!`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError('Failed to save recipe');
    }
  };

  const handleViewRecipe = (recipe) => {
    setSelectedRecipe(recipe);
    setShowRecipeView(true);
    setCommunityRecipes(prev => prev.map(r => 
      r.id === recipe.id 
        ? { ...r, views: r.views + 1 }
        : r
    ));
  };

  const handleCloseRecipeView = () => {
    setShowRecipeView(false);
    setSelectedRecipe(null);
  };

  if (loading) {
    return (
      <div className="community-browser">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading community recipes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="community-browser">
      {showRecipeView && selectedRecipe ? (
        <SocialRecipeView
          recipe={selectedRecipe}
          onClose={handleCloseRecipeView}
          onSave={handleSaveRecipe}
          onLike={handleLikeRecipe}
        />
      ) : (
        <>
          <div className="community-header">
            <h2>Community Recipes</h2>
            <p className="header-subtitle">Discover amazing recipes shared by the community</p>
          </div>

          {error && (
            <div className="message error-message">
              ❌ {error}
              <button onClick={() => setError('')} className="close-message">×</button>
            </div>
          )}
          {success && (
            <div className="message success-message">
              ✅ {success}
              <button onClick={() => setSuccess('')} className="close-message">×</button>
            </div>
          )}

          <div className="community-filters">
            <div className="search-section">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search recipes, authors, or ingredients..."
                className="search-input"
              />
            </div>
            
            <div className="filter-section">
              <div className="category-filters">
                {categories.map(category => (
                  <button
                    key={category.id}
                    className={`category-button ${selectedCategory === category.id ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(category.id)}
                  >
                    {category.name}
                    <span className="category-count">({category.count})</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="recipes-section">
            <div className="results-header">
              <h3>
                {filteredRecipes.length} recipe{filteredRecipes.length !== 1 ? 's' : ''} found
                {selectedCategory !== 'all' && (
                  <span> in {categories.find(c => c.id === selectedCategory)?.name}</span>
                )}
              </h3>
            </div>

            {filteredRecipes.length === 0 ? (
              <div className="empty-results">
                <span className="empty-icon">🔍</span>
                <h3>No recipes found</h3>
                <p>Try adjusting your search or filter criteria</p>
              </div>
            ) : (
              <div className="recipes-grid">
                {filteredRecipes.map(recipe => (
                  <div key={recipe.id} className="community-recipe-card">
                    <div className="recipe-image">
                      <img src={recipe.image} alt={recipe.title} />
                      <div className="recipe-overlay">
                        <div className="recipe-stats">
                          <span>❤️ {recipe.likes}</span>
                          <span>💾 {recipe.saves}</span>
                          <span>👁️ {recipe.views}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="recipe-content">
                      <div className="recipe-header">
                        <h4>{recipe.title}</h4>
                        <div className="recipe-rating">
                          <span className="stars">⭐ {recipe.rating}</span>
                          <span className="review-count">({recipe.reviews})</span>
                        </div>
                      </div>
                      
                      <p className="recipe-description">{recipe.description}</p>
                      
                      <div className="recipe-meta">
                        <div className="author-info">
                          <div className="author-avatar">{recipe.authorInitials}</div>
                          <span className="author-name">{recipe.author}</span>
                        </div>
                        <span className="recipe-time">{recipe.createdAt}</span>
                      </div>
                      
                      <div className="recipe-details">
                        <span className="prep-time">⏱️ {recipe.prepTime}</span>
                        <span className="cook-time">🔥 {recipe.cookTime}</span>
                        <span className="difficulty">📊 {recipe.difficulty}</span>
                      </div>
                      
                      <div className="recipe-tags">
                        {recipe.tags.slice(0, 3).map(tag => (
                          <span key={tag} className="recipe-tag">#{tag}</span>
                        ))}
                      </div>
                    </div>
                    
                    <div className="recipe-actions">
                      <button 
                        className="action-button like-button"
                        onClick={() => handleLikeRecipe(recipe)}
                      >
                        ❤️
                      </button>
                      <button 
                        className="action-button save-button"
                        onClick={() => handleSaveRecipe(recipe)}
                      >
                        💾
                      </button>
                      <button 
                        className="action-button view-button"
                        onClick={() => handleViewRecipe(recipe)}
                      >
                        👁️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default CommunityBrowser;