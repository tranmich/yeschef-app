// Auto-Save System for Recipe Editing (Notion-style)
// Handles automatic saving of user changes without manual save buttons

class AutoSaveManager {
  constructor(apiClient) {
    this.api = apiClient;
    this.saveQueue = new Map(); // recipeId -> pendingChanges
    this.saveTimeouts = new Map(); // recipeId -> timeoutId
    this.saveDelay = 2000; // 2 seconds after user stops typing
    this.isOnline = navigator.onLine;
    this.offlineQueue = new Map(); // Store changes when offline
    
    // Listen for online/offline events
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());
    
    // Save on page unload
    window.addEventListener('beforeunload', () => this.saveAllPending());
  }
  
  // Main method: Queue a change for auto-save
  queueSave(recipeId, changes) {
    console.log(`📝 Queuing auto-save for recipe ${recipeId}:`, changes);
    
    // Merge with existing pending changes
    const existingChanges = this.saveQueue.get(recipeId) || {};
    const mergedChanges = { ...existingChanges, ...changes, id: recipeId };
    this.saveQueue.set(recipeId, mergedChanges);
    
    // Clear existing timeout
    if (this.saveTimeouts.has(recipeId)) {
      clearTimeout(this.saveTimeouts.get(recipeId));
    }
    
    // Set new timeout for saving
    const timeoutId = setTimeout(() => {
      this.executeSave(recipeId);
    }, this.saveDelay);
    
    this.saveTimeouts.set(recipeId, timeoutId);
    
    // Show saving indicator
    this.showSavingIndicator(recipeId, 'pending');
  }
  
  // Execute the actual save
  async executeSave(recipeId) {
    const changes = this.saveQueue.get(recipeId);
    if (!changes) return;
    
    console.log(`💾 Auto-saving recipe ${recipeId}...`);
    this.showSavingIndicator(recipeId, 'saving');
    
    try {
      if (this.isOnline) {
        // Online: Save to server
        const result = await this.api.editRecipe(recipeId, changes);
        
        if (result.success) {
          console.log(`✅ Auto-save successful for recipe ${recipeId}`);
          this.showSavingIndicator(recipeId, 'saved');
          
          // Clear from queue
          this.saveQueue.delete(recipeId);
          this.saveTimeouts.delete(recipeId);
          
          // Handle copy-on-write scenario
          if (result.was_copied) {
            console.log(`📋 Recipe was copied, new ID: ${result.recipe_id}`);
            // Update UI to reflect new recipe ID
            this.handleRecipeCopied(recipeId, result.recipe_id);
          }
        } else {
          throw new Error(result.error || 'Save failed');
        }
      } else {
        // Offline: Store in local queue
        this.offlineQueue.set(recipeId, changes);
        this.showSavingIndicator(recipeId, 'offline');
        console.log(`📴 Stored offline changes for recipe ${recipeId}`);
      }
      
    } catch (error) {
      console.error(`❌ Auto-save failed for recipe ${recipeId}:`, error);
      this.showSavingIndicator(recipeId, 'error');
      
      // Retry after delay
      setTimeout(() => {
        this.executeSave(recipeId);
      }, 5000);
    }
  }
  
  // Handle coming back online
  async handleOnline() {
    this.isOnline = true;
    console.log('🌐 Back online - syncing offline changes...');
    
    // Save all offline changes
    for (const [recipeId, changes] of this.offlineQueue) {
      this.saveQueue.set(recipeId, changes);
      this.executeSave(recipeId);
    }
    
    this.offlineQueue.clear();
  }
  
  // Handle going offline
  handleOffline() {
    this.isOnline = false;
    console.log('📴 Gone offline - changes will be queued');
  }
  
  // Save all pending changes (called on page unload)
  saveAllPending() {
    for (const [recipeId, changes] of this.saveQueue) {
      // Use synchronous request for page unload
      navigator.sendBeacon('/api/recipes/' + recipeId + '/edit', 
        JSON.stringify(changes));
    }
  }
  
  // Show visual indicators for save status
  showSavingIndicator(recipeId, status) {
    const indicators = {
      pending: { text: '✏️ Editing...', color: '#ffa500' },
      saving: { text: '💾 Saving...', color: '#007bff' },
      saved: { text: '✅ Saved', color: '#28a745' },
      offline: { text: '📴 Saved offline', color: '#6c757d' },
      error: { text: '❌ Save error', color: '#dc3545' }
    };
    
    const indicator = indicators[status];
    const element = document.querySelector(`[data-recipe-id="${recipeId}"] .save-indicator`);
    
    if (element) {
      element.textContent = indicator.text;
      element.style.color = indicator.color;
      
      // Hide "saved" indicator after 2 seconds
      if (status === 'saved') {
        setTimeout(() => {
          element.textContent = '';
        }, 2000);
      }
    }
  }
  
  // Handle when a template recipe is copied for editing
  handleRecipeCopied(oldRecipeId, newRecipeId) {
    // Update URL without page reload
    if (window.location.pathname.includes(oldRecipeId)) {
      const newUrl = window.location.pathname.replace(oldRecipeId, newRecipeId);
      window.history.replaceState({}, '', newUrl);
    }
    
    // Update any recipe ID references in the DOM
    document.querySelectorAll(`[data-recipe-id="${oldRecipeId}"]`).forEach(el => {
      el.setAttribute('data-recipe-id', newRecipeId);
    });
    
    // Show notification
    this.showNotification('Recipe copied to your personal collection for editing');
  }
  
  // Show user notifications
  showNotification(message) {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.className = 'auto-save-toast';
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #28a745;
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      z-index: 10000;
      animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.remove();
    }, 3000);
  }
}

// React Hook for Auto-Save Integration
export const useAutoSave = (recipeId, initialData) => {
  const [data, setData] = useState(initialData);
  const [saveStatus, setSaveStatus] = useState('saved');
  const autoSaveManager = useRef(null);
  
  useEffect(() => {
    // Initialize auto-save manager
    autoSaveManager.current = new AutoSaveManager(api);
    
    return () => {
      // Save any pending changes on unmount
      if (autoSaveManager.current) {
        autoSaveManager.current.saveAllPending();
      }
    };
  }, []);
  
  const updateData = useCallback((changes) => {
    setData(prev => ({ ...prev, ...changes }));
    setSaveStatus('pending');
    
    // Queue auto-save
    if (autoSaveManager.current) {
      autoSaveManager.current.queueSave(recipeId, changes);
    }
  }, [recipeId]);
  
  return {
    data,
    updateData,
    saveStatus
  };
};

// CSS for auto-save indicators
const autoSaveStyles = `
  .save-indicator {
    font-size: 12px;
    margin-left: 8px;
    font-weight: 500;
  }
  
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  
  .auto-save-toast {
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }
`;

// Add styles to page
const styleSheet = document.createElement('style');
styleSheet.textContent = autoSaveStyles;
document.head.appendChild(styleSheet);

export default AutoSaveManager;
