import React, { useState } from "react";
import { apiUrl } from "../../api.js";
import {
  FileText,
  Loader2,
  Download,
  ChevronDown,
  Sparkles,
  Search,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";

const WORKFLOW_TEMPLATE = [
  {
    key: "upload",
    label: "Uploading resumes",
    detail: "Sending selected files to the server.",
    status: "pending",
    time: null,
  },
  {
    key: "compile",
    label: "Compile & analyze",
    detail:
      "Lexer → parser → semantic → IR → optimization → scoring (per resume).",
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

const cloneWorkflowTemplate = () => WORKFLOW_TEMPLATE.map((step) => ({ ...step }));

const ScoreBar = ({ score, max, label }) => {
  const pct = max > 0 ? Math.min(100, (score / max) * 100) : 0;
  const fill =
    pct < 40 ? "bg-primary" : pct < 70 ? "bg-accent" : "bg-plum";

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-foreground">{label}</span>
        <span className="tabular-nums text-muted-foreground">
          {score}/{max}
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className={cn("h-full rounded-full transition-all duration-500", fill)}
          style={{ width: `${pct}%` }}
        />
      </div>
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
    <div className="mt-4 rounded-lg border border-border/80 bg-muted/20">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-foreground transition-colors hover:bg-muted/60"
      >
        <Search className="size-4 shrink-0 text-plum" aria-hidden />
        <span className="flex-1">Compiler diagnostics</span>
        {errors.length > 0 ? (
          <Badge variant="destructive" className="font-normal">
            {errors.length} err
          </Badge>
        ) : null}
        {warnings.length > 0 ? (
          <Badge variant="outline" className="border-primary/40 text-primary">
            {warnings.length} warn
          </Badge>
        ) : null}
        {infos.length > 0 ? (
          <Badge variant="secondary" className="font-normal">
            {infos.length} info
          </Badge>
        ) : null}
        <ChevronDown
          className={cn(
            "size-4 shrink-0 text-muted-foreground transition-transform",
            expanded && "rotate-180",
          )}
          aria-hidden
        />
      </button>
      {expanded ? (
        <ul className="max-h-56 space-y-1 overflow-y-auto border-t border-border/60 px-3 py-2 text-xs">
          {diagnostics.map((d, i) => (
            <li
              key={i}
              className={cn(
                "rounded-md px-2 py-1.5 font-mono leading-relaxed",
                d.severity === "error" && "bg-destructive/10 text-destructive",
                d.severity === "warning" &&
                  "bg-primary/5 text-primary",
                d.severity === "info" && "bg-muted text-muted-foreground",
              )}
            >
              <span className="font-semibold uppercase">{d.severity}</span>{" "}
              <span className="text-muted-foreground">[{d.phase}]</span>{" "}
              {d.line ? <span>L{d.line} </span> : null}
              {d.message}
            </li>
          ))}
        </ul>
      ) : null}
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
          message: `Uploaded ${uploadedCount} resume${uploadedCount > 1 ? "s" : ""}.`,
        });
        setFiles([]);
        setJobRole("");

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
          if (rankings.length === 0 && details.length > 0) {
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
          "Network error — start Flask (`python app.py`) and keep Vite running.",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = () => {
    window.open(apiUrl("/download-ranked-resumes"), "_blank", "noopener,noreferrer");
  };

  const getScoreRingClass = (normalized) => {
    if (normalized >= 0.7) return "ring-accent/60 bg-accent/10 text-accent-foreground";
    if (normalized >= 0.4)
      return "ring-primary/35 bg-primary/5 text-foreground";
    return "ring-border bg-muted text-muted-foreground";
  };

  const showWorkflow =
    isUploading || workflowSteps.some((step) => step.status !== "pending");

  const getDetail = (filename) =>
    detailedResults.find((d) => d.filename === filename);

  const workflowBadge = (status) => {
    if (status === "completed")
      return (
        <Badge variant="wasabi" className="font-normal">
          Done
        </Badge>
      );
    if (status === "in-progress")
      return (
        <Badge variant="secondary" className="font-normal">
          Running
        </Badge>
      );
    if (status === "error")
      return (
        <Badge variant="destructive" className="font-normal">
          Failed
        </Badge>
      );
    return (
      <Badge variant="outline" className="font-normal text-muted-foreground">
        Pending
      </Badge>
    );
  };

  return (
    <div className="animate-fade-in space-y-8">
      <div className="space-y-1">
        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-plum">
          Workspace
        </p>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Upload & compile
        </h1>
        <p className="max-w-2xl text-sm text-muted-foreground sm:text-base">
          Drop PDFs or Word files, set the role, and run the full compiler
          pipeline — then explore ranked results in one calm view.
        </p>
      </div>

      <Card className="overflow-hidden border-border/70 shadow-sm shadow-plum/5">
        <CardHeader className="border-b border-border/60 bg-card pb-4">
          <div className="flex items-start gap-3">
            <div className="flex size-10 items-center justify-center rounded-lg bg-secondary text-plum">
              <Sparkles className="size-5" aria-hidden />
            </div>
            <div>
              <CardTitle className="text-lg sm:text-xl">New batch</CardTitle>
              <CardDescription>
                Job role drives keyword extraction and scoring against each resume.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6 pt-6">
          {uploadStatus ? (
            <Alert variant={uploadStatus.success ? "success" : "destructive"}>
              <AlertDescription>{uploadStatus.message}</AlertDescription>
            </Alert>
          ) : null}

          {showWorkflow ? (
            <div className="rounded-xl border border-border/70 bg-muted/25 p-4">
              <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Compiler pipeline
              </p>
              <ul className="space-y-3">
                {workflowSteps.map((step) => (
                  <li
                    key={step.key}
                    className="flex flex-wrap items-center gap-3 rounded-lg border border-border/50 bg-card/80 px-3 py-2.5"
                  >
                    <span
                      className={cn(
                        "size-2 shrink-0 rounded-full",
                        step.status === "completed" && "bg-accent",
                        step.status === "in-progress" && "bg-primary animate-pulse",
                        step.status === "error" && "bg-destructive",
                        step.status === "pending" && "bg-muted-foreground/30",
                      )}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-foreground">
                        {step.label}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {step.detail}
                      </p>
                    </div>
                    <div className="flex shrink-0 flex-col items-end gap-1 text-right">
                      {workflowBadge(step.status)}
                      {step.time ? (
                        <span className="text-[11px] text-muted-foreground">
                          {step.time}
                        </span>
                      ) : null}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          <form
            className="space-y-6"
            onSubmit={handleSubmit}
            onDragEnter={handleDrag}
          >
            <div className="space-y-2">
              <Label htmlFor="jobRole">Job role</Label>
              <Input
                id="jobRole"
                value={jobRole}
                onChange={(e) => setJobRole(e.target.value)}
                placeholder="e.g. Senior frontend engineer"
                required
              />
            </div>

            <div
              className={cn(
                "relative rounded-xl border-2 border-dashed transition-colors",
                dragActive
                  ? "border-accent bg-accent/10"
                  : files.length > 0
                    ? "border-plum/40 bg-secondary/40"
                    : "border-border bg-muted/15 hover:border-plum/35 hover:bg-muted/25",
              )}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                id="resumeFiles"
                onChange={handleFileChange}
                multiple
                accept=".pdf,.doc,.docx"
                className="absolute inset-0 z-10 cursor-pointer opacity-0"
                name="files"
              />
              <div className="pointer-events-none flex flex-col items-center gap-2 px-6 py-12 text-center">
                <div className="flex size-12 items-center justify-center rounded-full bg-card shadow-sm ring-1 ring-border">
                  <FileText className="size-6 text-plum" aria-hidden />
                </div>
                <p className="text-sm font-medium text-foreground">
                  {files.length > 0
                    ? `${files.length} file${files.length > 1 ? "s" : ""} selected`
                    : "Drop files here or click to browse"}
                </p>
                <p className="text-xs text-muted-foreground">
                  PDF, DOC, DOCX — multiple files supported
                </p>
              </div>
            </div>

            {files.length > 0 ? (
              <div className="rounded-lg border border-border/60 bg-card/50 px-3 py-3">
                <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Selected
                </p>
                <ul className="max-h-36 space-y-1.5 overflow-y-auto text-sm">
                  {files.map((file, index) => (
                    <li
                      key={`${file.name}-${index}`}
                      className="flex justify-between gap-2 rounded-md px-2 py-1 hover:bg-muted/50"
                    >
                      <span className="truncate font-medium text-foreground">
                        {file.name}
                      </span>
                      <span className="shrink-0 tabular-nums text-xs text-muted-foreground">
                        {(file.size / 1024).toFixed(1)} KB
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            <Button type="submit" className="w-full sm:w-auto" disabled={isUploading}>
              {isUploading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Working…
                </>
              ) : (
                <>
                  <Sparkles className="size-4" />
                  Upload & compile
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {rankedResumes.length > 0 ? (
        <section className="space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="font-display text-2xl font-semibold tracking-tight">
                Ranked resumes
              </h2>
              <p className="text-sm text-muted-foreground">
                Tap a row to expand score breakdown and diagnostics.
              </p>
            </div>
            <Button variant="plum" onClick={handleDownload} className="gap-2">
              <Download className="size-4" />
              Download ZIP
            </Button>
          </div>

          <div className="space-y-3">
            {rankedResumes.map((resume, index) => {
              const detail = getDetail(resume.filename);
              const isExpanded = expandedResume === index;
              const normalized = resume.normalized_score ?? resume.score ?? 0;
              const totalScore = resume.raw_score ?? normalized * 100;

              return (
                <Card
                  key={`${resume.filename}-${index}`}
                  className={cn(
                    "overflow-hidden border-border/70 transition-shadow",
                    isExpanded && "shadow-md ring-1 ring-plum/15",
                  )}
                >
                  <button
                    type="button"
                    onClick={() => setExpandedResume(isExpanded ? null : index)}
                    className="flex w-full items-center gap-3 px-4 py-4 text-left transition-colors hover:bg-muted/30 sm:px-5"
                  >
                    <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-plum text-sm font-bold text-plum-foreground">
                      {index + 1}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="truncate font-medium text-foreground">
                        {resume.filename}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Score {formatScore(totalScore)}/100
                      </p>
                    </div>
                    <div
                      className={cn(
                        "flex size-12 shrink-0 items-center justify-center rounded-full text-sm font-semibold ring-2 ring-offset-2 ring-offset-background",
                        getScoreRingClass(normalized),
                      )}
                    >
                      {Math.round(normalized * 100)}%
                    </div>
                    <ChevronDown
                      className={cn(
                        "size-5 shrink-0 text-muted-foreground transition-transform",
                        isExpanded && "rotate-180",
                      )}
                      aria-hidden
                    />
                  </button>

                  {isExpanded && detail ? (
                    <div className="space-y-4 border-t border-border/60 bg-muted/10 px-4 py-5 sm:px-5">
                      {detail.score?.breakdown ? (
                        <div className="space-y-3">
                          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                            Score breakdown
                          </p>
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
                      ) : null}

                      {detail.score?.breakdown?.skills ? (
                        <div className="grid gap-4 sm:grid-cols-2">
                          {detail.score.breakdown.skills.matched?.length > 0 ? (
                            <div className="rounded-lg border border-accent/30 bg-accent/5 p-3">
                              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-accent-foreground">
                                Matched skills
                              </p>
                              <div className="flex flex-wrap gap-1.5">
                                {detail.score.breakdown.skills.matched.map((s, i) => (
                                  <Badge key={i} variant="wasabi" className="font-normal">
                                    {s}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          ) : null}
                          {detail.score.breakdown.skills.missing?.length > 0 ? (
                            <div className="rounded-lg border border-primary/25 bg-primary/5 p-3">
                              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-primary">
                                Missing skills
                              </p>
                              <div className="flex flex-wrap gap-1.5">
                                {detail.score.breakdown.skills.missing.map((s, i) => (
                                  <Badge
                                    key={i}
                                    variant="outline"
                                    className="border-primary/40 font-normal text-primary"
                                  >
                                    {s}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          ) : null}
                        </div>
                      ) : null}

                      {detail.phases ? (
                        <div>
                          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                            Pipeline timings
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {Object.entries(detail.phases)
                              .filter(([k]) => k !== "total_ms")
                              .map(([phase, ms]) => (
                                <span
                                  key={phase}
                                  className="rounded-md border border-border bg-card px-2 py-1 font-mono text-[11px] text-muted-foreground"
                                >
                                  {phase.replace("_ms", "")}: {ms}ms
                                </span>
                              ))}
                          </div>
                        </div>
                      ) : null}

                      <DiagnosticsPanel diagnostics={detail.diagnostics} />
                    </div>
                  ) : null}
                </Card>
              );
            })}
          </div>
        </section>
      ) : null}
    </div>
  );
};

export default ResumeUpload;
