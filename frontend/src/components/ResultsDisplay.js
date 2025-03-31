import React from 'react';
import { 
  Paper, 
  Typography, 
  Grid, 
  CircularProgress,
  Alert,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  List,
  ListItem,
  ListItemText,
  Button,
  Card,
  CardContent,
  CardMedia,
  CardActions
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import DownloadIcon from '@mui/icons-material/Download';

export const ResultsDisplay = ({ results, loading, error }) => {
  const API_BASE_URL = 'http://127.0.0.1:5000';

  const downloadFile = async (filename) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/results/${filename}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  const analysisImages = [
    { title: 'Closing Prices', file: 'closing_prices.png' },
    { title: 'Volume Analysis', file: 'volume.png' },
    { title: 'Moving Averages', file: 'moving_averages.png' },
    { title: 'Daily Returns', file: 'daily_returns.png' }
  ];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          {error}
        </Typography>
        {results?.details && (
          <Typography variant="body2">
            {results.details}
          </Typography>
        )}
      </Alert>
    );
  }

  if (!results) {
    return null;
  }

  // Check for symbol-specific errors
  const hasErrors = results.errors && Object.keys(results.errors).length > 0;

  return (
    <Grid container spacing={3}>
      {/* Symbol-specific Errors */}
      {hasErrors && (
        <Grid item xs={12}>
          <Alert severity="warning">
            <Typography variant="subtitle1" gutterBottom>
              Some symbols encountered errors during analysis:
            </Typography>
            <List dense>
              {Object.entries(results.errors).map(([symbol, errorMsg]) => (
                <ListItem key={symbol}>
                  <ListItemText
                    primary={symbol}
                    secondary={errorMsg}
                  />
                </ListItem>
              ))}
            </List>
          </Alert>
        </Grid>
      )}

      {/* Prediction Charts */}
      {results.predictions && Object.entries(results.predictions).map(([symbol, data]) => {
        if (!data) return null; // Skip if no data for this symbol
        
        return (
          <Grid item xs={12} md={6} key={symbol}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                {symbol} Price Prediction
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => `$${value.toFixed(2)}`}
                  />
                  <Tooltip 
                    formatter={(value) => [`$${value.toFixed(2)}`, value === data[0].actual ? 'Actual Price' : 'Predicted Price']}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="actual" 
                    stroke="#8884d8" 
                    name="Actual Price" 
                    dot={false}
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="predicted" 
                    stroke="#82ca9d" 
                    name="Predicted Price" 
                    dot={false}
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={() => downloadFile(`${symbol}_prediction_report.txt`)}
                >
                  Download Report
                </Button>
              </Box>
            </Paper>
          </Grid>
        );
      })}

      {/* Performance Metrics */}
      {results.metrics && Object.values(results.metrics).some(m => m !== null) && (
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Model Performance Metrics
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Symbol</TableCell>
                    <TableCell>RMSE</TableCell>
                    <TableCell>Normalized RMSE</TableCell>
                    <TableCell>MAE</TableCell>
                    <TableCell>R² Score</TableCell>
                    <TableCell>Directional Accuracy</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(results.metrics).map(([symbol, metrics]) => {
                    if (!metrics) return null; // Skip if no metrics for this symbol
                    
                    return (
                      <TableRow key={symbol}>
                        <TableCell>{symbol}</TableCell>
                        <TableCell>${metrics.rmse.toFixed(2)}</TableCell>
                        <TableCell>{metrics.normalized_rmse.toFixed(2)}%</TableCell>
                        <TableCell>${metrics.mae.toFixed(2)}</TableCell>
                        <TableCell>{metrics.r2.toFixed(4)}</TableCell>
                        <TableCell>{metrics.directional_accuracy.toFixed(2)}%</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      )}

      {/* Technical Analysis */}
      {results.technical_analysis && (
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Technical Analysis
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(results.technical_analysis).map(([symbol, analysis]) => {
                if (analysis.error) return null; // Skip if there's an error for this symbol
                
                return (
                  <Grid item xs={12} md={6} key={symbol}>
                    <Paper 
                      elevation={2} 
                      sx={{ 
                        p: 2,
                        bgcolor: 'background.default',
                        transition: 'transform 0.2s',
                        '&:hover': {
                          transform: 'translateY(-4px)'
                        }
                      }}
                    >
                      <Typography variant="subtitle1" gutterBottom>
                        {symbol}
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        <Typography variant="body2" color={analysis.moving_averages === 'Bullish' ? 'success.main' : 'error.main'}>
                          Moving Averages: {analysis.moving_averages}
                        </Typography>
                        <Typography variant="body2" color={analysis.volume_trend === 'High' ? 'success.main' : 'text.secondary'}>
                          Volume Trend: {analysis.volume_trend}
                        </Typography>
                        <Typography variant="body2" color={analysis.price_trend === 'Upward' ? 'success.main' : 'error.main'}>
                          Price Trend: {analysis.price_trend}
                        </Typography>
                      </Box>
                    </Paper>
                  </Grid>
                );
              })}
            </Grid>
          </Paper>
        </Grid>
      )}

      {/* Analysis Diagrams */}
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Analysis Diagrams
          </Typography>
          <Grid container spacing={2}>
            {analysisImages.map((image) => (
              <Grid item xs={12} sm={6} md={3} key={image.file}>
                <Card>
                  <CardMedia
                    component="img"
                    height="200"
                    image={`${API_BASE_URL}/api/results/${image.file}`}
                    alt={image.title}
                  />
                  <CardContent>
                    <Typography variant="h6" component="div">
                      {image.title}
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button 
                      size="small" 
                      startIcon={<DownloadIcon />}
                      onClick={() => downloadFile(image.file)}
                    >
                      Download
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Grid>

      {/* Download Reports */}
      {results.predictions && Object.keys(results.predictions).length > 0 && (
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Analysis Reports
            </Typography>
            <Grid container spacing={2}>
              {Object.keys(results.predictions).map((symbol) => (
                <Grid item xs={12} sm={6} md={3} key={symbol}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" component="div">
                        {symbol} Analysis Report
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button 
                        size="small" 
                        startIcon={<DownloadIcon />}
                        onClick={() => downloadFile(`${symbol}_prediction_report.txt`)}
                      >
                        Download Report
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      )}
    </Grid>
  );
};