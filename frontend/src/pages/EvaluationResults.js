import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  CircularProgress,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import {
  Download as DownloadIcon,
  Visibility as ViewIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';

const EvaluationResults = () => {
  const { jobId } = useParams();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [filters, setFilters] = useState({
    fitLevel: 'all',
    minScore: '',
    maxScore: '',
  });
  const [jobDetails, setJobDetails] = useState(null);

  useEffect(() => {
    fetchResults();
    fetchJobDetails();
  }, [jobId, filters]);

  const fetchResults = async () => {
    setLoading(true);
    try {
      // Simulate API call - replace with actual API
      const mockResults = [
        {
          id: 1,
          resume_id: 101,
          candidate_name: 'John Smith',
          relevance_score: 87.5,
          skills_match_score: 85.0,
          experience_match_score: 90.0,
          education_match_score: 85.0,
          overall_fit: 'High',
          matched_skills: ['Python', 'React', 'AWS', 'Docker'],
          missing_skills: ['Kubernetes', 'GraphQL'],
          recommendations: 'Excellent candidate with strong technical skills...',
          evaluation_date: '2024-01-15T10:30:00Z',
        },
        {
          id: 2,
          resume_id: 102,
          candidate_name: 'Sarah Johnson',
          relevance_score: 72.3,
          skills_match_score: 70.0,
          experience_match_score: 75.0,
          education_match_score: 72.0,
          overall_fit: 'Medium',
          matched_skills: ['Python', 'SQL', 'Machine Learning'],
          missing_skills: ['React', 'AWS', 'Docker'],
          recommendations: 'Good candidate with potential for growth...',
          evaluation_date: '2024-01-15T10:35:00Z',
        },
        {
          id: 3,
          resume_id: 103,
          candidate_name: 'Mike Chen',
          relevance_score: 45.8,
          skills_match_score: 40.0,
          experience_match_score: 50.0,
          education_match_score: 47.0,
          overall_fit: 'Low',
          matched_skills: ['Java', 'SQL'],
          missing_skills: ['Python', 'React', 'AWS', 'Docker', 'Machine Learning'],
          recommendations: 'Candidate needs significant skill development...',
          evaluation_date: '2024-01-15T10:40:00Z',
        },
      ];

      // Apply filters
      let filteredResults = mockResults;
      if (filters.fitLevel !== 'all') {
        filteredResults = filteredResults.filter(r => r.overall_fit === filters.fitLevel);
      }
      if (filters.minScore) {
        filteredResults = filteredResults.filter(r => r.relevance_score >= parseFloat(filters.minScore));
      }
      if (filters.maxScore) {
        filteredResults = filteredResults.filter(r => r.relevance_score <= parseFloat(filters.maxScore));
      }

      setResults(filteredResults);
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchJobDetails = async () => {
    // Simulate API call
    const mockJob = {
      id: jobId,
      title: 'Senior Software Engineer',
      company: 'Innomatics Research Labs',
      location: 'Hyderabad',
      description: 'We are looking for a senior software engineer...',
    };
    setJobDetails(mockJob);
  };

  const handleViewDetails = (candidate) => {
    setSelectedCandidate(candidate);
    setDetailsOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
    setSelectedCandidate(null);
  };

  const handleFilterChange = (field) => (event) => {
    setFilters({
      ...filters,
      [field]: event.target.value,
    });
  };

  const exportResults = () => {
    // Implement CSV export
    const csvContent = [
      ['Candidate Name', 'Relevance Score', 'Skills Match', 'Experience Match', 'Education Match', 'Overall Fit'],
      ...results.map(r => [
        r.candidate_name,
        r.relevance_score,
        r.skills_match_score,
        r.experience_match_score,
        r.education_match_score,
        r.overall_fit,
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evaluation_results_job_${jobId}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getFitColor = (fit) => {
    switch (fit) {
      case 'High': return 'success';
      case 'Medium': return 'warning';
      case 'Low': return 'error';
      default: return 'default';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 75) return 'success.main';
    if (score >= 50) return 'warning.main';
    return 'error.main';
  };

  const columns = [
    { field: 'candidate_name', headerName: 'Candidate Name', width: 200 },
    {
      field: 'relevance_score',
      headerName: 'Relevance Score',
      width: 150,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          <Typography color={getScoreColor(params.value)}>
            {params.value.toFixed(1)}%
          </Typography>
        </Box>
      ),
    },
    {
      field: 'overall_fit',
      headerName: 'Fit Level',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={getFitColor(params.value)}
          size="small"
        />
      ),
    },
    { field: 'skills_match_score', headerName: 'Skills Match', width: 130 },
    { field: 'experience_match_score', headerName: 'Experience Match', width: 150 },
    { field: 'education_match_score', headerName: 'Education Match', width: 150 },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      renderCell: (params) => (
        <Button
          startIcon={<ViewIcon />}
          onClick={() => handleViewDetails(params.row)}
          size="small"
        >
          View
        </Button>
      ),
    },
  ];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4">Evaluation Results</Typography>
          {jobDetails && (
            <Typography color="textSecondary">
              {jobDetails.title} - {jobDetails.location}
            </Typography>
          )}
        </Box>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={exportResults}
        >
          Export Results
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Candidates
              </Typography>
              <Typography variant="h4">
                {results.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                High Fit
              </Typography>
              <Typography variant="h4" color="success.main">
                {results.filter(r => r.overall_fit === 'High').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Medium Fit
              </Typography>
              <Typography variant="h4" color="warning.main">
                {results.filter(r => r.overall_fit === 'Medium').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Average Score
              </Typography>
              <Typography variant="h4">
                {results.length > 0 
                  ? (results.reduce((sum, r) => sum + r.relevance_score, 0) / results.length).toFixed(1)
                  : 0
                }%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          <FilterIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Filters
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Fit Level</InputLabel>
              <Select
                value={filters.fitLevel}
                onChange={handleFilterChange('fitLevel')}
                label="Fit Level"
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="Low">Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              size="small"
              label="Min Score"
              type="number"
              value={filters.minScore}
              onChange={handleFilterChange('minScore')}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              size="small"
              label="Max Score"
              type="number"
              value={filters.maxScore}
              onChange={handleFilterChange('maxScore')}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Results Table */}
      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={results}
          columns={columns}
          pageSize={25}
          rowsPerPageOptions={[25, 50, 100]}
          checkboxSelection
          disableSelectionOnClick
        />
      </Paper>

      {/* Candidate Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        {selectedCandidate && (
          <>
            <DialogTitle>
              {selectedCandidate.candidate_name} - Detailed Evaluation
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Scores
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText
                        primary="Overall Relevance"
                        secondary={`${selectedCandidate.relevance_score.toFixed(1)}%`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Skills Match"
                        secondary={`${selectedCandidate.skills_match_score.toFixed(1)}%`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Experience Match"
                        secondary={`${selectedCandidate.experience_match_score.toFixed(1)}%`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Education Match"
                        secondary={`${selectedCandidate.education_match_score.toFixed(1)}%`}
                      />
                    </ListItem>
                  </List>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Skills Analysis
                  </Typography>
                  <Typography variant="subtitle2" gutterBottom>
                    Matched Skills:
                  </Typography>
                  <Box mb={2}>
                    {selectedCandidate.matched_skills.map((skill) => (
                      <Chip
                        key={skill}
                        label={skill}
                        color="success"
                        size="small"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Missing Skills:
                  </Typography>
                  <Box>
                    {selectedCandidate.missing_skills.map((skill) => (
                      <Chip
                        key={skill}
                        label={skill}
                        color="error"
                        variant="outlined"
                        size="small"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Recommendations
                  </Typography>
                  <Typography variant="body2">
                    {selectedCandidate.recommendations}
                  </Typography>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDetails}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default EvaluationResults;
