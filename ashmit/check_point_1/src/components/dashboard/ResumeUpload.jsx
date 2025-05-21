import React, { useState } from 'react';
import './ResumeUpload.css';

const ResumeUpload = () => {
  const [files, setFiles] = useState([]);
  const [jobRole, setJobRole] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [processedData, setProcessedData] = useState(null);
  const [rankedResumes, setRankedResumes] = useState([]);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!jobRole.trim()) {
      setUploadStatus({ success: false, message: 'Please enter a job role.' });
      return;
    }

    if (files.length === 0) {
      setUploadStatus({ success: false, message: 'Please select at least one file to upload' });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('jobRole', jobRole);

    try {
      const uploadRes = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
      });

      if (uploadRes.ok) {
        const data = await uploadRes.json();
        setUploadStatus({
          success: true,
          message: `Successfully uploaded ${files.length} resume${files.length > 1 ? 's' : ''}!`
        });
        setFiles([]);
        setJobRole('');

        const processRes = await fetch('http://127.0.0.1:5000/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });

        if (processRes.ok) {
          const processData = await processRes.json();
          setProcessedData(processData.processed_files);

          const rankRes = await fetch('http://127.0.0.1:5000/rankings');
          const rankData = await rankRes.json();
          if (rankData.status === 'success') {
            setRankedResumes(rankData.rankings);
          }
        } else {
          setUploadStatus({ success: false, message: 'Error processing the resumes' });
        }
      } else {
        const error = await uploadRes.json();
        setUploadStatus({
          success: false,
          message: error.message || 'Upload failed. Please try again.'
        });
      }
    } catch (error) {
      setUploadStatus({ success: false, message: 'Server error. Please try again later.' });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = () => {
    window.open('http://127.0.0.1:5000/download-ranked-resumes', '_blank');
  };

  return (
    <div className="resume-upload-container">
      <div className="resume-upload-card">
        <div className="resume-upload-header">
          <h2>Upload Resumes</h2>
          <p>Select or drag and drop resume files for parsing</p>
        </div>

        {uploadStatus && (
          <div className={`upload-status ${uploadStatus.success ? 'success' : 'error'}`}>
            {uploadStatus.message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="resume-upload-form" onDragEnter={handleDrag}>
          <div className="job-role-input">
            <label htmlFor="jobRole">Enter Job Role:</label>
            <input
              type="text"
              id="jobRole"
              value={jobRole}
              onChange={(e) => setJobRole(e.target.value)}
              placeholder="e.g., Frontend Developer"
              required
            />
          </div>

          <div
            className={`file-drop-area ${dragActive ? 'active' : ''} ${files.length > 0 ? 'has-files' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="file-input-container">
              <input
                type="file"
                id="resumeFiles"
                onChange={handleFileChange}
                multiple
                className="file-input"
                name="files"
              />
              <label htmlFor="resumeFiles" className="file-label">
                <div className="upload-icon">📄</div>
                <span className="upload-text">
                  {files.length > 0
                    ? `${files.length} file${files.length > 1 ? 's' : ''} selected`
                    : 'Choose files or drag them here'}
                </span>
              </label>
            </div>

            {files.length > 0 && (
              <div className="file-list">
                <h4>Selected Files:</h4>
                <ul>
                  {files.map((file, index) => (
                    <li key={index} className="file-item">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <button
            type="submit"
            className={`upload-button ${isUploading ? 'loading' : ''}`}
            disabled={isUploading}
          >
            {isUploading ? <span className="spinner"></span> : 'Upload Resumes'}
          </button>
        </form>

        {/* Ranked Output Section */}
        {rankedResumes.length > 0 && (
          <div className="parsed-results-container">
            <h3>Ranked Resumes</h3>
            <ol className="ranked-list">
              {rankedResumes.map((resume, index) => (
                <li key={index}>
                  {resume.filename} — Score: {resume.normalized_score.toFixed(4)}
                </li>
              ))}
            </ol>
            <button onClick={handleDownload} className="download-button">
              Download Ranked Resumes (ZIP)
            </button>
          </div>
        )}

      </div>
    </div>
  );
};

export default ResumeUpload;
