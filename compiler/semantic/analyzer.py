"""
Semantic Analyzer
==================
Validates the AST for logical correctness, normalizes skill names,
detects duplicates, validates date ranges, and checks for required sections.
"""

from compiler.ast_nodes.nodes import (
    ResumeNode, SectionNode, SkillNode, ExperienceNode, EducationNode,
)

# ── Skill name normalization map ─────────────────────────────────────────────
# Maps common aliases/variants to a canonical form.
SKILL_ALIASES = {
    # Languages
    "c++": "cpp", "c#": "csharp", "c sharp": "csharp",
    "javascript": "javascript", "js": "javascript", "es6": "javascript",
    "typescript": "typescript", "ts": "typescript",
    "python3": "python", "python2": "python",
    "golang": "go", "go lang": "go",
    "r lang": "r", "r language": "r",
    # Frontend
    "react.js": "react", "reactjs": "react", "react js": "react",
    "vue.js": "vue", "vuejs": "vue", "vue js": "vue",
    "angular.js": "angular", "angularjs": "angular",
    "next.js": "nextjs", "next js": "nextjs",
    "nuxt.js": "nuxtjs",
    "svelte.js": "svelte",
    "jquery": "jquery",
    "tailwind css": "tailwindcss", "tailwind": "tailwindcss",
    "bootstrap": "bootstrap",
    "sass": "sass", "scss": "sass",
    # Backend
    "node.js": "nodejs", "node js": "nodejs", "node": "nodejs",
    "express.js": "express", "expressjs": "express",
    "django rest framework": "django", "drf": "django",
    "flask": "flask", "fastapi": "fastapi",
    "spring boot": "springboot", "spring": "spring",
    "ruby on rails": "rails", "ror": "rails",
    ".net": "dotnet", "dot net": "dotnet", "asp.net": "dotnet",
    # Databases
    "mongodb": "mongodb", "mongo": "mongodb", "mongo db": "mongodb",
    "postgresql": "postgresql", "postgres": "postgresql", "psql": "postgresql",
    "mysql": "mysql", "my sql": "mysql",
    "sql server": "mssql", "ms sql": "mssql",
    "redis": "redis",
    "firebase": "firebase",
    "dynamodb": "dynamodb", "dynamo db": "dynamodb",
    "supabase": "supabase",
    # Cloud / DevOps
    "amazon web services": "aws", "a.w.s": "aws",
    "google cloud platform": "gcp", "google cloud": "gcp",
    "microsoft azure": "azure", "ms azure": "azure",
    "docker": "docker",
    "kubernetes": "kubernetes", "k8s": "kubernetes",
    "ci/cd": "cicd", "ci cd": "cicd",
    "jenkins": "jenkins",
    "github actions": "github-actions",
    "terraform": "terraform",
    "ansible": "ansible",
    # Data / ML
    "machine learning": "ml", "ml": "ml",
    "deep learning": "deep-learning", "dl": "deep-learning",
    "artificial intelligence": "ai", "a.i.": "ai",
    "natural language processing": "nlp",
    "computer vision": "computer-vision", "cv": "computer-vision",
    "tensorflow": "tensorflow", "tf": "tensorflow",
    "pytorch": "pytorch", "torch": "pytorch",
    "scikit-learn": "scikit-learn", "sklearn": "scikit-learn",
    "pandas": "pandas", "numpy": "numpy",
    "data science": "data-science",
    "data analysis": "data-analysis",
    "power bi": "powerbi",
    "tableau": "tableau",
    # Tools
    "git": "git", "github": "github", "gitlab": "gitlab",
    "bitbucket": "bitbucket",
    "jira": "jira", "confluence": "confluence",
    "vs code": "vscode", "visual studio code": "vscode",
    "postman": "postman",
    "figma": "figma",
    "linux": "linux", "ubuntu": "linux",
    "rest api": "rest-api", "restful": "rest-api", "rest": "rest-api",
    "graphql": "graphql",
    "webpack": "webpack", "vite": "vite",
    "agile": "agile", "scrum": "scrum",
}

