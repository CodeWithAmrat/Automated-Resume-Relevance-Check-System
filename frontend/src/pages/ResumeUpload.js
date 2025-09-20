import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  LinearProgress,
  Chip,
  Button,
  Alert,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  Delete as DeleteIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

const ResumeUpload = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle accepted files
    const newFiles = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      size: file.size,
      status: 'pending', // pending, uploading, success, error
      progress: 0,
      error: null,
    }));

    setFiles(prev => [...prev, ...newFiles]);

    // Handle rejected files
    if (rejectedFiles.length > 0) {
      console.log('Rejected files:', rejectedFiles);
      // You can show error messages for rejected files
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true,
  });

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      files.forEach(fileItem => {
        formData.append('files', fileItem.file);
      });

      // Simulate upload progress
      const uploadPromise = new Promise((resolve) => {
        let progress = 0;
        const interval = setInterval(() => {
          progress += 10;
          setUploadProgress(progress);
          
          if (progress >= 100) {
            clearInterval(interval);
            resolve();
          }
        }, 200);
      });

      await uploadPromise;

      // Update file statuses to success
      setFiles(prev => prev.map(file => ({
        ...file,
        status: 'success',
        progress: 100,
      })));

      // In real implementation, make API call:
      // const response = await fetch('/api/resumes/upload', {
      //   method: 'POST',
      //   body: formData,
      // });

    } catch (error) {
      console.error('Upload error:', error);
      setFiles(prev => prev.map(file => ({
        ...file,
        status: 'error',
        error: 'Upload failed',
      })));
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const clearSuccessfulUploads = () => {
    setFiles(prev => prev.filter(file => file.status !== 'success'));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <FileIcon />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'uploading':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload Resumes
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Upload candidate resumes in PDF, DOC, or DOCX format. Maximum file size: 10MB per file.
      </Alert>

      {/* Dropzone */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          mb: 3,
          textAlign: 'center',
          cursor: 'pointer',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          '&:hover': {
            borderColor: 'primary.main',
            backgroundColor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop the files here...' : 'Drag & drop resume files here'}
        </Typography>
        <Typography color="textSecondary">
          or click to select files
        </Typography>
        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
          Supported formats: PDF, DOC, DOCX
        </Typography>
      </Paper>

      {/* Upload Progress */}
      {uploading && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" gutterBottom>
            Uploading files... {uploadProgress}%
          </Typography>
          <LinearProgress variant="determinate" value={uploadProgress} />
        </Box>
      )}

      {/* File List */}
      {files.length > 0 && (
        <Paper sx={{ mb: 3 }}>
          <Box p={2} display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Selected Files ({files.length})
            </Typography>
            <Box>
              {files.some(f => f.status === 'success') && (
                <Button
                  onClick={clearSuccessfulUploads}
                  size="small"
                  sx={{ mr: 1 }}
                >
                  Clear Uploaded
                </Button>
              )}
              <Button
                variant="contained"
                onClick={uploadFiles}
                disabled={uploading || files.every(f => f.status === 'success')}
              >
                Upload All
              </Button>
            </Box>
          </Box>
          <List>
            {files.map((fileItem) => (
              <ListItem key={fileItem.id} divider>
                <ListItemIcon>
                  {getStatusIcon(fileItem.status)}
                </ListItemIcon>
                <ListItemText
                  primary={fileItem.name}
                  secondary={
                    <Box>
                      <Typography variant="caption" display="block">
                        Size: {formatFileSize(fileItem.size)}
                      </Typography>
                      {fileItem.error && (
                        <Typography variant="caption" color="error">
                          {fileItem.error}
                        </Typography>
                      )}
                    </Box>
                  }
                />
                <Box display="flex" alignItems="center" gap={1}>
                  <Chip
                    label={fileItem.status}
                    color={getStatusColor(fileItem.status)}
                    size="small"
                  />
                  <IconButton
                    onClick={() => removeFile(fileItem.id)}
                    disabled={uploading}
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Instructions */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Instructions
        </Typography>
        <Typography component="div">
          <ol>
            <li>Select or drag & drop resume files (PDF, DOC, DOCX format)</li>
            <li>Review the file list and remove any unwanted files</li>
            <li>Click "Upload All" to upload the resumes to the system</li>
            <li>Once uploaded, resumes will be automatically parsed and ready for evaluation</li>
            <li>Go to "Batch Processing" to evaluate resumes against job descriptions</li>
          </ol>
        </Typography>
      </Paper>
    </Box>
  );
};

export default ResumeUpload;
