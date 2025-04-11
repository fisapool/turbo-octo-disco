import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { useAuth } from '../contexts/AuthContext';
import AlertSystem from './AlertSystem';
import TrendAnalysis from './TrendAnalysis';
import AdvancedTrendAnalysis from './AdvancedTrendAnalysis';
import DashboardLayout from './DashboardLayout';
import RoleBasedView from './RoleBasedView';
import UserFeedback from './UserFeedback';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentView, setCurrentView] = useState('default');
  const [activityData, setActivityData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Keyboard Activity',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
      {
        label: 'Mouse Activity',
        data: [],
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
      },
    ],
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/analytics/activity');
        if (!response.ok) {
          throw new Error('Failed to fetch activity data');
        }
        const data = await response.json();
        
        setActivityData({
          labels: data.labels,
          datasets: [
            {
              ...activityData.datasets[0],
              data: data.keyboardActivity,
            },
            {
              ...activityData.datasets[1],
              data: data.mouseActivity,
            },
          ],
        });
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const handleViewChange = (view) => {
    setCurrentView(view);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  const renderWidget = (widgetId) => {
    switch (widgetId) {
      case 'activity':
        return (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Real-time Activity Monitoring
            </Typography>
            <Box sx={{ height: 400 }}>
              <Line
                data={activityData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                  plugins: {
                    legend: {
                      position: 'top',
                    },
                    tooltip: {
                      mode: 'index',
                      intersect: false,
                    },
                  },
                }}
              />
            </Box>
          </Paper>
        );
      case 'trends':
        return <TrendAnalysis />;
      case 'advanced_trends':
        return <AdvancedTrendAnalysis />;
      case 'productivity':
        return (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Productivity Metrics
            </Typography>
            {/* Add productivity metrics components here */}
          </Paper>
        );
      case 'system':
        return (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Health
            </Typography>
            {/* Add system health components here */}
          </Paper>
        );
      case 'alerts':
        return <AlertSystem />;
      case 'feedback':
        return <UserFeedback />;
      default:
        return null;
    }
  };

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6" gutterBottom>
              Welcome, {user.name}
            </Typography>
            <Typography variant="body1">
              Role: {user.role}
            </Typography>
          </Box>
          <AlertSystem />
        </Box>
      </Paper>

      <RoleBasedView onViewChange={handleViewChange} />

      <DashboardLayout>
        {renderWidget}
      </DashboardLayout>
    </Box>
  );
};

export default Dashboard; 