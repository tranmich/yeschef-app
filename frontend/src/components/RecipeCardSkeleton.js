/**
 * Recipe Card Skeleton
 * ====================
 * Loading placeholder for recipe cards
 * Shimmer animation for better perceived performance
 */

import React from 'react';
import './RecipeCardSkeleton.css';

const RecipeCardSkeleton = () => {
  return (
    <div className="recipe-card-skeleton">
      {/* Image skeleton */}
      <div className="skeleton-image shimmer"></div>
      
      {/* Content skeleton */}
      <div className="skeleton-content">
        <div className="skeleton-title shimmer"></div>
        <div className="skeleton-meta">
          <div className="skeleton-badge shimmer"></div>
          <div className="skeleton-time shimmer"></div>
        </div>
      </div>
    </div>
  );
};

export default RecipeCardSkeleton;
