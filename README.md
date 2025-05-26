# 📈 Stock Price Prediction Backend – GRU Microservice

This backend microservice is built with **FastAPI** and serves predictions from a **pre-trained GRU (Gated Recurrent Unit) neural network model** using **PyTorch**.  
It receives 10 recent stock prices and predicts the next day's price.

---

## 📁 Project Structure

```
stock-backend/
├── app/
│   ├── main.py              # FastAPI app and endpoint
│   ├── model_service.py     # Model logic: loading + predicting
│   ├── model.pth            # Trained GRU model (PyTorch)
│   ├── scaler.pkl           # Trained MinMaxScaler (joblib)
│   └── requirements.txt     # Python dependencies
├── unit_tests.py        # Unit tests for core logic
├── integration_test.py      # API endpoint test
├── Dockerfile               # Container definition
└── README.md                # Documentation
```

---

## 🚀 Run Locally (Dev Environment)

1. 🔽 Install requirements:
   ```bash
   pip install -r app/requirements.txt
   ```

2. ▶️ Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

3. 🌐 Open in browser:
   ```
   http://localhost:8000/docs
   ```
   Use the Swagger UI to test `/predict`.

---

## 🐳 Run with Docker (Production-Ready)

1. 🛠️ Build the Docker image:
   ```bash
   docker build -t stock-backend .
   ```

2. ▶️ Run the container:
   ```bash
   docker run -p 8000:8000 stock-backend
   ```

3. 🌍 Visit:
   ```
   http://localhost:8000/docs
   ```
4. Run the following to perform a test the backend work properly with cURL:
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"stock_symbol":"AAPL","historical_data":[150,152,151,153,155,157,156,158,160,162]}'

---

## 📬 API Endpoint

### 🔹 `POST /predict`

**Request Body:**

```json
{
  "stock_symbol": "AAPL",
  "historical_data": [150, 152, 151, 153, 155, 157, 156, 158, 160, 162]
}
```

**Response:**

```json
{
  "predicted_price": 164.23,
  "confidence": 0.9
}
```

> Note: The `historical_data` list **must contain exactly 10 values**.

---

## 🧠 Model Details

- **Model**: GRU-based time series predictor implemented with PyTorch.
- **Trained on**: Scaled TSLA stock data from Kaggle.
- **Saved as**: `model.pth` using `torch.save(model.state_dict())`
- **Scaler**: Fitted `MinMaxScaler`, saved as `scaler.pkl` using `joblib`.

---

## 🧪 Running Tests

### ✅ Unit Test

```bash
pytest app/unit_tests.py
```

### ✅ Integration Test

```bash
pytest integration_test.py
```

> Both tests validate the prediction logic and API response integrity.

---

## 📦 Dependencies

Defined in `app/requirements.txt`:

```
fastapi
uvicorn[standard]
torch
numpy
joblib
pydantic
```

Install with:

```bash
pip install -r app/requirements.txt
```

---

## 👨💻 Developed By

**Guy Bensky**  
Student at Holon Institute of Technology (HIT)  
Software Engineering Course – Final Project: Microservice-Based Stock Predictor

---

## 📌 Notes

- This backend can be integrated into a Docker Compose system alongside a frontend and additional services.
- Make sure `model.pth` and `scaler.pkl` exist before deploying or running.
