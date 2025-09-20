import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  People,
  Work,
  Assessment,
  CheckCircle,
  Schedule,
  Error,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalJobs: 0,
    totalResumes: 0,
    totalEvaluations: 0,
    averageScore: 0,
    highFitCount: 0,
    mediumFitCount: 0,
    lowFitCount: 0,
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [locationStats, setLocationStats] = useState([]);

  useEffect(() => {
    // Simulate API calls - replace with actual API calls
    setStats({
      totalJobs: 45,
      totalResumes: 2847,
      totalEvaluations: 1923,
      averageScore: 67.3,
      highFitCount: 423,
      mediumFitCount: 892,
      lowFitCount: 608,
    });

    setRecentActivity([
      { id: 1, type: 'evaluation', message: 'Batch evaluation completed for Senior Developer role', time: '2 minutes ago', status: 'success' },
      { id: 2, type: 'upload', message: '25 new resumes uploaded for Data Scientist position', time: '15 minutes ago', status: 'info' },
      { id: 3, type: 'job', message: 'New job posting created: Full Stack Developer - Bangalore', time: '1 hour ago', status: 'success' },
      { id: 4, type: 'evaluation', message: 'Evaluation failed for 3 resumes due to parsing errors', time: '2 hours ago', status: 'error' },
      { id: 5, type: 'batch', message: 'Started batch processing for ML Engineer role', time: '3 hours ago', status: 'info' },
    ]);

    setLocationStats([
      { name: 'Hyderabad', jobs: 15, resumes: 892, evaluations: 634 },
      { name: 'Bangalore', jobs: 12, resumes: 756, evaluations: 523 },
      { name: 'Pune', jobs: 10, resumes: 643, evaluations: 445 },
      { name: 'Delhi NCR', jobs: 8, resumes: 556, evaluations: 321 },
    ]);
  }, []);

  const fitDistributionData = [
    { name: 'High Fit', value: stats.highFitCount, color: '#4caf50' },
    { name: 'Medium Fit', value: stats.mediumFitCount, color: '#ff9800' },
    { name: 'Low Fit', value: stats.lowFitCount, color: '#f44336' },
  ];

  const getActivityIcon = (type, status) => {
    if (status === 'error') return <Error color="error" />;
    if (status === 'success') return <CheckCircle color="success" />;
    return <Schedule color="info" />;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'success';
      case 'error': return 'error';
      default: return 'info';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Work color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Jobs
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalJobs}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <People color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Resumes
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalResumes.toLocaleString()}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Assessment color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Evaluations
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalEvaluations.toLocaleString()}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg. Score
                  </Typography>
                  <Typography variant="h4">
                    {stats.averageScore}%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Fit Distribution Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Candidate Fit Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={fitDistributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {fitDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Location Performance */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Performance by Location
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={locationStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="jobs" fill="#1976d2" name="Jobs" />
                <Bar dataKey="evaluations" fill="#dc004e" name="Evaluations" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <List>
              {recentActivity.map((activity) => (
                <ListItem key={activity.id} divider>
                  <ListItemIcon>
                    {getActivityIcon(activity.type, activity.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={activity.message}
                    secondary={activity.time}
                  />
                  <Chip
                    label={activity.status}
                    color={getStatusColor(activity.status)}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
