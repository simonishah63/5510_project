import numpy as np
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from sklearn.preprocessing import MinMaxScaler
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from keras.callbacks import Callback, EarlyStopping
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import math
import os

class ProgressCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1} completed. Loss: {logs['loss']:.6f}")

def calculate_directional_accuracy(y_true, y_pred):
    """Calculate the directional accuracy of predictions"""
    try:
        y_true_direction = np.diff(y_true.flatten())
        y_pred_direction = np.diff(y_pred.flatten())
        
        correct_direction = np.sum((y_true_direction * y_pred_direction) > 0)
        return (correct_direction / len(y_true_direction)) * 100
    except Exception as e:
        print(f"Error calculating directional accuracy: {str(e)}")
        return 0.0

def save_prediction_plot(data, predictions, symbol):
    """Save prediction plot to results folder"""
    try:
        plt.figure(figsize=(12,6))
        plt.plot(data.index[-len(predictions):], data['Close'][-len(predictions):], label='Actual')
        plt.plot(data.index[-len(predictions):], predictions, label='Predicted')
        plt.title(f'{symbol} Stock Price Prediction')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Save plot
        plot_path = os.path.join(results_dir, f'{symbol}_prediction_plot.png')
        plt.savefig(plot_path)
        plt.close()
        
        return plot_path
    except Exception as e:
        print(f"Error saving prediction plot for {symbol}: {str(e)}")
        plt.close()
        return None

def save_prediction_report(metrics, symbol, data, predictions):
    """Save prediction metrics to text report"""
    try:
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        report_path = os.path.join(results_dir, f'{symbol}_prediction_report.txt')
        
        # Get last 30 days of actual and predicted values
        last_30_days = data.tail(30).copy()
        last_30_days['Predictions'] = predictions[-30:]
        
        with open(report_path, 'w') as f:
            f.write(f'Prediction Report for {symbol}\n')
            f.write('=' * 50 + '\n\n')
            
            # Model Architecture
            f.write('Model Architecture:\n')
            f.write('-' * 20 + '\n')
            f.write('- Input Layer: LSTM (128 units) with Dropout (0.2)\n')
            f.write('- Hidden Layer: LSTM (64 units) with Dropout (0.2)\n')
            f.write('- Dense Layer: 32 units (ReLU activation)\n')
            f.write('- Output Layer: 1 unit\n\n')
            
            # Performance Metrics
            f.write('Model Performance Metrics:\n')
            f.write('-' * 25 + '\n')
            f.write(f'Root Mean Square Error (RMSE): {metrics["rmse"]:.2f}\n')
            f.write(f'Normalized RMSE: {metrics["normalized_rmse"]:.2f}%\n')
            f.write(f'Mean Absolute Error (MAE): {metrics["mae"]:.2f}\n')
            f.write(f'R-squared Score: {metrics["r2"]:.4f}\n')
            f.write(f'Directional Accuracy: {metrics["directional_accuracy"]:.2f}%\n')
            f.write(f'Final Training Loss: {metrics["final_loss"]:.6f}\n\n')
            
            # Last 30 Days Predictions
            f.write('Last 30 Days Prediction vs Actual Values:\n')
            f.write('-' * 40 + '\n')
            f.write(f'{"Date":<12}{"Actual Price":>15}{"Predicted Price":>18}\n')
            f.write('-' * 45 + '\n')
            
            for date, row in last_30_days.iterrows():
                f.write(f'{date.strftime("%Y-%m-%d"):<12}')
                f.write(f'${row["Close"]:>14.2f}')
                f.write(f'${row["Predictions"]:>17.2f}\n')
        
        print(f"Report saved: {report_path}")
        
    except Exception as e:
        print(f"Error saving report for {symbol}: {str(e)}")
        raise

