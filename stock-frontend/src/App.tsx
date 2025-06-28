import { Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "./features/auth/context/AuthContext"
import ProtectedRoute from "./features/auth/components/ProtectedRoute"
import LoginPage from "./features/auth/pages/LoginPage"
import RegisterPage from "./features/auth/pages/RegisterPage"
import LandingPage from "./pages/LandingPage"
import ProfilePage from "./features/auth/pages/ProfilePage"
import Watchlist from "./pages/Watchlist"
import PredictPage from "./pages/Predict"
import WatchlistTicker from "./pages/WatchlistTicker"

function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* 🌐 PUBLIC ROUTES - No authentication required */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<div>Forgot Password Page</div>} />
        <Route path="/landing" element={<LandingPage />} />

        {/* 🔐 PROTECTED ROUTES - Authentication required */}

        {/* User-specific landing */}
        <Route
          path="/landing/:userId"
          element={
            <ProtectedRoute requiresUserMatch={true}>
              <LandingPage />
            </ProtectedRoute>
          }
        />

        {/* User-specific watchlist */}
        <Route
          path="/watchlist/:userId"
          element={
            <ProtectedRoute requiresUserMatch={true}>
              <Watchlist />
            </ProtectedRoute>
          }
        />

        {/* User profile */}
        <Route
          path="/profile/:userId"
          element={
            <ProtectedRoute requiresUserMatch={true}>
              <ProfilePage />
            </ProtectedRoute>
          }
        />

        {/* User settings */}
        <Route
          path="/settings/:userId"
          element={
            <ProtectedRoute requiresUserMatch={true}>
              <div>Settings Page - User {window.location.pathname.split("/")[2]}</div>
            </ProtectedRoute>
          }
        />

        {/* Predict page */}
        <Route
          path="/predict"
          element={
            <ProtectedRoute>
              <PredictPage />
            </ProtectedRoute>
          }
        />

        {/* WatchlistTicker page */}
        <Route
          path="/watchlist/:userId/:ticker"
          element={
            <ProtectedRoute requiresUserMatch={true}>
              <WatchlistTicker />
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/landing" replace />} />
        <Route path="*" element={<Navigate to="/landing" replace />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
