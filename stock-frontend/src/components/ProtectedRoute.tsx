import React from 'react';
import { Navigate } from 'react-router-dom'

interface Props extends React.PropsWithChildren<{}> {}

export default function ProtectedRoute({ children }: Props) {
  const isLoggedIn = Boolean(localStorage.getItem('token'))
  return isLoggedIn
    ? <>{children}</>
    : <Navigate to="/login" replace />
}

