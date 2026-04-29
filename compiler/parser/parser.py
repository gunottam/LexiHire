"""
Recursive Descent Resume Parser
=================================
Parses a token stream (from the Lexer) into an Abstract Syntax Tree.
Uses the CFG defined in grammar.py. Never fatally rejects — all
structural issues are reported as diagnostics.
"""

from compiler.lexer.tokens import TokenType
from compiler.ast_nodes.nodes import (
    ResumeNode, ContactNode, SectionNode, SkillNode,
    ExperienceNode, EducationNode, CertificationNode,
    ProjectNode, EntryNode,
)

# Degree keywords used to identify education entries
DEGREE_KEYWORDS = {
    "b.tech", "btech", "b.e", "be", "b.sc", "bsc", "b.a", "ba",
    "m.tech", "mtech", "m.e", "me", "m.sc", "msc", "m.a", "ma",
    "mba", "m.b.a", "phd", "ph.d", "doctorate",
    "bachelor", "bachelors", "master", "masters",
    "associate", "associates", "diploma", "certificate",
    "b.com", "bcom", "m.com", "mcom", "bba", "bca", "mca",
    "b.s", "bs", "m.s", "ms", "b.eng", "m.eng",
    "high school", "secondary", "12th", "10th", "hsc", "ssc",
}

# GPA-related keywords
GPA_KEYWORDS = {"gpa", "cgpa", "sgpa", "percentage", "percent", "%", "grade"}


