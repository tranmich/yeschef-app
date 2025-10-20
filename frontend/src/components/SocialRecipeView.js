import React, { useState, useEffect } from 'react';
import './SocialRecipeView.css';

const SocialRecipeView = ({ recipe, onClose, onSave, onLike }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [userRating, setUserRating] = useState(0);
  const [isLiked, setIsLiked] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (recipe) {
      loadRecipeData();
    }
  }, [recipe]);

  const loadRecipeData = async () => {
    setLoading(true);
    
    try {
      // Mock data for comments and interactions
      const mockComments = [
        {
          id: 1,
          author: 'FoodieKim',
          authorAvatar: 'FK',
          text: 'This recipe is absolutely amazing! Made it for my family and everyone loved it. The flavors are perfectly balanced.',
          rating: 5,
          postedAt: '2 days ago',
          likes: 12,
          helpful: true
        },
        {
          id: 2,
          author: 'ChefMaster',
          authorAvatar: 'CM',
          text: 'Great recipe! I added a bit more garlic and it was perfect. Thanks for sharing!',
          rating: 4,
          postedAt: '1 week ago',
          likes: 8,
          helpful: false
        },
        {
          id: 3,
          author: 'HealthyEater23',
          authorAvatar: 'HE',
          text: 'Love how healthy this is while still being delicious. I substituted the cream with coconut milk and it worked great.',
          rating: 5,
          postedAt: '2 weeks ago',
          likes: 15,
          helpful: true
        }
      ];
      
      setComments(mockComments);
      setIsLiked(false); // In real implementation, check if user has liked
      setIsSaved(false); // In real implementation, check if user has saved
    } catch (error) {
      setError('Failed to load recipe data');
      console.error('Error loading recipe data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitComment = async () => {
    if (!newComment.trim()) {
      setError('Please enter a comment');
      return;
    }
    
    if (userRating === 0) {
      setError('Please add a rating with your comment');
      return;
    }
    
    try {
      const comment = {
        id: Date.now(),
        author: 'You',
        authorAvatar: 'YU',
        text: newComment.trim(),
        rating: userRating,
        postedAt: 'Just now',
        likes: 0,
        helpful: false
      };
      
      setComments(prev => [comment, ...prev]);
      setNewComment('');
      setUserRating(0);
      setSuccess('Comment added successfully!');
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError('Failed to add comment');
    }
  };

  const handleLikeComment = async (commentId) => {
    try {
      setComments(prev => prev.map(comment => 
        comment.id === commentId 
          ? { ...comment, likes: comment.likes + 1 }
          : comment
      ));
    } catch (error) {
      setError('Failed to like comment');
    }
  };

  const handleToggleLike = async () => {
    try {
      setIsLiked(!isLiked);
      if (onLike) {
        onLike(recipe.id);
      }
      
      setSuccess(isLiked ? 'Removed from favorites' : 'Added to favorites!');
      setTimeout(() => setSuccess(''), 2000);
    } catch (error) {
      setError('Failed to update like status');
    }
  };

  const handleToggleSave = async () => {
    try {
      setIsSaved(!isSaved);
      if (onSave) {
        onSave(recipe);
      }
      
      setSuccess(isSaved ? 'Removed from collection' : 'Saved to your collection!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError('Failed to save recipe');
    }
  };

  const handleShare = async () => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: recipe.title,
          text: recipe.description,
          url: window.location.href
        });
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.writeText(window.location.href);
        setSuccess('Recipe link copied to clipboard!');
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (error) {
      setError('Failed to share recipe');
    }
  };

  const renderStars = (rating, interactive = false, onSelect = null) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <button
          key={i}
          className={`star ${i <= rating ? 'filled' : ''} ${interactive ? 'interactive' : ''}`}
          onClick={interactive ? () => onSelect(i) : undefined}
          disabled={!interactive}
        >
          ⭐
        </button>
      );
    }
    return <div className="stars-container">{stars}</div>;
  };

  const renderRecipeContent = () => {
    // Mock detailed recipe content
    const ingredients = [
      '2 lbs chicken breast, diced',
      '1 large onion, chopped',
      '3 cloves garlic, minced',
      '1 cup heavy cream',
      '2 tbsp olive oil',
      '1 tsp salt',
      '1/2 tsp black pepper',
      '1 tsp paprika',
      '2 tbsp fresh herbs'
    ];

    const instructions = [
      'Heat olive oil in a large skillet over medium-high heat.',
      'Add diced chicken and cook until golden brown on all sides, about 6-8 minutes.',
      'Add chopped onion and cook until softened, about 3-4 minutes.',
      'Add minced garlic and cook for another minute until fragrant.',
      'Season with salt, pepper, and paprika.',
      'Pour in heavy cream and bring to a gentle simmer.',
      'Reduce heat and let simmer for 10-15 minutes until sauce thickens.',
      'Stir in fresh herbs and serve immediately.',
      'Enjoy your delicious meal!'
    ];

    return (
      <div className="recipe-content">
        <div className="ingredients-section">
          <h3>🛒 Ingredients</h3>
          <ul className="ingredients-list">
            {ingredients.map((ingredient, index) => (
              <li key={index} className="ingredient-item">
                {ingredient}
              </li>
            ))}
          </ul>
        </div>

        <div className="instructions-section">
          <h3>👩‍🍳 Instructions</h3>
          <ol className="instructions-list">
            {instructions.map((instruction, index) => (
              <li key={index} className="instruction-step">
                {instruction}
              </li>
            ))}
          </ol>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="social-recipe-loading">
        <div className="loading-spinner"></div>
        <p>Loading recipe...</p>
      </div>
    );
  }

  return (
    <div className="social-recipe-view">
      <div className="recipe-header">
        <div className="header-top">
          <button className="close-button" onClick={onClose}>
            ← Back to Community
          </button>
          <div className="recipe-actions">
            <button
              className={`action-button ${isLiked ? 'liked' : ''}`}
              onClick={handleToggleLike}
              title={isLiked ? 'Remove from favorites' : 'Add to favorites'}
            >
              ❤️ {isLiked ? 'Liked' : 'Like'}
            </button>
            <button
              className={`action-button ${isSaved ? 'saved' : ''}`}
              onClick={handleToggleSave}
              title={isSaved ? 'Remove from collection' : 'Save to collection'}
            >
              💾 {isSaved ? 'Saved' : 'Save'}
            </button>
            <button
              className="action-button"
              onClick={handleShare}
              title="Share recipe"
            >
              📤 Share
            </button>
          </div>
        </div>

        <div 
          className="recipe-banner"
          style={{ backgroundColor: recipe.community_background }}
        >
          <div className="banner-content">
            <div className="recipe-icon-large">{recipe.community_icon}</div>
            <div className="recipe-info">
              <h1 className="recipe-title">{recipe.title}</h1>
              <p className="recipe-description">{recipe.description}</p>
              
              <div className="recipe-meta">
                <div className="meta-grid">
                  <div className="meta-item">
                    <span className="meta-label">Difficulty:</span>
                    <span className="meta-value">{recipe.difficulty}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Prep Time:</span>
                    <span className="meta-value">{recipe.prep_time}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Cook Time:</span>
                    <span className="meta-value">{recipe.cook_time}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Servings:</span>
                    <span className="meta-value">{recipe.servings}</span>
                  </div>
                </div>
                
                <div className="rating-section">
                  {renderStars(recipe.rating)}
                  <span className="rating-text">
                    {recipe.rating} ({recipe.reviews} reviews)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="author-section">
          <div className="author-info">
            <div className="author-avatar-large">{recipe.authorAvatar}</div>
            <div className="author-details">
              <h3 className="author-name">{recipe.author}</h3>
              <p className="shared-info">Shared {recipe.sharedAt}</p>
            </div>
          </div>
          
          <div className="recipe-stats">
            <div className="stat-item">
              <span className="stat-number">{recipe.likes}</span>
              <span className="stat-label">Likes</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{recipe.saves}</span>
              <span className="stat-label">Saves</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{comments.length}</span>
              <span className="stat-label">Comments</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
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

      {/* Recipe Content */}
      {renderRecipeContent()}

      {/* Comments Section */}
      <div className="comments-section">
        <h3>💬 Reviews & Comments ({comments.length})</h3>
        
        {/* Add Comment Form */}
        <div className="add-comment-form">
          <h4>Share your experience</h4>
          <div className="rating-input">
            <span>Your rating:</span>
            {renderStars(userRating, true, setUserRating)}
          </div>
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="How was this recipe? Share your thoughts and any modifications you made..."
            className="comment-input"
            rows={3}
          />
          <button
            className="submit-comment-button"
            onClick={handleSubmitComment}
            disabled={!newComment.trim() || userRating === 0}
          >
            📝 Add Review
          </button>
        </div>

        {/* Comments List */}
        <div className="comments-list">
          {comments.length === 0 ? (
            <div className="no-comments">
              <p>No reviews yet. Be the first to share your experience!</p>
            </div>
          ) : (
            comments.map(comment => (
              <div key={comment.id} className="comment-item">
                <div className="comment-header">
                  <div className="commenter-info">
                    <div className="commenter-avatar">{comment.authorAvatar}</div>
                    <div className="commenter-details">
                      <h5 className="commenter-name">{comment.author}</h5>
                      <div className="comment-meta">
                        {renderStars(comment.rating)}
                        <span className="comment-time">{comment.postedAt}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="comment-actions">
                    <button
                      className="like-comment-button"
                      onClick={() => handleLikeComment(comment.id)}
                    >
                      👍 {comment.likes}
                    </button>
                  </div>
                </div>
                
                <div className="comment-content">
                  <p>{comment.text}</p>
                  {comment.helpful && (
                    <span className="helpful-badge">✨ Marked as helpful</span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default SocialRecipeView;