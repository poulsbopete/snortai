/**
 * Main SnortAI Dashboard Page
 */
import React, { useState } from 'react';
import type { NextPage } from 'next';
import Head from 'next/head';
import { ThemeProvider, CssBaseline, Box, Container, Typography, AppBar, Toolbar, Tabs, Tab } from '@mui/material';
import { theme } from '../components/theme';
import AlertDashboard from '../components/AlertDashboard';
import SnortAI from '../components/AIAssistant';
import MCPServerAssistant from '../components/MCPServerAssistant';
import MCPServerStatus from '../components/MCPServerStatus';

const Home: NextPage = () => {
  const [snortAIPrefill, setSnortAIPrefill] = useState<string | undefined>(undefined);
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Head>
        <title>SnortAI - Alert Analysis Dashboard</title>
        <meta name="description" content="AI-powered Snort IDS alert analysis" />
      </Head>
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
              <Tab label="MCP Server Assistant" />
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
              <MCPServerStatus />
              <MCPServerAssistant />
            </>
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default Home;
