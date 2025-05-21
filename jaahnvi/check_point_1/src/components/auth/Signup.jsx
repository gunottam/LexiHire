import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getAuth, createUserWithEmailAndPassword, updateProfile } from 'firebase/auth';
import './signup.css';

const Signup = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState(1); // For multi-stage animation
  const navigate = useNavigate();
  const auth = getAuth();

  const validatePassword = () => {
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    if (password.length < 6) {
      setError('Password should be at least 6 characters');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!validatePassword()) return;
    
    setLoading(true);
    
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      
      // Update user profile with name
      await updateProfile(userCredential.user, {
        displayName: name
      });
      
      // Animate completion before redirecting
      setStage(2);
      
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
      
    } catch (error) {
      setError(error.message);
      setLoading(false);
      console.error("Signup error:", error);
    }
  };

  return (
    <div className="signup-container">
      <div className={`signup-card ${stage === 2 ? 'success' : ''}`}>
        {stage === 1 ? (
          <>
            <div className="signup-header">
              <h1>Create Account</h1>
              <p>Join us today and start your journey</p>
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <form onSubmit={handleSubmit} className="signup-form">
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <div className="input-container">
                  <i className="user-icon">👤</i>
                  <input
                    type="text"
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    placeholder="Enter your full name"
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <div className="input-container">
                  <i className="email-icon">✉️</i>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="Enter your email"
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="password">Password</label>
                <div className="input-container">
                  <i className="password-icon">🔒</i>
                  <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    placeholder="Create a password"
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="confirm-password">Confirm Password</label>
                <div className="input-container">
                  <i className="password-icon">🔒</i>
                  <input
                    type="password"
                    id="confirm-password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    placeholder="Confirm your password"
                  />
                </div>
              </div>
              <button 
                type="submit" 
                className={`signup-button ${loading ? 'loading' : ''}`}
                disabled={loading}
              >
                {loading ? (
                  <span className="spinner"></span>
                ) : (
                  'Create Account'
                )}
              </button>
            </form>
            
            <div className="login-prompt">
              <p>Already have an account? <Link to="/login" className="login-link">Sign In</Link></p>
            </div>
          </>
        ) : (
          <div className="success-message">
            <div className="success-icon">✓</div>
            <h2>Account Created!</h2>
            <p>Redirecting to dashboard...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Signup;