from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_api():
    payload = {
        "stock_symbol": "AAPL",
        "historical_data": [150, 152, 151, 153, 155, 157, 156, 158, 160, 162]
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "predicted_price" in response.json()