class ResumeParser:
    """
    Recursive descent parser for resume token streams.

    Usage:
        parser = ResumeParser(tokens, diagnostics)
        ast = parser.parse()
    """

    def __init__(self, tokens, diagnostics=None):
        self.tokens = tokens
        self.pos = 0
        self.diagnostics = diagnostics

    # ── Token navigation helpers ──────────────────────────────────────────

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def _advance(self):
        token = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def _at_end(self):
        return self._peek().type == TokenType.EOF

    def _check(self, *types):
        return self._peek().type in types

    def _match(self, *types):
        if self._peek().type in types:
            return self._advance()
        return None

    def _skip_newlines(self):
        while self._check(TokenType.NEWLINE):
            self._advance()

    def _diag_warn(self, msg, line=None):
        if self.diagnostics:
            self.diagnostics.warning("parser", msg, line=line)

    def _diag_error(self, msg, line=None):
        if self.diagnostics:
            self.diagnostics.error("parser", msg, line=line)

    # ── Main entry ────────────────────────────────────────────────────────

    def parse(self):
        """Parse the token stream into a ResumeNode AST."""
        resume = ResumeNode()
        self._skip_newlines()

        # Parse contact block (everything before the first HEADER)
        if not self._check(TokenType.HEADER):
            resume.contact = self._parse_contact()

        # Parse sections (hard cap avoids infinite loops on malformed token streams)
        parse_guard = 0
        parse_limit = max(5000, len(self.tokens) * 20)
        while not self._at_end():
            parse_guard += 1
            if parse_guard > parse_limit:
                self._diag_error(
                    "Parser iteration limit exceeded; stopping with partial AST."
                )
                break
            self._skip_newlines()
            if self._at_end():
                break
            if self._check(TokenType.HEADER):
                section = self._parse_section()
                if section:
                    resume.sections.append(section)
            else:
                # Unexpected token outside any section
                tok = self._advance()
                if tok.type != TokenType.NEWLINE:
                    self._diag_warn(
                        f"Unexpected token '{tok.value}' outside any section",
                        line=tok.line
                    )

        return resume

    # ── Contact block parser ──────────────────────────────────────────────

    def _parse_contact(self):
        """
        Parse everything before the first HEADER token as contact info.
        Extracts name, email, phone, and URLs.
        """
        contact = ContactNode()
        name_words = []
        first_line = self._peek().line

        while not self._at_end() and not self._check(TokenType.HEADER):
            tok = self._peek()

            if tok.type == TokenType.EMAIL:
                contact.email = self._advance().value
            elif tok.type == TokenType.PHONE:
                contact.phone = self._advance().value
            elif tok.type == TokenType.URL:
                contact.links.append(self._advance().value)
            elif tok.type == TokenType.WORD and tok.line == first_line:
                name_words.append(self._advance().value)
            elif tok.type == TokenType.NEWLINE:
                self._advance()
                # Update first_line tracking for name detection
                if not name_words:
                    first_line = self._peek().line if not self._at_end() else first_line
            else:
                self._advance()

        if name_words:
            contact.name = " ".join(name_words)

        return contact

    # ── Section parser ────────────────────────────────────────────────────

    def _parse_section(self):
        """
        Parse a section: HEADER NEWLINE SectionBody
        Dispatches to section-specific parsers based on header type.
        """
        header_tok = self._advance()  # consume HEADER
        section_type = header_tok.value  # canonical name from lexer
        section = SectionNode(section_type, header_tok.value, header_tok.line)

        self._skip_newlines()

        # Dispatch to section-specific parser
        dispatch = {
            "skills": self._parse_skills_body,
            "experience": self._parse_experience_body,
            "education": self._parse_education_body,
            "certifications": self._parse_certifications_body,
            "projects": self._parse_projects_body,
        }

        parser_fn = dispatch.get(section_type, self._parse_generic_body)
        entries = parser_fn(section)
        section.entries = entries
        return section

    # ── Skills section ────────────────────────────────────────────────────

    def _parse_skills_body(self, section):
        """
        Parse skills as comma/pipe/bullet/newline separated items.
        Each skill can be multi-word (e.g., "Machine Learning").
        """
        skills = []
        current_skill_words = []

        def flush_skill():
            if current_skill_words:
                name = " ".join(current_skill_words)
                name = name.strip(" .-:")
                if name:
                    skills.append(SkillNode(name, line=section.line))
                current_skill_words.clear()

        while not self._at_end() and not self._check(TokenType.HEADER):
            tok = self._peek()

            if tok.type in (TokenType.COMMA, TokenType.PIPE, TokenType.SEMICOLON):
                flush_skill()
                self._advance()
            elif tok.type == TokenType.BULLET:
                flush_skill()
                self._advance()
            elif tok.type == TokenType.NEWLINE:
                # Newline acts as a separator only if we have accumulated words
                if current_skill_words:
                    flush_skill()
                self._advance()
            elif tok.type == TokenType.WORD:
                current_skill_words.append(self._advance().value)
            elif tok.type in (TokenType.PLUS, TokenType.HASH, TokenType.DOT):
                # Attach to current skill (C++, C#, Node.js)
                if current_skill_words:
                    current_skill_words[-1] += self._advance().value
                else:
                    self._advance()
            elif tok.type == TokenType.NUMBER:
                # Part of a skill name like "Web3" or "Python3"
                if current_skill_words:
                    current_skill_words[-1] += self._advance().value
                else:
                    self._advance()
            elif tok.type == TokenType.SLASH:
                # "HTML/CSS" → treat as separator
                flush_skill()
                self._advance()
            elif tok.type == TokenType.COLON:
                # "Languages: Python, Java" → skip the colon, start skills
                flush_skill()
                self._advance()
            elif tok.type == TokenType.DASH:
                # Could be separator or part of name
                flush_skill()
                self._advance()
            else:
                self._advance()

        flush_skill()
        return skills

    # ── Experience section ────────────────────────────────────────────────

    def _parse_experience_body(self, section):
        """
        Parse experience entries. Each entry has:
          - A title line (with optional company, separated by dash/pipe/comma)
          - An optional date line
          - Optional bullet points
        """
        entries = []

        while not self._at_end() and not self._check(TokenType.HEADER):
            self._skip_newlines()
            if self._at_end() or self._check(TokenType.HEADER):
                break

            entry = ExperienceNode(line=self._peek().line)

            # Collect a "title line": everything until NEWLINE
            title_parts = []
            dates = []
            while not self._at_end() and not self._check(TokenType.HEADER, TokenType.NEWLINE):
                tok = self._peek()
                if tok.type == TokenType.DATE:
                    dates.append(self._advance().value)
                else:
                    title_parts.append(self._advance().value)
            self._match(TokenType.NEWLINE)

            # Split title_parts by dash/pipe to get title and company
            title_text = " ".join(title_parts)
            for sep in [" | ", " - ", " – ", " — ", ", "]:
                if sep in title_text:
                    parts = title_text.split(sep, 1)
                    entry.title = parts[0].strip()
                    entry.company = parts[1].strip()
                    break
            else:
                entry.title = title_text.strip()

            # Assign dates
            if len(dates) >= 2:
                entry.start_date = dates[0]
                entry.end_date = dates[1]
            elif len(dates) == 1:
                entry.end_date = dates[0]

            # Check next line for additional dates
            self._skip_newlines()
            if not self._at_end() and self._check(TokenType.DATE):
                additional_dates = []
                while self._check(TokenType.DATE):
                    additional_dates.append(self._advance().value)
                    self._match(TokenType.DASH)
                if not entry.start_date and len(additional_dates) >= 1:
                    entry.start_date = additional_dates[0]
                if not entry.end_date and len(additional_dates) >= 2:
                    entry.end_date = additional_dates[1]
                elif not entry.end_date and len(additional_dates) == 1:
                    entry.end_date = additional_dates[0]
                self._match(TokenType.NEWLINE)

            # Parse bullet points
            while not self._at_end() and not self._check(TokenType.HEADER):
                self._skip_newlines()
                if self._at_end() or self._check(TokenType.HEADER):
                    break

                # If we hit a bullet, it's a bullet point for this entry
                if self._check(TokenType.BULLET):
                    self._advance()  # consume bullet
                    bullet_words = []
                    while not self._at_end() and not self._check(
                        TokenType.NEWLINE, TokenType.HEADER, TokenType.BULLET
                    ):
                        bullet_words.append(self._advance().value)
                    entry.bullets.append(" ".join(bullet_words))
                    self._match(TokenType.NEWLINE)
                else:
                    # Not a bullet — probably a new entry title
                    # Check if this line has mostly WORDs (new entry)
                    next_tok = self._peek()
                    if next_tok.type == TokenType.WORD:
                        break
                    else:
                        self._advance()

            if entry.title:
                entries.append(entry)

        return entries

    # ── Education section ─────────────────────────────────────────────────

    def _parse_education_body(self, section):
        entries = []

        while not self._at_end() and not self._check(TokenType.HEADER):
            self._skip_newlines()
            if self._at_end() or self._check(TokenType.HEADER):
                break

            entry = EducationNode(line=self._peek().line)
            line_words = []
            dates = []
            gpa_value = None

            # Consume lines until we hit a blank line, header, or new entry
            lines_consumed = 0
            while not self._at_end() and not self._check(TokenType.HEADER):
                tok = self._peek()

                if tok.type == TokenType.NEWLINE:
                    self._advance()
                    lines_consumed += 1
                    # Two consecutive newlines = end of entry
                    if self._check(TokenType.NEWLINE):
                        break
                    # If next line starts with a degree keyword, it's a new entry
                    if not self._at_end() and self._peek().type == TokenType.WORD:
                        next_lower = self._peek().value.lower()
                        if next_lower in DEGREE_KEYWORDS and lines_consumed > 1:
                            break
                    continue

                if tok.type == TokenType.DATE:
                    dates.append(self._advance().value)
                elif tok.type == TokenType.WORD:
                    word = self._advance().value
                    lower = word.lower()
                    if lower in GPA_KEYWORDS:
                        # Next token might be the GPA value
                        self._match(TokenType.COLON)
                        if self._check(TokenType.NUMBER):
                            gpa_value = self._advance().value
                    else:
                        line_words.append(word)
                elif tok.type == TokenType.NUMBER:
                    num_val = self._advance().value
                    # Check if this is a GPA
                    try:
                        fval = float(num_val)
                        if 0 < fval <= 10 and gpa_value is None:
                            gpa_value = num_val
                        else:
                            line_words.append(num_val)
                    except ValueError:
                        line_words.append(num_val)
                elif tok.type == TokenType.DASH:
                    self._advance()
                else:
                    self._advance()

            # Assign fields from collected words
            full_text = " ".join(line_words)

            # Try to find a degree keyword in the text
            for dkw in sorted(DEGREE_KEYWORDS, key=len, reverse=True):
                if dkw in full_text.lower():
                    entry.degree = dkw.upper()
                    # The rest is institution/field
                    idx = full_text.lower().find(dkw)
                    remaining = (full_text[:idx] + full_text[idx+len(dkw):]).strip(" -,")
                    if remaining:
                        # Try to split into institution and field
                        for sep in [" in ", " of ", ", "]:
                            if sep in remaining.lower():
                                parts = remaining.split(sep, 1)
                                entry.institution = parts[0].strip()
                                entry.field = parts[1].strip()
                                break
                        else:
                            entry.institution = remaining
                    break
            else:
                # No degree keyword found — use full text as institution
                entry.institution = full_text if full_text else None

            if len(dates) >= 2:
                entry.start_date = dates[0]
                entry.end_date = dates[1]
            elif len(dates) == 1:
                entry.end_date = dates[0]

            entry.gpa = gpa_value

            if entry.institution or entry.degree:
                entries.append(entry)

        return entries

    # ── Certifications section ────────────────────────────────────────────

    def _parse_certifications_body(self, section):
        entries = []

        while not self._at_end() and not self._check(TokenType.HEADER):
            self._skip_newlines()
            if self._at_end() or self._check(TokenType.HEADER):
                break

            if self._check(TokenType.BULLET):
                self._advance()

            words = []
            date_val = None
            while not self._at_end() and not self._check(
                TokenType.NEWLINE, TokenType.HEADER, TokenType.BULLET
            ):
                tok = self._peek()
                if tok.type == TokenType.DATE:
                    date_val = self._advance().value
                else:
                    words.append(self._advance().value)
            self._match(TokenType.NEWLINE)

            name = " ".join(words).strip(" -–—,")
            if name:
                cert = CertificationNode(name=name, line=section.line)
                cert.date = date_val
                # Try to split by dash for issuer
                for sep in [" - ", " – ", " — ", " by "]:
                    if sep in name:
                        parts = name.split(sep, 1)
                        cert.name = parts[0].strip()
                        cert.issuer = parts[1].strip()
                        break
                entries.append(cert)

        return entries

    # ── Projects section ──────────────────────────────────────────────────

    def _parse_projects_body(self, section):
        entries = []

        while not self._at_end() and not self._check(TokenType.HEADER):
            self._skip_newlines()
            if self._at_end() or self._check(TokenType.HEADER):
                break

            project = ProjectNode(line=self._peek().line)

            # Project title line
            title_words = []
            while not self._at_end() and not self._check(
                TokenType.NEWLINE, TokenType.HEADER
            ):
                tok = self._peek()
                if tok.type == TokenType.URL:
                    project.link = self._advance().value
                else:
                    title_words.append(self._advance().value)
            self._match(TokenType.NEWLINE)
            project.name = " ".join(title_words).strip(" -–—,:|")

            # Bullet points or description lines
            while not self._at_end() and not self._check(TokenType.HEADER):
                self._skip_newlines()
                if self._at_end() or self._check(TokenType.HEADER):
                    break

                if self._check(TokenType.BULLET):
                    self._advance()
                    desc_words = []
                    while not self._at_end() and not self._check(
                        TokenType.NEWLINE, TokenType.HEADER, TokenType.BULLET
                    ):
                        desc_words.append(self._advance().value)
                    project.description.append(" ".join(desc_words))
                    self._match(TokenType.NEWLINE)
                elif self._check(TokenType.WORD):
                    # Could be next project title — peek ahead
                    # If next line has bullets, this is a description
                    # Otherwise, it's a new project
                    break
                else:
                    break

            if project.name:
                entries.append(project)

        return entries

    # ── Generic section (fallback) ────────────────────────────────────────

    def _parse_generic_body(self, section):
        entries = []

        while not self._at_end() and not self._check(TokenType.HEADER):
            self._skip_newlines()
            if self._at_end() or self._check(TokenType.HEADER):
                break

            words = []
            while not self._at_end() and not self._check(
                TokenType.NEWLINE, TokenType.HEADER
            ):
                words.append(self._advance().value)
            self._match(TokenType.NEWLINE)

            text = " ".join(words).strip()
            if text:
                entries.append(EntryNode(content=text, line=self._peek().line))

        return entries
