import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Tooltip,
  Collapse
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Refresh,
  SmartToy,
  Build,
  Chat,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';

const apiUrl = process.env.REACT_APP_API_URL || 'https://u3jq640fv3.execute-api.us-east-1.amazonaws.com';

interface OneChatStatus {
  status: 'healthy' | 'unhealthy';
  agents_count: number;
  tools_count: number;
  available_agents: Array<{ id: string; name: string }>;
  test_chat_successful: boolean;
  last_test_conversation_id?: string;
  timestamp: string;
  error?: string;
}

const OneChatStatus: React.FC = () => {
  const [status, setStatus] = useState<OneChatStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [agentsExpanded, setAgentsExpanded] = useState(false);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiUrl}/api/onechat/status`);
      if (!response.ok) {
        throw `HTTP error! status: ${response.status}`;
      }
      
      const data = await response.json();
      setStatus(data);
      setLastChecked(new Date());
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch 1Chat status');
      setStatus(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    
    // Refresh status every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'unhealthy':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle color="success" />;
      case 'unhealthy':
        return <Error color="error" />;
      default:
        return <Error color="disabled" />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  if (loading && !status) {
    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CircularProgress size={24} />
            <Typography>Checking 1Chat status...</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" component="h2">
            <SmartToy sx={{ mr: 1, verticalAlign: 'middle' }} />
            Elastic 1Chat Status
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {lastChecked && (
              <Typography variant="caption" color="text.secondary">
                Last checked: {lastChecked.toLocaleTimeString()}
              </Typography>
            )}
            <Tooltip title="Refresh Status">
              <IconButton onClick={fetchStatus} disabled={loading} size="small">
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {status && (
          <>
            {/* Overall Status */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              {getStatusIcon(status.status)}
              <Typography variant="body1">
                Status: 
              </Typography>
              <Chip 
                label={status.status.toUpperCase()} 
                color={getStatusColor(status.status) as any}
                size="small"
              />
              {status.test_chat_successful && (
                <Chip 
                  label="Chat Test Passed" 
                  color="success" 
                  size="small"
                  icon={<Chat />}
                />
              )}
            </Box>

            {/* Statistics */}
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Chip 
                label={`${status.agents_count} Agents`}
                icon={<SmartToy />}
                variant="outlined"
              />
              <Chip 
                label={`${status.tools_count} Tools`}
                icon={<Build />}
                variant="outlined"
              />
            </Box>

            {/* Available Agents */}
            {status.available_agents.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Box 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: 'action.hover' },
                    borderRadius: 1,
                    p: 0.5,
                    mb: 1
                  }}
                  onClick={() => setAgentsExpanded(!agentsExpanded)}
                >
                  <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
                    Available Agents ({status.available_agents.length}):
                  </Typography>
                  <IconButton size="small">
                    {agentsExpanded ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </Box>
                <Collapse in={agentsExpanded}>
                  <List dense>
                    {status.available_agents.map((agent, index) => (
                      <React.Fragment key={agent.id}>
                        <ListItem sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <SmartToy fontSize="small" />
                          </ListItemIcon>
                          <ListItemText 
                            primary={agent.name}
                            secondary={`ID: ${agent.id}`}
                          />
                        </ListItem>
                        {index < status.available_agents.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                </Collapse>
              </Box>
            )}

            {/* Error Details */}
            {status.error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                <Typography variant="subtitle2">Error Details:</Typography>
                <Typography variant="body2">{status.error}</Typography>
              </Alert>
            )}

            {/* Test Conversation ID */}
            {status.last_test_conversation_id && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Test Conversation ID: {status.last_test_conversation_id}
                </Typography>
              </Box>
            )}

            {/* Timestamp */}
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Status timestamp: {formatTimestamp(status.timestamp)}
              </Typography>
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default OneChatStatus;
