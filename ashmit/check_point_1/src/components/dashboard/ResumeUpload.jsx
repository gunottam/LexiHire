import React, { useState } from 'react';
import './ResumeUpload.css';

const ResumeUpload = () => {
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [processedData, setProcessedData] = useState(null); // New state for processed data
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
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
    
    if (files.length === 0) {
      setUploadStatus({
        success: false,
        message: "Please select at least one file to upload"
      });
      return;
    }
    
    setIsUploading(true);
    setUploadStatus(null);
    
    // Create form data
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    try {
      // Send the files to your API endpoint
      const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const data = await response.json();
        setUploadStatus({
          success: true,
          message: `Successfully uploaded ${files.length} resume${files.length > 1 ? 's' : ''}!`
        });
        setFiles([]);  // Clear selected files after upload
        
        // Now send the extracted text to the /process route for further processing
        const textToProcess = 'Extracted text from the files'; // You'll likely want to get this from the backend response
        const processResponse = await fetch('http://127.0.0.1:5000/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: textToProcess }), // Sending the text for further processing
        });

        if (processResponse.ok) {
          const processedData = await processResponse.json();
          setProcessedData(processedData.processed_data); // Store the processed data
        } else {
          setUploadStatus({
            success: false,
            message: 'Error processing the text'
          });
        }
        
      } else {
        const error = await response.json();
        setUploadStatus({
          success: false,
          message: error.message || "Upload failed. Please try again."
        });
      }
    } catch (error) {
      setUploadStatus({
        success: false,
        message: "Server error. Please try again later."
      });
    } finally {
      setIsUploading(false);
    }
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
        
        {processedData && (
          <div className="processed-data">
            <h3>Processed Data:</h3>
            <pre>{processedData}</pre>
          </div>
        )}
        
        <form 
          onSubmit={handleSubmit} 
          className="resume-upload-form"
          onDragEnter={handleDrag}
        >
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
            value="Upload"
            className={`upload-button ${isUploading ? 'loading' : ''}`}
            disabled={isUploading}
          >
            {isUploading ? (
              <span className="spinner"></span>
            ) : (
              'Upload Resumes'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResumeUpload;
