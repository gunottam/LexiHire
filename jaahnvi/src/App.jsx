// filepath: /Users/jaahnvisharma/Lexihire/jaahnvi/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Signup from './components/auth/Signup';
import Login from './components/auth/Login';
import ResumeParser from './components/dashboard/ResumeParser';
import ResumeUpload from './components/dashboard/ResumeUpload';
import AuthPage from './components/auth/authpage';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/signup" element={<Signup/>} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ResumeParser />} />
        <Route path="/upload" element={<ResumeUpload />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
};

export default App;