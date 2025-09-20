import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Alert,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  CheckCircle as CompleteIcon,
  Schedule as PendingIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const BatchProcessing = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [resumes, setResumes] = useState([]);
  const [batches, setBatches] = useState([]);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedResumes, setSelectedResumes] = useState([]);
  const [batchName, setBatchName] = useState('');
  const [loading, setLoading] = useState(false);

  const steps = ['Select Job', 'Select Resumes', 'Start Processing', 'View Results'];

  useEffect(() => {
    fetchJobs();
    fetchResumes();
    fetchBatches();
  }, []);

  const fetchJobs = async () => {
    // Simulate API call
    const mockJobs = [
      { id: 1, title: 'Senior Software Engineer', location: 'Hyderabad', is_active: true },
      { id: 2, title: 'Data Scientist', location: 'Bangalore', is_active: true },
      { id: 3, title: 'Full Stack Developer', location: 'Pune', is_active: true },
    ];
    setJobs(mockJobs);
  };

  const fetchResumes = async () => {
    // Simulate API call
    const mockResumes = [
      { id: 101, candidate_name: 'John Smith', file_name: 'john_smith_resume.pdf', is_parsed: true },
      { id: 102, candidate_name: 'Sarah Johnson', file_name: 'sarah_johnson_resume.pdf', is_parsed: true },
      { id: 103, candidate_name: 'Mike Chen', file_name: 'mike_chen_resume.docx', is_parsed: true },
      { id: 104, candidate_name: 'Emily Davis', file_name: 'emily_davis_resume.pdf', is_parsed: false },
      { id: 105, candidate_name: 'Alex Wilson', file_name: 'alex_wilson_resume.doc', is_parsed: true },
    ];
    setResumes(mockResumes);
  };

  const fetchBatches = async () => {
    // Simulate API call
    const mockBatches = [
      {
        id: 1,
        batch_name: 'Senior Dev Batch 1',
        job_title: 'Senior Software Engineer',
        status: 'completed',
        total_resumes: 25,
        processed_resumes: 25,
        high_fit_count: 8,
        medium_fit_count: 12,
        low_fit_count: 5,
        average_score: 67.3,
        started_at: '2024-01-15T10:00:00Z',
        completed_at: '2024-01-15T10:15:00Z',
      },
      {
        id: 2,
        batch_name: 'Data Science Batch 1',
        job_title: 'Data Scientist',
        status: 'processing',
        total_resumes: 30,
        processed_resumes: 18,
        high_fit_count: 5,
        medium_fit_count: 8,
        low_fit_count: 5,
        average_score: 72.1,
        started_at: '2024-01-15T11:00:00Z',
        completed_at: null,
      },
      {
        id: 3,
        batch_name: 'Full Stack Batch 1',
        job_title: 'Full Stack Developer',
        status: 'pending',
        total_resumes: 20,
        processed_resumes: 0,
        high_fit_count: 0,
        medium_fit_count: 0,
        low_fit_count: 0,
        average_score: 0,
        started_at: null,
        completed_at: null,
      },
    ];
    setBatches(mockBatches);
  };

  const handleCreateBatch = () => {
    setCreateDialogOpen(true);
    setBatchName(`Batch_${new Date().toISOString().slice(0, 10)}`);
  };

  const handleCloseDialog = () => {
    setCreateDialogOpen(false);
    setSelectedJob('');
    setSelectedResumes([]);
    setBatchName('');
  };

  const handleResumeSelection = (resumeId) => {
    setSelectedResumes(prev => {
      if (prev.includes(resumeId)) {
        return prev.filter(id => id !== resumeId);
      } else {
        return [...prev, resumeId];
      }
    });
  };

  const handleStartBatch = async () => {
    if (!selectedJob || selectedResumes.length === 0) {
      return;
    }

    setLoading(true);
    try {
      // Simulate API call
      const batchData = {
        job_id: selectedJob,
        resume_ids: selectedResumes,
        batch_name: batchName,
      };

      console.log('Starting batch processing:', batchData);
      
      // Simulate delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Refresh batches
      await fetchBatches();
      
      handleCloseDialog();
    } catch (error) {
      console.error('Error starting batch:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CompleteIcon color="success" />;
      case 'processing':
        return <PendingIcon color="info" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      default:
        return <PendingIcon color="disabled" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'info';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const calculateProgress = (batch) => {
    if (batch.total_resumes === 0) return 0;
    return (batch.processed_resumes / batch.total_resumes) * 100;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Batch Processing</Typography>
        <Box>
          <Button
            startIcon={<RefreshIcon />}
            onClick={fetchBatches}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<StartIcon />}
            onClick={handleCreateBatch}
          >
            Create New Batch
          </Button>
        </Box>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        Batch processing allows you to evaluate multiple resumes against a job description simultaneously. 
        This is ideal for handling large volumes of applications efficiently.
      </Alert>

      {/* Processing Steps */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Processing Workflow
        </Typography>
        <Stepper activeStep={-1} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* Active Batches */}
      <Grid container spacing={3}>
        {batches.map((batch) => (
          <Grid item xs={12} md={6} lg={4} key={batch.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" gutterBottom>
                    {batch.batch_name}
                  </Typography>
                  <Chip
                    label={batch.status}
                    color={getStatusColor(batch.status)}
                    size="small"
                  />
                </Box>
                
                <Typography color="textSecondary" gutterBottom>
                  {batch.job_title}
                </Typography>

                {batch.status === 'processing' && (
                  <Box mb={2}>
                    <Typography variant="body2" gutterBottom>
                      Progress: {batch.processed_resumes}/{batch.total_resumes}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={calculateProgress(batch)}
                    />
                  </Box>
                )}

                <Grid container spacing={2} sx={{ mb: 2 }}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Total Resumes
                    </Typography>
                    <Typography variant="h6">
                      {batch.total_resumes}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="textSecondary">
                      Avg Score
                    </Typography>
                    <Typography variant="h6">
                      {batch.average_score.toFixed(1)}%
                    </Typography>
                  </Grid>
                </Grid>

                {batch.status === 'completed' && (
                  <Box mb={2}>
                    <Typography variant="body2" gutterBottom>
                      Results Distribution:
                    </Typography>
                    <Box display="flex" gap={1}>
                      <Chip
                        label={`High: ${batch.high_fit_count}`}
                        color="success"
                        size="small"
                      />
                      <Chip
                        label={`Medium: ${batch.medium_fit_count}`}
                        color="warning"
                        size="small"
                      />
                      <Chip
                        label={`Low: ${batch.low_fit_count}`}
                        color="error"
                        size="small"
                      />
                    </Box>
                  </Box>
                )}

                <Typography variant="caption" display="block" gutterBottom>
                  Started: {formatDate(batch.started_at)}
                </Typography>
                {batch.completed_at && (
                  <Typography variant="caption" display="block" gutterBottom>
                    Completed: {formatDate(batch.completed_at)}
                  </Typography>
                )}

                <Box mt={2}>
                  {batch.status === 'completed' && (
                    <Button
                      size="small"
                      onClick={() => navigate(`/results/${batch.job_id || 1}`)}
                    >
                      View Results
                    </Button>
                  )}
                  {batch.status === 'processing' && (
                    <Button
                      size="small"
                      startIcon={<StopIcon />}
                      color="error"
                    >
                      Stop
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create Batch Dialog */}
      <Dialog open={createDialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>Create New Batch Processing</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Batch Name"
                value={batchName}
                onChange={(e) => setBatchName(e.target.value)}
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Select Job</InputLabel>
                <Select
                  value={selectedJob}
                  onChange={(e) => setSelectedJob(e.target.value)}
                  label="Select Job"
                >
                  {jobs.map((job) => (
                    <MenuItem key={job.id} value={job.id}>
                      {job.title} - {job.location}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Select Resumes ({selectedResumes.length} selected)
              </Typography>
              <Paper sx={{ maxHeight: 300, overflow: 'auto' }}>
                <List>
                  {resumes.map((resume) => (
                    <ListItem
                      key={resume.id}
                      button
                      onClick={() => handleResumeSelection(resume.id)}
                      disabled={!resume.is_parsed}
                    >
                      <ListItemIcon>
                        <input
                          type="checkbox"
                          checked={selectedResumes.includes(resume.id)}
                          onChange={() => handleResumeSelection(resume.id)}
                          disabled={!resume.is_parsed}
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={resume.candidate_name}
                        secondary={
                          <Box>
                            <Typography variant="caption" display="block">
                              {resume.file_name}
                            </Typography>
                            {!resume.is_parsed && (
                              <Chip
                                label="Not Parsed"
                                color="error"
                                size="small"
                              />
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleStartBatch}
            variant="contained"
            disabled={!selectedJob || selectedResumes.length === 0 || loading}
          >
            {loading ? 'Starting...' : 'Start Processing'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BatchProcessing;
