// src/components/layout/dashboardlayout/DashboardLayout.jsx
import React from 'react';
import Navbar from './Navbar.jsx';
import { Outlet } from 'react-router-dom';

const DashboardLayout = () => {
  return (
    <>
      <Navbar />
      <main style={{ padding: '20px' }}>
        <Outlet />
      </main>
    </>
  );
};

export default DashboardLayout;
