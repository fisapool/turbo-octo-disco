import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const RoleBasedView = ({ onViewChange }) => {
  const { user } = useAuth();
  const [selectedView, setSelectedView] = useState('default');
  const [customViews, setCustomViews] = useState([]);
  const [open, setOpen] = useState(false);
  const [newViewName, setNewViewName] = useState('');

  useEffect(() => {
    // Load saved views from localStorage
    const savedViews = localStorage.getItem(`dashboardViews_${user.role}`);
    if (savedViews) {
      setCustomViews(JSON.parse(savedViews));
    }
  }, [user.role]);

  const handleViewChange = (view) => {
    setSelectedView(view);
    if (onViewChange) {
      onViewChange(view);
    }
  };

  const handleCreateView = () => {
    if (newViewName.trim()) {
      const newView = {
        id: Date.now(),
        name: newViewName,
        role: user.role,
        widgets: [], // Will be populated from current layout
      };
      setCustomViews([...customViews, newView]);
      localStorage.setItem(
        `dashboardViews_${user.role}`,
        JSON.stringify([...customViews, newView])
      );
      setNewViewName('');
      setOpen(false);
    }
  };

  const handleDeleteView = (viewId) => {
    const updatedViews = customViews.filter(view => view.id !== viewId);
    setCustomViews(updatedViews);
    localStorage.setItem(
      `dashboardViews_${user.role}`,
      JSON.stringify(updatedViews)
    );
  };

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">Dashboard View</Typography>
        <Button variant="outlined" onClick={() => setOpen(true)}>
          Create New View
        </Button>
      </Box>

      <FormControl fullWidth sx={{ mt: 2 }}>
        <InputLabel>Select View</InputLabel>
        <Select
          value={selectedView}
          label="Select View"
          onChange={(e) => handleViewChange(e.target.value)}
        >
          <MenuItem value="default">Default View</MenuItem>
          {customViews.map((view) => (
            <MenuItem key={view.id} value={view.id}>
              {view.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <List sx={{ mt: 2 }}>
        {customViews.map((view) => (
          <ListItem
            key={view.id}
            secondaryAction={
              <Button
                color="error"
                onClick={() => handleDeleteView(view.id)}
              >
                Delete
              </Button>
            }
          >
            <ListItemText
              primary={view.name}
              secondary={`Role: ${view.role}`}
            />
          </ListItem>
        ))}
      </List>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Create New View</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>View Name</InputLabel>
            <Select
              value={newViewName}
              label="View Name"
              onChange={(e) => setNewViewName(e.target.value)}
            >
              <MenuItem value="Manager View">Manager View</MenuItem>
              <MenuItem value="HR View">HR View</MenuItem>
              <MenuItem value="Employee View">Employee View</MenuItem>
              <MenuItem value="Custom View">Custom View</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateView} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default RoleBasedView; 