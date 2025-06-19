import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset
import os
import kagglehub
import joblib

# Download latest version
path = "C:/Users/Guy Bensky/Desktop/EASS project/app/stock-market-dataset"

print("Path to dataset files:", path)

file_path = os.path.join(path + '/stocks/TSLA.csv')  # Path to TSLA stock data
data = pd.read_csv(file_path)

print(data.head())
print(data.tail())

data['Date'] = pd.to_datetime(data['Date']) # Converting to datetime format before visualizing
plt.figure(figsize=(12, 6))
plt.plot(data['Date'], data['Close'], label='Closing Price')
plt.title('TSLA Stock Price Over Time')
plt.xlabel('Date')
plt.ylabel('Closing Price (USD)')
plt.xticks(rotation=45)
plt.legend()
plt.grid()
plt.show()

# Scale the data
scaler = MinMaxScaler(feature_range=(0,1))
data['Close_scaled'] = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

joblib.dump(scaler, 'scaler.pkl')


# Create sequences for GRU
def create_sequences(data, seq_length):
    sequences = []
    for i in range(len(data) - seq_length):
        seq = data[i:i+seq_length]
        label = data[i+seq_length]
        sequences.append((seq, label))
    return sequences

seq_length = 10  # Use the last 10 days to predict the next day
sequences = create_sequences(data['Close_scaled'].values, seq_length)

# Split the data
train_data, test_data = train_test_split(sequences, test_size=0.2, random_state=42)

class StockDataset(Dataset):
    def __init__(self, sequences):
        self.sequences = sequences

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq, label = self.sequences[idx]
        return torch.FloatTensor(seq), torch.FloatTensor([label])

# Split the training data into training and validation sets
train_data, val_data = train_test_split(train_data, test_size=0.2, random_state=42)

# Create datasets
train_dataset = StockDataset(train_data)
val_dataset = StockDataset(val_data)
test_dataset = StockDataset(test_data)

# Create data loaders
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)


class GRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout_prob=0.2):
        super(GRUModel, self).__init__()
        # Add dropout within the GRU layer
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout_prob)
        self.dropout = nn.Dropout(dropout_prob)  # Additional dropout after GRU output
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # GRU returns output and hidden state
        _, hidden = self.gru(x)
        hidden = self.dropout(hidden[-1])  # Apply dropout to the final hidden state
        return self.fc(hidden)



# Initialize the model
model = GRUModel(input_size=1, hidden_size=10, num_layers=2, output_size=1, dropout_prob=0.2)

