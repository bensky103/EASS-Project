import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Home from './pages/Home'
import Watchlist from './pages/Watchlist'
import LandingPage from './pages/LandingPage'
import TestPage from './pages/TestPage'
import { AuthProvider } from './features/auth/context/AuthContext';
import LoginPage from './features/auth/pages/LoginPage';
import RegisterPage from './features/auth/pages/RegisterPage';
import { useAuth } from './features/auth/hooks/useAuth';

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage/>} />
      <Route path="/register" element={<RegisterPage/>} />
      <Route path="/test" element={<TestPage/>} />
      
      {/* Landing page for unauthenticated users */}
      <Route path="/landing" element={<LandingPage/>} />
      
      {/* Public routes (no ProtectedRoute) */}
      <Route path="/dashboard" element={<Home/>} />
      <Route path="/watchlist" element={<Watchlist/>} />
      
      {/* Root route - redirect based on auth status */}
      <Route path="/" element={
        isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/landing" replace />
      } />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
