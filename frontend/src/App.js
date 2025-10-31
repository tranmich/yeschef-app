import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Public Pages
import LandingPage from './pages/LandingPageSimple';
import Story from './pages/Story';
import Privacy from './pages/Privacy';

// Admin Pages
import WaitlistAdmin from './pages/WaitlistAdmin';

// Auth Components
import Login from './components/auth/Login';
import Register from './components/auth/Register';

// Main App - now the primary interface (MainApp with new layout)
import MainApp from './pages/MainApp';

import './components/Header.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="hungie-app">
          <Routes>
            {/* Landing Page - Public */}
            <Route path="/" element={<LandingPage />} />
            
            {/* Public Routes */}
            <Route path="/story" element={<Story />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Routes - Main app */}
            <Route path="/app" element={
              <ProtectedRoute>
                <MainApp />
              </ProtectedRoute>
            } />

            {/* Admin Routes - Protected */}
            <Route path="/admin/waitlist" element={
              <ProtectedRoute>
                <WaitlistAdmin />
              </ProtectedRoute>
            } />

            {/* Redirect old routes to main app */}
            <Route path="/dashboard" element={<Navigate to="/app" replace />} />
            <Route path="/home" element={<Navigate to="/app" replace />} />

            {/* Legacy routes for other features - redirect to main for now */}
            <Route path="/search" element={<Navigate to="/app" replace />} />
            <Route path="/recipe/:id" element={<Navigate to="/app" replace />} />
            <Route path="/categories" element={<Navigate to="/app" replace />} />

            {/* Catch all - redirect to landing */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
