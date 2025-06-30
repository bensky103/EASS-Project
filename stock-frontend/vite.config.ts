import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  define: {
    'process.env': {}
  },
  server: {
    proxy: {
      // Auth service (FastAPI) - user, auth, and fetch endpoints
      '/auth': 'http://10.0.0.27:8001',
      '/user': 'http://10.0.0.27:8001',
      '/fetch': 'http://10.0.0.27:8002', // <-- Route /fetch to stock data fetching service
      // Stock data fetching service (for explicit /stock_data_fetching path)
      '/stock_data_fetching': 'http://10.0.0.27:8002',
      // LLM service
      '/llm_service': {
        target: 'http://10.0.0.27:8003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/llm_service/, ''),
      },
      // Ollama (LLM backend)
      '/ollama': 'http://10.0.0.27:11434',
      // Legacy/compatibility (if frontend expects /stock)
      '/stock': 'http://10.0.0.27:8002',
      // Add more proxies as needed
    },
  },
})
