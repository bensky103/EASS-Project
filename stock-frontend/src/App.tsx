import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import Watchlist from './pages/Watchlist'
import ProtectedRoute from './components/ProtectedRoute'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login"    element={<Login/>} />
        <Route path="/register" element={<Register/>} />

        <Route path="/" element={
          <ProtectedRoute><Home/></ProtectedRoute>
        }/>
        <Route path="/watchlist" element={
          <ProtectedRoute><Watchlist/></ProtectedRoute>
        }/>

        {/* catch-all: redirect unknown URLs */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
