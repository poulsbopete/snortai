import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import { Send, Refresh, Person, SmartToy, History } from '@mui/icons-material';

// Use relative API URL since we're on the same domain
const apiUrl = typeof window !== 'undefined' ? window.location.origin : '';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: any[];
}

interface Agent {
  id: string;
  name: string;
  description: string;
}

interface Conversation {
  id: string;
  title?: string;
  last_activity?: string;
}

const MCPServerAssistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('snortai');
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showConversations, setShowConversations] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadAgents();
    loadConversations();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await fetch('/api/mcp/agents');
      const data = await response.json();
      if (data.agents) {
        setAgents(data.agents);
      }
    } catch (err) {
      console.error('Failed to load agents:', err);
    }
  };

  const loadConversations = async () => {
    try {
      const response = await fetch('/api/mcp/conversations');
      const data = await response.json();
      if (data.conversations) {
        setConversations(data.conversations);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const loadConversation = async (convId: string) => {
    try {
      const response = await fetch(`/api/mcp/conversations/${convId}`);
      const data = await response.json();
      if (data.conversation) {
        // Convert conversation data to messages format
        const conversationMessages: Message[] = [];
        // This would need to be adapted based on the actual conversation structure
        setMessages(conversationMessages);
        setConversationId(convId);
        setShowConversations(false);
      }
    } catch (err) {
      console.error('Failed to load conversation:', err);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const requestBody: any = {
        input: userMessage.content
      };

      if (conversationId) {
        requestBody.conversation_id = conversationId;
      }
      // Always use 'snortai' agent, or selectedAgent if user changed it
      requestBody.agent_id = selectedAgent || 'snortai';

      const response = await fetch('/api/mcp/converse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        timestamp: new Date(),
        citations: data.citations
      };

      setMessages(prev => [...prev, assistantMessage]);
      setConversationId(data.conversation_id);
      loadConversations(); // Refresh conversations list

    } catch (err: any) {
      setError(err.message || 'Error communicating with 1Chat');
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString();
  };

  return (
    <Paper sx={{ p: 3, height: '600px', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" component="h2">
          <SmartToy sx={{ mr: 1, verticalAlign: 'middle' }} />
          Elastic MCP Server Assistant
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="New Conversation">
            <IconButton onClick={startNewConversation} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Conversation History">
            <IconButton 
              onClick={() => setShowConversations(!showConversations)} 
              color="primary"
            >
              <History />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Agent Selection */}
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Select Agent (Optional)</InputLabel>
        <Select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          label="Select Agent (Optional)"
        >
          <MenuItem value="">
            <em>Default Agent</em>
          </MenuItem>
          {agents.map((agent) => (
            <MenuItem key={agent.id} value={agent.id}>
              {agent.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Conversation History Sidebar */}
      {showConversations && (
        <Paper sx={{ p: 2, mb: 2, maxHeight: '200px', overflow: 'auto' }}>
          <Typography variant="h6" gutterBottom>Recent Conversations</Typography>
          <List dense>
            {conversations.map((conv) => (
              <ListItem 
                key={conv.id} 
                component="button"
                onClick={() => loadConversation(conv.id)}
                sx={{ 
                  cursor: 'pointer', 
                  textAlign: 'left', 
                  width: '100%',
                  backgroundColor: conv.id === conversationId ? 'action.selected' : 'transparent'
                }}
              >
                <ListItemText 
                  primary={conv.title || `Conversation ${conv.id.slice(0, 8)}`}
                  secondary={conv.last_activity}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Messages */}
      <Box sx={{ flex: 1, overflow: 'auto', mb: 2, border: '1px solid #e0e0e0', borderRadius: 1, p: 1 }}>
        {messages.length === 0 ? (
          <Typography color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
            Start a conversation with the MCP Server assistant...
          </Typography>
        ) : (
          messages.map((message) => (
            <Box key={message.id} sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                {message.role === 'user' ? (
                  <Person sx={{ mr: 1, color: 'primary.main' }} />
                ) : (
                  <SmartToy sx={{ mr: 1, color: 'secondary.main' }} />
                )}
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                  {message.role === 'user' ? 'You' : 'MCP Server Assistant'}
                </Typography>
                <Typography variant="caption" sx={{ ml: 'auto', color: 'text.secondary' }}>
                  {formatTimestamp(message.timestamp)}
                </Typography>
              </Box>
              <Typography sx={{ 
                whiteSpace: 'pre-wrap', 
                p: 1, 
                backgroundColor: message.role === 'user' ? 'primary.light' : 'grey.100',
                borderRadius: 1,
                ml: 3
              }}>
                {message.content}
              </Typography>
              {message.citations && message.citations.length > 0 && (
                <Box sx={{ ml: 3, mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Sources:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                    {message.citations.map((citation, index) => (
                      <Chip 
                        key={index} 
                        label={`Source ${index + 1}`} 
                        size="small" 
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}
              <Divider sx={{ mt: 1 }} />
            </Box>
          ))
        )}
        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', p: 2 }}>
            <CircularProgress size={20} sx={{ mr: 2 }} />
            <Typography>MCP Server is thinking...</Typography>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Input */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask MCP Server anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          disabled={loading}
          multiline
          maxRows={3}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          sx={{ minWidth: 'auto', px: 2 }}
        >
          <Send />
        </Button>
      </Box>

      {/* Conversation ID Display */}
      {conversationId && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
          Conversation ID: {conversationId}
        </Typography>
      )}
    </Paper>
  );
};

export default MCPServerAssistant;
