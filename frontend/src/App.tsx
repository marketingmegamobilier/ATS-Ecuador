import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import Dashboard from './pages/Dashboard';
import PeriodoDetail from './pages/PeriodoDetail';
import ATSValidator from './pages/ATSValidator';
import ATSFileValidator from './pages/ATSFileValidator';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/periodo/:id" element={<PeriodoDetail />} />
          <Route path="/periodo/:id/validar" element={<ATSValidator />} />
          <Route path="/validar-archivo" element={<ATSFileValidator />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
