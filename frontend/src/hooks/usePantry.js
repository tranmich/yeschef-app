import { useState, useEffect } from 'react';
import { getApiUrl } from '../utils/api';

/**
 * Custom hook for managing pantry data across components
 * Now uses backend API instead of localStorage for persistent, user-specific data
 */
export const usePantry = () => {
  const [pantryItems, setPantryItems] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load pantry from backend on component mount
  useEffect(() => {
    loadPantryFromAPI();
  }, []);

  // Load pantry items from backend API
  const loadPantryFromAPI = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const token = localStorage.getItem('authToken');
      const userStr = localStorage.getItem('user');
      
      if (!token || !userStr) {
        console.log('🔑 usePantry Hook - No auth token or user, skipping pantry load');
        setPantryItems([]);
        return;
      }
      
      const user = JSON.parse(userStr);
      const userId = user?.id;
      
      if (!userId) {
        console.log('🔑 usePantry Hook - No user ID, skipping pantry load');
        setPantryItems([]);
        return;
      }

      // V2 endpoint with user_id in path
      const response = await fetch(`${getApiUrl()}/api/v2/pantry/user/${userId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('🥫 usePantry Hook - Loaded from v2 API:', data.data?.items?.length || data.items?.length || 0, 'items');
        console.log('🥫 usePantry Hook - API response data:', data);
        
        // Handle v2 response structure
        const items = data.data?.items || data.items || [];
        setPantryItems(items);
      } else if (response.status === 401) {
        console.log('🔑 usePantry Hook - Unauthorized, clearing pantry');
        setPantryItems([]);
      } else {
        const errorText = await response.text();
        console.error('❌ usePantry Hook - Load API error:', response.status, errorText);
        throw new Error(`Failed to load pantry: ${response.status} - ${errorText}`);
      }
    } catch (err) {
      console.error('❌ usePantry Hook - Error loading from API:', err);
      setError('Failed to load pantry items');
      // Don't clear pantry on network errors, keep existing state
    } finally {
      setIsLoading(false);
    }
  };

  // Add item to pantry via API
  const addPantryItem = async (ingredient) => {
    let tempId = null; // Declare tempId in function scope
    try {
      console.log('🥫 usePantry Hook - Adding to pantry via v2 API:', ingredient);
      
      const token = localStorage.getItem('authToken');
      const userStr = localStorage.getItem('user');
      
      console.log('🔑 usePantry Hook - Auth token present:', !!token);
      
      setError(null);
      
      if (!token || !userStr) {
        setError('Please log in to manage pantry');
        return;
      }
      
      const user = JSON.parse(userStr);
      const userId = user?.id;
      
      if (!userId) {
        setError('User ID not found');
        return;
      }

      // Optimistic update
      tempId = Date.now(); // Assign to function-scoped variable
      const newItem = {
        id: tempId,
        name: ingredient.name,
        category: ingredient.category || 'other',
        amount: ingredient.amount || 'some',
        addedAt: new Date().toISOString()
      };

      setPantryItems(prev => {
        const exists = prev.find(item => item.name.toLowerCase() === ingredient.name.toLowerCase());
        if (exists) {
          console.log('⚠️ usePantry Hook - Item already in pantry:', ingredient.name);
          return prev;
        }
        console.log('✅ usePantry Hook - Optimistic update applied, current items:', prev.length + 1);
      return [...prev, newItem];
      });

      // Save to backend - v2 endpoint
      console.log('🌐 usePantry Hook - Making v2 API request to:', `${getApiUrl()}/api/v2/pantry`);
      const requestBody = JSON.stringify({
        user_id: userId,  // V2 requires user_id
        name: ingredient.name,
        category: ingredient.category || 'other',
        amount: ingredient.amount || 'some'
      });
      console.log('📤 usePantry Hook - Request body:', requestBody);
      
      const response = await fetch(`${getApiUrl()}/api/v2/pantry`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: requestBody
      });

      console.log('📡 usePantry Hook - API response status:', response.status);
      console.log('📡 usePantry Hook - API response ok:', response.ok);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ usePantry Hook - Added to v2 API successfully:', data);
        
        // Handle v2 response structure
        const returnedItem = data.data?.item || data.item;
        
        // Update with real ID from backend
        setPantryItems(prev => 
          prev.map(item => 
            item.id === tempId 
              ? { ...item, id: returnedItem?.id || tempId }
              : item
          )
        );
      } else {
        const errorText = await response.text();
        console.error('❌ usePantry Hook - API error response:', errorText);
        throw new Error(`Failed to add item: ${response.status} - ${errorText}`);
      }
      
    } catch (err) {
      console.error('❌ usePantry Hook - Error adding to API:', err);
      setError('Failed to add item to pantry');
      
      // Revert optimistic update
      if (tempId) {
        setPantryItems(prev => prev.filter(item => item.id !== tempId));
      }
    }
  };

  // Remove item from pantry via API
  const removePantryItem = async (itemId) => {
    console.log('🗑️ usePantry Hook - Removing from pantry via v2 API:', itemId);
    setError(null);
    
    const token = localStorage.getItem('authToken');
    const userStr = localStorage.getItem('user');
    
    if (!token || !userStr) {
      setError('Please log in to manage pantry');
      return;
    }
    
    const user = JSON.parse(userStr);
    const userId = user?.id;
    
    if (!userId) {
      setError('User ID not found');
      return;
    }

    // Get reference to item before try block
    const itemToRemove = pantryItems.find(item => item.id === itemId);
    
    try {
      // Optimistic update
      setPantryItems(prev => prev.filter(item => item.id !== itemId));

      // Remove from backend - v2 endpoint with user_id query param
      const response = await fetch(`${getApiUrl()}/api/v2/pantry/${itemId}?user_id=${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        console.log('✅ usePantry Hook - Removed from v2 API successfully');
      } else {
        throw new Error(`Failed to remove item: ${response.status}`);
      }
      
    } catch (err) {
      console.error('❌ usePantry Hook - Error removing from API:', err);
      setError('Failed to remove item from pantry');
      
      // Revert optimistic update
      if (itemToRemove) {
        setPantryItems(prev => [...prev, itemToRemove]);
      }
    }
  };

  // Update item amount via API
  const updatePantryAmount = async (itemId, newAmount) => {
    console.log('🔄 usePantry Hook - Updating amount via API:', itemId, newAmount);
    setError(null);
    
    const token = localStorage.getItem('authToken');
    if (!token) {
      setError('Please log in to manage pantry');
      return;
    }

    // Get old amount before try block
    const oldAmount = pantryItems.find(item => item.id === itemId)?.amount;
    
    try {
      // Optimistic update
      setPantryItems(prev =>
        prev.map(item =>
          item.id === itemId ? { ...item, amount: newAmount } : item
        )
      );

      // Update backend
      const response = await fetch(`${getApiUrl()}/api/pantry/${itemId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          amount: newAmount
        })
      });

      if (response.ok) {
        console.log('✅ usePantry Hook - Amount updated successfully');
      } else {
        throw new Error(`Failed to update amount: ${response.status}`);
      }
      
    } catch (err) {
      console.error('❌ usePantry Hook - Error updating amount:', err);
      setError('Failed to update item amount');
      
      // Revert optimistic update
      setPantryItems(prev =>
        prev.map(item =>
          item.id === itemId ? { ...item, amount: oldAmount } : item
        )
      );
    }
  };

  // Refresh pantry from API
  const refreshPantry = () => {
    loadPantryFromAPI();
  };

  // Get pantry items formatted for API
  const getPantryForAPI = () => {
    return pantryItems.map(item => ({
      name: item.name,
      category: item.category,
      amount: item.amount
    }));
  };

  // Clear all pantry items via API
  const clearPantry = async () => {
    console.log('🧹 usePantry Hook - Clearing pantry via API');
    setError(null);
    
    const token = localStorage.getItem('authToken');
    if (!token) {
      setError('Please log in to manage pantry');
      return;
    }

    // Save old items before try block
    const oldItems = [...pantryItems];
    
    try {
      // Optimistic update
      setPantryItems([]);

      // Clear backend (delete all items)
      const deletePromises = oldItems.map(item => 
        fetch(`${getApiUrl()}/api/pantry/${item.id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
      );

      await Promise.all(deletePromises);
      console.log('✅ usePantry Hook - Pantry cleared successfully');
      
    } catch (err) {
      console.error('❌ usePantry Hook - Error clearing pantry:', err);
      setError('Failed to clear pantry');
      
      // Revert optimistic update
      setPantryItems(oldItems);
    }
  };

  return {
    pantryItems,
    isLoading,
    error,
    addPantryItem,
    removePantryItem,
    updatePantryAmount,
    getPantryForAPI,
    clearPantry,
    refreshPantry,
    pantryCount: pantryItems.length,
    hasItems: pantryItems.length > 0
  };
};
