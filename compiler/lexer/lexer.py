"""
Resume Lexer — Lexical Analysis
=================================
Reads raw resume text character by character and produces a stream of
typed tokens. Implements a state-machine approach with lookahead for
multi-character patterns (dates, emails, URLs, phone numbers).

No external libraries are used — all pattern recognition is hand-built.
"""

from .tokens import Token, TokenType

# ── Section headers recognized by the lexer ──────────────────────────────────
# Each key is the canonical name; values are alternative spellings.
SECTION_HEADERS = {
    "skills": [
        "skills", "technical skills", "technologies", "tech stack",
        "technical expertise", "core competencies", "competencies",
        "areas of expertise", "proficiencies", "tools & technologies",
        "tools and technologies", "programming languages", "languages",
        "frameworks", "tools",
    ],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "work history", "employment",
        "professional background", "career history", "internships",
        "internship experience", "relevant experience",
    ],
    "education": [
        "education", "academic background", "academics",
        "educational qualifications", "qualifications",
        "academic qualifications", "academic history",
    ],
    "certifications": [
        "certifications", "certificates", "professional certifications",
        "licenses & certifications", "licenses and certifications",
        "certification", "accreditations",
    ],
    "projects": [
        "projects", "personal projects", "academic projects",
        "key projects", "notable projects", "side projects",
        "project experience",
    ],
    "summary": [
        "summary", "objective", "profile", "professional summary",
        "career objective", "about me", "about", "personal statement",
        "career summary", "professional profile",
    ],
    "contact": [
        "contact", "contact information", "contact info",
        "personal information", "personal info", "personal details",
    ],
    "achievements": [
        "achievements", "awards", "honors", "honours",
        "awards & achievements", "accomplishments",
    ],
    "publications": [
        "publications", "research", "papers", "research papers",
    ],
    "references": [
        "references",
    ],
    "hobbies": [
        "hobbies", "interests", "hobbies & interests",
        "hobbies and interests", "extracurricular activities",
        "activities", "extracurricular",
    ],
}

# Build a flat lookup: lowered phrase → canonical section name
_HEADER_LOOKUP = {}
for canonical, aliases in SECTION_HEADERS.items():
    for alias in aliases:
        _HEADER_LOOKUP[alias.lower()] = canonical

# Longest known header alias is well under this; skip line-wide header work on huge lines.
_MAX_HEADER_LINE_CHARS = 96

# ── Month names for date detection ───────────────────────────────────────────
MONTH_NAMES = {
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept",
    "oct", "nov", "dec",
}

# ── Bullet characters ────────────────────────────────────────────────────────
BULLET_CHARS = set("•►▪▸▹◦◆◇■□●○➤➢➣⁃‣⮞")


