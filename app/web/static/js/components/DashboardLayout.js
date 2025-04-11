import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  DragHandle as DragHandleIcon,
  Tooltip,
} from '@mui/material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { useAuth } from '../contexts/AuthContext';

const DashboardLayout = ({ children, onLayoutChange }) => {
  const { user } = useAuth();
  const [layout, setLayout] = useState([]);
  const [open, setOpen] = useState(false);
  const [currentView, setCurrentView] = useState('default');
  const [availableWidgets, setAvailableWidgets] = useState([
    { id: 'activity', name: 'Activity Monitor', roles: ['admin', 'manager', 'employee'] },
    { id: 'trends', name: 'Trend Analysis', roles: ['admin', 'manager'] },
    { id: 'productivity', name: 'Productivity Metrics', roles: ['admin', 'manager'] },
    { id: 'system', name: 'System Health', roles: ['admin'] },
    { id: 'alerts', name: 'Alert System', roles: ['admin', 'manager'] },
  ]);

  useEffect(() => {
    // Load saved layout from localStorage based on role and view
    const savedLayout = localStorage.getItem(`dashboardLayout_${user.role}_${currentView}`);
    if (savedLayout) {
      setLayout(JSON.parse(savedLayout));
    } else {
      // Default layout based on role
      const defaultLayout = getDefaultLayout(user.role);
      setLayout(defaultLayout);
    }
  }, [user.role, currentView]);

  const getDefaultLayout = (role) => {
    const roleWidgets = availableWidgets.filter(widget => 
      widget.roles.includes(role)
    );
    
    return roleWidgets.map((widget, index) => ({
      id: widget.id,
      x: index % 2 === 0 ? 0 : 6,
      y: Math.floor(index / 2) * 4,
      w: 6,
      h: 4,
    }));
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(layout);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setLayout(items);
    saveLayout(items);
    if (onLayoutChange) {
      onLayoutChange(items);
    }
  };

  const handleAddWidget = (widgetId) => {
    const newLayout = [...layout];
    const widget = availableWidgets.find(w => w.id === widgetId);
    
    if (widget && widget.roles.includes(user.role)) {
      newLayout.push({
        id: widget.id,
        x: 0,
        y: Math.max(...newLayout.map(item => item.y)) + 4,
        w: 6,
        h: 4,
      });
      
      setLayout(newLayout);
      saveLayout(newLayout);
      if (onLayoutChange) {
        onLayoutChange(newLayout);
      }
    }
    
    setOpen(false);
  };

  const handleRemoveWidget = (widgetId) => {
    const newLayout = layout.filter(item => item.id !== widgetId);
    setLayout(newLayout);
    saveLayout(newLayout);
    if (onLayoutChange) {
      onLayoutChange(newLayout);
    }
  };

  const saveLayout = (layout) => {
    localStorage.setItem(
      `dashboardLayout_${user.role}_${currentView}`,
      JSON.stringify(layout)
    );
  };

  const handleViewChange = (view) => {
    setCurrentView(view);
  };

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between' }}>
        <Button
          variant="outlined"
          onClick={() => setOpen(true)}
        >
          Customize Layout
        </Button>
      </Box>

      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="dashboard">
          {(provided) => (
            <Grid
              container
              spacing={2}
              {...provided.droppableProps}
              ref={provided.innerRef}
            >
              {layout.map((item, index) => (
                <Draggable
                  key={item.id}
                  draggableId={item.id}
                  index={index}
                >
                  {(provided) => (
                    <Grid
                      item
                      xs={12}
                      md={item.w === 6 ? 6 : 12}
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                    >
                      <Paper
                        sx={{
                          p: 2,
                          height: '100%',
                          position: 'relative',
                        }}
                      >
                        <Box
                          {...provided.dragHandleProps}
                          sx={{
                            position: 'absolute',
                            top: 8,
                            right: 8,
                            cursor: 'move',
                          }}
                        >
                          <Tooltip title="Drag to reorder">
                            <DragHandleIcon />
                          </Tooltip>
                        </Box>
                        <IconButton
                          size="small"
                          onClick={() => handleRemoveWidget(item.id)}
                          sx={{
                            position: 'absolute',
                            top: 8,
                            right: 40,
                          }}
                        >
                          ×
                        </IconButton>
                        {React.Children.map(children, (child) =>
                          React.cloneElement(child, { widgetId: item.id })
                        )}
                      </Paper>
                    </Grid>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </Grid>
          )}
        </Droppable>
      </DragDropContext>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Add Widget</DialogTitle>
        <DialogContent>
          <List>
            {availableWidgets
              .filter(widget => 
                !layout.some(item => item.id === widget.id) &&
                widget.roles.includes(user.role)
              )
              .map((widget) => (
                <ListItem
                  button
                  key={widget.id}
                  onClick={() => handleAddWidget(widget.id)}
                >
                  <ListItemText 
                    primary={widget.name}
                    secondary={`Available for: ${widget.roles.join(', ')}`}
                  />
                </ListItem>
              ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DashboardLayout; 