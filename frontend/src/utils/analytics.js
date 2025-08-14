// Google Analytics Configuration
import ReactGA from 'react-ga4';

const GA_TRACKING_ID = process.env.REACT_APP_GA_TRACKING_ID;

export const initGA = () => {
  if (GA_TRACKING_ID && process.env.REACT_APP_ENVIRONMENT === 'production') {
    ReactGA.initialize(GA_TRACKING_ID);
    console.log('Google Analytics initialized');
  }
};

export const trackPageView = (path) => {
  if (GA_TRACKING_ID && process.env.REACT_APP_ENVIRONMENT === 'production') {
    ReactGA.send({ hitType: 'pageview', page: path });
  }
};

export const trackEvent = (category, action, label = '', value = 0) => {
  if (GA_TRACKING_ID && process.env.REACT_APP_ENVIRONMENT === 'production') {
    ReactGA.event({
      category,
      action,
      label,
      value
    });
  }
};

// Custom tracking events for Hungie
export const trackChatMessage = (messageType) => {
  trackEvent('Chat', 'Message Sent', messageType);
};

export const trackSubstitutionRequest = (ingredient) => {
  trackEvent('Substitutions', 'Request', ingredient);
};

export const trackRecipeView = (recipeId, recipeName) => {
  trackEvent('Recipes', 'View', recipeName, 1);
};

export const trackRecipeSearch = (searchTerm, resultsCount) => {
  trackEvent('Search', 'Recipe Query', searchTerm, resultsCount);
};

export default {
  initGA,
  trackPageView,
  trackEvent,
  trackChatMessage,
  trackSubstitutionRequest,
  trackRecipeView,
  trackRecipeSearch
};
