# model_service.py
import numpy as np
import torch
from torch import nn
import joblib
import os
import yfinance as yf
import pandas as pd

# Define your GRU model class (copy from your notebook)
class GRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout_prob=0.2):
        super(GRUModel, self).__init__()
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout_prob)
        self.dropout = nn.Dropout(dropout_prob)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        _, hidden = self.gru(x)
        hidden = self.dropout(hidden[-1])
        return self.fc(hidden)

def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "model.pth")
    model = GRUModel(input_size=1, hidden_size=10, num_layers=2, output_size=1, dropout_prob=0.2)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

# Load scaler
scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")
scaler = joblib.load(scaler_path)
model = load_model()

def fetch_historical_data(symbol, period="60d", interval="1d"):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval=interval)
    return hist['Close'].values  # or adjust as per your model's needs

def preprocess_data(raw_data):
    # Reshape if needed, e.g., (-1, 1) for MinMaxScaler
    data = np.array(raw_data).reshape(-1, 1)
    scaled = scaler.transform(data)
    return scaled

# Predict function
def predict_next_10_days(symbol):
    raw_data = fetch_historical_data(symbol)
    processed = preprocess_data(raw_data)
    
    # Initialize list to store predictions
    all_predictions = []
    
    # Get the last 60 days of data
    current_sequence = processed[-60:].reshape(1, 60, 1)
    
    # Generate 10 predictions
    for _ in range(10):
        # Convert to PyTorch tensor
        input_tensor = torch.FloatTensor(current_sequence)
        
        # Set model to evaluation mode
        model.eval()
        
        # Disable gradient calculation
        with torch.no_grad():
            pred = model(input_tensor)
        
        # Store prediction
        all_predictions.append(float(pred.numpy()[0][0]))  # Convert to float explicitly
        
        # Update sequence for next prediction
        current_sequence = np.roll(current_sequence, -1)
        current_sequence[0, -1, 0] = pred.numpy()[0][0]
    
    # Inverse transform all predictions
    all_predictions = np.array(all_predictions).reshape(-1, 1)
    all_predictions = scaler.inverse_transform(all_predictions)
    
    # Convert to list of floats
    return [float(x) for x in all_predictions.flatten()]
