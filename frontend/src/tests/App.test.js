import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../App';
import { StockInput } from '../components/StockInput';

describe('App Component', () => {
  beforeEach(() => {
    // Mocking fetch API
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('initial state', () => {
    render(<App />);
    expect(screen.queryByText(/Analyzing/i)).toBeNull();
    expect(screen.queryByRole('alert')).toBeNull();
  });

  test('successful stock prediction', async () => {
    const mockResponse = {
      predictions: { AAPL: 150, GOOG: 2800 },
    };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: jest.fn().mockResolvedValueOnce(mockResponse),
    });

    render(<App />);
    const input = screen.getByPlaceholderText(/Enter stock symbol/i);
    const addButton = screen.getByTestId('stock-add-button'); 
    
    fireEvent.change(input, { target: { value: 'AAPL' } });
    fireEvent.click(addButton);
    
    fireEvent.change(input, { target: { value: 'GOOG' } });
    fireEvent.click(addButton);

    fireEvent.click(screen.getByText(/Analyze Stocks/i));

    await waitFor(() => {
      expect(screen.getByText(/Analysis completed successfully/i)).toBeInTheDocument();
    });
  });

  test('error handling for API call', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: jest.fn().mockResolvedValueOnce({ error: 'Network error' }),
    });

    render(<App />);
    const input = screen.getByPlaceholderText(/Enter stock symbol/i);
    const addButton = screen.getByTestId('stock-add-button'); 
    
    fireEvent.change(input, { target: { value: 'AAPL' } });
    fireEvent.click(addButton);

    fireEvent.click(screen.getByText(/Analyze Stocks/i));

    await waitFor(() => {
      expect(screen.getByText(/Error: Network error/i)).toBeInTheDocument();
    });
  });

  // test('snackbar display handling', async () => {
  //   const mockResponse = {
  //     predictions: { AAPL: 150 },
  //   };
  //   fetch.mockResolvedValueOnce({
  //     ok: true,
  //     json: jest.fn().mockResolvedValueOnce(mockResponse),
  //   });

  //   render(<App />);
  //   const input = screen.getByPlaceholderText(/Enter stock symbol/i);
  //   const addButton = screen.getByTestId('stock-add-button'); 
    
  //   fireEvent.change(input, { target: { value: 'AAPL' } });
  //   fireEvent.click(addButton);

  //   fireEvent.click(screen.getByText(/Analyze Stocks/i));

  //   await waitFor(() => {
  //     expect(screen.getByText(/Analysis completed successfully/i)).toBeInTheDocument();
  //   });

  //   fireEvent.click(screen.getByRole('button', { name: /Close/i }));

  //   expect(screen.queryByText(/Analysis completed successfully/i)).toBeNull();
  // });

  test('no valid predictions handling', async () => {
    const mockResponse = {
      predictions: {},
    };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: jest.fn().mockResolvedValueOnce(mockResponse),
    });

    render(<App />);
    const input = screen.getByPlaceholderText(/Enter stock symbol/i);
    const addButton = screen.getByTestId('stock-add-button'); 
    
    fireEvent.change(input, { target: { value: 'AAPL' } });
    fireEvent.click(addButton);

    fireEvent.click(screen.getByText(/Analyze Stocks/i));

    await waitFor(() => {
      expect(screen.getByText(/No valid predictions could be generated/i)).toBeInTheDocument();
    });
  });

  // test('loading state handling', async () => {
  //   const mockResponse = {
  //     predictions: { AAPL: 150 },
  //   };
  //   fetch.mockResolvedValueOnce({
  //     ok: true,
  //     json: jest.fn().mockResolvedValueOnce(mockResponse),
  //   });

  //   render(<App />);
  //   const input = screen.getByPlaceholderText(/Enter stock symbol/i);
  //   const addButton = screen.getByTestId('stock-add-button'); 
    
  //   fireEvent.change(input, { target: { value: 'AAPL' } });
  //   fireEvent.click(addButton);

  //   fireEvent.click(screen.getByText(/Analyze Stocks/i));
    
  //   expect(screen.getByTestId('stock-submit', { name: /Analyzing.../i })).toBeInTheDocument();
  // });
});