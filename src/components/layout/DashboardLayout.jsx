// src/components/layout/dashboardlayout/DashboardLayout.jsx
import React from "react";
import Navbar from "./Navbar.jsx";
import { Outlet } from "react-router-dom";
import "./DashboardLayout.css";

const DashboardLayout = () => {
  return (
    <div className="dashboard-shell">
      <Navbar />
      <main className="dashboard-main">
        <Outlet />
      </main>
    </div>
  );
};

export default DashboardLayout;
