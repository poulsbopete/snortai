import React, { useState, useEffect } from 'react';
import { Box, Typography, TextField, Button, Paper, CircularProgress } from '@mui/material';

const apiUrl = process.env.REACT_APP_API_URL || 'https://u3jq640fv3.execute-api.us-east-1.amazonaws.com';

interface SnortAIProps {
  prefill?: string;
}

const SnortAI: React.FC<SnortAIProps> = ({ prefill }) => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submittedQuestion, setSubmittedQuestion] = useState('');

  useEffect(() => {
    if (prefill !== undefined) {
      setQuestion(prefill);
    }
  }, [prefill]);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    setAnswer('');
    setSubmittedQuestion(question);
    try {
      const response = await fetch(`${apiUrl}/api/ai-assistant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const data = await response.json();
      setAnswer(data.answer || 'No answer returned.');
    } catch (err: any) {
      setError(err.message || 'Error contacting Snort AI');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 2, mt: 4 }}>
      <Typography variant="h6" gutterBottom>Snort AI</Typography>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Ask a question about your alerts..."
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleAsk(); }}
          disabled={loading}
        />
        <Button variant="contained" color="primary" onClick={handleAsk} disabled={loading || !question.trim()}>
          {loading ? <CircularProgress size={22} /> : 'Ask'}
        </Button>
      </Box>
      <Box sx={{ mt: 2 }}>
        {submittedQuestion && (
          <Typography><b>You asked:</b> {submittedQuestion}</Typography>
        )}
        {loading && (
          <Typography sx={{ mt: 1 }}>AI Searching for "{question}"...</Typography>
        )}
        {error && <Typography color="error">{error}</Typography>}
        {answer && !loading && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom><b>AI responded:</b></Typography>
            <Typography sx={{ whiteSpace: 'pre-wrap' }}>{answer}</Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default SnortAI; 