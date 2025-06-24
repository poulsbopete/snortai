import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Paper, CircularProgress } from '@mui/material';

const apiUrl = process.env.REACT_APP_API_URL || 'https://u3jq640fv3.execute-api.us-east-1.amazonaws.com';

const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState<{ user: string; ai: string }[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/api/ai-assistant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
      });
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      setMessages([...messages, { user: input, ai: data.answer }]);
      setInput('');
    } catch (err: any) {
      setError(err.message || 'Error contacting AI assistant');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 2, mt: 4 }}>
      <Typography variant="h6" gutterBottom>AI Assistant</Typography>
      <Box sx={{ minHeight: 120, mb: 2 }}>
        {messages.length === 0 && <Typography color="text.secondary">Ask a question about Snort alerts...</Typography>}
        {messages.map((msg, idx) => (
          <Box key={idx} sx={{ mb: 2 }}>
            <Typography variant="body2" color="primary"><strong>You:</strong> {msg.user}</Typography>
            <Typography variant="body2" color="secondary"><strong>AI:</strong> {msg.ai}</Typography>
          </Box>
        ))}
        {loading && <CircularProgress size={24} />}
        {error && <Typography color="error">{error}</Typography>}
      </Box>
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Type your question..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
          disabled={loading}
        />
        <Button variant="contained" color="primary" onClick={handleSend} disabled={loading || !input.trim()}>
          Send
        </Button>
      </Box>
    </Paper>
  );
};

export default AIAssistant; 