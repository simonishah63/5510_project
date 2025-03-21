import { render, screen, fireEvent } from '@testing-library/react';
import { StockInput } from '../components/StockInput';

describe('StockInput Component', () => {
    test('initial state', () => {
        render(<StockInput onSubmit={jest.fn()} loading={false} />);
        expect(screen.getByPlaceholderText(/Enter stock symbol/i)).toHaveValue('');
        expect(screen.queryByText(/This symbol has already been added/i)).toBeNull();
    });

    test('valid stock symbol addition', () => {
        render(<StockInput onSubmit={jest.fn()} loading={false} />);
        const input = screen.getByPlaceholderText(/Enter stock symbol/i);
        const addButton = screen.getByTestId('stock-add-button'); 
        
        fireEvent.change(input, { target: { value: 'AAPL' } });
        fireEvent.click(addButton);
        
        expect(screen.getByText('AAPL')).toBeInTheDocument();
        expect(input).toHaveValue('');
    });

    test('invalid stock symbol format', () => {
        render(<StockInput onSubmit={jest.fn()} loading={false} />);
        const input = screen.getByPlaceholderText(/Enter stock symbol/i);
        const addButton = screen.getByTestId('stock-add-button'); 
        
        fireEvent.change(input, { target: { value: 'INVALID_SYMBOL' } });
        fireEvent.click(addButton);
        
        expect(screen.getByText(/Invalid symbol format/i)).toBeInTheDocument();
    });


    test('duplicate stock symbol addition', () => {
        render(<StockInput onSubmit={jest.fn()} loading={false} />);
        const input = screen.getByPlaceholderText(/Enter stock symbol/i);
        const addButton = screen.getByTestId('stock-add-button'); 
        
        fireEvent.change(input, { target: { value: 'AAPL' } });
        fireEvent.click(addButton);
        
        fireEvent.change(input, { target: { value: 'AAPL' } });
        fireEvent.click(addButton);
    
        expect(screen.getByText(/This symbol has already been added/i)).toBeInTheDocument();
    });

    test('maximum symbol limit', () => {
        render(<StockInput onSubmit={jest.fn()} loading={false} />);
        const input = screen.getByPlaceholderText(/Enter stock symbol/i);
        const addButton = screen.getByTestId('stock-add-button'); 
        const symbols = ['AAPL', 'GOOG', 'AMZN', 'MSFT', 'TSLA'];
    
        symbols.forEach(symbol => {
          fireEvent.change(input, { target: { value: symbol } });
          fireEvent.click(addButton);
        });
    
        expect(screen.getByText(/Maximum number of symbols/i)).toBeInTheDocument();
    });
    
    test('submission with valid symbols', () => {
        const mockOnSubmit = jest.fn();
        render(<StockInput onSubmit={mockOnSubmit} loading={false} />);
        const input = screen.getByPlaceholderText(/Enter stock symbol/i);
        const addButton = screen.getByTestId('stock-add-button'); 
        
        fireEvent.change(input, { target: { value: 'AAPL' } });
        fireEvent.click(addButton);
        expect(screen.getByText('AAPL')).toBeInTheDocument();

        fireEvent.change(input, { target: { value: 'GOOG' } });
        fireEvent.click(addButton);
        expect(screen.getByText('GOOG')).toBeInTheDocument();

        fireEvent.click(screen.getByTestId('stock-submit'));
        
        expect(mockOnSubmit).toHaveBeenCalledWith(['AAPL', 'GOOG']);
        expect(mockOnSubmit).toHaveBeenCalledTimes(1);
    });
    
    test('loading state handling', () => {
        const mockOnSubmit = jest.fn();
        render(<StockInput onSubmit={mockOnSubmit} loading={true} />);
        
        expect(screen.getByTestId('stock-submit')).toBeDisabled();
    });
});
