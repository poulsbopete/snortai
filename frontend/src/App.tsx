import React, { useState } from 'react';
import { ThemeProvider, CssBaseline, Box, Container, Typography, AppBar, Toolbar } from '@mui/material';
import { theme } from './theme';
import AlertDashboard from './components/AlertDashboard';
import SnortAI from './components/AIAssistant';

function App() {
  const [snortAIPrefill, setSnortAIPrefill] = useState<string | undefined>(undefined);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" color="primary">
          <Toolbar>
            <img src="/snort-logo.png" alt="Snort Logo" style={{ height: 40, marginRight: 16 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              SnortAI
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Snort Alert Analysis
          </Typography>
          <AlertDashboard onPrefill={setSnortAIPrefill} />
          <SnortAI prefill={snortAIPrefill} />
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
