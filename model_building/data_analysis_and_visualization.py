import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import yfinance as yf
from datetime import datetime
import numpy as np
import math

# Optional import for candlestick charts
try:
    import mplfinance as mpf
    MPLFINANCE_AVAILABLE = True
except ImportError:
    MPLFINANCE_AVAILABLE = False

def create_subplot_layout(n):
    """Calculate optimal subplot layout based on number of stocks"""
    if n <= 1:
        return 1, 1
    elif n <= 2:
        return 1, 2
    else:
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        return rows, cols

def plot_closing_prices(company_list, tech_list):
    """Plot historical view of closing prices"""
    if not company_list:
        print("No data available for plotting closing prices")
        return
        
    rows, cols = create_subplot_layout(len(company_list))
    plt.figure(figsize=(15, 10))
    
    for i, company in enumerate(company_list, 1):
        plt.subplot(rows, cols, i)
        company['Adj Close'].plot()
        plt.ylabel('Adj Close')
        plt.xlabel(None)
        plt.title(f"Closing Price of {company['company_name'].iloc[0]}")
    
    plt.tight_layout()
    plt.savefig('results/closing_prices.png')
    plt.close()

def plot_volume(company_list, tech_list):
    """Plot volume of sales"""
    if not company_list:
        print("No data available for plotting volume")
        return
        
    rows, cols = create_subplot_layout(len(company_list))
    plt.figure(figsize=(15, 10))
    
    for i, company in enumerate(company_list, 1):
        plt.subplot(rows, cols, i)
        company['Volume'].plot()
        plt.ylabel('Volume')
        plt.xlabel(None)
        plt.title(f"Sales Volume for {company['company_name'].iloc[0]}")
    
    plt.tight_layout()
    plt.savefig('results/volume.png')
    plt.close()

def calculate_moving_average(company_list):
    """Calculate moving average for different periods"""
    if not company_list:
        print("No data available for calculating moving averages")
        return
        
    ma_day = [10, 20, 50]
    
    for ma in ma_day:
        for company in company_list:
            column_name = f"MA for {ma} days"
            company[column_name] = company['Adj Close'].rolling(ma).mean()
    
    # Plot moving averages
    rows, cols = create_subplot_layout(len(company_list))
    fig = plt.figure(figsize=(15, 10))
    
    for i, company in enumerate(company_list, 1):
        ax = fig.add_subplot(rows, cols, i)
        company[['Adj Close', 'MA for 10 days', 'MA for 20 days', 'MA for 50 days']].plot(ax=ax)
        ax.set_title(company['company_name'].iloc[0])
    
    plt.tight_layout()
    plt.savefig('results/moving_averages.png')
    plt.close()

def analyze_daily_returns(company_list):
    """Analyze and plot daily returns"""
    if not company_list:
        print("No data available for analyzing daily returns")
        return
        
    for company in company_list:
        company['Daily Return'] = company['Adj Close'].pct_change()
    
    rows, cols = create_subplot_layout(len(company_list))
    fig = plt.figure(figsize=(15, 10))
    
    for i, company in enumerate(company_list, 1):
        ax = fig.add_subplot(rows, cols, i)
        company['Daily Return'].hist(bins=50, ax=ax)
        ax.set_title(f"Daily Returns for {company['company_name'].iloc[0]}")
    
    plt.tight_layout()
    plt.savefig('results/daily_returns.png')
    plt.close()

def plot_correlation_analysis(tech_list):
    """Analyze correlation between stocks"""
    if len(tech_list) < 2:
        print("Need at least 2 stocks for correlation analysis")
        return pd.DataFrame()  # Return empty DataFrame if not enough stocks
        
    try:
        # Get closing prices for all stocks
        closing_df = yf.download(tech_list, 
                               start=datetime.now() - pd.DateOffset(years=1),
                               end=datetime.now(),
                               progress=False)['Adj Close']
        
        # Calculate daily returns
        tech_rets = closing_df.pct_change()
        
        # Plot correlation heatmaps
        fig, axes = plt.subplots(1, 2, figsize=(15, 7))
        
        sns.heatmap(tech_rets.corr(), annot=True, cmap='summer', ax=axes[0])
        axes[0].set_title('Correlation of Stock Returns')
        
        sns.heatmap(closing_df.corr(), annot=True, cmap='summer', ax=axes[1])
        axes[1].set_title('Correlation of Stock Prices')
        
        plt.tight_layout()
        plt.savefig('results/correlation_analysis.png')
        plt.close()
        
        return tech_rets
        
    except Exception as e:
        print(f"Error in correlation analysis: {str(e)}")
        return pd.DataFrame()

def plot_candlestick_charts(company_list, tech_list):
    """Plot candlestick charts"""
    if not MPLFINANCE_AVAILABLE:
        print("mplfinance is not available. Skipping candlestick charts.")
        return
    
    if not company_list:
        print("No data available for candlestick charts")
        return
        
    for company in company_list:
        try:
            symbol = company['company_name'].iloc[0]
            filename = f'results/candlestick_{symbol}.png'
            mpf.plot(company, type='candle', 
                    title=f"Candlestick Chart for {symbol}",
                    savefig=filename)
        except Exception as e:
            print(f"Error creating candlestick chart for {symbol}: {str(e)}")

def main_analysis(company_list, tech_list):
    """Main function to run all analyses"""
    try:
        # Create results directory if it doesn't exist
        import os
        os.makedirs('results', exist_ok=True)
        
        print("\nGenerating analysis plots...")
        plot_closing_prices(company_list, tech_list)
        print("- Closing prices plot saved")
        
        plot_volume(company_list, tech_list)
        print("- Volume plot saved")
        
        calculate_moving_average(company_list)
        print("- Moving averages plot saved")
        
        analyze_daily_returns(company_list)
        print("- Daily returns plot saved")
        
        tech_rets = plot_correlation_analysis(tech_list)
        if not tech_rets.empty:
            print("- Correlation analysis plots saved")
        
        plot_candlestick_charts(company_list, tech_list)
        print("- Candlestick charts saved")
        
        print("\nAll analysis plots have been saved to the 'results' directory.")
        return tech_rets
        
    except Exception as e:
        print(f"Error in main analysis: {str(e)}")
        return pd.DataFrame()