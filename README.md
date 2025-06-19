# 📈 EASS Project – Microservice Stock Platform

This project is a microservice-based platform for stock data analysis and prediction, built with Python (FastAPI), React (Vite), and Docker. It features modular services for authentication, stock data fetching, and LLM-powered stock analysis.

---

## 🚧 Project Progress
- [x] **Auth Service**: User authentication and management
- [x] **Stock Data Fetching Service**: Fetches and computes stock indicators, fundamentals, and news sentiment
- [x] **LLM Service**: Provides LLM-based stock recommendations and reasoning
- [x] **Dockerized environment**: All services can be run together
- [ ] **Frontend**: React + Vite scaffolded (to be completed)

---

## 🛠️ Technologies Used
- **Python** (FastAPI, Pydantic, httpx, pandas, joblib)
- **React + Vite** (TypeScript, Tailwind CSS)
- **Docker & Docker Compose**
- **Alpha Vantage API** (stock data)
- **Ollama** (LLM inference)
- **CORS, Logging, etc.**

---

## 🏗️ Design Patterns & Architecture
- **Microservices architecture**: Each service is independently deployable and communicates via HTTP APIs
- **Separation of concerns**: Auth, data fetching, and LLM logic are isolated
- **Stateless APIs**: Services are stateless, with state managed externally if needed
- **Docker Compose orchestration**: All services can be spun up together for local/dev environments

---

## 🧩 Microservices Overview

### 1. Auth Service
- **Tech**: FastAPI, CORS
- **Logic**: Handles user registration, login, and authentication. Provides `/`, `/health`, and routes for user and auth management.
- **Endpoints**:
  - `GET /` – Service status
  - `GET /health` – Health check
  - `/auth/*`, `/user/*` – Auth and user management (see code for details)

### 2. Stock Data Fetching Service
- **Tech**: FastAPI, pandas, Alpha Vantage API, Pydantic
- **Logic**: Fetches and computes technical indicators, volume features, fundamentals, and news sentiment for a given stock symbol.
- **Endpoints**:
  - `GET /health` – Health check
  - `POST /fetch` – Fetch stock data (symbol, timeframe, date)
  - `POST /predict` – (If implemented) Predict using fetched features

### 3. LLM Service
- **Tech**: FastAPI, httpx, Pydantic, Ollama (LLaMA 3)
- **Logic**: Accepts stock features and optional news sentiment, formats a prompt, and queries an LLM for a prediction (BUY/SELL/HOLD, confidence, reasoning, price forecast).
- **Endpoints**:
  - `GET /health` – Health check
  - `POST /predict` – LLM-based stock prediction (symbol, features, time_frame)

### 4. Frontend (Placeholder)
- **Tech**: React, Vite, TypeScript, Tailwind CSS
- **Status**: _To be completed. (Frontend documentation and usage will be added here)_

---

## 📬 API Endpoints & Usage

### Auth Service
- `GET /` – Returns `{ "status": "ok" }`
- `GET /health` – Returns `{ "status": "ok" }`
- `/auth/*`, `/user/*` – See service code for registration, login, and user management endpoints

### Stock Data Fetching Service
- `GET /health` – Returns service health
- `POST /fetch` – Request:
  ```json
  {
    "symbol": "AAPL",
    "timeframe": "daily",
    "date": "2024-07-01"
  }
  ```
  Response: Technical indicators, volume features, fundamentals, news sentiment, etc.
- `POST /predict` – (If implemented) Predict using features

### LLM Service
- `GET /health` – Returns service health
- `POST /predict` – Request:
```json
{
    "symbol": "AAPL",
    "features": { /* see StockFeatures schema */ },
    "time_frame": "next 5 trading days"
}
```
  Response:
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

## 🐳 Docker & Local Development

### Prerequisites
- Docker & Docker Compose installed

### Running All Services
1. Build and start all services:
```bash
   docker-compose up --build
```
2. Access services at their respective ports (see `docker-compose.yml`)

### Stopping Services
```bash
docker-compose down
```

---

## 🖥️ Frontend (To be completed)
_Placeholder for frontend documentation, usage, and integration instructions._

---

## 📝 What Might Be Missing?
- Monitoring/logging/alerting setup //grafana(?)
- Frontend integration with backend APIs

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` and fill in your secrets/keys. Example variables:

```
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
OLLAMA_API_URL=http://eass_ollama:11434/api/generate
OLLAMA_MODEL=llama3

JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
MONGO_URI=mongodb://mongo:27017
```



**Feel free to update this README as the project evolves!**
