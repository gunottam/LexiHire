// src/App.jsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Signup from "./components/auth/Signup.jsx";
import Login from "./components/auth/Login.jsx";
import ResumeUpload from "./components/dashboard/ResumeUpload.jsx";
// import ParsedResults from './components/dashboard/ParsedResults.jsx';
import DashboardLayout from "./components/layout/DashboardLayout.jsx";
import PrivateRoute from "./components/auth/PrivateRoute";

const App = () => {
  return (
    <Routes>
      {/* Public Auth Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      {/* Protected Dashboard Route (Upload only) */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <DashboardLayout />
          </PrivateRoute>
        }
      >
        <Route path="upload" element={<ResumeUpload />} />
      </Route>

      {/* Default and fallback redirect to dashboard */}
      <Route path="/" element={<Navigate to="/dashboard/upload" replace />} />
      <Route path="*" element={<Navigate to="/dashboard/upload" replace />} />
    </Routes>
  );
};

export default App;
