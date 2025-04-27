import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Signup from './Signup';
import './AuthPage.css';

const AuthPage = () => {
  const [currentForm, setCurrentForm] = useState('login');
  return (
    <div className="auth-page-container">
      <div className="auth-page-wrapper">
        <div className="auth-sidebar">
          <div className="brand-logo">
            <span className="logo-icon">LH</span>
            <h2>LexiHire</h2>
          </div>
          
          <div className="auth-info">
            <h3>{currentForm === 'login' ? 'Welcome Back!' : 'Join Today'}</h3>
            <p>
              {currentForm === 'login' 
                ? 'Join us to access your account and continue your journey with us.'
                : 'Create an account to explore all the features and benefits of our platform.'}
            </p>
            
            <div className="auth-features">
              <div className="feature">
                <div className="feature-icon">🚀</div>
                <div className="feature-text">
                  <h4>Streamline Your Hiring</h4>
                  <p>Quick access with secure authentication</p>
                </div>
              </div>
              
              <div className="feature">
                <div className="feature-icon">🎯</div>
                <div className="feature-text">
                  <h4>Precision Matching</h4>
                  <p>Score candidates with smart ranking</p>
                </div>
              </div>
              
              <div className="feature">
                <div className="feature-icon">🧠</div>
                <div className="feature-text">
                  <h4>Professional Tools</h4>
                  <p>Automate resume screening with AI</p>
                </div>
              </div>

              <div className="feature">
                <div className="feature-icon">🌟</div>
                <div className="feature-text">
                  <h4>Inclusive and Bias-Free Hiring</h4>
                  <p>Promote fair and objective recruitment</p>
                </div>
              </div>
            </div>
          </div>
          
          {/* <div className="auth-toggle">
            <p>
              {currentForm === 'login' 
                ? "Don't have an account?" 
                : "Already have an account?"}
            </p>
            <button 
              onClick={() => setCurrentForm(currentForm === 'login' ? 'signup' : 'login')}
              className="toggle-button"
            >
              {currentForm === 'login' ? 'Sign Up' : 'Sign In'}
            </button>
          </div> */}
        </div>
        
        <div className="auth-content">
          <Router>
            <Routes>
              <Route 
                path="/login" 
                element={<Login />} 
                onEnter={() => setCurrentForm('login')} 
              />
              <Route 
                path="/signup" 
                element={<Signup />} 
                onEnter={() => setCurrentForm('signup')} 
              />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </Router>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;