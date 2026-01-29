import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ChatPage from './pages/ChatPage';

const ProtectedRoute = ({ children }) => {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
};

const PublicRoute = ({ children }) => {
  const { token } = useAuth();
  if (token) return <Navigate to="/app" replace />;
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          } />
          <Route path="/signup" element={
            <PublicRoute>
              <SignupPage />
            </PublicRoute>
          } />
          <Route path="/app" element={
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          } />
          <Route path="/" element={<Navigate to="/app" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
