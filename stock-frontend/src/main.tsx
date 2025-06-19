import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'      // ← make sure this is AFTER any other imports

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
