import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import { StockInput } from './components/StockInput';
import { Header } from './components/Header';
import { Alert, Snackbar } from '@mui/material';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#0a1929',
      paper: '#1e2a3a',
    },
    success: {
      main: '#66bb6a',
    },
    error: {
      main: '#f44336',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  const [currentSymbol, setCurrentSymbol] = useState(null);

  const handleStockSubmit = async (symbols) => {
    setLoading(true);
    setError(null);
    setResults(null);
    setCurrentSymbol(symbols[0]);
    try {
      setSnackbar({
        open: true,
        message: `Analyzing ${symbols.length} stock${symbols.length > 1 ? 's' : ''}...`,
        severity: 'info'
      });

      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ symbols }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || data.details || 'Failed to fetch prediction results');
      }
      
      // Check if we have any successful predictions
      const hasValidPredictions = Object.values(data.predictions || {}).some(pred => pred !== null);
      
      if (!hasValidPredictions) {
        throw new Error('No valid predictions could be generated for the provided symbols');
      }
      
      setResults(data);
      
      // Show success message
      setSnackbar({
        open: true,
        message: 'Analysis completed successfully!',
        severity: 'success'
      });
      
    } catch (err) {
      setError(err.message);
      setSnackbar({
        open: true,
        message: `Error: ${err.message}`,
        severity: 'error'
      });
    } finally {
      setLoading(false);
      setCurrentSymbol(null);
    }
  };

  const handleSnackbarClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          bgcolor: 'background.default',
          color: 'text.primary',
          pb: 4,
        }}
      >
        <Header />
        <Container maxWidth="lg">
          <Box sx={{ my: 4 }}>
            <StockInput onSubmit={handleStockSubmit} loading={loading} />
          </Box>
        </Container>
        <Snackbar 
          open={snackbar.open} 
          autoHideDuration={6000} 
          onClose={handleSnackbarClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleSnackbarClose} 
            severity={snackbar.severity}
            variant="filled"
            sx={{ width: '100%' }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;