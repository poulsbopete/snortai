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

const AlertDashboard: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Replace with actual API call
    const fetchAlerts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/alerts');
        const data = await response.json();
        setAlerts(data);
      } catch (error) {
        console.error('Error fetching alerts:', error);
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
        borderColor: theme.palette.primary.main,
        backgroundColor: theme.palette.primary.main,
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
        backgroundColor: theme.palette.primary.main,
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
          <Line
            data={chartData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  reverse: true,
                },
              },
            }}
          />
        </Paper>
      </Grid>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
          <Typography component="h2" variant="h6" color="primary" gutterBottom>
            Alert Types
          </Typography>
          <Bar
            data={alertTypesData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
            }}
          />
        </Paper>
      </Grid>
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography component="h2" variant="h6" color="primary" gutterBottom>
            Recent Alerts
          </Typography>
          <List>
            {alerts.slice(0, 10).map((alert, index) => (
              <ListItem key={index} divider>
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
        </Paper>
      </Grid>
    </Grid>
  );
};

export default AlertDashboard; 