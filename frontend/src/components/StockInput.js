import React, { useState } from 'react';
import { 
  Paper, 
  TextField, 
  Button, 
  Box, 
  Typography,
  Chip,
  CircularProgress,
  Alert,
  Tooltip
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';

export const StockInput = ({ onSubmit, loading }) => {
  const [inputValue, setInputValue] = useState('');
  const [symbols, setSymbols] = useState([]);
  const [error, setError] = useState('');

  const validateSymbol = (symbol) => {
    const symbolRegex = /^[A-Z]{1,5}$/;
    return symbolRegex.test(symbol);
  };

  const handleInputChange = (event) => {
    const value = event.target.value.toUpperCase();
    setInputValue(value);
    setError('');
  };

  const handleInputKeyPress = (event) => {
    if (event.key === 'Enter' && inputValue.trim()) {
      addSymbol();
    }
  };

  const addSymbol = () => {
    const symbol = inputValue.trim().toUpperCase();
    
    if (!symbol) {
      setError('Please enter a stock symbol');
      return;
    }

    if (!validateSymbol(symbol)) {
      setError('Invalid symbol format. Stock symbols should be 1-5 capital letters.');
      return;
    }

    if (symbols.includes(symbol)) {
      setError('This symbol has already been added');
      return;
    }

    if (symbols.length >= 5) {
      setError('Maximum of 5 symbols allowed at once');
      return;
    }

    setSymbols([...symbols, symbol]);
    setInputValue('');
    setError('');
  };

  const removeSymbol = (symbolToRemove) => {
    setSymbols(symbols.filter(symbol => symbol !== symbolToRemove));
    setError('');
  };

  const handleSubmit = () => {
    if (symbols.length === 0) {
      setError('Please add at least one stock symbol');
      return;
    }
    onSubmit(symbols);
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 3, 
        mb: 3,
        bgcolor: 'background.paper',
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'translateY(-2px)'
        }
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Enter Stock Symbols
        </Typography>
        <Tooltip title="Enter stock symbols (e.g., AAPL for Apple Inc.) to analyze and predict their prices. Add up to 5 symbols." arrow>
          <InfoOutlinedIcon sx={{ ml: 1, color: 'text.secondary', cursor: 'help' }} />
        </Tooltip>
      </Box>

      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Enter stock symbol (e.g., AAPL)"
          value={inputValue}
          onChange={handleInputChange}
          onKeyPress={handleInputKeyPress}
          disabled={loading}
          error={!!error}
          helperText={error}
          InputProps={{
            sx: { textTransform: 'uppercase' }
          }}
        />
        <Button
          variant="contained"
          onClick={addSymbol}
          disabled={!inputValue.trim() || loading}
          startIcon={<AddIcon />}
        >
          Add
        </Button>
      </Box>
      
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2, minHeight: '40px' }}>
        {symbols.map((symbol) => (
          <Chip
            key={symbol}
            label={symbol}
            onDelete={() => removeSymbol(symbol)}
            disabled={loading}
            color="primary"
            sx={{
              transition: 'all 0.2s',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: 1
              }
            }}
          />
        ))}
      </Box>

      <Button
        fullWidth
        variant="contained"
        color="primary"
        onClick={handleSubmit}
        disabled={symbols.length === 0 || loading}
        startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
        sx={{
          height: '48px',
          transition: 'all 0.2s',
          '&:not(:disabled):hover': {
            transform: 'translateY(-2px)',
            boxShadow: 2
          }
        }}
      >
        {loading ? 'Analyzing...' : 'Analyze Stocks'}
      </Button>

      {symbols.length === 5 && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Maximum number of symbols (5) reached
        </Alert>
      )}
    </Paper>
  );
};
