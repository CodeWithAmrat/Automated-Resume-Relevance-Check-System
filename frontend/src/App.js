import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import JobManagement from './pages/JobManagement';
import ResumeUpload from './pages/ResumeUpload';
import EvaluationResults from './pages/EvaluationResults';
import BatchProcessing from './pages/BatchProcessing';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<JobManagement />} />
          <Route path="/upload" element={<ResumeUpload />} />
          <Route path="/results/:jobId" element={<EvaluationResults />} />
          <Route path="/batch" element={<BatchProcessing />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default App;
