/**
 * Shared recipe formatting utilities for consistent display across all components
 * Ensures professional, clean formatting of recipe data everywhere
 */

export const formatRecipeText = {
  // Clean and format ingredients list
  formatIngredients: (ingredients) => {
    console.log('formatIngredients called with:', ingredients);
    console.log('formatIngredients type check:', typeof ingredients, Array.isArray(ingredients));
    
    if (!ingredients) return '';
    
    let processedIngredients = ingredients;
    
    // Handle JSON string input
    if (typeof ingredients === 'string') {
      // Check if it's a JSON array string
      if (ingredients.trim().startsWith('[') && ingredients.trim().endsWith(']')) {
        try {
          processedIngredients = JSON.parse(ingredients);
          console.log('Parsed JSON ingredients:', processedIngredients);
        } catch (e) {
          // If JSON parsing fails, treat as regular string
          console.warn('Failed to parse ingredients JSON:', ingredients);
          processedIngredients = ingredients;
        }
      }
    }
    
    // Handle array input (could be strings or objects)
    if (Array.isArray(processedIngredients)) {
      console.log('Processing ingredients array with length:', processedIngredients.length);
      
      const result = processedIngredients
        .filter(ingredient => {
          // Better filtering - check if ingredient exists and has usable content
          if (!ingredient) {
            console.log('Filtering out null/undefined ingredient');
            return false;
          }
          
          // If it's an object, check if it has meaningful properties
          if (typeof ingredient === 'object') {
            const hasUsefulData = ingredient.ingredient || ingredient.text || ingredient.name || ingredient.description;
            console.log('Filtering ingredient object:', ingredient, 'Has useful data:', !!hasUsefulData);
            return !!hasUsefulData;
          }
          
          // If it's a string, check if it's not empty or just '[object Object]'
          const stringValue = ingredient.toString().trim();
          const isValid = stringValue && stringValue !== '[object Object]';
          console.log('Filtering ingredient string:', stringValue, 'Valid:', isValid);
          return isValid;
        })
        .map((ingredient, index) => {
          console.log(`Processing ingredient ${index}:`, ingredient);
          let formatted = '';
          
          // Handle object ingredients
          if (typeof ingredient === 'object' && ingredient !== null) {
            console.log('Processing object ingredient with keys:', Object.keys(ingredient));
            // Try different common object structures
            if (ingredient.ingredient) {
              // This is the exact format we're seeing: {"ingredient": "text"}
              formatted = ingredient.ingredient;
              console.log('Used ingredient.ingredient:', formatted);
            } else if (ingredient.text) {
              formatted = ingredient.text;
              console.log('Used ingredient.text:', formatted);
            } else if (ingredient.name) {
              // Sometimes stored as name field
              const parts = [];
              if (ingredient.quantity) parts.push(ingredient.quantity);
              if (ingredient.unit) parts.push(ingredient.unit);
              parts.push(ingredient.name);
              formatted = parts.join(' ');
              console.log('Built from name parts:', formatted);
            } else if (ingredient.description) {
              formatted = ingredient.description;
              console.log('Used ingredient.description:', formatted);
            } else {
              // Try to extract meaningful text from object
              const values = Object.values(ingredient).filter(v => 
                v && typeof v === 'string' && v.trim() && v !== '[object Object]'
              );
              formatted = values.join(' ') || '[Unable to parse ingredient]';
              console.log('Used fallback values:', formatted);
            }
          } else {
            // Handle string ingredients
            formatted = ingredient.toString().trim();
            console.log('Used string ingredient:', formatted);
          }
          
          // Remove extra whitespace
          formatted = formatted.replace(/\s+/g, ' ');
          
          // Handle unicode characters
          formatted = formatted.replace(/\\u([0-9a-fA-F]{4})/g, (match, unicode) => {
            return String.fromCharCode(parseInt(unicode, 16));
          });
          
          // Standardize bullet points
          formatted = formatted.replace(/^[-*•]\s*/, '• ');
          if (!formatted.startsWith('• ') && !formatted.match(/^\d+/)) {
            formatted = '• ' + formatted;
          }
          
          console.log('Final formatted ingredient:', formatted);
          return formatted;
        })
        .join('\n');
      
      console.log('Final ingredients result:', result);
      return result;
    }
    
    // Handle string input
    return processedIngredients
      .split(/\n+/)
      .filter(line => line.trim())
      .map(ingredient => {
        let formatted = ingredient.trim();
        
        // Remove extra whitespace
        formatted = formatted.replace(/\s+/g, ' ');
        
        // Handle unicode characters
        formatted = formatted.replace(/\\u([0-9a-fA-F]{4})/g, (match, unicode) => {
          return String.fromCharCode(parseInt(unicode, 16));
        });
        
        // Standardize bullet points
        formatted = formatted.replace(/^[-*•]\s*/, '• ');
        if (!formatted.startsWith('• ') && !formatted.match(/^\d+/)) {
          formatted = '• ' + formatted;
        }
        
        return formatted;
      })
      .join('\n');
  },

  // Clean and format instructions
  formatInstructions: (instructions) => {
    if (!instructions) return '';
    
    let processedInstructions = instructions;
    
    // Handle JSON string input
    if (typeof instructions === 'string') {
      // Check if it's a JSON array string
      if (instructions.trim().startsWith('[') && instructions.trim().endsWith(']')) {
        try {
          processedInstructions = JSON.parse(instructions);
        } catch (e) {
          // If JSON parsing fails, treat as regular string
          console.warn('Failed to parse instructions JSON:', instructions);
          processedInstructions = instructions;
        }
      }
    }
    
    // Handle array input
    if (Array.isArray(processedInstructions)) {
      return processedInstructions
        .filter(step => step && step.toString().trim())
        .map((step, index) => {
          let formatted = step.toString().trim();
          
          // Remove extra whitespace
          formatted = formatted.replace(/\s+/g, ' ');
          
          // Handle unicode characters
          formatted = formatted.replace(/\\u([0-9a-fA-F]{4})/g, (match, unicode) => {
            return String.fromCharCode(parseInt(unicode, 16));
          });
          
          // Standardize numbering
          formatted = formatted.replace(/^\d+[.)]\s*/, '');
          formatted = formatted.replace(/^step\s*\d+:?\s*/i, '');
          
          return `${index + 1}. ${formatted}`;
        })
        .join('\n');
    }
    
    // Handle string input - including long concatenated strings
    let instructionText = processedInstructions;
    
    // If it's a long string with numbered steps run together, split it
    if (typeof instructionText === 'string' && instructionText.includes(' 1.') && instructionText.includes(' 2.')) {
      // Split on patterns like " 2.", " 3.", etc. but keep the numbers
      const steps = instructionText.split(/(\s+\d+\.)/).filter(part => part.trim());
      const formattedSteps = [];
      
      for (let i = 0; i < steps.length; i++) {
        const part = steps[i].trim();
        if (/^\d+\.$/.test(part)) {
          // This is a step number, combine with next part
          const stepNumber = part;
          const stepText = steps[i + 1] ? steps[i + 1].trim() : '';
          if (stepText) {
            formattedSteps.push(stepNumber + ' ' + stepText);
            i++; // Skip the next part since we used it
          }
        } else if (i === 0) {
          // First part might not have a number
          formattedSteps.push('1. ' + part);
        }
      }
      
      return formattedSteps
        .filter(step => step.trim())
        .map((step, index) => {
          let formatted = step.trim();
          
          // Handle unicode characters
          formatted = formatted.replace(/\\u([0-9a-fA-F]{4})/g, (match, unicode) => {
            return String.fromCharCode(parseInt(unicode, 16));
          });
          
          // Clean up the step text - remove existing numbers and re-add proper ones
          formatted = formatted.replace(/^\d+\.\s*/, '');
          
          return `${index + 1}. ${formatted}`;
        })
        .join('\n');
    }
    
    // Original string splitting logic for normal cases
    return instructionText
      .split(/\n+/)
      .filter(line => line.trim())
      .map((step, index) => {
        let formatted = step.trim();
        
        // Remove extra whitespace
        formatted = formatted.replace(/\s+/g, ' ');
        
        // Handle unicode characters
        formatted = formatted.replace(/\\u([0-9a-fA-F]{4})/g, (match, unicode) => {
          return String.fromCharCode(parseInt(unicode, 16));
        });
        
        // Standardize numbering
        formatted = formatted.replace(/^\d+[.)]\s*/, '');
        formatted = formatted.replace(/^step\s*\d+:?\s*/i, '');
        
        return `${index + 1}. ${formatted}`;
      })
      .join('\n');
  },

  // Format cooking time consistently
  formatTime: (timeString) => {
    if (!timeString) return '';
    
    // Convert various time formats to standard format
    let time = timeString.toString().toLowerCase();
    
    // Handle numeric minutes
    if (/^\d+$/.test(time)) {
      return `${time} min`;
    }
    
    // Standardize time formats
    time = time.replace(/(\d+)\s*hours?\s*(\d+)\s*min/, '$1h $2min');
    time = time.replace(/(\d+)\s*hours?/, '$1h');
    time = time.replace(/(\d+)\s*minutes?/, '$1min');
    time = time.replace(/(\d+)\s*mins?/, '$1min');
    time = time.replace(/\b(\d+)\s*h\s*(\d+)\s*m\b/, '$1h $2min');
    
    return time;
  },

  // Format servings consistently
  formatServings: (servings) => {
    if (!servings) return '';
    
    let formatted = servings.toString().toLowerCase();
    
    // Standardize serving formats
    if (/^\d+$/.test(formatted)) {
      return `Serves ${formatted}`;
    }
    
    formatted = formatted.replace(/serves?\s*(\d+)/, 'Serves $1');
    formatted = formatted.replace(/(\d+)\s*servings?/, 'Serves $1');
    formatted = formatted.replace(/(\d+)\s*people/, 'Serves $1');
    
    return formatted.charAt(0).toUpperCase() + formatted.slice(1);
  },

  // Format difficulty consistently
  formatDifficulty: (difficulty) => {
    if (!difficulty) return '';
    
    const formatted = difficulty.toString().toLowerCase();
    return formatted.charAt(0).toUpperCase() + formatted.slice(1);
  },

  // Format cuisine type consistently
  formatCuisineType: (cuisineType) => {
    if (!cuisineType) return '';
    
    return cuisineType
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }
};

export default formatRecipeText;
