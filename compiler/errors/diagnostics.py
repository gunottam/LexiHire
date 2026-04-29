"""
Compiler Diagnostics System
============================
Provides compiler-style error, warning, and info messages
that accumulate across all pipeline phases.

Example diagnostics:
  - "Semantic Warning [line 12]: Duplicate skill 'Python'"
  - "Syntax Error [line 5]: Unexpected token in EXPERIENCE section"
  - "Info: Resume has 4 of 4 required sections"
"""

from enum import Enum


class DiagnosticSeverity(Enum):
    """Severity levels for compiler diagnostics."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Diagnostic:
    """
    A single compiler diagnostic message.

    Attributes:
        severity: ERROR, WARNING, or INFO
        phase: The compiler phase that produced this diagnostic
        message: Human-readable description of the issue
        line: Source line number (1-indexed), or None if not applicable
        column: Source column number (1-indexed), or None if not applicable
    """

    __slots__ = ("severity", "phase", "message", "line", "column")

    def __init__(self, severity, phase, message, line=None, column=None):
        self.severity = severity
        self.phase = phase
        self.message = message
        self.line = line
        self.column = column

    def to_dict(self):
        return {
            "severity": self.severity.value,
            "phase": self.phase,
            "message": self.message,
            "line": self.line,
            "column": self.column,
        }

    def __repr__(self):
        loc = ""
        if self.line is not None:
            loc = f" [line {self.line}"
            if self.column is not None:
                loc += f", col {self.column}"
            loc += "]"
        return (
            f"{self.severity.value.upper()}{loc} "
            f"({self.phase}): {self.message}"
        )


class DiagnosticCollector:
    """
    Accumulates diagnostics across all compiler phases.

    Usage:
        dc = DiagnosticCollector()
        dc.error("parser", "Unexpected token SYMBOL", line=5, column=12)
        dc.warning("semantic", "Duplicate skill 'Python'", line=12)
        dc.info("scorer", "Skills section scored 34/40")

        if dc.has_errors():
            print("Compilation failed!")

        for d in dc.all():
            print(d)
    """

    def __init__(self):
        self._diagnostics = []

    def _add(self, severity, phase, message, line=None, column=None):
        self._diagnostics.append(
            Diagnostic(severity, phase, message, line, column)
        )

    def error(self, phase, message, line=None, column=None):
        """Record a compiler error."""
        self._add(DiagnosticSeverity.ERROR, phase, message, line, column)

    def warning(self, phase, message, line=None, column=None):
        """Record a compiler warning."""
        self._add(DiagnosticSeverity.WARNING, phase, message, line, column)

    def info(self, phase, message, line=None, column=None):
        """Record an informational message."""
        self._add(DiagnosticSeverity.INFO, phase, message, line, column)

    def has_errors(self):
        """Return True if any ERROR-level diagnostics were recorded."""
        return any(
            d.severity == DiagnosticSeverity.ERROR for d in self._diagnostics
        )

    def error_count(self):
        return sum(
            1 for d in self._diagnostics
            if d.severity == DiagnosticSeverity.ERROR
        )

    def warning_count(self):
        return sum(
            1 for d in self._diagnostics
            if d.severity == DiagnosticSeverity.WARNING
        )

    def all(self):
        """Return all diagnostics in insertion order."""
        return list(self._diagnostics)

    def to_list(self):
        """Serialize all diagnostics to a list of dicts."""
        return [d.to_dict() for d in self._diagnostics]

    def summary(self):
        """Return a human-readable summary string."""
        e = self.error_count()
        w = self.warning_count()
        i = len(self._diagnostics) - e - w
        parts = []
        if e:
            parts.append(f"{e} error{'s' if e != 1 else ''}")
        if w:
            parts.append(f"{w} warning{'s' if w != 1 else ''}")
        if i:
            parts.append(f"{i} info")
        return ", ".join(parts) if parts else "No diagnostics"

    def __len__(self):
        return len(self._diagnostics)

    def __repr__(self):
        return f"DiagnosticCollector({self.summary()})"
