import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data(stock_list):
    """Get stock data for analysis"""
    # Set up End and Start times for data grab
    end = datetime.now()
    
    start = end - timedelta(days = 1*365)
    
    # Get stock data
    company_list = []
    failed_downloads = []
    
    for symbol in stock_list:
        try:
            print(f"\nFetching data for {symbol}...")
            stock_data = yf.download(symbol, start=start, end=end, progress=False)
            
            if stock_data.empty:
                print(f"Warning: No data found for {symbol}")
                failed_downloads.append((symbol, "No data found"))
                continue
                
            print(f"Available columns: {stock_data.columns.tolist()}")
            
            # Check for required price columns
            if 'Adj Close' not in stock_data.columns and 'Close' not in stock_data.columns:
                print(f"Warning: No price data available for {symbol}")
                failed_downloads.append((symbol, "No price data available"))
                continue
            
            if len(stock_data) < 60:
                print(f"Warning: Insufficient data for {symbol}. Found only {len(stock_data)} days.")
                failed_downloads.append((symbol, "Insufficient historical data"))
                continue
            
            # Handle NaN values
            if stock_data.isna().any().any():
                print(f"Warning: Found NaN values in {symbol} data. Attempting to fill...")
                stock_data = stock_data.fillna(method='ffill').fillna(method='bfill')
                
                if stock_data.isna().any().any():
                    print(f"Warning: Unable to fill all NaN values for {symbol}")
                    failed_downloads.append((symbol, "Contains missing values"))
                    continue
            
            stock_data['company_name'] = symbol
            company_list.append(stock_data)
            print(f"Successfully downloaded {len(stock_data)} days of data for {symbol}")
            
        except Exception as e:
            failed_downloads.append((symbol, str(e)))
            print(f"Error downloading {symbol}: {str(e)}")
    
    if not company_list:
        raise ValueError("No valid stock data was downloaded. Please check the stock symbols.")
    
    # Combine all stock data into one DataFrame
    df = pd.concat(company_list, keys=[data['company_name'].iloc[0] for data in company_list])
    
    # Report any failed downloads
    if failed_downloads:
        print("\nFailed to download data for the following symbols:")
        for symbol, reason in failed_downloads:
            print(f"- {symbol}: {reason}")
    
    valid_symbols = [data['company_name'].iloc[0] for data in company_list]
    print(f"\nSuccessfully processed {len(valid_symbols)} symbols: {', '.join(valid_symbols)}")
    
    return df, company_list, valid_symbols
