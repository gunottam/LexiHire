import React, { useState } from "react";
import { apiUrl } from "../../api.js";
import ResumeUpload from "./ResumeUpload";
import "./ResumeParser.css";

const ResumeParser = () => {
  const [activeTab, setActiveTab] = useState("upload");
  const [parsedResumes, setParsedResumes] = useState([]);

  const fetchParsedResumes = async () => {
    try {
      const response = await fetch(apiUrl("/resumes"));
      if (!response.ok) throw new Error("Failed to fetch parsed resumes.");
      const data = await response.json();
      setParsedResumes(data); // Backend should return a list of parsed resumes
      setActiveTab("results");
    } catch (error) {
      console.error("Error fetching resumes:", error);
      setParsedResumes([]); // Optional fallback
    }
  };

  return (
    <div className="resume-parser-container">
      <div className="resume-parser-header">
        <h1>Resume Parser</h1>
        <p>Upload and analyze resumes automatically</p>
      </div>

      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === "upload" ? "active" : ""}`}
          onClick={() => setActiveTab("upload")}
        >
          Upload Resumes
        </button>
        <button
          className={`tab-button ${activeTab === "results" ? "active" : ""}`}
          onClick={fetchParsedResumes}
        >
          Parsed Results
        </button>
      </div>

      <div className="tab-content">
        {activeTab === "upload" ? (
          <ResumeUpload />
        ) : (
          <div className="parsed-results">
            <div className="results-header">
              <h3>Parsed Resumes</h3>
              <div className="results-actions">
                <button className="export-button">Export to CSV</button>
                <div className="search-container">
                  <input type="text" placeholder="Search resumes..." />
                  <button className="search-button">Search</button>
                </div>
              </div>
            </div>

            {parsedResumes.length > 0 ? (
              <div className="results-table-container">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Phone</th>
                      <th>Skills</th>
                      <th>Upload Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parsedResumes.map((resume) => (
                      <tr key={resume.id} className="resume-row">
                        <td>
                          <div className="candidate-info">
                            <div className="candidate-avatar">
                              {resume.name?.charAt(0) || "?"}
                            </div>
                            <div className="candidate-name">
                              {resume.name}
                              <span className="file-name">
                                {resume.fileName}
                              </span>
                            </div>
                          </div>
                        </td>
                        <td>{resume.email}</td>
                        <td>{resume.phone}</td>
                        <td>
                          <div className="skills-list">
                            {resume.skills?.map((skill, index) => (
                              <span key={index} className="skill-tag">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td>{resume.uploadDate}</td>
                        <td>
                          <div className="action-buttons">
                            <button className="view-button">View</button>
                            <button className="download-button">
                              Download
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="no-results">
                <div className="no-results-icon">📄</div>
                <h3>No Resumes Found</h3>
                <p>Upload resumes to see parsed results here</p>
                <button
                  className="upload-now-button"
                  onClick={() => setActiveTab("upload")}
                >
                  Upload Now
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeParser;
