import time
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fetch_stock_data import fetch_stock_data

def get_valid_stock_symbols():
    """Get valid stock symbols from user input"""
    while True:
        stock_list = input("Enter the stock symbols (separated by spaces): ").split()
        if not stock_list:
            print("Error: Please enter at least one stock symbol.")
            continue
        # Remove any empty strings and whitespace
        stock_list = [symbol.strip() for symbol in stock_list if symbol.strip()]
        if not stock_list:
            print("Error: Please enter valid stock symbols.")
            continue
        return stock_list

def main():
    """Main function to run the analysis"""
    start_time = time.time()
    
    # Ask user for stock names with validation
    stock_list = get_valid_stock_symbols()
    
    # Get stock data
    df, company_list, _ = fetch_stock_data(stock_list)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\nExecution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    main()