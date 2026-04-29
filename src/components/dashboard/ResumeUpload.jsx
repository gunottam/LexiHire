import React, { useState } from "react";
import { apiUrl } from "../../api.js";
import "./ResumeUpload.css";

const WORKFLOW_TEMPLATE = [
  {
    key: "upload",
    label: "Uploading Resumes",
    detail: "Sending selected resume files to backend storage.",
    status: "pending",
    time: null,
  },
  {
    key: "compile",
    label: "Compile & analyze",
    detail:
      "Lexer → parser → semantic → IR → optimization → scoring (runs on the server for each resume).",
    status: "pending",
    time: null,
  },
  {
    key: "rank",
    label: "Ranking",
    detail: "Sort results and refresh the ranked list.",
    status: "pending",
    time: null,
  },
];

const cloneWorkflowTemplate = () =>
  WORKFLOW_TEMPLATE.map((step) => ({ ...step }));

const ScoreBar = ({ score, max, label }) => {
  const pct = max > 0 ? (score / max) * 100 : 0;
  let colorClass = "score-bar-green";
  if (pct < 40) colorClass = "score-bar-red";
  else if (pct < 70) colorClass = "score-bar-yellow";

  return (
    <div className="score-bar-row">
      <span className="score-bar-label">{label}</span>
      <div className="score-bar-track">
        <div
          className={`score-bar-fill ${colorClass}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="score-bar-value">
        {score}/{max}
      </span>
    </div>
  );
};

const DiagnosticsPanel = ({ diagnostics }) => {
  const [expanded, setExpanded] = useState(false);
  if (!diagnostics || diagnostics.length === 0) return null;

  const errors = diagnostics.filter((d) => d.severity === "error");
  const warnings = diagnostics.filter((d) => d.severity === "warning");
  const infos = diagnostics.filter((d) => d.severity === "info");

  return (
    <div className="diagnostics-panel">
      <button
        className="diagnostics-toggle"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="diagnostics-icon">🔍</span>
        Compiler Diagnostics
        {errors.length > 0 && (
          <span className="diag-badge diag-error">{errors.length} error{errors.length > 1 ? "s" : ""}</span>
        )}
        {warnings.length > 0 && (
          <span className="diag-badge diag-warning">{warnings.length} warning{warnings.length > 1 ? "s" : ""}</span>
        )}
        {infos.length > 0 && (
          <span className="diag-badge diag-info">{infos.length} info</span>
        )}
        <span className={`chevron ${expanded ? "open" : ""}`}>▸</span>
      </button>
      {expanded && (
        <ul className="diagnostics-list">
          {diagnostics.map((d, i) => (
            <li key={i} className={`diag-item diag-${d.severity}`}>
              <span className="diag-severity">{d.severity.toUpperCase()}</span>
              <span className="diag-phase">[{d.phase}]</span>
              {d.line && <span className="diag-line">L{d.line}</span>}
              <span className="diag-msg">{d.message}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

const ResumeUpload = () => {
  const [files, setFiles] = useState([]);
  const [jobRole, setJobRole] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [rankedResumes, setRankedResumes] = useState([]);
  const [detailedResults, setDetailedResults] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [workflowSteps, setWorkflowSteps] = useState(cloneWorkflowTemplate());
  const [expandedResume, setExpandedResume] = useState(null);

  const formatScore = (score) => {
    const num = Number(score);
    return Number.isFinite(num) ? num.toFixed(2) : "0.00";
  };

  const mergeFiles = (existingFiles, incomingFiles) => {
    const map = new Map();
    [...existingFiles, ...incomingFiles].forEach((file) => {
      const key = `${file.name}__${file.size}__${file.lastModified}`;
      map.set(key, file);
    });
    return Array.from(map.values());
  };

  const nowStamp = () =>
    new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

  const resetWorkflow = () => {
    setWorkflowSteps(cloneWorkflowTemplate());
  };

  const updateWorkflowStep = (key, status) => {
    setWorkflowSteps((prev) =>
      prev.map((step) =>
        step.key === key
          ? {
              ...step,
              status,
              time:
                status === "completed" || status === "error"
                  ? nowStamp()
                  : step.time,
            }
          : step,
      ),
    );
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles((prev) => mergeFiles(prev, Array.from(e.target.files)));
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
      setFiles((prev) => mergeFiles(prev, Array.from(e.dataTransfer.files)));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!jobRole.trim()) {
      setUploadStatus({ success: false, message: "Please enter a job role." });
      return;
    }

    if (files.length === 0) {
      setUploadStatus({
        success: false,
        message: "Please select at least one file to upload",
      });
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);
    setDetailedResults([]);
    setExpandedResume(null);
    resetWorkflow();
    updateWorkflowStep("upload", "in-progress");

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("jobRole", jobRole);

    try {
      const uploadRes = await fetch(apiUrl("/upload"), {
        method: "POST",
        body: formData,
      });

      if (uploadRes.ok) {
        const data = await uploadRes.json();
        const uploadedCount = data?.uploaded_count ?? files.length;
        updateWorkflowStep("upload", "completed");
        setUploadStatus({
          success: true,
          message: `Successfully uploaded ${uploadedCount} resume${uploadedCount > 1 ? "s" : ""}!`,
        });
        setFiles([]);
        setJobRole("");

        // Single server round-trip runs the full pipeline; keep one UI step in progress.
        updateWorkflowStep("compile", "in-progress");

        const processRes = await fetch(apiUrl("/process"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });

        if (processRes.ok) {
          const processData = await processRes.json();

          updateWorkflowStep("compile", "completed");
          updateWorkflowStep("rank", "in-progress");

          const details = Array.isArray(processData.details)
            ? processData.details
            : [];
          setDetailedResults(details);

          let rankings = Array.isArray(processData.rankings)
            ? processData.rankings
            : [];
          if (
            rankings.length === 0 &&
            details.length > 0
          ) {
            rankings = details.map((d) => ({
              filename: d.filename,
              raw_score: d.score?.total_score ?? 0,
              normalized_score: d.score?.normalized_score ?? 0,
            }));
          }
          setRankedResumes(rankings);

          if (rankings.length > 0) {
            updateWorkflowStep("rank", "completed");
          } else {
            const rankRes = await fetch(apiUrl("/rankings"));
            const rankData = await rankRes.json().catch(() => ({}));
            if (
              rankData.status === "success" &&
              Array.isArray(rankData.rankings) &&
              rankData.rankings.length > 0
            ) {
              setRankedResumes(rankData.rankings);
              updateWorkflowStep("rank", "completed");
            } else {
              updateWorkflowStep("rank", "error");
            }
          }
        } else {
          const processError = await processRes.json().catch(() => ({}));
          const fallback =
            processError && processError.message
              ? processError.message
              : `Processing failed (HTTP ${processRes.status}).`;
          updateWorkflowStep("compile", "error");
          updateWorkflowStep("rank", "error");
          setUploadStatus({
            success: false,
            message: fallback,
          });
        }
      } else {
        const errJson = await uploadRes.json().catch(() => null);
        const errText = errJson ? null : await uploadRes.text().catch(() => "");
        const message =
          (errJson && errJson.message) ||
          errText ||
          `Upload failed (HTTP ${uploadRes.status}). Is the API running on port 8000?`;
        ["upload", "compile", "rank"].forEach((k) => updateWorkflowStep(k, "error"));
        setUploadStatus({
          success: false,
          message,
        });
      }
    } catch (error) {
      ["upload", "compile", "rank"].forEach((k) => updateWorkflowStep(k, "error"));
      setUploadStatus({
        success: false,
        message:
          error?.message ||
          "Network error — start Flask (`python app.py`) and keep Vite dev server running.",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = () => {
    window.open(apiUrl("/download-ranked-resumes"), "_blank", "noopener,noreferrer");
  };

  const getScoreColor = (normalized) => {
    if (normalized >= 0.7) return "score-high";
    if (normalized >= 0.4) return "score-medium";
    return "score-low";
  };

  const showWorkflow =
    isUploading || workflowSteps.some((step) => step.status !== "pending");

  // Find detail for a given filename
  const getDetail = (filename) =>
    detailedResults.find((d) => d.filename === filename);

  return (
    <div className="resume-upload-container">
      <div className="resume-upload-card">
        <div className="resume-upload-header">
          <h2>Upload Resumes</h2>
          <p>Select or drag and drop resume files for compiler analysis</p>
        </div>

        {uploadStatus && (
          <div
            className={`upload-status ${uploadStatus.success ? "success" : "error"}`}
          >
            {uploadStatus.message}
          </div>
        )}

        {showWorkflow && (
          <div className="workflow-panel">
            <h3>Compiler Pipeline</h3>
            <ul className="workflow-list">
              {workflowSteps.map((step) => (
                <li
                  key={step.key}
                  className={`workflow-item workflow-${step.status}`}
                >
                  <span className="workflow-dot" />
                  <div className="workflow-content">
                    <p className="workflow-title">{step.label}</p>
                    <p className="workflow-detail">{step.detail}</p>
                  </div>
                  <span className="workflow-meta">
                    {step.status === "in-progress" ? "In progress" : null}
                    {step.status === "completed" && step.time
                      ? `Done ${step.time}`
                      : null}
                    {step.status === "error" && step.time
                      ? `Failed ${step.time}`
                      : null}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="resume-upload-form"
          onDragEnter={handleDrag}
        >
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
            className={`file-drop-area ${dragActive ? "active" : ""} ${files.length > 0 ? "has-files" : ""}`}
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
                accept=".pdf,.doc,.docx"
                className="file-input"
                name="files"
              />
              <label htmlFor="resumeFiles" className="file-label">
                <div className="upload-icon">📄</div>
                <span className="upload-text">
                  {files.length > 0
                    ? `${files.length} file${files.length > 1 ? "s" : ""} selected`
                    : "Choose files or drag them here"}
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
                      <span className="file-size">
                        ({(file.size / 1024).toFixed(1)} KB)
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <button
            type="submit"
            className={`upload-button ${isUploading ? "loading" : ""}`}
            disabled={isUploading}
          >
            {isUploading ? <span className="spinner"></span> : "Upload & Compile"}
          </button>
        </form>

        {/* Ranked Output Section */}
        {rankedResumes.length > 0 && (
          <div className="parsed-results-container">
            <h3>Ranked Resumes</h3>
            <div className="ranked-cards">
              {rankedResumes.map((resume, index) => {
                const detail = getDetail(resume.filename);
                const isExpanded = expandedResume === index;
                const normalized = resume.normalized_score ?? resume.score ?? 0;
                const totalScore = resume.raw_score ?? (normalized * 100);

                return (
                  <div
                    key={index}
                    className={`ranked-card ${getScoreColor(normalized)}`}
                  >
                    <div
                      className="ranked-card-header"
                      onClick={() =>
                        setExpandedResume(isExpanded ? null : index)
                      }
                    >
                      <div className="rank-badge">#{index + 1}</div>
                      <div className="ranked-card-info">
                        <span className="ranked-filename">
                          {resume.filename}
                        </span>
                        <span className="ranked-score-label">
                          Score: {formatScore(totalScore)}/100
                        </span>
                      </div>
                      <div className="ranked-score-circle">
                        <span>{Math.round(normalized * 100)}%</span>
                      </div>
                      <span className={`chevron ${isExpanded ? "open" : ""}`}>
                        ▸
                      </span>
                    </div>

                    {isExpanded && detail && (
                      <div className="ranked-card-detail">
                        {/* Score Breakdown */}
                        {detail.score?.breakdown && (
                          <div className="score-breakdown">
                            <h4>Score Breakdown</h4>
                            <ScoreBar
                              score={detail.score.breakdown.skills?.score ?? 0}
                              max={detail.score.breakdown.skills?.max ?? 40}
                              label="Skills"
                            />
                            <ScoreBar
                              score={detail.score.breakdown.experience?.score ?? 0}
                              max={detail.score.breakdown.experience?.max ?? 30}
                              label="Experience"
                            />
                            <ScoreBar
                              score={detail.score.breakdown.education?.score ?? 0}
                              max={detail.score.breakdown.education?.max ?? 15}
                              label="Education"
                            />
                            <ScoreBar
                              score={detail.score.breakdown.structure?.score ?? 0}
                              max={detail.score.breakdown.structure?.max ?? 15}
                              label="Structure"
                            />
                          </div>
                        )}

                        {/* Matched & Missing Skills */}
                        {detail.score?.breakdown?.skills && (
                          <div className="skills-match-panel">
                            {detail.score.breakdown.skills.matched?.length > 0 && (
                              <div className="skills-matched">
                                <h5>✅ Matched Skills</h5>
                                <div className="skill-tags">
                                  {detail.score.breakdown.skills.matched.map(
                                    (s, i) => (
                                      <span key={i} className="skill-tag matched">
                                        {s}
                                      </span>
                                    ),
                                  )}
                                </div>
                              </div>
                            )}
                            {detail.score.breakdown.skills.missing?.length > 0 && (
                              <div className="skills-missing">
                                <h5>❌ Missing Skills</h5>
                                <div className="skill-tags">
                                  {detail.score.breakdown.skills.missing.map(
                                    (s, i) => (
                                      <span key={i} className="skill-tag missing">
                                        {s}
                                      </span>
                                    ),
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Phase Timings */}
                        {detail.phases && (
                          <div className="phase-timings">
                            <h5>⏱ Pipeline Timings</h5>
                            <div className="timing-chips">
                              {Object.entries(detail.phases)
                                .filter(([k]) => k !== "total_ms")
                                .map(([phase, ms]) => (
                                  <span key={phase} className="timing-chip">
                                    {phase.replace("_ms", "")}: {ms}ms
                                  </span>
                                ))}
                            </div>
                          </div>
                        )}

                        {/* Diagnostics */}
                        <DiagnosticsPanel
                          diagnostics={detail.diagnostics}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
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
