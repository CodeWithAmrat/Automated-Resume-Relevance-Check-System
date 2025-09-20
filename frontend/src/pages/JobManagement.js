import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  IconButton,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const JobManagement = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [open, setOpen] = useState(false);
  const [editingJob, setEditingJob] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    company: 'Innomatics Research Labs',
    location: '',
    description: '',
    requirements: '',
    skills_required: [],
    experience_min: 0,
    experience_max: 10,
    department: '',
    employment_type: 'Full-time',
  });

  const locations = ['Hyderabad', 'Bangalore', 'Pune', 'Delhi NCR'];
  const departments = ['Engineering', 'Data Science', 'Product', 'Marketing', 'Sales', 'HR'];
  const employmentTypes = ['Full-time', 'Part-time', 'Contract', 'Internship'];

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    // Simulate API call - replace with actual API
    const mockJobs = [
      {
        id: 1,
        title: 'Senior Software Engineer',
        company: 'Innomatics Research Labs',
        location: 'Hyderabad',
        description: 'We are looking for a senior software engineer...',
        requirements: 'Bachelor\'s degree in Computer Science, 5+ years experience...',
        skills_required: ['Python', 'React', 'AWS', 'Docker'],
        experience_min: 5,
        experience_max: 10,
        department: 'Engineering',
        employment_type: 'Full-time',
        created_at: '2024-01-15T10:30:00Z',
        is_active: true,
      },
      {
        id: 2,
        title: 'Data Scientist',
        company: 'Innomatics Research Labs',
        location: 'Bangalore',
        description: 'Join our data science team to build ML models...',
        requirements: 'Master\'s in Data Science or related field, 3+ years experience...',
        skills_required: ['Python', 'Machine Learning', 'TensorFlow', 'SQL'],
        experience_min: 3,
        experience_max: 8,
        department: 'Data Science',
        employment_type: 'Full-time',
        created_at: '2024-01-10T14:20:00Z',
        is_active: true,
      },
    ];
    setJobs(mockJobs);
  };

  const handleOpen = (job = null) => {
    if (job) {
      setEditingJob(job);
      setFormData(job);
    } else {
      setEditingJob(null);
      setFormData({
        title: '',
        company: 'Innomatics Research Labs',
        location: '',
        description: '',
        requirements: '',
        skills_required: [],
        experience_min: 0,
        experience_max: 10,
        department: '',
        employment_type: 'Full-time',
      });
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingJob(null);
  };

  const handleChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
  };

  const handleSkillsChange = (event) => {
    const skills = event.target.value.split(',').map(skill => skill.trim()).filter(skill => skill);
    setFormData({
      ...formData,
      skills_required: skills,
    });
  };

  const handleSubmit = async () => {
    try {
      if (editingJob) {
        // Update job - API call
        console.log('Updating job:', formData);
      } else {
        // Create job - API call
        console.log('Creating job:', formData);
      }
      handleClose();
      fetchJobs(); // Refresh the list
    } catch (error) {
      console.error('Error saving job:', error);
    }
  };

  const handleDelete = async (jobId) => {
    if (window.confirm('Are you sure you want to delete this job?')) {
      try {
        // Delete job - API call
        console.log('Deleting job:', jobId);
        fetchJobs(); // Refresh the list
      } catch (error) {
        console.error('Error deleting job:', error);
      }
    }
  };

  const handleViewResults = (jobId) => {
    navigate(`/results/${jobId}`);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Job Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpen()}
        >
          Create New Job
        </Button>
      </Box>

      <Grid container spacing={3}>
        {jobs.map((job) => (
          <Grid item xs={12} md={6} lg={4} key={job.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {job.title}
                </Typography>
                <Typography color="textSecondary" gutterBottom>
                  {job.location} • {job.department}
                </Typography>
                <Typography variant="body2" paragraph>
                  {job.description.substring(0, 150)}...
                </Typography>
                <Box mb={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Required Skills:
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={0.5}>
                    {job.skills_required.slice(0, 4).map((skill) => (
                      <Chip key={skill} label={skill} size="small" />
                    ))}
                    {job.skills_required.length > 4 && (
                      <Chip label={`+${job.skills_required.length - 4} more`} size="small" variant="outlined" />
                    )}
                  </Box>
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Experience: {job.experience_min}-{job.experience_max} years
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Type: {job.employment_type}
                </Typography>
              </CardContent>
              <CardActions>
                <IconButton onClick={() => handleViewResults(job.id)} color="primary">
                  <ViewIcon />
                </IconButton>
                <IconButton onClick={() => handleOpen(job)} color="primary">
                  <EditIcon />
                </IconButton>
                <IconButton onClick={() => handleDelete(job.id)} color="error">
                  <DeleteIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Job Form Dialog */}
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingJob ? 'Edit Job' : 'Create New Job'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Job Title"
                value={formData.title}
                onChange={handleChange('title')}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Company"
                value={formData.company}
                onChange={handleChange('company')}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Location</InputLabel>
                <Select
                  value={formData.location}
                  onChange={handleChange('location')}
                  label="Location"
                >
                  {locations.map((location) => (
                    <MenuItem key={location} value={location}>
                      {location}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Department</InputLabel>
                <Select
                  value={formData.department}
                  onChange={handleChange('department')}
                  label="Department"
                >
                  {departments.map((dept) => (
                    <MenuItem key={dept} value={dept}>
                      {dept}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Job Description"
                multiline
                rows={4}
                value={formData.description}
                onChange={handleChange('description')}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Requirements"
                multiline
                rows={4}
                value={formData.requirements}
                onChange={handleChange('requirements')}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Required Skills (comma-separated)"
                value={formData.skills_required.join(', ')}
                onChange={handleSkillsChange}
                placeholder="Python, React, AWS, Docker"
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Min Experience (years)"
                type="number"
                value={formData.experience_min}
                onChange={handleChange('experience_min')}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Max Experience (years)"
                type="number"
                value={formData.experience_max}
                onChange={handleChange('experience_max')}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Employment Type</InputLabel>
                <Select
                  value={formData.employment_type}
                  onChange={handleChange('employment_type')}
                  label="Employment Type"
                >
                  {employmentTypes.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingJob ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default JobManagement;
