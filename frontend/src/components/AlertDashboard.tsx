import React, { useEffect, useState } from 'react';
import { Grid, Paper, Typography, List, ListItem, ListItemText, Box } from '@mui/material';
import { Line, Bar } from 'react-chartjs-2';
import { theme } from '../theme';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface Alert {
  timestamp: string;
  alert_type: string;
  priority: number;
  message: string;
  source_ip: string;
  destination_ip: string;
  protocol: string;
}

interface AlertDashboardProps {
  onPrefill?: (question: string) => void;
}

const AlertDashboard: React.FC<AlertDashboardProps> = ({ onPrefill }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch('https://u3jq640fv3.execute-api.us-east-1.amazonaws.com/api/alerts');
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        if (!Array.isArray(data)) {
          throw new Error('API did not return an array');
        }
        setAlerts(data);
      } catch (error: any) {
        setError(error.message || 'Error fetching alerts');
        setAlerts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  const chartData = {
    labels: alerts.map(alert => new Date(alert.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Alert Priority',
        data: alerts.map(alert => alert.priority),
        borderColor: theme.palette.secondary.main,
        backgroundColor: theme.palette.secondary.light,
        tension: 0.3,
        fill: false,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  const alertTypesData = {
    labels: Array.from(new Set(alerts.map(alert => alert.alert_type))),
    datasets: [
      {
        label: 'Alert Types',
        data: Array.from(new Set(alerts.map(alert => alert.alert_type))).map(
          type => alerts.filter(alert => alert.alert_type === type).length
        ),
        backgroundColor: theme.palette.secondary.main,
      },
    ],
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
          <Typography component="h2" variant="h6" color="primary" gutterBottom>
            Alert Timeline
          </Typography>
          {loading ? (
            <Typography>Loading...</Typography>
          ) : error ? (
            <Typography color="error">{error}</Typography>
          ) : alerts.length === 0 ? (
            <Typography>No alerts found.</Typography>
          ) : (
            <Line
              data={chartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false },
                  title: { display: false },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                  x: {
                    ticks: { maxTicksLimit: 5 },
                  },
                },
              }}
            />
          )}
        </Paper>
      </Grid>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
          <Typography component="h2" variant="h6" color="primary" gutterBottom>
            Alert Types
          </Typography>
          {loading ? (
            <Typography>Loading...</Typography>
          ) : error ? (
            <Typography color="error">{error}</Typography>
          ) : alerts.length === 0 ? (
            <Typography>No alerts found.</Typography>
          ) : (
            <Bar
              data={alertTypesData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false },
                  title: { display: false },
                },
                scales: {
                  y: { beginAtZero: true },
                  x: { ticks: { maxTicksLimit: 5 } },
                },
              }}
            />
          )}
        </Paper>
      </Grid>
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography component="h2" variant="h6" color="primary" gutterBottom>
            Recent Alerts
          </Typography>
          {loading ? (
            <Typography>Loading...</Typography>
          ) : error ? (
            <Typography color="error">{error}</Typography>
          ) : alerts.length === 0 ? (
            <Typography>No alerts found.</Typography>
          ) : (
            <List>
              {alerts.slice(0, 5).map((alert, index) => (
                <ListItem key={index} divider button onClick={() => onPrefill && onPrefill(`Explain this alert: ${alert.message}`)}>
                  <ListItemText
                    primary={alert.message}
                    secondary={
                      <>
                        <Typography component="span" variant="body2" color="text.primary">
                          {alert.alert_type} - Priority {alert.priority}
                        </Typography>
                        <br />
                        {alert.source_ip} → {alert.destination_ip} ({alert.protocol})
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Paper>
      </Grid>
    </Grid>
  );
};

export default AlertDashboard; 