import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { apiCall } from '../utils/api';

/**
 * AuthContext - V2 API Migration Complete
 * 
 * Migrated to V2 auth endpoints on Oct 31, 2025
 * Changes:
 * - /api/auth/* → /api/v2/auth/*
 * - Token: access_token → data.token
 * - User: response.user → data.user
 * - Response format: { success, data, message }
 * 
 * V2 Features:
 * - ✅ Email validation
 * - ✅ Password strength validation (6+ chars)
 * - ✅ Consistent error responses
 * - ✅ Better security
 */

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  // Configure axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is logged in on app start
  useEffect(() => {
    const initializeAuth = async () => {
      if (typeof window !== 'undefined') {
        const savedToken = localStorage.getItem('authToken');
        if (savedToken) {
          try {
            setToken(savedToken);
            // V2 API: /api/v2/auth/me
            const response = await apiCall('/api/v2/auth/me', {
              method: 'GET',
              headers: {
                'Authorization': `Bearer ${savedToken}`
              }
            });
            
            // V2 response format: { success, data: { user } }
            if (response.success && response.data) {
              setUser(response.data.user);
            } else {
              logout();
            }
          } catch (error) {
            console.error('Token validation failed:', error);
            logout();
          }
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    try {
      // V2 API: /api/v2/auth/login
      const response = await apiCall('/api/v2/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email,
          password
        })
      });

      // V2 response format: { success, data: { token, user }, message }
      if (response.success && response.data) {
        const { token: authToken, user: userData } = response.data;

        // Store token and user data (with SSR safety)
        if (typeof window !== 'undefined') {
          localStorage.setItem('authToken', authToken);
        }
        setToken(authToken);
        setUser(userData);

        return { success: true, user: userData };
      } else {
        return {
          success: false,
          message: response.error || 'Login failed'
        };
      }
    } catch (error) {
      console.error('Login failed:', error);
      return {
        success: false,
        message: error.message || 'Login failed'
      };
    }
  };

  const register = async (name, email, password) => {
    try {
      // V2 API: /api/v2/auth/register
      const response = await apiCall('/api/v2/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name,
          email,
          password
        })
      });

      // V2 response format: { success, data: { token, user }, message }
      if (response.success && response.data) {
        const { token: authToken, user: userData } = response.data;

        // Store token and user data (with SSR safety)
        if (typeof window !== 'undefined') {
          localStorage.setItem('authToken', authToken);
        }
        setToken(authToken);
        setUser(userData);

        return { success: true, user: userData };
      } else {
        return {
          success: false,
          message: response.error || 'Registration failed'
        };
      }
    } catch (error) {
      console.error('Registration failed:', error);
      return {
        success: false,
        message: error.message || 'Registration failed'
      };
    }
  };

  const logout = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('authToken');
    }
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
    console.log('User logged out and token cleared');
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!token && !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
