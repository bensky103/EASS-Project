"use client"

import type { ReactNode } from "react"
import { Navigate, useParams, useLocation } from "react-router-dom"
import { useContext } from "react"
import { AuthContext } from "../context/AuthContext"

interface ProtectedRouteProps {
  children: ReactNode
  requiresUserMatch?: boolean // If true, checks if the URL userId matches the logged-in user
  redirectTo?: string // Custom redirect path
}

export default function ProtectedRoute({
  children,
  requiresUserMatch = false,
  redirectTo = "/login",
}: ProtectedRouteProps) {
  const { user, isLoading } = useContext(AuthContext)!
  const { userId } = useParams()
  const location = useLocation()

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />
  }

  // If route requires user match (like /profile/123), verify the userId matches
  if (requiresUserMatch && userId && user.id !== userId) {
    // Redirect to user's own page instead of showing error
    const currentPath = location.pathname.split("/")[1] // Get 'watchlist', 'profile', etc.
    return <Navigate to={`/${currentPath}/${user.id}`} replace />
  }

  return <>{children}</>
}
