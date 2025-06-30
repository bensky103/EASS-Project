# 📈 EASS Project – Microservice Stock Platform

A modern, microservice-based platform for stock data analysis, prediction, and portfolio management. Built with Python (FastAPI), React (Vite), and Docker, it features modular services for authentication, stock data fetching, and LLM-powered stock analysis, all orchestrated for scalability and ease of development.

---

## 📝 1. Project Description & Purpose

EASS Project is designed to empower traders and investors with:
- 🤖 **AI-powered stock predictions** using advanced LLMs (Ollama/LLaMA 3)
- 📊 **Comprehensive stock data**: technical indicators, fundamentals, and news sentiment
- 🔐 **User authentication and management**
- 💻 **Seamless frontend experience** for making predictions, managing watchlists, and viewing analytics

The platform is fully containerized for local development and production, and is extensible for future features (e.g., portfolio optimization, alerts, etc.).

---

## 🛠️ 2. Technologies Used

- 🐍 **Backend**: Python, FastAPI, Pydantic, httpx, pandas, joblib, scikit-learn, yfinance
- ⚛️ **Frontend**: React, Vite, TypeScript, Tailwind CSS, shadcn/ui, axios, recharts
- 🧠 **AI/LLM**: Ollama (LLaMA 3), Alpha Vantage API
- 🍃 **Database**: MongoDB (via Motor)
- 🛡️ **Authentication**: JWT, python-jose, passlib
- 🐳 **Containerization**: Docker, Docker Compose
- 🌐 **Web Server/Proxy**: Nginx
- 🧪 **Testing**: pytest, httpx, React Testing Library, Jest, Cypress/Playwright
- ⚙️ **Other**: CORS, Logging, dotenv, etc.

---

## 🏗️ 3. Design Pattern & Architecture

- 🏢 **Microservices architecture**: Each service is independently deployable and communicates via HTTP APIs
- 🧩 **Separation of concerns**: Auth, data fetching, and LLM logic are isolated
- 🗃️ **Stateless APIs**: Services are stateless, with state managed externally (MongoDB)
- 🐳 **Docker Compose orchestration**: All services (including frontend, backend, LLM, and database) can be spun up together
- 🌐 **Nginx**: Serves frontend and proxies API requests to the correct backend service

### 📁 Directory Structure
```
EASS-Project-main/
├── app/                  # Model service (GRU predictor)
├── auth_service/         # User authentication microservice
├── stock_data_fetching/  # Stock data fetching and feature engineering
├── llm_service/          # LLM-powered stock analysis
├── stock-frontend/       # React frontend
├── nginx/                # Nginx config for serving/proxying
├── docker-compose.yml    # Orchestrates all services
└── ...
```

---

## 🧩 4. Microservices Overview

### 1. 🔐 **Auth Service**
- **Tech**: FastAPI, MongoDB
- **Purpose**: Handles user registration, login, JWT authentication, and user management (watchlist, profile, etc.)
- **How it works**: Provides `/auth/*` and `/user/*` endpoints. Stores user data in MongoDB. Secures endpoints with JWT.

### 2. 📊 **Stock Data Fetching Service**
- **Tech**: FastAPI, pandas, Alpha Vantage API
- **Purpose**: Fetches and computes technical indicators, volume features, fundamentals, and news sentiment for a given stock symbol
- **How it works**: Accepts requests for stock data, fetches from Alpha Vantage, computes features, and returns a unified data object for prediction

### 3. 🤖 **LLM Service**
- **Tech**: FastAPI, httpx, Pydantic, Ollama (LLaMA 3)
- **Purpose**: Accepts stock features and optional news sentiment, formats a prompt, and queries an LLM for a prediction (BUY/SELL/HOLD, confidence, reasoning, price forecast)
- **How it works**: Receives features, builds a prompt, calls Ollama, parses and returns the LLM's structured response

### 4. 💻 **Frontend**
- **Tech**: React, Vite, TypeScript, Tailwind CSS, shadcn/ui
- **Purpose**: Provides a modern UI for users to register/login, manage watchlists, make predictions, and view analytics
- **How it works**: Communicates with backend APIs via REST. Handles authentication, prediction flows, and data visualization

---

## 📬 5. API Endpoints & Usage

