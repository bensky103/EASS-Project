import joblib
import numpy as np

scaler = joblib.load("scaler.pkl")  # Use the scaler saved during training

def preprocess_data(raw_data):
    # Reshape if needed, e.g., (-1, 1) for MinMaxScaler
    data = np.array(raw_data).reshape(-1, 1)
    scaled = scaler.transform(data)
    return scaled