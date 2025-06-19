from app.model_service import predict_next_10_days

def test_predict_valid():
    predictions = predict_next_10_days("AAPL")
    
    # Test that we get exactly 10 predictions
    assert len(predictions) == 10
    
    # Test that all predictions are valid numbers
    assert all(isinstance(p, float) for p in predictions)
    assert all(p > 0 for p in predictions)  # Stock prices should be positive