class Lexer:
    """
    Character-level lexer for resume text.

    Usage:
        lexer = Lexer(raw_text, diagnostics)
        tokens = lexer.tokenize()
    """

    def __init__(self, text, diagnostics=None):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.diagnostics = diagnostics

    # ── Helpers ───────────────────────────────────────────────────────────

    def _peek(self, offset=0):
        """Return character at current position + offset, or ''."""
        idx = self.pos + offset
        return self.text[idx] if idx < len(self.text) else ""

    def _advance(self):
        """Consume the current character and return it."""
        ch = self.text[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _at_end(self):
        return self.pos >= len(self.text)

    def _emit(self, token_type, value, line, column):
        self.tokens.append(Token(token_type, value, line, column))

    def _remaining_on_line(self):
        """Return text from current position to end of line (exclusive)."""
        end = self.text.find("\n", self.pos)
        if end == -1:
            end = len(self.text)
        return self.text[self.pos:end]

    # ── Main entry ────────────────────────────────────────────────────────

    def tokenize(self):
        """
        Process the entire text and return a list of Tokens.
        """
        # Safety valve: a bug that fails to advance `pos` would otherwise spin forever.
        max_steps = len(self.text) + 4096
        steps = 0
        while not self._at_end():
            steps += 1
            if steps > max_steps:
                if self.diagnostics:
                    self.diagnostics.error(
                        "lexer",
                        "Lexer stopped early: iteration limit exceeded (malformed input or lexer bug).",
                    )
                break
            prev_pos = self.pos
            self._scan_token()
            if self.pos == prev_pos and not self._at_end():
                if self.diagnostics:
                    self.diagnostics.error(
                        "lexer",
                        "Lexer stuck: scanner did not advance position; forcing skip.",
                    )
                if self.pos < len(self.text):
                    self._advance()
                else:
                    break

        self._emit(TokenType.EOF, "", self.line, self.column)
        return self.tokens

    # ── Scanner dispatch ──────────────────────────────────────────────────

    def _scan_token(self):
        ch = self._peek()

        # ── Newline ──
        if ch == "\n":
            start_line, start_col = self.line, self.column
            self._advance()
            self._emit(TokenType.NEWLINE, "\n", start_line, start_col)
            return

        # ── Skip whitespace (non-newline) ──
        if ch in " \t\r":
            self._advance()
            return

        # ── Bullet characters ──
        if ch in BULLET_CHARS:
            start_line, start_col = self.line, self.column
            self._advance()
            self._emit(TokenType.BULLET, ch, start_line, start_col)
            return

        # ── Dash as bullet (at start of content on a line) ──
        if ch in "-*" and self.column <= 4:
            # Check if this looks like a bullet (beginning of line)
            next_ch = self._peek(1)
            if next_ch in " \t":
                start_line, start_col = self.line, self.column
                self._advance()
                self._emit(TokenType.BULLET, ch, start_line, start_col)
                return

        # ── Try multi-character patterns first ──
        if self._try_url():
            return
        if self._try_email():
            return
        if self._try_phone():
            return
        if self._try_date():
            return

        # ── Numbers ──
        if ch.isdigit():
            self._scan_number()
            return

        # ── Words (may form headers) ──
        if ch.isalpha() or ch == "_":
            self._scan_word_or_header()
            return

        # ── Single-character symbols ──
        start_line, start_col = self.line, self.column
        self._advance()
        sym_map = {
            ",": TokenType.COMMA,
            ":": TokenType.COLON,
            ";": TokenType.SEMICOLON,
            "|": TokenType.PIPE,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "/": TokenType.SLASH,
            "#": TokenType.HASH,
            ".": TokenType.DOT,
            "@": TokenType.AT,
            "+": TokenType.PLUS,
            "&": TokenType.AMPERSAND,
        }
        if ch in sym_map:
            self._emit(sym_map[ch], ch, start_line, start_col)
        elif ch in "-–—":
            self._emit(TokenType.DASH, ch, start_line, start_col)
        else:
            self._emit(TokenType.SYMBOL, ch, start_line, start_col)

    # ── Word / Header scanning ────────────────────────────────────────────

    def _scan_word_or_header(self):
        """
        Scan an alphabetic word. Then check if the current line
        (from this word onward) matches a known section header.
        """
        start_line = self.line
        start_col = self.column

        # Section headers are short; avoid scanning/stripping very long lines per word.
        end = self.text.find("\n", self.pos)
        if end == -1:
            end = len(self.text)
        if end - self.pos <= _MAX_HEADER_LINE_CHARS:
            rest = self.text[self.pos:end].strip()
            rest_clean = rest.rstrip(":").rstrip("-").rstrip("–").rstrip("—").strip()
            rest_lower = rest_clean.lower()
        else:
            rest_clean = None

        if rest_clean is not None and rest_lower in _HEADER_LOOKUP:
            canonical = _HEADER_LOOKUP[rest_lower]
            # Advance past the entire header text
            consumed = 0
            while consumed < len(rest_clean) and not self._at_end():
                self._advance()
                consumed += 1
            # Also consume trailing colon/dash/spaces before newline
            while not self._at_end() and self._peek() in ": \t-–—":
                self._advance()
            self._emit(TokenType.HEADER, canonical, start_line, start_col)
            return

        # Not a header — just scan a single word
        word = ""
        while not self._at_end():
            ch = self._peek()
            # Allow letters, digits (inside words like "H2O"), apostrophes,
            # hyphens between letters, dots for abbreviations (U.S.A),
            # plus and hash for C++, C#
            if ch.isalpha() or ch == "'":
                word += self._advance()
            elif ch in "+-#" and word:
                # C++, C#
                word += self._advance()
            elif ch == "." and not self._at_end():
                # Dots in abbreviations (U.S.A, B.Tech) and
                # library names (Node.js, Express.js, React.js)
                next_after_dot = self._peek(1)
                if next_after_dot.isalpha():
                    word += self._advance()
                else:
                    break
            elif ch == "-" and word and not self._at_end():
                # Hyphenated word like "self-taught"
                next_after = self._peek(1)
                if next_after.isalpha():
                    word += self._advance()
                else:
                    break
            elif ch.isdigit() and word:
                # Allow digits inside words (e.g., "H2O", "web3")
                word += self._advance()
            else:
                break

        if word:
            self._emit(TokenType.WORD, word, start_line, start_col)

    # ── Number scanning ───────────────────────────────────────────────────

    def _scan_number(self):
        start_line, start_col = self.line, self.column
        num = ""
        while not self._at_end() and (self._peek().isdigit() or self._peek() == "."):
            num += self._advance()
        # Remove trailing dot if it's a sentence period, not a decimal
        if num.endswith(".") and (self._at_end() or not self._peek().isdigit()):
            num = num[:-1]
            # put the dot back
            self.pos -= 1
            self.column -= 1
        self._emit(TokenType.NUMBER, num, start_line, start_col)

    # ── Multi-character pattern matchers ──────────────────────────────────

    def _try_url(self):
        """Detect http://, https://, or www. prefixed URLs."""
        rest = self._remaining_on_line()
        for prefix in ("https://", "http://", "www."):
            if rest.lower().startswith(prefix):
                start_line, start_col = self.line, self.column
                url = ""
                while not self._at_end() and self._peek() not in " \t\n,;|()":
                    url += self._advance()
                # Strip trailing punctuation that's unlikely part of URL
                while url and url[-1] in ".,;:!?)":
                    url = url[:-1]
                    self.pos -= 1
                    self.column -= 1
                self._emit(TokenType.URL, url, start_line, start_col)
                return True
        return False

    def _try_email(self):
        """
        Detect email addresses by scanning ahead for the @ pattern.
        We look for: word-chars @ word-chars . word-chars
        """
        # Quick reject: current char must be alphanumeric
        if not self._peek().isalnum():
            return False

        rest = self._remaining_on_line()
        # Simple email pattern check via scanning
        at_pos = rest.find("@")
        if at_pos <= 0:
            return False

        # Check everything before @ is word-like
        local = rest[:at_pos]
        if not all(c.isalnum() or c in "._+-" for c in local):
            return False

        # Check something after @ has at least one dot
        after_at = rest[at_pos + 1:]
        dot_pos = after_at.find(".")
        if dot_pos <= 0:
            return False

        # Scan the full email
        start_line, start_col = self.line, self.column
        email = ""
        while not self._at_end() and self._peek() not in " \t\n,;|()":
            email += self._advance()
        # Strip trailing punctuation
        while email and email[-1] in ".,;:!?":
            email = email[:-1]
            self.pos -= 1
            self.column -= 1
        if "@" in email and "." in email.split("@")[-1]:
            self._emit(TokenType.EMAIL, email, start_line, start_col)
            return True
        else:
            # False positive — rewind
            self.pos -= len(email)
            self.column -= len(email)
            return False

    def _try_phone(self):
        """
        Detect phone numbers. Patterns:
          +91-XXXXX-XXXXX, (XXX) XXX-XXXX, XXX-XXX-XXXX, +1XXXXXXXXXX
        """
        ch = self._peek()
        if ch != "+" and not ch.isdigit():
            return False

        rest = self._remaining_on_line()
        # Count digits in the prefix
        digits_only = ""
        for c in rest:
            if c.isdigit():
                digits_only += c
            elif c in " \t":
                # stop if we hit text after a reasonable phone length
                if len(digits_only) >= 7:
                    break
            elif c in "+-(). ":
                continue
            else:
                break

        if len(digits_only) < 7 or len(digits_only) > 15:
            return False

        # Heuristic: a phone number is a sequence of digits/symbols
        # that has 7–15 digits total and starts with + or digit
        start_line, start_col = self.line, self.column
        phone = ""
        digit_count = 0
        while not self._at_end():
            c = self._peek()
            if c.isdigit():
                phone += self._advance()
                digit_count += 1
            elif c in "+-(). " and digit_count < 15:
                phone += self._advance()
            else:
                break

        phone = phone.strip()
        if digit_count >= 7:
            self._emit(TokenType.PHONE, phone, start_line, start_col)
            return True
        else:
            # Rewind
            self.pos = self.pos - len(phone)
            self.column = start_col
            self.line = start_line
            return False

    def _try_date(self):
        """
        Detect date patterns:
          - MM/YYYY, MM-YYYY, MM.YYYY
          - YYYY (standalone 4-digit year between 1950-2040)
          - Month YYYY (e.g., "January 2023", "Jan 2023")
          - "Present", "Current"
        """
        rest = self._remaining_on_line()
        rest_lower = rest.lstrip().lower()

        # "Present" or "Current" as date stand-in
        for keyword in ("present", "current", "ongoing", "till date"):
            if rest_lower.startswith(keyword):
                next_ch_idx = len(keyword)
                if next_ch_idx >= len(rest_lower) or not rest_lower[next_ch_idx].isalpha():
                    start_line, start_col = self.line, self.column
                    for _ in range(len(keyword)):
                        self._advance()
                    self._emit(TokenType.DATE, "Present", start_line, start_col)
                    return True

        # Month name followed by optional year
        for month in MONTH_NAMES:
            if rest_lower.startswith(month):
                # Check the character after month name isn't alphabetic
                after = len(month)
                if after < len(rest_lower) and rest_lower[after].isalpha():
                    continue
                start_line, start_col = self.line, self.column
                date_str = ""
                # Consume the month name
                for _ in range(len(month)):
                    date_str += self._advance()
                # Consume optional spaces + year
                while not self._at_end() and self._peek() in " \t":
                    date_str += self._advance()
                year = ""
                while not self._at_end() and self._peek().isdigit():
                    year += self._advance()
                    date_str += year[-1]
                if len(year) == 4:
                    self._emit(TokenType.DATE, date_str.strip(), start_line, start_col)
                    return True
                elif len(year) == 0:
                    # Just a month name alone — treat as a word, rewind
                    self.pos -= len(date_str)
                    self.column = start_col
                    self.line = start_line
                    return False
                else:
                    # Partial year — emit what we have
                    self._emit(TokenType.DATE, date_str.strip(), start_line, start_col)
                    return True

        # MM/YYYY or MM-YYYY or MM.YYYY patterns
        ch = self._peek()
        if ch.isdigit():
            # Look ahead for NN/NNNN or NN-NNNN pattern
            match = ""
            saved_pos = self.pos
            saved_line = self.line
            saved_col = self.column

            # Consume 1-2 digits
            d1 = ""
            while not self._at_end() and self._peek().isdigit() and len(d1) < 2:
                d1 += self._advance()

            sep = self._peek() if not self._at_end() else ""
            if sep in "/-." and len(d1) <= 2:
                self._advance()  # consume separator
                d2 = ""
                while not self._at_end() and self._peek().isdigit() and len(d2) < 4:
                    d2 += self._advance()
                if len(d2) == 4:
                    try:
                        year = int(d2)
                        month = int(d1) if d1 else 0
                        if 1950 <= year <= 2040 and (0 <= month <= 12):
                            date_val = f"{d1}{sep}{d2}"
                            self._emit(TokenType.DATE, date_val, saved_line, saved_col)
                            return True
                    except ValueError:
                        pass

            # Rewind — not a date
            self.pos = saved_pos
            self.line = saved_line
            self.column = saved_col

            # Standalone 4-digit year
            if ch.isdigit():
                saved_pos2 = self.pos
                saved_line2 = self.line
                saved_col2 = self.column
                digits = ""
                while not self._at_end() and self._peek().isdigit() and len(digits) < 5:
                    digits += self._advance()
                if len(digits) == 4:
                    try:
                        year = int(digits)
                        if 1950 <= year <= 2040:
                            # Make sure next char isn't a digit (not a bigger number)
                            if self._at_end() or not self._peek().isdigit():
                                self._emit(TokenType.DATE, digits, saved_line2, saved_col2)
                                return True
                    except ValueError:
                        pass
                # Rewind
                self.pos = saved_pos2
                self.line = saved_line2
                self.column = saved_col2

        return False
