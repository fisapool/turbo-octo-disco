import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Send as SendIcon,
} from '@mui/icons-material';

const PilotProgram = () => {
  const [participants, setParticipants] = useState([]);
  const [surveys, setSurveys] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(true);

  const steps = [
    'Define Objectives',
    'Select Participants',
    'Create Survey',
    'Launch Program',
    'Collect Feedback',
    'Analyze Results',
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [participantsRes, surveysRes] = await Promise.all([
          fetch('/api/pilot/participants'),
          fetch('/api/pilot/surveys'),
        ]);

        if (!participantsRes.ok || !surveysRes.ok) {
          throw new Error('Failed to fetch pilot program data');
        }

        const participantsData = await participantsRes.json();
        const surveysData = await surveysRes.json();

        setParticipants(participantsData);
        setSurveys(surveysData);
      } catch (error) {
        console.error('Error fetching pilot program data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleAddParticipant = async (participant) => {
    try {
      const response = await fetch('/api/pilot/participants', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(participant),
      });

      if (!response.ok) {
        throw new Error('Failed to add participant');
      }

      const newParticipant = await response.json();
      setParticipants([...participants, newParticipant]);
    } catch (error) {
      console.error('Error adding participant:', error);
    }
  };

  const handleCreateSurvey = async (survey) => {
    try {
      const response = await fetch('/api/pilot/surveys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(survey),
      });

      if (!response.ok) {
        throw new Error('Failed to create survey');
      }

      const newSurvey = await response.json();
      setSurveys([...surveys, newSurvey]);
    } catch (error) {
      console.error('Error creating survey:', error);
    }
  };

  const handleSendSurvey = async (surveyId) => {
    try {
      const response = await fetch(`/api/pilot/surveys/${surveyId}/send`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to send survey');
      }

      // Update survey status
      setSurveys(surveys.map(survey =>
        survey.id === surveyId ? { ...survey, status: 'sent' } : survey
      ));
    } catch (error) {
      console.error('Error sending survey:', error);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Pilot Program Management
        </Typography>
        <Stepper activeStep={currentStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Participants
            </Typography>
            <List>
              {participants.map((participant) => (
                <ListItem key={participant.id}>
                  <ListItemText
                    primary={participant.name}
                    secondary={`Role: ${participant.role} | Department: ${participant.department}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton edge="end" aria-label="delete">
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
            <Button
              variant="contained"
              onClick={() => setOpenDialog(true)}
              sx={{ mt: 2 }}
            >
              Add Participant
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Surveys
            </Typography>
            <List>
              {surveys.map((survey) => (
                <ListItem key={survey.id}>
                  <ListItemText
                    primary={survey.title}
                    secondary={`Status: ${survey.status} | Responses: ${survey.responses}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      aria-label="send"
                      onClick={() => handleSendSurvey(survey.id)}
                      disabled={survey.status === 'sent'}
                    >
                      <SendIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
            <Button
              variant="contained"
              onClick={() => setOpenDialog(true)}
              sx={{ mt: 2 }}
            >
              Create Survey
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>
          {currentStep === 1 ? 'Add Participant' : 'Create Survey'}
        </DialogTitle>
        <DialogContent>
          {currentStep === 1 ? (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Name"
                margin="normal"
              />
              <TextField
                fullWidth
                label="Email"
                margin="normal"
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Role</InputLabel>
                <Select label="Role">
                  <MenuItem value="employee">Employee</MenuItem>
                  <MenuItem value="manager">Manager</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth margin="normal">
                <InputLabel>Department</InputLabel>
                <Select label="Department">
                  <MenuItem value="hr">HR</MenuItem>
                  <MenuItem value="it">IT</MenuItem>
                  <MenuItem value="operations">Operations</MenuItem>
                </Select>
              </FormControl>
            </Box>
          ) : (
            <Box sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Survey Title"
                margin="normal"
              />
              <TextField
                fullWidth
                label="Description"
                margin="normal"
                multiline
                rows={4}
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>Target Audience</InputLabel>
                <Select label="Target Audience">
                  <MenuItem value="all">All Participants</MenuItem>
                  <MenuItem value="managers">Managers Only</MenuItem>
                  <MenuItem value="employees">Employees Only</MenuItem>
                </Select>
              </FormControl>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              setOpenDialog(false);
              setCurrentStep(prev => prev + 1);
            }}
          >
            {currentStep === 1 ? 'Add Participant' : 'Create Survey'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PilotProgram; 