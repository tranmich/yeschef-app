import React from 'react';
import DraggableRecipeCard from './DraggableRecipeCard';
import './FavoritesPanel.css';

const FavoritesPanel = ({ favorites = [], onToggleFavorite, onRefresh }) => {
    const handleRefresh = () => {
        if (onRefresh) {
            onRefresh();
        }
    };

    return (
        <div className="favorites-panel">
            <div className="favorites-header">
                <h3>⭐ Favorites</h3>
                <div className="favorites-controls">
                    <span className="favorites-count">
                        {favorites.length} recipe{favorites.length !== 1 ? 's' : ''}
                    </span>
                    <button 
                        onClick={handleRefresh}
                        className="refresh-btn"
                        title="Refresh favorites"
                    >
                        🔄
                    </button>
                </div>
            </div>

            <div className="favorites-content">
                {favorites.length === 0 ? (
                    <div className="no-favorites">
                        <p>No favorite recipes yet!</p>
                        <p className="hint">
                            Click the ⭐ on any recipe to add it to your favorites
                        </p>
                    </div>
                ) : (
                    <div className="favorites-list">
                        {favorites.map(favorite => (
                            <DraggableRecipeCard
                                key={`favorite-${favorite.recipe_id}`}
                                recipe={{
                                    id: favorite.recipe_id,
                                    title: favorite.title,
                                    description: favorite.description,
                                    hands_on_time: favorite.hands_on_time,
                                    total_time: favorite.total_time,
                                    servings: favorite.servings,
                                    category: favorite.category,
                                    url: favorite.url,
                                    added_date: favorite.added_date,
                                    notes: favorite.notes
                                }}
                                id={favorite.recipe_id.toString()}
                                onToggleFavorite={onToggleFavorite}
                                isFavorite={true}
                                compact={true}
                            />
                        ))}
                    </div>
                )}
            </div>

            {favorites.length > 0 && (
                <div className="favorites-footer">
                    <p className="footer-hint">
                        💡 Drag favorites to your meal plan or click ⭐ to remove
                    </p>
                </div>
            )}
        </div>
    );
};

export default FavoritesPanel;
