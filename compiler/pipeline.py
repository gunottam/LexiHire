"""
Compiler Pipeline Orchestrator
================================
Chains all compiler phases together:
  Lexer → Parser → Semantic Analyzer → IR Builder → Optimizer → Scorer

Each phase is timed and produces diagnostics.
"""

import time
from compiler.errors.diagnostics import DiagnosticCollector
from compiler.lexer.lexer import Lexer
from compiler.parser.parser import ResumeParser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.ir.builder import IRBuilder
from compiler.optimizer.optimizer import Optimizer
from compiler.scorer.scorer import ResumeScorer

# Guardrail for pathological PDFs / pasted blobs (keeps tokenize responsive).
_MAX_RESUME_CHARS = 120_000


class CompilerPipeline:
    """
    Orchestrates the full resume compilation pipeline.

    Usage:
        pipeline = CompilerPipeline()
        result = pipeline.compile(raw_text, job_role)
    """

    def compile(self, raw_text, job_role, return_ast=False):
        """
        Run the complete compiler pipeline on raw resume text.

        Args:
            raw_text: The raw text extracted from a resume file
            job_role: The target job role for scoring

        Returns:
            dict with keys: ast, ir, score, diagnostics, phases
        """
        diagnostics = DiagnosticCollector()
        phases = {}

        if len(raw_text) > _MAX_RESUME_CHARS:
            diagnostics.warning(
                "lexer",
                f"Resume text truncated to {_MAX_RESUME_CHARS} characters for analysis.",
            )
            raw_text = raw_text[:_MAX_RESUME_CHARS]

        n_chars = len(raw_text)
        print(f"    … lexer: {n_chars} chars", flush=True)

        # ── Phase 1: Lexical Analysis ─────────────────────────────────
        t0 = time.time()
        lexer = Lexer(raw_text, diagnostics)
        tokens = lexer.tokenize()
        phases["lexer_ms"] = round((time.time() - t0) * 1000, 2)
        print(f"    … lexer done: {len(tokens)} tokens ({phases['lexer_ms']} ms)", flush=True)

        diagnostics.info(
            "lexer",
            f"Produced {len(tokens)} tokens "
            f"({sum(1 for t in tokens if t.type.name == 'WORD')} words, "
            f"{sum(1 for t in tokens if t.type.name == 'HEADER')} headers)",
        )

        # ── Phase 2: Syntax Analysis (Parsing) ───────────────────────
        t0 = time.time()
        print("    … parser", flush=True)
        parser = ResumeParser(tokens, diagnostics)
        ast = parser.parse()
        phases["parser_ms"] = round((time.time() - t0) * 1000, 2)
        print(f"    … parser done ({phases['parser_ms']} ms)", flush=True)

        diagnostics.info(
            "parser",
            f"Parsed {len(ast.sections)} section(s)"
            + (f", contact: {ast.contact.name}" if ast.contact and ast.contact.name else ""),
        )

        # ── Phase 3: Semantic Analysis ────────────────────────────────
        t0 = time.time()
        print("    … semantic", flush=True)
        analyzer = SemanticAnalyzer(ast, diagnostics)
        ast = analyzer.analyze()
        phases["semantic_ms"] = round((time.time() - t0) * 1000, 2)
        print(f"    … semantic done ({phases['semantic_ms']} ms)", flush=True)

        # ── Phase 4: IR Generation ────────────────────────────────────
        t0 = time.time()
        print("    … IR", flush=True)
        ir_builder = IRBuilder(ast, diagnostics)
        ir = ir_builder.build()
        phases["ir_ms"] = round((time.time() - t0) * 1000, 2)

        # ── Phase 5: Optimization ─────────────────────────────────────
        t0 = time.time()
        optimizer = Optimizer(ir, diagnostics)
        ir = optimizer.optimize()
        phases["optimizer_ms"] = round((time.time() - t0) * 1000, 2)

        # ── Phase 6: Scoring ──────────────────────────────────────────
        t0 = time.time()
        print("    … scorer", flush=True)
        scorer = ResumeScorer(ir, job_role, diagnostics)
        score_result = scorer.score()
        phases["scorer_ms"] = round((time.time() - t0) * 1000, 2)

        # ── Total time ────────────────────────────────────────────────
        phase_keys = (
            "lexer_ms", "parser_ms", "semantic_ms", "ir_ms",
            "optimizer_ms", "scorer_ms",
        )
        phases["total_ms"] = round(sum(phases.get(k, 0) for k in phase_keys), 2)

        # Building the full AST dict is expensive and unused by the Flask API.
        ast_payload = ast.to_dict() if return_ast else None

        return {
            "ast": ast_payload,
            "ir": ir,
            "score": score_result,
            "diagnostics": diagnostics.to_list(),
            "diagnostics_summary": diagnostics.summary(),
            "phases": phases,
        }
