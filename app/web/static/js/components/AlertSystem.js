import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Badge,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

const AlertSystem = () => {
  const [alerts, setAlerts] = useState([]);
  const [anchorEl, setAnchorEl] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch('/api/alerts');
        if (!response.ok) {
          throw new Error('Failed to fetch alerts');
        }
        const data = await response.json();
        setAlerts(data);
        setUnreadCount(data.filter(alert => !alert.read).length);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleAlertClick = async (alertId) => {
    try {
      const response = await fetch(`/api/alerts/${alertId}/read`, {
        method: 'PUT',
      });
      if (!response.ok) {
        throw new Error('Failed to mark alert as read');
      }
      setAlerts(alerts.map(alert =>
        alert.id === alertId ? { ...alert, read: true } : alert
      ));
      setUnreadCount(prev => prev - 1);
    } catch (error) {
      console.error('Error marking alert as read:', error);
    }
  };

  const getAlertIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      case 'success':
        return <CheckCircleIcon color="success" />;
      default:
        return <InfoIcon />;
    }
  };

  return (
    <Box>
      <IconButton
        color="inherit"
        onClick={handleMenuOpen}
        aria-controls="alert-menu"
        aria-haspopup="true"
      >
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Menu
        id="alert-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        PaperProps={{
          style: {
            width: 400,
            maxHeight: 500,
          },
        }}
      >
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Alerts
          </Typography>
          <List>
            {alerts.length === 0 ? (
              <ListItem>
                <ListItemText primary="No alerts" />
              </ListItem>
            ) : (
              alerts.map((alert) => (
                <ListItem
                  key={alert.id}
                  button
                  onClick={() => handleAlertClick(alert.id)}
                  sx={{
                    bgcolor: alert.read ? 'transparent' : 'action.hover',
                  }}
                >
                  <ListItemIcon>
                    {getAlertIcon(alert.severity)}
                  </ListItemIcon>
                  <ListItemText
                    primary={alert.message}
                    secondary={new Date(alert.timestamp).toLocaleString()}
                  />
                  <Chip
                    label={alert.severity}
                    size="small"
                    color={
                      alert.severity === 'critical'
                        ? 'error'
                        : alert.severity === 'warning'
                        ? 'warning'
                        : 'default'
                    }
                  />
                </ListItem>
              ))
            )}
          </List>
        </Paper>
      </Menu>
    </Box>
  );
};

export default AlertSystem; 