### 🔐 Auth Service
- `GET /` – Returns `{ "status": "ok" }`
- `GET /health` – Returns `{ "status": "ok" }`
- `POST /auth/register` – Register a new user
- `POST /auth/login` – Login and receive JWT
- `GET/POST /user/watchlist` – Manage user watchlist (add/remove/list tickers)
- `GET/PUT /user/profile` – Get or update user profile

### 📊 Stock Data Fetching Service
- `GET /health` – Returns service health
- `POST /fetch` – Fetch stock data
  - **Request:**
    ```json
    {
      "symbol": "AAPL",
      "timeframe": "daily",
      "date": "2024-07-01"
    }
    ```
  - **Response:** Technical indicators, volume features, fundamentals, news sentiment, etc.
- `POST /predict` – Predict using features collected by /fetch

### 🤖 LLM Service
- `GET /health` – Returns service health
- `POST /predict` – LLM-based stock prediction
  - **Request:**
    ```json
    {
      "symbol": "AAPL",
      "features": { /* see StockFeatures schema */ },
      "time_frame": "next 5 trading days"
    }
    ```
  - **Response:**
    ```json
    {
      "symbol": "AAPL",
      "recommendation": "BUY",
      "confidence": 0.85,
      "reasoning": "...",
      "time_frame": "next 5 trading days",
      "price_predictions": { "2024-07-02": 175.5, ... },
      "timestamp": "..."
    }
    ```

---

## 🐳 6. Docker & Local Development

### ⚡ Prerequisites
- 🐳 Docker & Docker Compose installed

### ▶️ Running All Services
1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```
2. **Access services at their respective ports:**
   - 🌐 Frontend: [http://localhost](http://localhost)
   - 🔐 Auth: [http://localhost:8001](http://localhost:8001)
   - 📊 Stock Data: [http://localhost:8002](http://localhost:8002)
   - 🤖 LLM: [http://localhost:8003](http://localhost:8003)

### ⏹️ Stopping Services
```bash
docker-compose down
```

### 📝 Notes
- 🌐 Nginx serves the frontend and proxies API requests to the correct backend service
- 🍃 MongoDB and 🤖 Ollama run as containers
- 🔄 All services are hot-reloadable for development

---

## 💻 7. Frontend Explanation & User Guide

### ✨ Features
- 🏠 **Landing Page**: Overview, features, and call-to-action
- 🔐 **Authentication**: Register, login, and protected routes
- ⭐ **Watchlist**: Add/remove stocks, view predictions
- 🤖 **Prediction**: Enter a ticker, fetch data, and generate AI-powered predictions
- 👤 **Profile**: View and edit user profile, change password, set preferences
- 📱 **Responsive UI**: Modern design with Tailwind CSS and shadcn/ui

### 🚀 Usage
1. **Install dependencies**
   ```bash
   cd stock-frontend
   npm install
   ```
2. **Run in development mode**
   ```bash
   npm run dev
   ```
   The app will be available at [http://localhost:5173](http://localhost:5173) (or as proxied by Docker/Nginx)
3. **Build for production**
   ```bash
   npm run build
   ```
4. **Run tests**
   ```bash
   npm test
   # or for E2E: npx cypress open
   ```

### 🧭 User Flow
- 🔐 Register or log in
- ⭐ Add stocks to your watchlist
- 🤖 Make predictions using the AI-powered prediction tool
- 📈 View prediction history and analytics
- 👤 Manage your profile and preferences

---

## 🔑 8. Environment Variables (.env example)

Copy `.env.example` to `.env` and fill in your secrets/keys. Example:
```
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
OLLAMA_API_URL=http://eass_ollama:11434/api/generate
OLLAMA_MODEL=llama3

JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
MONGO_URI=mongodb://mongo:27017
```

---

## ℹ️ 9. Additional Information

- 🧱 **Extensibility**: The platform is designed for easy addition of new services (e.g., portfolio optimization, alerts, analytics)
- 🧪 **Testing**: Unit and integration tests are provided for both backend and frontend
- 🔒 **Security**: JWT-based authentication, CORS, and secure password storage
- 📝 **Logging**: Centralized logging for all services
- 🤝 **Contribution**: PRs and issues are welcome! Please follow the code style and add tests for new features
- 🛠️ **Troubleshooting**: If you encounter issues, check service logs (`docker-compose logs <service>`) and ensure all environment variables are set

---

**Feel free to update this README as the project evolves! 🚀**
