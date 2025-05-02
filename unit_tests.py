from app.model_service import predict

def test_predict_valid():
    result = predict("AAPL", [150, 152, 151, 153, 155, 157, 156, 158, 160, 162])
    assert "predicted_price" in result
    assert "confidence" in result
