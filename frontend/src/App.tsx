import React from 'react';
import { ThemeProvider, CssBaseline, Box, Container, Typography, AppBar, Toolbar } from '@mui/material';
import { theme } from './theme';
import AlertDashboard from './components/AlertDashboard';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" color="primary">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              SnortAI
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Snort Alert Analysis
          </Typography>
          <AlertDashboard />
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
