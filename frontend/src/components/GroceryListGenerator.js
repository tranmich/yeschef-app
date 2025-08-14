import React, { useState, useEffect } from 'react';
import './GroceryListGenerator.css';
import { getApiUrl } from '../utils/api';

const GroceryListGenerator = ({ recipeIds = [], onClose }) => {
    const [groceryList, setGroceryList] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [viewMode, setViewMode] = useState('sections'); // 'sections', 'alphabetical', 'text'

    useEffect(() => {
        if (recipeIds.length > 0) {
            generateGroceryList();
        }
    }, [recipeIds]);

    const generateGroceryList = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${getApiUrl()}/api/grocery-list`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    recipe_ids: recipeIds
                })
            });

            const data = await response.json();

            if (data.success) {
                setGroceryList(data.grocery_list);
            } else {
                setError(data.message || 'Failed to generate grocery list');
            }
        } catch (err) {
            setError('Network error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text).then(() => {
            alert('Grocery list copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            alert('Failed to copy to clipboard');
        });
    };

    const exportToGoogleKeep = () => {
        if (!groceryList || !groceryList.google_keep_format) return;

        const items = groceryList.google_keep_format.join('\n');
        copyToClipboard(items);
    };

    const renderSectionView = () => {
        if (!groceryList || !groceryList.by_section) return null;

        return (
            <div className="grocery-sections">
                {Object.entries(groceryList.by_section).map(([section, items]) => (
                    <div key={section} className="grocery-section">
                        <h4 className="section-title">
                            {section.replace('_', ' ').toUpperCase()}
                        </h4>
                        <ul className="section-items">
                            {items.map((item, index) => (
                                <li key={index} className="grocery-item">
                                    <label className="grocery-item-label">
                                        <input
                                            type="checkbox"
                                            className="grocery-checkbox"
                                        />
                                        <span className="item-text">
                                            {item.display_text}
                                        </span>
                                        {item.recipes && item.recipes.length > 0 && (
                                            <span className="item-recipes">
                                                (from: {item.recipes.join(', ')})
                                            </span>
                                        )}
                                    </label>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
        );
    };

    const renderAlphabeticalView = () => {
        if (!groceryList || !groceryList.alphabetical) return null;

        return (
            <div className="grocery-alphabetical">
                <ul className="alphabetical-items">
                    {groceryList.alphabetical.map((item, index) => (
                        <li key={index} className="grocery-item">
                            <label className="grocery-item-label">
                                <input
                                    type="checkbox"
                                    className="grocery-checkbox"
                                />
                                <span className="item-text">
                                    {item.display_text}
                                </span>
                                {item.recipes && item.recipes.length > 0 && (
                                    <span className="item-recipes">
                                        (from: {item.recipes.join(', ')})
                                    </span>
                                )}
                            </label>
                        </li>
                    ))}
                </ul>
            </div>
        );
    };

    const renderTextView = () => {
        if (!groceryList || !groceryList.text_format) return null;

        return (
            <div className="grocery-text">
                <pre className="text-format">
                    {groceryList.text_format}
                </pre>
            </div>
        );
    };

    if (recipeIds.length === 0) {
        return (
            <div className="grocery-list-modal">
                <div className="grocery-list-content">
                    <div className="grocery-list-header">
                        <h3>🛒 Grocery List Generator</h3>
                        <button onClick={onClose} className="close-btn">❌</button>
                    </div>
                    <div className="no-recipes">
                        <p>Add some recipes to your meal plan to generate a grocery list!</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="grocery-list-modal">
            <div className="grocery-list-content">
                <div className="grocery-list-header">
                    <h3>🛒 Grocery List</h3>
                    <div className="header-controls">
                        <span className="recipe-count">
                            From {recipeIds.length} recipe{recipeIds.length !== 1 ? 's' : ''}
                        </span>
                        <button onClick={onClose} className="close-btn">❌</button>
                    </div>
                </div>

                {loading && (
                    <div className="loading-state">
                        <p>🔄 Generating grocery list...</p>
                    </div>
                )}

                {error && (
                    <div className="error-state">
                        <p>❌ {error}</p>
                        <button onClick={generateGroceryList} className="retry-btn">
                            🔄 Retry
                        </button>
                    </div>
                )}

                {groceryList && !loading && !error && (
                    <>
                        <div className="grocery-list-controls">
                            <div className="view-mode-selector">
                                <button
                                    className={`view-btn ${viewMode === 'sections' ? 'active' : ''}`}
                                    onClick={() => setViewMode('sections')}
                                >
                                    📂 By Section
                                </button>
                                <button
                                    className={`view-btn ${viewMode === 'alphabetical' ? 'active' : ''}`}
                                    onClick={() => setViewMode('alphabetical')}
                                >
                                    🔤 Alphabetical
                                </button>
                                <button
                                    className={`view-btn ${viewMode === 'text' ? 'active' : ''}`}
                                    onClick={() => setViewMode('text')}
                                >
                                    📄 Text Format
                                </button>
                            </div>

                            <div className="export-controls">
                                <button
                                    onClick={exportToGoogleKeep}
                                    className="export-btn google-keep-btn"
                                    title="Copy format suitable for Google Keep"
                                >
                                    📱 Copy for Google Keep
                                </button>
                                <button
                                    onClick={() => copyToClipboard(groceryList.text_format)}
                                    className="export-btn copy-btn"
                                >
                                    📋 Copy Text
                                </button>
                            </div>
                        </div>

                        <div className="grocery-list-summary">
                            <span>
                                📊 {groceryList.ingredient_count || 0} unique ingredients
                            </span>
                        </div>

                        <div className="grocery-list-body">
                            {viewMode === 'sections' && renderSectionView()}
                            {viewMode === 'alphabetical' && renderAlphabeticalView()}
                            {viewMode === 'text' && renderTextView()}
                        </div>

                        <div className="grocery-list-footer">
                            <p className="footer-text">
                                💡 Tip: Check off items as you shop!
                            </p>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default GroceryListGenerator;