REQUIRED_SECTIONS = {"skills", "experience", "education"}


class SemanticAnalyzer:
    """
    Performs semantic analysis on a ResumeNode AST:
      1. Checks for required sections
      2. Normalizes skill names
      3. Detects duplicate skills
      4. Validates date ranges in experience/education
      5. Computes experience duration metadata

    Usage:
        analyzer = SemanticAnalyzer(ast, diagnostics)
        analyzer.analyze()
    """

    def __init__(self, ast, diagnostics):
        self.ast = ast
        self.diagnostics = diagnostics

    def analyze(self):
        """Run all semantic checks on the AST."""
        self._check_required_sections()
        self._normalize_skills()
        self._detect_duplicate_skills()
        self._validate_dates()
        return self.ast

    # ── Required sections ─────────────────────────────────────────────────

    def _check_required_sections(self):
        found = {s.section_type for s in self.ast.sections}
        for req in REQUIRED_SECTIONS:
            if req not in found:
                self.diagnostics.warning(
                    "semantic",
                    f"Missing recommended section: '{req.upper()}'",
                )
        self.diagnostics.info(
            "semantic",
            f"Resume has {len(found)} section(s): {', '.join(sorted(found))}",
        )

    # ── Skill normalization ───────────────────────────────────────────────

    def _normalize_skills(self):
        for section in self.ast.sections:
            if section.section_type != "skills":
                continue
            for skill_node in section.entries:
                if not isinstance(skill_node, SkillNode):
                    continue
                lower = skill_node.name.lower().strip()
                if lower in SKILL_ALIASES:
                    old = skill_node.name
                    skill_node.name = SKILL_ALIASES[lower]
                    if old.lower() != skill_node.name:
                        self.diagnostics.info(
                            "semantic",
                            f"Normalized skill '{old}' → '{skill_node.name}'",
                            line=skill_node.line,
                        )
                else:
                    # Default normalization: lowercase, strip
                    skill_node.name = lower

    # ── Duplicate detection ───────────────────────────────────────────────

    def _detect_duplicate_skills(self):
        for section in self.ast.sections:
            if section.section_type != "skills":
                continue
            seen = {}
            for skill_node in section.entries:
                if not isinstance(skill_node, SkillNode):
                    continue
                key = skill_node.name.lower()
                if key in seen:
                    self.diagnostics.warning(
                        "semantic",
                        f"Duplicate skill '{skill_node.name}' "
                        f"(first seen at line {seen[key]})",
                        line=skill_node.line,
                    )
                else:
                    seen[key] = skill_node.line

    # ── Date validation ───────────────────────────────────────────────────

    def _validate_dates(self):
        for section in self.ast.sections:
            for entry in section.entries:
                if isinstance(entry, (ExperienceNode, EducationNode)):
                    if entry.start_date and entry.end_date:
                        start_y = self._extract_year(entry.start_date)
                        end_y = self._extract_year(entry.end_date)
                        if start_y and end_y and end_y < start_y:
                            self.diagnostics.error(
                                "semantic",
                                f"Invalid date range: start={entry.start_date} "
                                f"is after end={entry.end_date}",
                                line=entry.line,
                            )

    @staticmethod
    def _extract_year(date_str):
        """Extract a 4-digit year from a date string."""
        if not date_str:
            return None
        if date_str.lower() in ("present", "current", "ongoing"):
            return 9999  # sentinel for "ongoing"
        # Find 4-digit number
        digits = ""
        for ch in date_str:
            if ch.isdigit():
                digits += ch
            else:
                if len(digits) == 4:
                    break
                if not ch.isdigit():
                    digits = ""
        if len(digits) >= 4:
            try:
                return int(digits[:4])
            except ValueError:
                return None
        return None
