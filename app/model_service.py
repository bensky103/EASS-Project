# model_service.py
import numpy as np
import torch
from torch import nn
import joblib
import os

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

# Predict function
def predict(stock_symbol: str, historical_data: list[float]):
    x = np.array(historical_data).reshape(1, -1)
    x_scaled = scaler.transform(x.reshape(-1, 1)).reshape(1, len(historical_data), 1)
    x_tensor = torch.tensor(x_scaled).float()

    with torch.no_grad():
        y_pred = model(x_tensor)
        predicted_price = y_pred.numpy()[0][0]
        predicted_price = scaler.inverse_transform([[predicted_price]])[0][0]

    return {"predicted_price": float(predicted_price), "confidence": 0.9}
