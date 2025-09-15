import React, { useState } from 'react';
import { ThemeProvider, CssBaseline, Box, Container, Typography, AppBar, Toolbar, Tabs, Tab } from '@mui/material';
import { theme } from './theme';
import AlertDashboard from './components/AlertDashboard';
import SnortAI from './components/AIAssistant';
import OneChatAssistant from './components/OneChatAssistant';
import OneChatStatus from './components/OneChatStatus';

function App() {
  const [snortAIPrefill, setSnortAIPrefill] = useState<string | undefined>(undefined);
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" color="primary">
          <Toolbar>
            <img src="/snort-logo.png" alt="Snort Logo" style={{ height: 60, marginRight: 16 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              SnortAI
            </Typography>
            <Tabs value={activeTab} onChange={handleTabChange} textColor="inherit">
              <Tab label="Alert Dashboard" />
              <Tab label="Snort AI" />
              <Tab label="1Chat Assistant" />
            </Tabs>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Snort Alert Analysis
          </Typography>
          
          {activeTab === 0 && (
            <AlertDashboard onPrefill={setSnortAIPrefill} prefill={snortAIPrefill} />
          )}
          
          {activeTab === 1 && (
            <SnortAI prefill={snortAIPrefill} />
          )}
          
          {activeTab === 2 && (
            <>
              <OneChatStatus />
              <OneChatAssistant />
            </>
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
