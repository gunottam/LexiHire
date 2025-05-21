// src/components/layout/navbar/Navbar.jsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <NavLink to="/upload" className="tab" activeclassname="active">Upload Resumes</NavLink>
      {/* <NavLink to="/rankings" className="tab" activeclassname="active">Parsed Results</NavLink> */}
    </nav>
  );
};

export default Navbar;
