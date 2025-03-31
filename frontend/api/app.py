from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys
import os
import pandas as pd
import numpy as np
import matplotlib
import shutil
import mimetypes
matplotlib.use('Agg')

# Get absolute paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
MAIN_RESULTS_DIR = os.path.join(PROJECT_ROOT, 'results')
API_RESULTS_DIR = os.path.join(CURRENT_DIR, 'results')

# Add parent directory to path to import from main project
sys.path.insert(0, PROJECT_ROOT)

from backend.fetch_stock_data import fetch_stock_data
from model_building.model_training_and_prediction import predict_stock_price
from model_building.data_analysis_and_visualization import main_analysis

app = Flask(__name__)
CORS(app)

def get_mime_type(filename):
    """Get MIME type based on file extension"""
    if filename.endswith('.pdf'):
        return 'application/pdf'
    elif filename.endswith('.png'):
        return 'image/png'
    elif filename.endswith('.txt'):
        return 'text/plain'
    return 'application/octet-stream'

def copy_results():
    """Copy results from main directory to API directory"""
    try:
        # Create API results directory if it doesn't exist
        os.makedirs(API_RESULTS_DIR, exist_ok=True)
        
        # Copy all files from main results to API results
        for file in os.listdir(MAIN_RESULTS_DIR):
            src = os.path.join(MAIN_RESULTS_DIR, file)
            dst = os.path.join(API_RESULTS_DIR, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"Copied: {file}")
    except Exception as e:
        print(f"Error copying results: {str(e)}")

@app.route('/api/results/<path:filename>')
def serve_result_file(filename):
    """Serve result files with forced download"""
    try:
        # Ensure results are copied to API directory
        copy_results()
        
        file_path = os.path.join(API_RESULTS_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        # Get MIME type
        mime_type = get_mime_type(filename)
        
        # Force download with proper MIME type and headers
        response = send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=filename
        )
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response
    except Exception as e:
        return jsonify({'error': f'Error serving file: {str(e)}'}), 500

def calculate_trend_signals(predictions_df, stock_data):
    """Calculate technical analysis signals"""
    try:
        # Calculate moving average signal
        actual_mean = predictions_df['Close'].mean()
        pred_mean = predictions_df['Predictions'].mean()
        ma_signal = 'Bullish' if float(actual_mean) < float(pred_mean) else 'Bearish'
        
        # Calculate volume trend using iloc to access Series values
        recent_volume = stock_data['Volume'].tail(10).mean()
        overall_volume = stock_data['Volume'].mean()
        volume_trend = 'High' if float(recent_volume.iloc[0]) > float(overall_volume.iloc[0]) else 'Low'
        
        # Calculate price trend
        first_pred = float(predictions_df['Predictions'].iloc[0])
        last_pred = float(predictions_df['Predictions'].iloc[-1])
        price_trend = 'Upward' if last_pred > first_pred else 'Downward'
        
        return {
            'moving_averages': ma_signal,
            'volume_trend': volume_trend,
            'price_trend': price_trend
        }
    except Exception as e:
        print(f"Error calculating trends: {str(e)}")
        return {
            'moving_averages': 'Unknown',
            'volume_trend': 'Unknown',
            'price_trend': 'Unknown',
            'error': str(e)
        }

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'No stock symbols provided'}), 400

        print(f"\nProcessing request for symbols: {', '.join(symbols)}")
        
        # Get stock data
        try:
            print("\nFetching stock data...")
            df, company_list, valid_symbols = fetch_stock_data(symbols)
            
            if not valid_symbols:
                return jsonify({
                    'error': 'No valid data found for any of the provided symbols',
                    'details': 'Please check the symbol names and try again'
                }), 400
            
            invalid_symbols = set(symbols) - set(valid_symbols)
            if invalid_symbols:
                print(f"Warning: Invalid or missing data for symbols: {', '.join(invalid_symbols)}")
            
            print(f"Successfully fetched data for: {', '.join(valid_symbols)}")
            
        except Exception as e:
            print(f"Error fetching stock data: {str(e)}")
            return jsonify({
                'error': 'Error fetching stock data',
                'details': str(e)
            }), 500
        
        # Perform analysis
        try:
            if len(valid_symbols) > 0:
                print("\nPerforming technical analysis...")
                tech_rets = main_analysis(company_list, valid_symbols)
                print("Technical analysis completed")
            else:
                tech_rets = pd.DataFrame()
            
        except Exception as e:
            print(f"Error in technical analysis: {str(e)}")
            return jsonify({
                'error': 'Error in technical analysis',
                'details': str(e)
            }), 500
        
        # Store results
        predictions = {}
        metrics = {}
        technical_analysis = {}
        errors = {}
        
        # Get predictions for each symbol
        print("\nGenerating predictions for each symbol...")
        for symbol in symbols:
            try:
                if symbol not in valid_symbols:
                    raise ValueError("No valid data available")
                
                # Get the stock data for technical analysis
                stock_data = next((comp for comp in company_list if comp['company_name'].iloc[0] == symbol), None)
                if stock_data is None:
                    raise ValueError("Failed to retrieve stock data")
                
                print(f"\nProcessing predictions for {symbol}...")
                predictions_df, symbol_metrics = predict_stock_price(symbol)
                
                if predictions_df is not None and not predictions_df.empty:
                    print(f"Successfully generated predictions for {symbol}")
                    
                    # Convert predictions to list format for JSON
                    predictions[symbol] = [
                        {
                            'date': str(date),
                            'actual': float(row['Close']),
                            'predicted': float(row['Predictions'])
                        }
                        for date, row in predictions_df.tail(30).iterrows()
                    ]
                    
                    # Store metrics
                    metrics[symbol] = {
                        'rmse': float(symbol_metrics['rmse']),
                        'normalized_rmse': float(symbol_metrics['normalized_rmse']),
                        'mae': float(symbol_metrics['mae']),
                        'r2': float(symbol_metrics['r2']),
                        'directional_accuracy': float(symbol_metrics['directional_accuracy'])
                    }
                    
                    # Add technical analysis
                    technical_analysis[symbol] = calculate_trend_signals(predictions_df, stock_data)
                    
                else:
                    raise ValueError("Failed to generate predictions")
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error processing {symbol}: {error_msg}")
                errors[symbol] = error_msg
                predictions[symbol] = None
                metrics[symbol] = None
                technical_analysis[symbol] = {'error': error_msg}
        
        # Copy results to API directory after processing
        copy_results()
        
        # Check if we have any valid predictions
        if not any(pred is not None for pred in predictions.values()):
            return jsonify({
                'error': 'Failed to generate predictions for all symbols',
                'details': errors
            }), 500
        
        response_data = {
            'predictions': predictions,
            'metrics': metrics,
            'technical_analysis': technical_analysis
        }
        
        if errors:
            response_data['errors'] = errors
            
        print("\nRequest processing completed successfully")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'Unexpected error occurred',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)