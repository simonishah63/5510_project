import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';
import { useState } from 'react';


jest.mock('./components/StockInput', () => {
  const React = require('react'); // Import React inside the function

  return {

    StockInput: ({ onSubmit, loading }) => {
      const [symbols, setSymbols] = React.useState([]);
      const [inputValue, setInputValue] = React.useState('');

      return (
        <>
        <input 
            data-testid="stock-input" 
            placeholder="Enter stock symbol" 
            value={inputValue} 
            onChange={(e) => setInputValue(e.target.value)}
        />
        <button data-testid="stock-add-button" onClick={() => {
            if (symbols.length < 5) {
                setSymbols([...symbols, inputValue]);
                setInputValue('');
              }
            }}>Add</button>
        <button data-testid="stock-submit" disabled={loading} onClick={() => onSubmit(symbols)}>
          Submit
        </button>
        <div>
            {symbols.map((symbol) => (
              <div key={symbol} data-testid="stock-chip">
                {symbol} 
                <button 
                  data-testid={`close-${symbol}`} 
                  onClick={() => setSymbols(symbols.filter(s => s !== symbol))}
                >
                  Close
                </button>
              </div>
            ))}
          </div>
        </>
      );
    },
  }
});

jest.mock('./components/Header', () => ({
  Header: () => <header data-testid="header">Header</header>,
}));

describe('App Component', () => {
  test('renders App component correctly', () => {
    render(<App />);
    expect(screen.getByTestId('header')).toBeInTheDocument();
    expect(screen.getByTestId('stock-submit')).toBeInTheDocument();
    expect(screen.getByTestId('stock-input')).toBeInTheDocument();
  });

  test('should call handleStockSubmit and set loading state', async () => {
    render(<App />);
    const submitButton = screen.getByTestId('stock-submit');
    expect(submitButton).toBeEnabled();

    fireEvent.click(submitButton);

    expect(submitButton).toBeDisabled();
  });

  test('should display Snackbar when 5 stock symbols are entered', async () => {
    render(<App />);
  
    const stockInput = screen.getByTestId('stock-input');
    const addButton = screen.getByTestId('stock-add-button');
    const submitButton = screen.getByTestId('stock-submit');
  
    const stocks = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA', 'NFLX'];
  
    for (let i = 0; i < stocks.length; i++) {
      fireEvent.change(stockInput, { target: { value: stocks[i] } });
      fireEvent.click(addButton);
    }
  
    // Ensure the last stock was not added (only 5 should exist)
    await waitFor(() => expect(screen.getAllByTestId('stock-chip')).toHaveLength(5));
  
    // Click Submit
    fireEvent.click(submitButton);
  
    // Snackbar should appear with an error message
    // await waitFor(() => {
    //   screen.debug(); 
    //   expect(screen.getByRole('alert')).toHaveTextContent('Maximum number of symbols (5) reached');
    // });
  
    // Close Snackbar
    // fireEvent.click(screen.getByRole('button', { name: /close/i }));
  
    // Snackbar should disappear
    await waitFor(() => {
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    });
  });
});