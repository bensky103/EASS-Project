import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'      // ← make sure this is AFTER any other imports
import { ThemeProvider } from '@/components/theme-provider'
import { BrowserRouter } from 'react-router-dom'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
)
