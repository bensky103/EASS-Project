from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_api():
    payload = {
        "stock_symbol": "AAPL"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert len(data["predictions"]) == 10
    for pred in data["predictions"]:
        assert "date" in pred
        assert "predicted_price" in pred
        assert isinstance(pred["predicted_price"], float)
        assert pred["predicted_price"] > 0
