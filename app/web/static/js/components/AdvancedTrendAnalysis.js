import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Button,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  Line,
  Bar,
  Pie,
  Scatter,
} from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const AdvancedTrendAnalysis = () => {
  const [timeRange, setTimeRange] = useState('week');
  const [metric, setMetric] = useState('activity');
  const [chartType, setChartType] = useState('line');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `/api/analytics/trends?timeRange=${timeRange}&metric=${metric}`
        );
        if (!response.ok) {
          throw new Error('Failed to fetch trend data');
        }
        const result = await response.json();
        setData(result);

        if (comparisonMode) {
          const comparisonResponse = await fetch(
            `/api/analytics/trends?timeRange=${timeRange}&metric=${metric}&compare=true`
          );
          if (comparisonResponse.ok) {
            const comparisonResult = await comparisonResponse.json();
            setComparisonData(comparisonResult);
          }
        }
      } catch (error) {
        console.error('Error fetching trend data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeRange, metric, comparisonMode]);

  const renderChart = () => {
    if (!data) return null;

    const chartData = {
      labels: data.labels,
      datasets: [
        {
          label: data.metricLabel,
          data: data.values,
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 2,
          fill: chartType === 'line',
        },
        ...(comparisonData ? [{
          label: `${data.metricLabel} (Comparison)`,
          data: comparisonData.values,
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 2,
          fill: chartType === 'line',
        }] : []),
      ],
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false,
        },
        title: {
          display: true,
          text: `${data.metricLabel} Trend Analysis`,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    };

    switch (chartType) {
      case 'line':
        return <Line data={chartData} options={options} />;
      case 'bar':
        return <Bar data={chartData} options={options} />;
      case 'pie':
        return <Pie data={chartData} options={options} />;
      case 'scatter':
        return <Scatter data={chartData} options={options} />;
      default:
        return <Line data={chartData} options={options} />;
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Advanced Trend Analysis
      </Typography>
      
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid item xs={12} sm={3}>
          <FormControl fullWidth>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="hour">Last Hour</MenuItem>
              <MenuItem value="day">Last Day</MenuItem>
              <MenuItem value="week">Last Week</MenuItem>
              <MenuItem value="month">Last Month</MenuItem>
              <MenuItem value="quarter">Last Quarter</MenuItem>
              <MenuItem value="year">Last Year</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={3}>
          <FormControl fullWidth>
            <InputLabel>Metric</InputLabel>
            <Select
              value={metric}
              label="Metric"
              onChange={(e) => setMetric(e.target.value)}
            >
              <MenuItem value="activity">Activity Level</MenuItem>
              <MenuItem value="productivity">Productivity</MenuItem>
              <MenuItem value="focus">Focus Time</MenuItem>
              <MenuItem value="breaks">Break Frequency</MenuItem>
              <MenuItem value="stress">Stress Levels</MenuItem>
              <MenuItem value="posture">Posture Quality</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={3}>
          <FormControl fullWidth>
            <InputLabel>Chart Type</InputLabel>
            <Select
              value={chartType}
              label="Chart Type"
              onChange={(e) => setChartType(e.target.value)}
            >
              <MenuItem value="line">Line Chart</MenuItem>
              <MenuItem value="bar">Bar Chart</MenuItem>
              <MenuItem value="pie">Pie Chart</MenuItem>
              <MenuItem value="scatter">Scatter Plot</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} sm={3}>
          <ToggleButtonGroup
            value={comparisonMode}
            exclusive
            onChange={(e, newValue) => setComparisonMode(newValue)}
            aria-label="comparison mode"
          >
            <ToggleButton value={true} aria-label="comparison on">
              Comparison Mode
            </ToggleButton>
          </ToggleButtonGroup>
        </Grid>
      </Grid>

      <Box sx={{ height: 400 }}>
        {loading ? (
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            height="100%"
          >
            <Typography>Loading...</Typography>
          </Box>
        ) : (
          renderChart()
        )}
      </Box>
    </Paper>
  );
};

export default AdvancedTrendAnalysis; 