def predict_stock_price(symbol):
    """Predict stock price using LSTM"""
    try:
        print(f"\nProcessing predictions for {symbol}...")
        
        # Get the stock data
        end = datetime.now()
        start = end - timedelta(days=1*365)  # Get 5 years of data
        
        print(f"Fetching data from {start.date()} to {end.date()}...")
        df = yf.download(symbol, start=start, end=end)
        
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        
        print(f"Retrieved {len(df)} days of data")
        print(f"Available columns: {df.columns.tolist()}")
        
        # Check if 'Adj Close' is available, if not use 'Close'
        if 'Adj Close' in df.columns:
            price_column = 'Adj Close'
        elif 'Close' in df.columns:
            price_column = 'Close'
        else:
            raise ValueError(f"No price data (Close or Adj Close) available for {symbol}")
            
        # Create a new dataframe with only the price column
        data = df[[price_column]].copy()
        data.columns = ['Close']  # Rename to 'Close' for consistency
        
        if data.empty:
            raise ValueError(f"No price data available for {symbol}")
            
        if len(data) < 60:
            raise ValueError(f"Insufficient historical data for {symbol}. Need at least 60 days, got {len(data)} days.")
        
        # Check for and handle NaN values
        if data['Close'].isna().any():
            print(f"Warning: Found {data['Close'].isna().sum()} NaN values. Filling with forward fill method.")
            data['Close'] = data['Close'].fillna(method='ffill')
            if data['Close'].isna().any():
                data['Close'] = data['Close'].fillna(method='bfill')
                
        # Convert to numpy array and ensure proper shape
        dataset = data['Close'].values.reshape(-1, 1)
        print(f"Dataset shape: {dataset.shape}")
        
        # Calculate training size
        training_data_len = int(np.ceil(len(dataset) * .80))
        print(f"Training data length: {training_data_len}")
        
        # Scale the data
        scaler = MinMaxScaler(feature_range=(0,1))
        scaled_data = scaler.fit_transform(dataset)
        
        # Create training dataset
        train_data = scaled_data[0:training_data_len, :]
        x_train = []
        y_train = []
        
        sequence_length = 60
        print(f"Creating sequences with length {sequence_length}...")
        
        for i in range(sequence_length, len(train_data)):
            x_train.append(train_data[i-sequence_length:i, 0])
            y_train.append(train_data[i, 0])
        
        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        
        print(f"Training data shape: X={x_train.shape}, y={y_train.shape}")
        
        # Build LSTM model
        print("Building LSTM model...")
        model = Sequential()
        model.add(LSTM(128, return_sequences=True, input_shape=(x_train.shape[1], 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(64, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1))
        
        # Add early stopping
        early_stopping = EarlyStopping(
            monitor='loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Compile and train the model
        print("Training model...")
        model.compile(optimizer='adam', loss='huber')
        
        history = model.fit(
            x_train, 
            y_train, 
            batch_size=32,
            epochs=100,
            callbacks=[ProgressCallback(), early_stopping],
            verbose=0  # Disable default progress bar
        )
        
        # Create testing dataset
        test_data = scaled_data[training_data_len - sequence_length:, :]
        x_test = []
        y_test = dataset[training_data_len:, :]
        
        for i in range(sequence_length, len(test_data)):
            x_test.append(test_data[i-sequence_length:i, 0])
        
        x_test = np.array(x_test)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
        
        print("Generating predictions...")
        # Get predictions
        predictions = model.predict(x_test, verbose=0)
        predictions = scaler.inverse_transform(predictions)
        
        # Calculate metrics
        rmse = math.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        directional_accuracy = calculate_directional_accuracy(y_test, predictions)
        
        # Calculate normalized RMSE
        normalized_rmse = rmse / np.mean(y_test) * 100
        
        print(f"\nPrediction metrics for {symbol}:")
        print(f"RMSE: {rmse:.2f}")
        print(f"Normalized RMSE: {normalized_rmse:.2f}%")
        print(f"MAE: {mae:.2f}")
        print(f"R² Score: {r2:.4f}")
        print(f"Directional Accuracy: {directional_accuracy:.2f}%")
        
        # Create DataFrame with predictions
        valid = data[training_data_len:].copy()
        valid.loc[:, 'Predictions'] = predictions
        
        metrics = {
            'rmse': rmse,
            'normalized_rmse': normalized_rmse,
            'mae': mae,
            'r2': r2,
            'directional_accuracy': directional_accuracy,
            'final_loss': history.history['loss'][-1]
        }
        
        # Save prediction plot and report
        plot_path = save_prediction_plot(data, predictions, symbol)
        save_prediction_report(metrics, symbol, data[training_data_len:], predictions)
        
        print(f"Successfully completed predictions for {symbol}")
        return valid, metrics
        
    except Exception as e:
        print(f"Error in predict_stock_price for {symbol}: {str(e)}")
        raise ValueError(f"Failed to process {symbol}: {str(e)}")