# Define loss and optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Train the model
num_epochs = 20
for epoch in range(num_epochs):
    model.train()
    train_loss = 0.0

    for sequences, labels in train_loader:
        optimizer.zero_grad()
        output = model(sequences.unsqueeze(-1))
        loss = criterion(output, labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    # Calculate average training loss
    train_loss /= len(train_loader)

    # Validation phase
    model.eval()
    val_loss = 0.0

    with torch.no_grad():
        for sequences, labels in val_loader:  # Assuming val_loader is defined
            output = model(sequences.unsqueeze(-1))
            loss = criterion(output, labels)
            val_loss += loss.item()

    # Calculate average validation loss
    val_loss /= len(val_loader)

    print(f"Epoch {epoch+1}, Training Loss: {train_loss:.4f}, Validation Loss: {val_loss:.4f}")

# ✅ Save the trained model after training
torch.save(model.state_dict(), "model.pth")
print("Saved model.pth:", os.path.exists("model.pth"))

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import math

# Evaluate the model and calculate RMSE
model.eval()
predictions = []
actuals = []

with torch.no_grad():
    for sequences, labels in test_loader:
        output = model(sequences.unsqueeze(-1))  # Add channel dimension
        predictions.extend(output.numpy().flatten())  # Store predictions
        actuals.extend(labels.numpy().flatten())      # Store actual labels

# Calculate RMSE
rmse = math.sqrt(mean_squared_error(actuals, predictions))
print(f"Root Mean Squared Error (RMSE): {rmse}")


# Calculate MAE
mae = mean_absolute_error(actuals, predictions)
print(f"Mean Absolute Error (MAE): {mae}")

# Calculate R-squared
r2 = r2_score(actuals, predictions)
print(f"R-squared (R²): {r2}")


# Convert actual and predicted prices into a DataFrame for aggregation
df = pd.DataFrame({
    'Date': data['Date'].tail(len(actuals)).values,
    'Actual': actuals,
    'Predicted': predictions
})

# Resample by week and compute mean
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df_weekly = df.resample('W').mean()

# Plot weekly averages
plt.figure(figsize=(12, 6))
plt.plot(df_weekly.index, df_weekly['Actual'], label='Actual Prices (10 Day Avg)', color='blue')
plt.plot(df_weekly.index, df_weekly['Predicted'], label='Predicted Prices (10 Day Avg)', color='red', linestyle='dashed')
plt.title('TSLA Stock Price Prediction vs Actual (10 Day Averages)')
plt.xlabel('Date')
plt.ylabel('Stock Price (USD)')
plt.legend()
plt.xticks(rotation=45)
plt.grid()
plt.show()


# Define a custom dataset class for sequences
class StockDataset(Dataset):
    def __init__(self, sequences):
        self.sequences = sequences

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        seq = self.sequences[idx]
        return torch.FloatTensor(seq)

# List of stock tickers
stock_tickers = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA']

predictions_dict = {}  # Store predictions for each stock

# Prepare the data for each stock
for ticker in stock_tickers:
    # Load stock data
    file_path = os.path.join(path, f'stocks/{ticker}.csv')
    data = pd.read_csv(file_path)

    # Use the 'Close' column for prediction
    prices = data['Close'].values.reshape(-1, 1)

    # Scale the data
    scaler = MinMaxScaler()
    scaled_prices = scaler.fit_transform(prices)

    # Create sequences for the model
    sequence_length = 10
    sequences = []
    for i in range(len(scaled_prices) - sequence_length):
        seq = scaled_prices[i:i + sequence_length]
        sequences.append(seq)

    # Create a DataLoader for the sequences
    dataset = StockDataset(sequences)
    loader = DataLoader(dataset, batch_size=32, shuffle=False)

    # Display the first few rows of each stock's data
    print(f"Data for {ticker}:\n", data.head())

    # Make predictions for the current ticker
    model.eval()
    predictions = []
    with torch.no_grad():
        for batch in loader:
            output = model(batch)
            predictions.extend(output.numpy().flatten())

    # Inverse transform and store predictions for the current ticker
    predicted_prices = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
    predictions_dict[ticker] = predicted_prices

# Iterate over the predictions for each stock
for ticker in stock_tickers:
    # Load the stock data
    file_path = os.path.join(path, f'stocks/{ticker}.csv')
    data = pd.read_csv(file_path)

    # Use the 'Close' column as actual prices
    actuals = data['Close'].tail(len(predictions_dict[ticker])).values
    predictions = predictions_dict[ticker]  # Predicted prices from the model

    # Convert actual and predicted prices into a DataFrame for aggregation
    df = pd.DataFrame({
        'Date': data['Date'].tail(len(actuals)).values,
        'Actual': actuals,
        'Predicted': predictions
    })

    # Resample by week and compute mean
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df_weekly = df.resample('W').mean()

    # Plot weekly averages
    plt.figure(figsize=(12, 6))
    plt.plot(df_weekly.index, df_weekly['Actual'], label=f'Actual Prices (Weekly Avg)', color='blue')
    plt.plot(df_weekly.index, df_weekly['Predicted'], label=f'Predicted Prices (Weekly Avg)', color='red', linestyle='dashed')
    plt.title(f'{ticker} Stock Price Prediction vs Actual (Weekly Averages)')
    plt.xlabel('Date')
    plt.ylabel('Stock Price (USD)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()
