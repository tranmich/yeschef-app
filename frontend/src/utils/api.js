import axios from "axios";

const getApiUrl = () => {
  // Use environment variable if available, otherwise fallback to hardcoded URL
  const envUrl = process.env.REACT_APP_API_URL;
  const fallbackUrl = "https://yeschefapp-production.up.railway.app";

  const apiUrl = envUrl || fallbackUrl;
  console.log("🌐 Current window location:", window.location.href);
  console.log("🔧 Environment variables:", {
    REACT_APP_API_URL: process.env.REACT_APP_API_URL,
    REACT_APP_ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT,
    NODE_ENV: process.env.NODE_ENV
  });
  console.log("📡 API URL Source:", envUrl ? "Environment Variable" : "Hardcoded Fallback");
  console.log("📡 Final API URL:", apiUrl);

  return apiUrl;
};

const api = axios.create({
  baseURL: getApiUrl(),
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("authToken");
      localStorage.removeItem("user");
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export const apiCall = async (endpoint, options = {}) => {
  try {
    const config = {
      url: endpoint,
      method: options.method || "GET",
      ...options,
    };

    if (options.body) {
      config.data = JSON.parse(options.body);
    }

    const response = await api(config);
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data?.message || error.response.data?.error || "Request failed");
    }
    throw error;
  }
};

export default api;
export { api };
export { getApiUrl };

// Additional API functions for compatibility
export const searchRecipes = (query) => apiCall(`/api/search?q=${encodeURIComponent(query)}`);
export const getRecipe = (id) => apiCall(`/api/recipes/${id}`);
export const smartSearch = (message, context = '', options = {}) => apiCall('/api/smart-search', {
  method: 'POST',
  body: JSON.stringify({
    message,
    context,
    skipRecipeSearch: options.skipRecipeSearch || false,
    user_pantry: options.user_pantry || [],
    pantry_first: options.pantry_first || false
  }),
});

// Export the full API object with all functions
api.searchRecipes = searchRecipes;
api.getRecipe = getRecipe;
api.smartSearch = smartSearch;

// Add intelligent session-aware search function
api.searchRecipesIntelligent = async (query, sessionId, shownRecipeIds, pageSize = 5, options = {}) => {
  const apiUrl = getApiUrl();
  const response = await fetch(`${apiUrl}/api/search/intelligent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query.trim(),
      session_id: sessionId,
      shown_recipe_ids: shownRecipeIds,
      page_size: pageSize,
      user_pantry: options.user_pantry || [],
      pantry_first: options.pantry_first || false
    })
  });

  if (!response.ok) {
    throw new Error(`Search failed: ${response.status} ${response.statusText}`);
  }

  return await response.json();
};

// Add function to check if intelligent search is available
api.isIntelligentSearchAvailable = async () => {
  try {
    const apiUrl = getApiUrl();
    const response = await fetch(`${apiUrl}/api/search/intelligent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: 'test',
        session_id: 'test',
        shown_recipe_ids: [],
        page_size: 1
      })
    });
    return response.status !== 404;
  } catch {
    return false;
  }
};
