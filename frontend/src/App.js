import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import SearchResults from './pages/SearchResults';
import RecipeDetail from './pages/RecipeDetail';
import Categories from './pages/Categories';

// Auth Components
import Login from './components/auth/Login';
import Register from './components/auth/Register';

// Main App - now the primary interface (RecipeDetail with new layout)
import MainApp from './pages/RecipeDetail';

import './components/Header.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="hungie-app">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Protected Routes - Main app is now the default */}
            <Route path="/" element={
              <ProtectedRoute>
                <MainApp />
              </ProtectedRoute>
            } />
            
            {/* Redirect old dashboard and any other paths to main app */}
            <Route path="/dashboard" element={<Navigate to="/" replace />} />
            <Route path="/home" element={<Navigate to="/" replace />} />
            
            {/* Legacy routes for other features - redirect to main for now */}
            <Route path="/search" element={<Navigate to="/" replace />} />
            <Route path="/recipe/:id" element={<Navigate to="/" replace />} />
            <Route path="/categories" element={<Navigate to="/" replace />} />
            
            {/* Catch all - redirect to main */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
