import { Navigate } from 'react-router-dom'

interface Props { children: JSX.Element }

export default function ProtectedRoute({ children }: Props) {
  const isLoggedIn = Boolean(localStorage.getItem('token'))
  return isLoggedIn
    ? children
    : <Navigate to="/login" replace />
}

