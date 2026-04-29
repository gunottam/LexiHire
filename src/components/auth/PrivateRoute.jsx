// src/components/auth/PrivateRoute.jsx
import React from "react";
// Auth bypass enabled: always allow access while login is disabled
const PrivateRoute = ({ children }) => {
  return children;
};

export default PrivateRoute;
