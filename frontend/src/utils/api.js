import axios from "axios";

const getApiUrl = () => {
  // HARDCODE the correct URL to bypass all environment variable issues
  console.log("HARDCODED API URL: https://yeschefapp-production.up.railway.app");
  return "https://yeschefapp-production.up.railway.app";
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
    skipRecipeSearch: options.skipRecipeSearch || false
  }),
});

// Export the full API object with all functions
api.searchRecipes = searchRecipes;
api.getRecipe = getRecipe;
api.smartSearch = smartSearch;
