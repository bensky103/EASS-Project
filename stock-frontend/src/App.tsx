import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import ThemeToggle from './components/ThemeToggle'
import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import Watchlist from './pages/Watchlist'
import ProtectedRoute from './components/ProtectedRoute'

export default function App() {
  return (
    <BrowserRouter>
      {/* theme toggle button */}
      <ThemeToggle/>

      <Routes>
        <Route path="/login"    element={<Login/>} />
        <Route path="/register" element={<Register/>} />

        <Route path="/" element={
          <ProtectedRoute><Home/></ProtectedRoute>
        }/>
        <Route path="/watchlist" element={
          <ProtectedRoute><Watchlist/></ProtectedRoute>
        }/>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
