import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Rating,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  Snackbar,
  Chip,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const UserFeedback = () => {
  const { user } = useAuth();
  const [feedback, setFeedback] = useState({
    type: 'general',
    rating: 0,
    comment: '',
    sentiment: 'neutral',
  });
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [submissionStatus, setSubmissionStatus] = useState(null);

  const feedbackTypes = [
    { value: 'general', label: 'General Feedback' },
    { value: 'feature', label: 'Feature Request' },
    { value: 'bug', label: 'Bug Report' },
    { value: 'suggestion', label: 'Suggestion' },
    { value: 'other', label: 'Other' },
  ];

  const handleSubmit = async () => {
    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...feedback,
          userId: user.id,
          timestamp: new Date().toISOString(),
        }),
      });

      if (response.ok) {
        setSubmissionStatus('success');
        setFeedback({
          type: 'general',
          rating: 0,
          comment: '',
          sentiment: 'neutral',
        });
      } else {
        setSubmissionStatus('error');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setSubmissionStatus('error');
    }
    setOpenSnackbar(true);
  };

  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };

  const handleSentimentChange = (newSentiment) => {
    setFeedback({ ...feedback, sentiment: newSentiment });
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Provide Feedback
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Feedback Type</InputLabel>
            <Select
              value={feedback.type}
              label="Feedback Type"
              onChange={(e) => setFeedback({ ...feedback, type: e.target.value })}
            >
              {feedbackTypes.map((type) => (
                <MenuItem key={type.value} value={type.value}>
                  {type.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6}>
          <Box>
            <Typography component="legend">Rating</Typography>
            <Rating
              value={feedback.rating}
              onChange={(e, newValue) => {
                setFeedback({ ...feedback, rating: newValue });
              }}
            />
          </Box>
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Your Feedback"
            value={feedback.comment}
            onChange={(e) => setFeedback({ ...feedback, comment: e.target.value })}
          />
        </Grid>

        <Grid item xs={12}>
          <Typography gutterBottom>Sentiment</Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {['positive', 'neutral', 'negative'].map((sentiment) => (
              <Chip
                key={sentiment}
                label={sentiment}
                color={feedback.sentiment === sentiment ? 'primary' : 'default'}
                onClick={() => handleSentimentChange(sentiment)}
                variant={feedback.sentiment === sentiment ? 'filled' : 'outlined'}
              />
            ))}
          </Box>
        </Grid>

        <Grid item xs={12}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleSubmit}
            disabled={!feedback.comment.trim()}
          >
            Submit Feedback
          </Button>
        </Grid>
      </Grid>

      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={submissionStatus === 'success' ? 'success' : 'error'}
          sx={{ width: '100%' }}
        >
          {submissionStatus === 'success'
            ? 'Thank you for your feedback!'
            : 'Failed to submit feedback. Please try again.'}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default UserFeedback; 