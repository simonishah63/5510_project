from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import matplotlib
matplotlib.use('Agg')

# Get absolute paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))

# Add parent directory to path to import from main project
sys.path.insert(0, PROJECT_ROOT)

from backend.fetch_stock_data import fetch_stock_data

app = Flask(__name__)
CORS(app)

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
        

        response_data = {}
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
